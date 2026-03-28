"""Render slide JSON into HTML using Jinja2 templates."""

from pathlib import Path

import mistune
from markupsafe import Markup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.schemas.presentation import Presentation, Slide

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "slides"


# ---------------------------------------------------------------------------
# Rich-text filter: inline markdown → HTML via mistune
# ---------------------------------------------------------------------------

# Inline-only renderer: converts **bold**, *italic*, `code`, [link](url)
# without wrapping in <p> tags or handling block-level elements.
_inline_md = mistune.create_markdown(escape=False, renderer=mistune.html)


def _rich_text(value: str) -> Markup:
    """Convert inline markdown to HTML. Returns Markup so Jinja2 won't re-escape."""
    if not isinstance(value, str):
        return value
    # mistune wraps output in <p>...</p> — strip it for inline use
    result = _inline_md(value).strip()
    if result.startswith("<p>") and result.endswith("</p>"):
        result = result[3:-4]
    return Markup(result)


# ---------------------------------------------------------------------------
# Jinja2 environment
# ---------------------------------------------------------------------------

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(enabled_extensions=("html",), default_for_string=True),
    trim_blocks=True,
    lstrip_blocks=True,
)
_env.filters["rich_text"] = _rich_text


def render_slide(slide: Slide) -> str:
    """Render a single slide to HTML string."""
    template = _env.get_template(f"{slide.layout}.html.j2")
    return template.render(slide=slide)


def render_presentation(presentation: Presentation) -> str:
    """Render all slides and return a single HTML string."""
    return "\n".join(render_slide(s) for s in presentation.slides)
