"""Agent configuration."""

from typing import Type

from pydantic import BaseModel

from app.core.prompts.registry import PromptRegistry
from app.core.schemas.presentation import Presentation


class AgentConfig:
    """Configuration for a single agent type."""

    def __init__(
        self,
        name: str,
        output_type: Type[BaseModel],
        system_prompt_template: str,
        user_prompt_template: str,
        default_query: str,
        max_history_tokens: int = 100_000,
        max_model_calls: int = 40,
        recursion_limit: int = 100,
    ):
        self.name = name
        self.output_type = output_type
        self.system_prompt_template = system_prompt_template
        self.user_prompt_template = user_prompt_template
        self.default_query = default_query
        self.max_history_tokens = max_history_tokens
        self.max_model_calls = max_model_calls
        self.recursion_limit = recursion_limit


_CONFIG = AgentConfig(
    name="presentation",
    output_type=Presentation,
    system_prompt_template=PromptRegistry.SYSTEM_PROMPT,
    user_prompt_template=PromptRegistry.USER_PROMPT,
    default_query="Create a professional presentation on the given topic.",
    max_history_tokens=100_000,
    max_model_calls=40,
    recursion_limit=100,
)


def get_agent_config() -> AgentConfig:
    """Return the presentation agent configuration."""
    return _CONFIG
