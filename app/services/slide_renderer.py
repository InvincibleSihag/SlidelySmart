"""Render slide JSON into HTML using Jinja2 templates."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.schemas.presentation import Presentation, Slide

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "slides"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(enabled_extensions=("html",), default_for_string=True),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_slide(slide: Slide) -> str:
    """Render a single slide to HTML string."""
    template = _env.get_template(f"{slide.layout}.html.j2")
    return template.render(slide=slide)


def render_presentation(presentation: Presentation) -> str:
    """Render all slides and return a single HTML string."""
    return "\n".join(render_slide(s) for s in presentation.slides)
