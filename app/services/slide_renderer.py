"""Render slide JSON into HTML using Jinja2 templates."""

import re
from functools import lru_cache
from pathlib import Path

import mistune
from markupsafe import Markup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.schemas.presentation import Presentation, Slide

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "slides"
_THEMES_DIR = _TEMPLATES_DIR / "themes"


# ---------------------------------------------------------------------------
# Rich-text filter: inline markdown → HTML via mistune
# ---------------------------------------------------------------------------

# Inline-only renderer: converts **bold**, *italic*, `code`, [link](url)
# without wrapping in <p> tags or handling block-level elements.
_inline_md = mistune.create_markdown(escape=False)


def _rich_text(value: str | list) -> Markup:
    """Convert inline markdown to HTML. Returns Markup so Jinja2 won't re-escape."""
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    if not isinstance(value, str):
        return Markup(str(value))
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


# ---------------------------------------------------------------------------
# Theme CSS loading
# ---------------------------------------------------------------------------

@lru_cache(maxsize=16)
def _load_theme_css(theme: str) -> str:
    """Load base CSS + theme CSS, concatenated. Falls back to 'default' theme."""
    base_path = _THEMES_DIR / "base.css"
    base_css = base_path.read_text() if base_path.is_file() else ""

    theme_path = _THEMES_DIR / f"{theme}.css"
    if not theme_path.is_file():
        theme_path = _THEMES_DIR / "default.css"
    theme_css = theme_path.read_text() if theme_path.is_file() else ""

    return base_css + "\n" + theme_css


# ---------------------------------------------------------------------------
# Theme CSS variable extraction (for agent context)
# ---------------------------------------------------------------------------
# NOTE: @sawan - Regex is not good approach, for now this is fine
_AGENT_RELEVANT_VARS = frozenset({
    "--slide-bg", "--text-primary", "--text-secondary",
    "--accent", "--accent-light", "--accent-dark",
})


# NOTE: @sawan - Regex is not good pattern
@lru_cache(maxsize=8)
def get_theme_variables(theme: str) -> dict[str, str]:
    """Parse CSS custom properties from a theme file. Cached after first read.

    Returns a dict of agent-relevant CSS variable names to their values,
    e.g. ``{"--accent": "#1e3a6e", "--slide-bg": "#f8f9fc", ...}``.
    """
    theme_path = _THEMES_DIR / f"{theme}.css"
    if not theme_path.is_file():
        theme_path = _THEMES_DIR / "default.css"
    css = theme_path.read_text()
    props = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+)", css))
    return {k: v.strip() for k, v in props.items() if k in _AGENT_RELEVANT_VARS}


# ---------------------------------------------------------------------------
# Full presentation render
# ---------------------------------------------------------------------------


def render_presentation(presentation: Presentation) -> str:
    """Render all slides and return a self-contained HTML string with embedded CSS."""
    css = _load_theme_css(presentation.theme or "default")
    if presentation.custom_css:
        css += "\n" + presentation.custom_css

    slides_html = "\n".join(render_slide(s) for s in presentation.slides)
    return f"<style>\n{css}\n</style>\n{slides_html}"
