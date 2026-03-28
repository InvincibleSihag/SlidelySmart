---
name: slide_design
description: Slide layouts, element types, content schemas, and design best practices for creating presentations
tags: [design, layout, elements, creation]
---

# Slide Design

## Slide Layouts

Available layout types:
- `title` — Title slide with main title and subtitle
- `content` — Standard content slide with heading and body
- `section_header` — Section divider between major topics
- `two_column` — Two-column layout for comparisons or side-by-side content
- `blank` — Free-form slide with arbitrary elements
- `image_text` — Image placeholder alongside text content

## Slide Elements

Each slide contains elements. Every element must have an `id`, `type`, and `content`:

- `title` — Main title text (content: string)
- `subtitle` — Subtitle text (content: string)
- `heading` — Slide heading (content: string)
- `text` — Paragraph text (content: string)
- `bullets` — Bullet point list (content: list of strings)
- `numbered_list` — Numbered list (content: list of strings)
- `image` — Image placeholder (content: description string, metadata: {"url": "...", "alt": "..."})
- `quote` — Block quote (content: string)
- `code` — Code block (content: string, metadata: {"language": "python"})
- `table` — Table data (table_data: list of lists — first row is header)
- `notes` — Speaker notes (content: string)

## Element ID Convention

Every element must have a unique `id` within its slide. Use the pattern `el-{n}`:
- `el-1`, `el-2`, `el-3`, etc.
- IDs must be unique within the slide (not across slides)

## Rich Text

All text content supports inline markdown:
- `**bold**`, `*italic*`, `` `code` ``, `[link](url)`
- Use naturally in titles, headings, bullets, text, quotes, and table cells

## Element Styling

Any element can have an optional `style` object with visual overrides:
- `font_size`, `font_weight`, `font_style`, `color`, `text_align`, `background_color`, `opacity`
- Use sparingly for emphasis — don't style every element

## Design Best Practices

- Maximum 5-6 bullet points per slide
- Keep text concise — no full paragraphs on slides
- Use speaker notes for detailed explanations
- Vary layouts to keep the presentation engaging
- Include a clear title slide and closing slide
- Use section headers to break up major topics
- Use images and quotes to add visual interest
- Use **bold** and *italic* to highlight key phrases in text
- Use element `style` for emphasis on key metrics or headings, not for every element

## Two-Column Layout

For `two_column` layout, use `metadata.column` to assign elements to columns:
- Elements without column metadata → rendered in the left column
- Elements with `"metadata": {"column": "right"}` → rendered in the right column
- The heading element renders above both columns

## Layout Selection Guide

| Purpose | Recommended Layout |
|---|---|
| Opening / closing | `title` |
| Main content delivery | `content` |
| Topic transitions | `section_header` |
| Pros/cons, comparisons | `two_column` |
| Custom diagrams, charts | `blank` |
| Visual storytelling | `image_text` |

## Reference Files

For more detailed specs, use `ReadSkillFile`:
- `refs/layout_specs.md` — Per-layout recommended element combinations
- `refs/element_schemas.md` — Detailed content format specs with examples
