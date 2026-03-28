"""Presentation JSON schema — the structured output the agent builds via tools."""

from typing import Literal

from pydantic import BaseModel, Field


class SlideElement(BaseModel):
    """A single element within a slide (heading, bullet list, image, etc.)."""

    type: Literal[
        "title", "subtitle", "heading", "text", "bullets", "numbered_list",
        "image", "quote", "code", "table", "notes",
    ]
    content: str | list[str] | list[list[str]] | None = None
    metadata: dict | None = Field(default=None, description="Style hints, image URLs, etc.")


class Slide(BaseModel):
    """A single slide with layout and elements."""

    id: str = Field(..., description="Unique slide ID, e.g. 'slide-1'")
    layout: Literal["title", "content", "section_header", "two_column", "blank", "image_text"]
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
