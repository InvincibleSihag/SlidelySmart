"""LangGraph agent for presentation generation with tool-based slide manipulation.

Graph flow:
    START → call_model → [route] → handle_tool_calls → call_model (loop)
                                 → handle_hitl → call_model (loop)
                                 → finalize → END

The agent uses CreateSlide/EditSlide/DeleteSlide/ReorderSlides tools to build
the presentation incrementally. AskHuman triggers an interrupt for HITL.

All non-serializable dependencies (LLM, tool executor, pusher trigger) are
injected via PresentationGraphBuilder constructor — nothing is hardcoded.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, trim_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import AnyMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, interrupt

from app.core.config import settings
from app.core.logging import get_logger
from app.core.schemas.presentation import Presentation
from app.services.agents.config import AgentConfig
from app.services.agents.graph.state import AgentState, HITLRequest
from app.services.agents.graph.streaming import SupportsStream, TriggerFn, stream_model_response

logger = get_logger(__name__)

ToolExecutorFn = Callable[[str, dict, Presentation], str]


def _get_db_connection_string() -> str:
    """Get async-compatible connection string for checkpointer."""
    url = settings.database_url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class PresentationGraphBuilder:
    """Builds the presentation agent graph with injected dependencies.

    Non-serializable dependencies (model, tool executor, pusher trigger) are
    provided at construction time and captured by node closures, keeping the
    graph definition free of hardcoded imports.
    """

    def __init__(
        self,
        *,
        model: SupportsStream,
        model_without_tools: SupportsStream,
        tool_executor: ToolExecutorFn,
        trigger: TriggerFn,
        agent_config: AgentConfig,
    ) -> None:
        self._model = model
        self._model_without_tools = model_without_tools
        self._tool_executor = tool_executor
        self._trigger = trigger
        self._agent_config = agent_config

    # --- Node Functions ---

    def call_model(self, state: AgentState) -> dict:
        """Invoke LLM with trimmed history and return the streamed response.

        On the final allowed call (max_model_calls reached), the model is
        invoked without tools and with a finalization instruction so it
        produces a closing text response instead of more tool calls.
        """
        messages = trim_messages(
            state["messages"],
            strategy="last",
            max_tokens=self._agent_config.max_history_tokens,
            token_counter="approximate",
            include_system=True,
            start_on="human",
            allow_partial=False,
        )

        call_count = state.get("model_call_count", 0) + 1
        is_final_call = call_count >= self._agent_config.max_model_calls

        if is_final_call:
            logger.warning("Agent reached max turns, final_model_call", call_number=call_count, limit=self._agent_config.max_model_calls)
            model = self._model_without_tools
        else:
            model = self._model

        logger.info("call_model", message_count=len(state["messages"]), trimmed_count=len(messages), call_number=call_count)

        response = stream_model_response(
            model=model,
            messages=messages,
            channel=state.get("pusher_channel_id"),
            trigger=self._trigger,
        )
        return {"messages": [response], "model_call_count": call_count}

    def route_after_model(self, state: AgentState) -> str:
        """Route based on last message: tool calls -> handle appropriately, else -> finalize."""
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            ask_human_calls = [tc for tc in last.tool_calls if tc["name"] == "AskHuman"]
            if len(ask_human_calls) > 1:
                return "reject_multiple_hitl"
            if ask_human_calls:
                return "handle_hitl"
            return "handle_tool_calls"
        return "finalize"

    def reject_multiple_hitl(self, state: AgentState) -> dict:
        """Reject multiple parallel AskHuman calls; instruct model to ask one at a time."""
        logger.info("reject_multiple_ask_human")
        correction = HumanMessage(content=(
            "You invoked AskHuman multiple times in parallel. Only ONE question is allowed at a time. "
            "Please ask a single, most important clarifying question and invoke AskHuman only once."
        ))
        return {"messages": [correction]}

    def handle_hitl(self, state: AgentState) -> dict:
        """Pause for human input using interrupt().

        When resumed via Command(resume=value), that value becomes
        the return of interrupt() and flows as a ToolMessage.
        """
        last = state["messages"][-1]
        tool_call = next(tc for tc in last.tool_calls if tc["name"] == "AskHuman")

        hitl_request = HITLRequest(
            question=tool_call["args"].get("question", ""),
            form_type=tool_call["args"].get("form_type", "single_choice"),
            options=tool_call["args"].get("options"),
        )

        logger.info("handle_hitl_interrupt", question=hitl_request.question)
        human_response = interrupt(hitl_request.model_dump())

        tool_message = ToolMessage(content=str(human_response), tool_call_id=tool_call["id"])
        logger.info("handle_hitl_resumed", response=str(human_response)[:100])
        return {"messages": [tool_message]}

    def handle_tool_calls(self, state: AgentState) -> dict:
        """Execute slide manipulation tools and return ToolMessages."""
        last = state["messages"][-1]
        presentation = Presentation.model_validate(state.get("presentation") or {})
        tool_messages = []

        for tc in last.tool_calls:
            result_text = self._tool_executor(tc["name"], tc["args"], presentation)
            tool_messages.append(ToolMessage(content=result_text, tool_call_id=tc["id"]))

        # Emit slide count update via Pusher
        channel = state.get("pusher_channel_id")
        if channel:
            self._trigger(channel, "agent_status", {
                "stage": "processing",
                "message": f"Working on slides... ({len(presentation.slides)} slides so far)",
            })

        return {"messages": tool_messages, "presentation": presentation.model_dump()}

    def finalize(self, state: AgentState) -> dict:
        """Package the final presentation."""
        presentation = Presentation.model_validate(state.get("presentation") or {})
        logger.info("finalize", slide_count=len(presentation.slides))
        return {"presentation": presentation.model_dump()}

    # --- Graph Builder ---

    @asynccontextmanager
    async def build(self) -> AsyncIterator[CompiledStateGraph]:
        """Build the presentation agent graph.

        Must be used as an async context manager so the checkpointer's DB
        connection is properly managed.

        Flow:
            START -> call_model -> [route] -> handle_tool_calls -> call_model (loop)
                                           -> reject_multiple_hitl -> call_model (loop)
                                           -> handle_hitl -> call_model (loop)
                                           -> finalize -> END
        """
        builder = StateGraph(AgentState)

        builder.add_node("call_model", self.call_model)
        builder.add_node("reject_multiple_hitl", self.reject_multiple_hitl)
        builder.add_node("handle_hitl", self.handle_hitl)
        builder.add_node("handle_tool_calls", self.handle_tool_calls)
        builder.add_node("finalize", self.finalize)

        builder.add_edge(START, "call_model")
        builder.add_conditional_edges(
            "call_model",
            self.route_after_model,
            ["reject_multiple_hitl", "handle_hitl", "handle_tool_calls", "finalize"],
        )
        builder.add_edge("reject_multiple_hitl", "call_model")
        builder.add_edge("handle_hitl", "call_model")
        builder.add_edge("handle_tool_calls", "call_model")
        builder.add_edge("finalize", END)

        async with AsyncPostgresSaver.from_conn_string(_get_db_connection_string()) as checkpointer:
            await checkpointer.setup()
            yield builder.compile(checkpointer=checkpointer)


# --- Public API ---

async def run_graph(
    *,
    graph: CompiledStateGraph,
    thread_id: str,
    recursion_limit: int = 100,
    presentation: Presentation | None = None,
    initial_messages: list[AnyMessage] | None = None,
    resume_value: str | None = None,
    pusher_channel_id: str | None = None,
) -> dict:
    """Run or resume the graph.

    Single entry point for both flows:
    - Initial run: pass initial_messages
    - Resume: pass resume_value (from human response)

    Returns the final state dict which includes:
    - slides: list of slide dicts if complete
    - __interrupt__: if waiting for human input
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": recursion_limit,
    }

    if resume_value is not None:
        logger.info("run_graph_resume", thread_id=thread_id)
        return await graph.ainvoke(Command(resume=resume_value), config=config)

    logger.info("run_graph_initial", thread_id=thread_id, message_count=len(initial_messages or []))
    initial_state = {
        "messages": initial_messages or [],
        "presentation": (presentation or Presentation()).model_dump(),
        "pusher_channel_id": pusher_channel_id,
        "model_call_count": 0,
    }
    return await graph.ainvoke(initial_state, config=config)
