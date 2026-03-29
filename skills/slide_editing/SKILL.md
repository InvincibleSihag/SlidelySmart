---
name: slide_editing
description: Strategies and patterns for modifying existing presentations effectively
tags: [editing, modification, revision]
---

# Slide Editing

## Core Principles

1. **Review all existing slides first** — understand the current structure before making changes.
2. **Minimize disruption** — only modify what the user explicitly asks for. Preserve unchanged slides.
3. **Maintain consistency** — if you add new slides, match the style and layout patterns of existing ones.
4. **Use the most precise tool** — prefer surgical edits over wholesale replacements.

## Tool Selection Guide

| Scenario | Tool | Why |
|----------|------|-----|
| Change one element's content (a heading, a bullet list, etc.) | `EditElement` | Patch semantics — only touches the target element |
| Change an element's type (e.g., bullets → numbered_list) | `EditElement` | Set the `type` field |
| Add a new element to an existing slide | `AddElement` | Inserts at a specific position or appends |
| Remove one element from a slide | `RemoveElement` | Surgical removal by element ID |
| Replace ALL elements or change layout | `EditSlide` | Full replacement when restructuring |
| Remove an entire slide | `DeleteSlide` | Removes the whole slide |
| Add a brand new slide | `CreateSlide` | Creates with layout and elements |
| Change slide order | `ReorderSlides` | Must include ALL slide IDs |

## Common Edit Patterns

### Editing a single element
Use `EditElement` with the slide ID and element ID. Only provide the fields you want to change.

### Adding content to a slide
Use `AddElement` with the slide ID and the new element. Use `position` to control placement.

### Removing content from a slide
Use `RemoveElement` with the slide ID and element ID.

### Replacing all elements (layout change, full rewrite)
Use `EditSlide` with the full elements array. All elements must include `id`, `type`, and `content`.

### Inserting slides between existing ones
1. `CreateSlide` with the new content
2. `ReorderSlides` with the complete desired order including the new slide

### Restructuring a section
1. Review the section's slides
2. Edit, delete, or create as needed
3. `ReorderSlides` to set the final order

### Changing the theme or style
Use `SetTheme` to change the presentation-wide theme (default, dark, modern).
For per-element adjustments, use `EditElement` with `style` overrides.

## ID Conventions

- Existing slides keep their original IDs
- New slides should use IDs that continue the existing pattern (e.g., if slides go up to "slide-8", start new ones at "slide-9")
- Never reuse a deleted slide's ID in the same edit session
- Element IDs follow the pattern `el-{n}` within each slide (e.g., `el-1`, `el-2`)
- New elements added via `AddElement` must have unique IDs within the slide

## Reference Files

For concrete examples, use `ReadSkillFile`:
- `refs/edit_examples.md` — Before/after tool call examples for common operations
