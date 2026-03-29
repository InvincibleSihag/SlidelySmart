"""Agent tool definitions and executors for slide manipulation, HITL, and skills.

All tool schemas (Pydantic models) and their execution logic live here.
ALL_TOOLS and create_tool_executor() are injected into the graph builder by
the agent service — the graph module itself has no direct dependency on this file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.image_search import search_image
from app.core.schemas.presentation import (
    ElementMetadata,
    ElementStyle,
    ElementType,
    LayoutType,
    Presentation,
    Slide,
    SlideElement,
    ThemeType,
)

if TYPE_CHECKING:
    from app.services.orchestration.skills import SkillStore

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Tool Schemas (bound to the LLM)
# ---------------------------------------------------------------------------

class CreateSlide(BaseModel):
    """Create a new slide in the presentation.

    Use this tool to add a slide. Provide a unique id, layout type, and elements.
    Each element has an id, type, and content. Supported element types:
    title, subtitle, heading, text, bullets, numbered_list, image, quote, code, table, notes.
    """

    id: str = Field(..., description="Unique slide ID, e.g. 'slide-1'")
    layout: LayoutType = Field(..., description="Slide layout type")
    elements: list[SlideElement] = Field(
        ..., description="List of slide elements"
    )
    notes: str = Field(default="", description="Speaker notes for this slide")


class EditSlide(BaseModel):
    """Edit an existing slide by its ID.

    Provide the slide ID and the fields to update. Only provided fields will be changed.
    Use this for full rewrites (replacing all elements or changing layout).
    For single-element changes, prefer EditElement.
    """

    id: str = Field(..., description="ID of the slide to edit")
    elements: list[SlideElement] | None = Field(default=None, description="New elements (replaces all)")
    layout: LayoutType | None = Field(default=None, description="New layout type")
    notes: str | None = Field(default=None, description="New speaker notes")


class DeleteSlide(BaseModel):
    """Delete a slide from the presentation by its ID."""

    id: str = Field(..., description="ID of the slide to delete")


class ReorderSlides(BaseModel):
    """Reorder slides by providing the desired sequence of slide IDs."""

    slide_ids: list[str] = Field(..., description="Ordered list of slide IDs")


class EditElement(BaseModel):
    """Edit a single element within a slide by element ID.

    Use patch semantics: only provided fields are updated. Prefer this over
    EditSlide when changing a single element (e.g., updating one bullet point,
    changing a heading, modifying image metadata or style).
    """

    slide_id: str = Field(..., description="ID of the slide containing the element")
    element_id: str = Field(..., description="ID of the element to edit")
    content: str | list[str] | None = Field(default=None, description="New content (replaces existing)")
    table_data: list[list[str]] | None = Field(default=None, description="2D array for table elements. First row is the header row.")
    metadata: ElementMetadata | None = Field(default=None, description="Metadata updates (shallow-merged with existing)")
    type: ElementType | None = Field(default=None, description="New element type")
    style: ElementStyle | None = Field(default=None, description="Style overrides (shallow-merged with existing)")


class AddElement(BaseModel):
    """Add a new element to an existing slide.

    Use this to insert an element at a specific position or append to the end.
    """

    slide_id: str = Field(..., description="ID of the slide to add the element to")
    element: SlideElement = Field(..., description="The element to add")
    position: int | None = Field(default=None, description="Insert at this index. None = append to end.")


class RemoveElement(BaseModel):
    """Remove a single element from a slide by element ID."""

    slide_id: str = Field(..., description="ID of the slide containing the element")
    element_id: str = Field(..., description="ID of the element to remove")


class SetTheme(BaseModel):
    """Set the presentation's visual theme and optionally inject custom CSS.

    Available themes:
    - 'default': Clean, professional light theme with blue accents on white
    - 'dark': Dark background with light text and cyan accents
    - 'modern': Contemporary style with purple accents and subtle gradients

    Call this before creating slides to set the overall look, or call it
    later to change the theme retroactively (all slides update).
    Use custom_css for advanced overrides beyond the predefined themes.
    """

    theme: ThemeType = Field(..., description="Theme name to apply")
    custom_css: str | None = Field(
        default=None,
        description="Optional raw CSS appended after theme stylesheet for custom overrides",
    )


class SearchImage(BaseModel):
    """Search for a real image by description. Returns a URL to put in the image element's `content` field.

    Call this BEFORE creating or editing an image element so you have a real URL.
    Put the returned URL in the element's `content` field (not metadata).
    Write a specific, descriptive query that describes the photo you need.

    Good queries: "modern office team collaborating", "abstract blue technology network"
    Bad queries: "image", "picture", "photo"
    """

    query: str = Field(..., description="Descriptive search query for the image, e.g. 'startup team celebrating product launch'")
    orientation: Literal["landscape", "portrait", "squarish"] = Field(
        default="landscape",
        description="Image orientation — 'landscape' for wide slides, 'portrait' for tall visuals, 'squarish' for balanced",
    )


class AskHuman(BaseModel):
    """Ask the user a clarifying question when the request is ambiguous.

    Use when:
    - The topic is too broad and needs narrowing
    - Audience or purpose is unclear
    - Multiple valid interpretations exist
    - Key details are missing (number of slides, depth, style)
    """

    question: str = Field(..., description="Clear, specific question to ask the user")
    options: list[str] | None = Field(default=None, description="Optional choices if multiple-choice")
    form_type: Literal["single_choice", "multi_choice"] = Field(
        ..., description="Type of form to display to the user (single_choice or multi_choice)"
    )


class LoadSkill(BaseModel):
    """Load the full instructions for a skill.

    Use this when you need detailed guidance on a specific topic before
    creating or editing slides. The skill catalog in the system prompt
    lists available skills and their descriptions.
    """

    skill_name: str = Field(..., description="Name of the skill to load (from the catalog)")


class ReadSkillFile(BaseModel):
    """Read a reference file from within a skill's directory.

    Use this after loading a skill, when its instructions reference
    additional files (templates, specs, examples) for fine-grained detail.
    """

    skill_name: str = Field(..., description="Name of the skill")
    file_path: str = Field(
        ...,
        description="Relative path to the file within the skill directory (e.g., 'refs/layouts.md')",
    )


# ---------------------------------------------------------------------------
# Tool Collections
# ---------------------------------------------------------------------------

# Slide manipulation tools
SLIDE_TOOLS = [CreateSlide, EditSlide, EditElement, AddElement, RemoveElement, DeleteSlide, ReorderSlides, SetTheme, SearchImage, AskHuman]

# Skill knowledge tools (read-only, no slide side effects)
SKILL_TOOLS = [LoadSkill, ReadSkillFile]

# All tools bound to the LLM at initialization
ALL_TOOLS = SLIDE_TOOLS + SKILL_TOOLS


# ---------------------------------------------------------------------------
# Tool Executors — receive typed Presentation model
# ---------------------------------------------------------------------------

def _execute_create_slide(args: dict, presentation: Presentation) -> str:
    """Add a new slide to the presentation."""
    elements = [SlideElement.model_validate(e) for e in args["elements"]]
    slide = Slide(
        id=args["id"],
        layout=args["layout"],
        elements=elements,
        notes=args.get("notes", ""),
    )
    if any(s.id == slide.id for s in presentation.slides):
        return f"Error: Slide with id '{slide.id}' already exists. Use EditSlide to modify it."
    presentation.slides.append(slide)
    return f"Created slide '{slide.id}' with layout '{slide.layout}' and {len(slide.elements)} elements."


def _execute_edit_slide(args: dict, presentation: Presentation) -> str:
    """Modify an existing slide."""
    target_id = args["id"]
    for slide in presentation.slides:
        if slide.id == target_id:
            if args.get("elements") is not None:
                slide.elements = [SlideElement.model_validate(e) for e in args["elements"]]
            if args.get("layout") is not None:
                slide.layout = args["layout"]
            if args.get("notes") is not None:
                slide.notes = args["notes"]
            return f"Updated slide '{target_id}'."
    return f"Error: Slide '{target_id}' not found."


def _execute_delete_slide(args: dict, presentation: Presentation) -> str:
    """Remove a slide by ID."""
    target_id = args["id"]
    for i, slide in enumerate(presentation.slides):
        if slide.id == target_id:
            presentation.slides.pop(i)
            return f"Deleted slide '{target_id}'."
    return f"Error: Slide '{target_id}' not found."


def _execute_edit_element(args: dict, presentation: Presentation) -> str:
    """Edit a single element within a slide using patch semantics."""
    slide_id = args["slide_id"]
    element_id = args["element_id"]
    for slide in presentation.slides:
        if slide.id == slide_id:
            for element in slide.elements:
                if element.id == element_id:
                    if args.get("content") is not None:
                        element.content = args["content"]
                    if args.get("table_data") is not None:
                        element.table_data = args["table_data"]
                    if args.get("type") is not None:
                        element.type = args["type"]
                    if args.get("metadata") is not None:
                        existing_meta = element.metadata.model_dump(exclude_none=True) if element.metadata else {}
                        new_meta = args["metadata"] if isinstance(args["metadata"], dict) else args["metadata"]
                        merged = {**existing_meta, **new_meta}
                        # Re-validate through the union so the merged dict becomes the right typed model
                        element.metadata = SlideElement.model_validate(
                            {"id": element.id, "type": element.type, "metadata": merged},
                        ).metadata
                    if args.get("style") is not None:
                        existing = element.style.model_dump(exclude_none=True) if element.style else {}
                        merged = {**existing, **args["style"]}
                        element.style = ElementStyle.model_validate(merged)
                    return f"Updated element '{element_id}' in slide '{slide_id}'."
            return f"Error: Element '{element_id}' not found in slide '{slide_id}'."
    return f"Error: Slide '{slide_id}' not found."


def _execute_add_element(args: dict, presentation: Presentation) -> str:
    """Add a new element to an existing slide."""
    slide_id = args["slide_id"]
    for slide in presentation.slides:
        if slide.id == slide_id:
            new_element = SlideElement.model_validate(args["element"])
            if any(e.id == new_element.id for e in slide.elements):
                return f"Error: Element with id '{new_element.id}' already exists in slide '{slide_id}'."
            position = args.get("position")
            if position is not None:
                slide.elements.insert(position, new_element)
            else:
                slide.elements.append(new_element)
            return f"Added element '{new_element.id}' to slide '{slide_id}'."
    return f"Error: Slide '{slide_id}' not found."


def _execute_remove_element(args: dict, presentation: Presentation) -> str:
    """Remove a single element from a slide."""
    slide_id = args["slide_id"]
    element_id = args["element_id"]
    for slide in presentation.slides:
        if slide.id == slide_id:
            for i, element in enumerate(slide.elements):
                if element.id == element_id:
                    slide.elements.pop(i)
                    return f"Removed element '{element_id}' from slide '{slide_id}'."
            return f"Error: Element '{element_id}' not found in slide '{slide_id}'."
    return f"Error: Slide '{slide_id}' not found."


def _execute_set_theme(args: dict, presentation: Presentation) -> str:
    """Set the presentation theme and optional custom CSS."""
    presentation.theme = args["theme"]
    if args.get("custom_css") is not None:
        presentation.custom_css = args["custom_css"]
    return f"Theme set to '{presentation.theme}'."


def _execute_search_image(args: dict, presentation: Presentation) -> str:
    """Search for a real image and return its URL."""
    return search_image(args["query"], args.get("orientation", "landscape"))


def _execute_reorder_slides(args: dict, presentation: Presentation) -> str:
    """Reorder slides by ID sequence."""
    desired_order = args["slide_ids"]
    slide_map = {s.id: s for s in presentation.slides}
    missing = [sid for sid in desired_order if sid not in slide_map]
    if missing:
        return f"Error: Slides not found: {missing}"
    reordered = [slide_map[sid] for sid in desired_order]
    remaining = [s for s in presentation.slides if s.id not in set(desired_order)]
    presentation.slides = reordered + remaining
    return f"Reordered slides: {desired_order}"


# Registry: tool name -> executor function (slide tools only)
_SLIDE_EXECUTORS: dict[str, Callable[[dict, Presentation], str]] = {
    "CreateSlide": _execute_create_slide,
    "EditSlide": _execute_edit_slide,
    "EditElement": _execute_edit_element,
    "AddElement": _execute_add_element,
    "RemoveElement": _execute_remove_element,
    "DeleteSlide": _execute_delete_slide,
    "ReorderSlides": _execute_reorder_slides,
    "SetTheme": _execute_set_theme,
    "SearchImage": _execute_search_image,
}

# Names of skill tools for dispatch routing
_SKILL_TOOL_NAMES = frozenset(t.__name__ for t in SKILL_TOOLS)


# ---------------------------------------------------------------------------
# Skill Tool Executors
# ---------------------------------------------------------------------------

def _execute_load_skill(args: dict, skill_store: SkillStore) -> str:
    """Load full SKILL.md instructions for a skill."""
    return skill_store.load_skill(args["skill_name"])


def _execute_read_skill_file(args: dict, skill_store: SkillStore) -> str:
    """Read a reference file from a skill's directory."""
    return skill_store.read_skill_file(args["skill_name"], args["file_path"])


_SKILL_EXECUTORS: dict[str, Callable] = {
    "LoadSkill": _execute_load_skill,
    "ReadSkillFile": _execute_read_skill_file,
}


# ---------------------------------------------------------------------------
# Unified Tool Executor Factory
# ---------------------------------------------------------------------------

def create_tool_executor(
    skill_store: SkillStore | None = None,
) -> Callable[[str, dict, Presentation], str]:
    """Create a tool executor closure that captures the SkillStore.

    Returns a callable with signature ``(tool_name, tool_args, presentation) -> str``
    matching the ToolExecutorFn protocol used by the graph builder.

    Skill tools are dispatched to SkillStore (presentation unused).
    Slide tools are dispatched to the slide executors which receive a typed
    Presentation model and mutate it in place.
    """

    def _execute(tool_name: str, tool_args: dict, presentation: Presentation) -> str:
        logger.info("tool_invoked", tool=tool_name, args=tool_args)

        # Skill tools: dispatch to SkillStore (presentation unused)
        if tool_name in _SKILL_TOOL_NAMES and skill_store is not None:
            skill_executor = _SKILL_EXECUTORS.get(tool_name)
            if skill_executor:
                result = skill_executor(tool_args, skill_store)
                logger.info("skill_tool_executed", tool=tool_name, result_length=len(result))
                return result

        # Slide tools: dispatch to slide executors
        slide_executor = _SLIDE_EXECUTORS.get(tool_name)
        if slide_executor:
            result = slide_executor(tool_args, presentation)
            logger.info("tool_executed", tool=tool_name, result=result[:200])
            return result

        result = f"Unknown tool: {tool_name}"
        logger.warning("unknown_tool", tool=tool_name)
        return result

    return _execute
