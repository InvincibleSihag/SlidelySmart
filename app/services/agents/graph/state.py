"""Agent state definitions."""

from typing import Annotated, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from app.core.schemas.presentation import Presentation


class HITLRequest(BaseModel):
    """Human-in-the-loop request sent to client when clarification is needed."""

    question: str = Field(..., description="The question to ask the user")
    options: list[str] | None = Field(default=None, description="Optional list of choices")
    form_type: Literal["single_choice", "multi_choice"] = Field(
        ..., description="Type of form to display to the user"
    )


class AgentState(BaseModel):
    """State for the presentation agent graph.

    Uses add_messages reducer for proper message accumulation.
    presentation holds a serialized Presentation dict (validated via Pydantic
    at every read/write boundary in graph nodes and tool executors).
    model_call_count tracks how many times the LLM has been invoked.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    presentation: Presentation  # Serialized Presentation — {title, theme, slides}
    pusher_channel_id: str | None
    model_call_count: int
