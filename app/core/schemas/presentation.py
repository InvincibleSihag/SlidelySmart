"""Presentation JSON schema — the structured output the agent builds via tools."""

from typing import Literal

from pydantic import BaseModel, Field

# Reusable type aliases for element types and layout types
ElementType = Literal[
    "title", "subtitle", "heading", "text", "bullets", "numbered_list",
    "image", "quote", "code", "table", "notes",
]

LayoutType = Literal["title", "content", "section_header", "two_column", "blank", "image_text"]


# ---------------------------------------------------------------------------
# Element Metadata — typed per element kind
# ---------------------------------------------------------------------------

class ImageMetadata(BaseModel):
    """Metadata for `image` elements."""

    url: str | None = Field(default=None, description="Direct image URL if available")
    alt: str = Field(..., description="Accessibility text describing the image")


class CodeMetadata(BaseModel):
    """Metadata for `code` elements — specifies the language for syntax highlighting."""

    language: str = Field(
        ...,
        description="Programming language for syntax highlighting, e.g. 'python', 'javascript', 'sql'",
    )


class ColumnMetadata(BaseModel):
    """Metadata for elements in a `two_column` layout — specifies column placement."""

    column: Literal["right"] = Field(
        ...,
        description="Set to 'right' to place this element in the right column. Left is the default.",
    )


# Union of all metadata types. The LLM picks the appropriate shape based on element type.
ElementMetadata = ImageMetadata | CodeMetadata | ColumnMetadata


# ---------------------------------------------------------------------------
# Element Style
# ---------------------------------------------------------------------------

class ElementStyle(BaseModel):
    """Per-element visual style overrides. All fields optional — theme defaults apply when absent."""

    font_size: str | None = Field(default=None, description="e.g. '24px', '1.5em'")
    font_weight: str | None = Field(default=None, description="e.g. 'bold', 'normal', '600'")
    font_style: str | None = Field(default=None, description="e.g. 'italic', 'normal'")
    color: str | None = Field(default=None, description="Text color, e.g. '#ff0000'")
    text_align: str | None = Field(default=None, description="e.g. 'left', 'center', 'right'")
    background_color: str | None = Field(default=None, description="Element background color")
    opacity: float | None = Field(default=None, description="0.0 - 1.0")


# ---------------------------------------------------------------------------
# Slide Element
# ---------------------------------------------------------------------------

class SlideElement(BaseModel):
    """A single element within a slide (heading, bullet list, image, etc.)."""

    id: str = Field(..., description="Unique element ID within the slide, e.g. 'el-1'")
    type: ElementType
    content: str | list[str] | None = None
    table_data: list[list[str]] | None = Field(
        default=None,
        description="2D array for table elements. First row is the header row.",
    )
    metadata: ElementMetadata | None = Field(
        default=None,
        description=(
            "Type-specific metadata. "
            "image elements: {url?, alt}. "
            "code elements: {language}. "
            "two_column right-side elements: {column: 'right'}."
        ),
    )
    style: ElementStyle | None = Field(default=None, description="Visual style overrides")


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
    theme: str = Field(default="default", description="Color scheme name")
    slides: list[Slide] = []


class SlideDeckPayload(BaseModel):
    """Unified payload for worker — handles both initial and resume flows."""

    slide_deck_id: str
    # Initial flow fields
    user_query: str | None = None
    # Resume flow field
    resume_value: str | None = None
