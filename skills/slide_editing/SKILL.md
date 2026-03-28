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
4. **Use the right tool**:
   - `EditSlide` — change content, layout, or notes of an existing slide
   - `DeleteSlide` — remove a slide entirely
   - `CreateSlide` — add new slides (use IDs that don't conflict with existing ones)
   - `ReorderSlides` — change slide order (must include ALL slide IDs)

## Common Edit Patterns

### Adding content to existing slides
Use EditSlide with the full elements array. Elements are replaced wholesale — you must include both the unchanged and new elements.

### Inserting slides between existing ones
1. CreateSlide with the new content
2. ReorderSlides with the complete desired order including the new slide

### Restructuring a section
1. Review the section's slides
2. Edit, delete, or create as needed
3. ReorderSlides to set the final order

### Changing the theme or style
Edit each affected slide individually. There is no batch-update tool.

## ID Conventions

- Existing slides keep their original IDs
- New slides should use IDs that continue the existing pattern (e.g., if slides go up to "slide-8", start new ones at "slide-9")
- Never reuse a deleted slide's ID in the same edit session

## Reference Files

For concrete examples, use `ReadSkillFile`:
- `refs/edit_examples.md` — Before/after tool call examples for common operations
