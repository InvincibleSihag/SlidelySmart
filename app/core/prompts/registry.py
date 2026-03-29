"""Prompt registry: load and render Jinja templates by name."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

# app/core/prompts/registry.py -> app/prompts (3 levels up, then /prompts)
_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"
_env = Environment(
    loader=FileSystemLoader(str(_PROMPTS_DIR)),
    autoescape=select_autoescape(enabled_extensions=(), default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


class PromptRegistry:
    """Central registry of prompt template names. Add names here as you add .j2 files."""

    SYSTEM_PROMPT = "system_prompt.j2"
    USER_PROMPT = "user_prompt.j2"


def get_prompt(name: str, **context: Any) -> str:
    """Load and render a prompt template. Returns the rendered string."""
    template = _env.get_template(name)
    return template.render(**context).strip()
