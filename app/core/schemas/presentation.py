"""Presentation JSON schema — the structured output the agent builds via tools."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Reusable type aliases for element types and layout types
ElementType = Literal[
    "title", "subtitle", "heading", "text", "bullets", "numbered_list",
    "image", "quote", "code", "table", "notes",
]

LayoutType = Literal["title", "content", "section_header", "two_column", "blank", "image_text"]

ThemeType = Literal["default", "dark", "modern"]


# ---------------------------------------------------------------------------
# Element Metadata — typed per element kind
# ---------------------------------------------------------------------------

class ImageMetadata(BaseModel):
    """Metadata for `image` elements."""

    alt: str = Field(..., description="Accessibility text describing the image")


class CodeMetadata(BaseModel):
    """Metadata for `code` elements — specifies the language for syntax highlighting."""

    language: str = Field(
        ...,
        description="Programming language for syntax highlighting, e.g. 'python', 'javascript', 'sql'",
    )


class ColumnMetadata(BaseModel):
    """Metadata for elements in a `two_column` layout — specifies column placement."""

    column: Literal["left", "right"] = Field(
        ...,
        description="Which column to place this element in: 'left' or 'right'.",
    )


# Union of all metadata types. The LLM picks the appropriate shape based on element type.
ElementMetadata = ImageMetadata | CodeMetadata | ColumnMetadata


# ---------------------------------------------------------------------------
# Element Style
# ---------------------------------------------------------------------------

class ElementStyle(BaseModel):
    """Per-element visual style overrides. All fields optional — theme defaults apply when absent.

    The slide canvas is 960x540px. All sizes must fit within this space.
    Use style sparingly — 1-2 elements per slide for emphasis, not every element.
    """

    font_size: str | None = Field(
        default=None,
        description="CSS font size, 12px-72px range. e.g. '24px', '1.5em'. Larger sizes consume more vertical space.",
    )
    font_weight: str | None = Field(default=None, description="e.g. 'bold', 'normal', '600'")
    font_style: str | None = Field(default=None, description="e.g. 'italic', 'normal'")
    color: str | None = Field(default=None, description="Text color, e.g. '#2563eb'. Use theme accent colors.")
    text_align: str | None = Field(default=None, description="'left', 'center', or 'right'")
    background_color: str | None = Field(default=None, description="Element background color for card effects, e.g. '#eff6ff'")
    opacity: float | None = Field(default=None, ge=0.0, le=1.0, description="0.0 (transparent) to 1.0 (opaque)")
    padding: str | None = Field(
        default=None,
        description="Inner spacing. Non-negative, max ~60px per side. e.g. '16px', '10px 20px'. Adds to total height.",
    )
    margin: str | None = Field(
        default=None,
        description="Outer spacing. Non-negative, max ~60px per side. e.g. '12px 0', '0 auto'. Adds to total height.",
    )
    border_radius: str | None = Field(default=None, description="e.g. '8px', '12px'")
    width: str | None = Field(
        default=None,
        description="Element width. Use percentages (max 100%) or px (max 960px). e.g. '80%', '400px'.",
    )
    max_width: str | None = Field(default=None, description="e.g. '600px', '100%'. Cannot exceed 960px.")
    line_height: str | None = Field(default=None, description="e.g. '1.6', '28px'")


# ---------------------------------------------------------------------------
# Slide Element
# ---------------------------------------------------------------------------

class SlideElement(BaseModel):
    """A single element within a slide (heading, bullet list, image, etc.).

    Content limits (canvas is 960x540px, overflow is clipped):
    - bullets/numbered_list: max 5 items, each under ~80 chars (one line)
    - table: max 5 rows (1 header + 4 data), max 4 columns
    - text: max ~150 chars. Move longer content to speaker notes.
    - code: max ~8 lines at default font size
    """

    id: str = Field(..., description="Unique element ID within the slide, e.g. 'el-1'")
    type: ElementType
    content: str | list[str] | None = Field(
        default=None,
        description=(
            "Plain string for title, subtitle, heading, text, quote, code, and notes elements. "
            "For image elements: the image URL (from SearchImage). "
            "list[str] ONLY for bullets and numbered_list — each item becomes one bullet/list entry. "
            "Keep bullets to max 5 items, each under ~80 chars. Keep text under ~150 chars."
        ),
    )
    table_data: list[list[str]] | None = Field(
        default=None,
        description="2D array for table elements. First row is header. Max 5 rows (1 header + 4 data), max 4 columns.",
    )
    metadata: ElementMetadata | None = Field(
        default=None,
        description=(
            "Type-specific metadata. "
            "image elements: {alt}. "
            "code elements: {language}. "
            "two_column elements: {column: 'left' | 'right'}."
        ),
    )
    style: ElementStyle | None = Field(default=None, description="Visual style overrides. Use sparingly — 1-2 per slide.")


# ---------------------------------------------------------------------------
# Slide & Presentation
# ---------------------------------------------------------------------------

class Slide(BaseModel):
    """A single slide with layout and elements."""

    id: str = Field(..., description="Unique slide ID, e.g. 'slide-1'")
    layout: LayoutType
    elements: list[SlideElement] = []
    background: str | None = Field(default=None, description="Optional background color/gradient")
    notes: str = Field(default="", description="Speaker notes")


class Presentation(BaseModel):
    """Complete presentation structure."""

    title: str = ""
    theme: ThemeType = Field(
        default="default",
        description="Visual theme: 'default' (corporate navy), 'dark' (black & white minimalist), 'modern' (green contemporary)",
    )
    custom_css: str | None = Field(
        default=None,
        description="Optional custom CSS appended after the theme stylesheet for advanced overrides",
    )
    slides: list[Slide] = []


class SlideDeckPayload(BaseModel):
    """Unified payload for worker — handles both initial and resume flows."""

    slide_deck_id: str
    # Initial flow fields
    user_query: str | None = None
    # Resume flow field
    resume_value: str | None = None
