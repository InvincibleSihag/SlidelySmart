"""Agent service - single code path for running presentation agents.

Handles both initial runs and resume flows through the same function.
The only difference is whether resume_value is provided.

This is the composition root for agent dependencies: the LLM, tools, and
pusher trigger are constructed here and injected into the graph builder.
"""

from datetime import date
from typing import Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.prompts.registry import get_prompt
from app.core.schemas.presentation import Presentation
from app.db.managers.version import VersionManager
from app.services.orchestration.config import get_agent_config
from app.services.orchestration.graph.graph import PresentationGraphBuilder, run_graph
from app.services.orchestration.graph.state import HITLRequest
from app.services.orchestration.graph.tools import ALL_TOOLS, create_tool_executor
from app.services.orchestration.skills import SkillStore
from app.services.pusher import trigger as pusher_trigger

logger = get_logger(__name__)

MODEL_NAME = "gemini-3-flash-preview"

StatusCallback = Callable[[str, dict], None]


def _build_models() -> tuple[ChatGoogleGenerativeAI, ChatGoogleGenerativeAI]:
    """Construct the LLM with and without tools.

    Returns (model_with_tools, model_without_tools). The tool-free variant
    is used on the final call when max_model_calls is reached, forcing the
    model to produce a text response instead of more tool calls.
    """
    base_model = ChatGoogleGenerativeAI(model=MODEL_NAME, include_thoughts=True)
    return base_model.bind_tools(ALL_TOOLS), base_model


def _build_initial_messages(
    system_prompt: str,
    user_prompt: str,
) -> list:
    """Build initial message list with system prompt and user content."""
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]


def _build_user_prompt(
    user_query: str | None,
    template: str,
    default_query: str,
    slide_summary: str = "",
) -> str:
    """Build user prompt from template."""
    return get_prompt(
        template,
        today_date=date.today().isoformat(),
        user_query=user_query.strip() if user_query and user_query.strip() else default_query,
        slide_summary=slide_summary,
    )


def _build_system_prompt(
    template: str,
    skill_catalog: str = "",
) -> str:
    """Build system prompt from template."""
    return get_prompt(
        template,
        skill_catalog=skill_catalog,
    )


def _state_to_presentation(state: dict) -> Presentation | None:
    """Validate the presentation dict from graph state into a Presentation model."""
    pres_data = state.get("presentation")
    if not pres_data or not pres_data.get("slides"):
        return None
    return Presentation.model_validate(pres_data)


class AgentResult(BaseModel):
    """Result of an agent run."""

    model_config = {"arbitrary_types_allowed": True}

    complete: bool = False
    output: dict | None = None
    hitl_request: HITLRequest | None = None
    thread_id: str = ""
    messages: list = []  # LangChain message objects for persistence


async def run_agent(
    thread_id: str,
    on_status: StatusCallback,
    *,
    user_query: str | None = None,
    resume_value: str | None = None,
    pusher_channel_id: str | None = None,
    snapshot_messages: list | None = None,
    existing_presentation: Presentation | None = None,
    slide_deck_id: str | None = None,
    version_num: int | None = None,
) -> tuple[Presentation | None, AgentResult]:
    """Run or resume a presentation agent.

    Three flows via single entry point:
    - Initial run: provide user_query
    - Follow-up: provide user_query + snapshot_messages + existing_presentation
    - Resume: provide resume_value (human response to HITL question)

    Returns:
        Tuple of (presentation, agent_result)
        - If complete: (Presentation, AgentResult(complete=True))
        - If waiting: (None, AgentResult(hitl_request=...))
    """
    config = get_agent_config()
    is_resume = resume_value is not None
    is_followup = snapshot_messages is not None

    on_status("agent_status", {
        "message": "Resuming agent" if is_resume else "Agent is starting presentation generation",
        "stage": "resuming" if is_resume else "start",
    })

    logger.info(
        "run_agent",
        thread_id=thread_id,
        is_resume=is_resume,
        is_followup=is_followup,
    )

    # Construct non-serializable dependencies and inject into graph builder
    skill_store = SkillStore()
    model_with_tools, model_without_tools = _build_models()
    graph_builder = PresentationGraphBuilder(
        model=model_with_tools,
        model_without_tools=model_without_tools,
        tool_executor=create_tool_executor(skill_store),
        trigger=pusher_trigger,
        agent_config=config,
    )

    async with graph_builder.build() as graph:
        if is_resume:
            # HITL resume — checkpointer has state, just resume
            result = await run_graph(
                graph=graph,
                thread_id=thread_id,
                recursion_limit=config.recursion_limit,
                resume_value=resume_value,
            )
        elif is_followup:
            # Follow-up query — inject snapshot + new query
            history = [m for m in snapshot_messages if not isinstance(m, SystemMessage)]
            system_prompt = _build_system_prompt(
                config.system_prompt_template,
                skill_catalog=skill_store.catalog_text(),
            )

            slide_summary = ""
            if existing_presentation and existing_presentation.slides:
                slide_summary = VersionManager.format_slide_summary(existing_presentation)

            user_prompt = _build_user_prompt(
                user_query,
                config.user_prompt_template,
                config.default_query,
                slide_summary=slide_summary,
            )
            initial_messages = [
                SystemMessage(content=system_prompt),
                *history,
                HumanMessage(content=user_prompt),
            ]
            result = await run_graph(
                graph=graph,
                thread_id=thread_id,
                recursion_limit=config.recursion_limit,
                initial_messages=initial_messages,
                presentation=existing_presentation,
                pusher_channel_id=pusher_channel_id,
                slide_deck_id=slide_deck_id,
                version_num=version_num,
            )
        else:
            # First run — build from templates
            user_prompt = _build_user_prompt(
                user_query,
                config.user_prompt_template,
                config.default_query,
            )
            initial_messages = _build_initial_messages(
                _build_system_prompt(
                    config.system_prompt_template,
                    skill_catalog=skill_store.catalog_text(),
                ),
                user_prompt,
            )
            result = await run_graph(
                graph=graph,
                thread_id=thread_id,
                recursion_limit=config.recursion_limit,
                initial_messages=initial_messages,
                pusher_channel_id=pusher_channel_id,
                slide_deck_id=slide_deck_id,
                version_num=version_num,
            )

        # Check for interrupt (HITL request)
        if "__interrupt__" in result:
            interrupts = result["__interrupt__"]
            if interrupts:
                hitl_data = interrupts[0].value
                hitl_request = HITLRequest(**hitl_data)

                on_status("agent_status", {
                    "message": "Waiting for your input",
                    "stage": "waiting_for_input",
                    "hitl_request": hitl_request.model_dump(),
                })

                logger.info("run_agent_hitl", thread_id=thread_id, question=hitl_request.question)

                return None, AgentResult(
                    complete=False,
                    hitl_request=hitl_request,
                    thread_id=thread_id,
                )

        # Complete - build Presentation from slides
        presentation = _state_to_presentation(result)
        if presentation and presentation.slides:
            output_data = presentation.model_dump()
            on_status("agent_status", {
                "message": f"Presentation complete with {len(presentation.slides)} slides.",
                "stage": "complete",
            })
            logger.info("run_agent_complete", thread_id=thread_id, slide_count=len(presentation.slides))

            return presentation, AgentResult(
                complete=True,
                output=output_data,
                thread_id=thread_id,
                messages=[m for m in result.get("messages", []) if not isinstance(m, SystemMessage)],
            )

        # No output produced
        on_status("agent_status", {"message": "No output produced.", "stage": "error"})
        return None, AgentResult(complete=False, thread_id=thread_id)
