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

Each slide contains elements. Each element has a `type` and `content`:

- `title` — Main title text (content: string)
- `subtitle` — Subtitle text (content: string)
- `heading` — Slide heading (content: string)
- `text` — Paragraph text (content: string)
- `bullets` — Bullet point list (content: list of strings)
- `numbered_list` — Numbered list (content: list of strings)
- `image` — Image placeholder (content: description string, metadata: {"url": "...", "alt": "..."})
- `quote` — Block quote (content: string)
- `code` — Code block (content: string, metadata: {"language": "python"})
- `table` — Table data (content: list of lists — first row is header)
- `notes` — Speaker notes (content: string)

## Design Best Practices

- Maximum 5-6 bullet points per slide
- Keep text concise — no full paragraphs on slides
- Use speaker notes for detailed explanations
- Vary layouts to keep the presentation engaging
- Include a clear title slide and closing slide
- Use section headers to break up major topics
- Use images and quotes to add visual interest

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
