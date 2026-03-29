---
name: slide_design
description: Slide layouts, element types, content schemas, and design best practices for creating presentations
tags: [design, layout, elements, creation]
---

# Slide Design

## Design-First Workflow

1. **Choose your theme** — Call SetTheme before any slide creation. Pick based on audience and tone, not habit.
2. **Plan your structure** — Decide slide count, layout sequence, and narrative arc before building. Think about the story, not just the content.
3. **Build with variety** — Alternate layouts. Never use `content` layout 3+ times in a row. Mix in `two_column`, `section_header`, `blank`, `image_text`.
4. **Apply visual hierarchy** — Style 1-2 key elements per slide to draw the eye. Leave the rest to theme defaults.
5. **Review and refine** — After building all slides, check: does the deck flow visually? Is there rhythm? Would the audience stay engaged?

## Themes

Use **SetTheme** to set the visual style before creating slides:

- `default` — Clean white canvas with confident blue accents. Professional, trustworthy, versatile. Best for: business presentations, quarterly reviews, client proposals, formal reports.
- `dark` — Deep slate background with luminous cyan accents. Sophisticated, technical, modern. Best for: tech talks, product launches, data presentations, conference stages, evening events.
- `modern` — Warm neutral background with bold teal accents and subtle gradients. Contemporary, energetic, creative. Best for: startup pitches, educational content, portfolio reviews, creative proposals.

**Always call SetTheme before creating slides.** The theme sets the visual foundation — colors, fonts, and decorative elements all flow from it. Don't default to `default` — choose based on the content and audience.

## Visual Hierarchy Techniques

The difference between a bland slide and a compelling one is visual hierarchy. Use these patterns:

### Big Number / Hero Metric
When a slide's main point is a number or statistic, make it dominant:
- Use a `text` element with style: `{"font_size": "56px", "font_weight": "bold", "color": "<accent>", "text_align": "center"}`
- Place a smaller `text` element below as the label/context (18-20px, secondary color)
- Works best on `blank` or `content` layouts
- Example accent colors: `#2563eb` (default), `#38bdf8` (dark), `#0d9488` (modern)

### Accent Headings
For the most important slides, style the heading with the theme's accent color:
- Add `"style": {"color": "<accent-color>"}` to the heading element
- Use sparingly — 2-3 slides per deck, not every slide
- Reserve for slides that carry the deck's key message

### Card Callout
To highlight a key insight or important statement:
- Use a `text` element with `"style": {"background_color": "<accent-light>", "padding": "24px 32px", "border_radius": "12px", "font_size": "20px"}`
- Creates a visually distinct "card" that draws the eye
- Works on any layout

### Theme Accent Colors Reference
When using style overrides, use colors that harmonize with the active theme:

| Theme | Accent | Accent Light | Accent Dark |
|-------|--------|--------------|-------------|
| `default` | `#2563eb` | `#eff6ff` | `#1d4ed8` |
| `dark` | `#38bdf8` | `rgba(56,189,248,0.10)` | `#0ea5e9` |
| `modern` | `#0d9488` | `rgba(13,148,136,0.08)` | `#0f766e` |

## Content Strategy

### Text Brevity
- **Bullet points**: 3-6 words each. Start with a verb or key noun.
- **Headings**: 2-6 words. Be specific ("Revenue Grew 40%" not "Financial Results").
- **No full sentences on slides.** If you need a sentence, it goes in speaker notes.
- **Titles should hook**: "The Quarter That Changed Everything" beats "Q3 Report".

### One Idea Per Slide
Each slide should answer ONE question or make ONE point. If you're covering two ideas, split into two slides. A 12-slide deck with clear slides beats an 8-slide deck with cluttered ones.

### Speaker Notes
Write notes on EVERY content slide. Notes should contain:
- What the presenter should SAY about this slide
- Context and details too verbose for the slide surface
- Transition phrasing to the next slide

## Deck Narrative Flow

Every presentation needs a story arc:
1. **Opening** (title layout) — Hook with a compelling title and clear subtitle
2. **Context** (1-2 slides) — Why this topic matters, set the stage
3. **Body** (core content) — Deliver the substance with varied layouts
4. **Synthesis** (1 slide) — Key takeaways or summary
5. **Closing** (title layout) — End with a clear call to action or memorable statement

## Slide Space Constraints

The slide canvas is **960x540px** (16:9) with **72px horizontal** and **56px vertical** padding. Content that overflows is **clipped and invisible**. Treat every slide as a fixed canvas — budget content tightly.

### Content Budgets by Layout

**`content` layout** (heading + ONE body element):
- Heading uses ~58px of vertical space
- **Bullets**: Maximum **5 items**. Each bullet ~39px. Keep each item under ~80 chars.
- **Numbered list**: Same as bullets — max 5 items
- **Table**: Maximum **4 data rows** + 1 header. Max **4 columns**. Each row ~41px.
- **Code block**: Maximum ~8 lines at default size
- **Text**: 1-2 short sentences, under ~150 chars. Longer text goes in speaker notes.
- **Quote**: 1 sentence max.

**`two_column` layout** (heading + two column bodies):
- Each column has **half the width** with 40px gap between them
- Keep bullets to **3 items per column** maximum
- Tables in columns: max 3 rows and 3 columns
- Text should be very brief per column

**`image_text` layout** (image + text side-by-side):
- Image takes left half, text takes right half
- Keep text-side to **2-3 bullets** or 1-2 short sentences

**`title` / `section_header` layouts**:
- Title + optional subtitle only. Keep title under ~60 chars, subtitle under ~80 chars.

**`blank` layout**:
- Best for hero metric slides (large number + label)
- Max 2-3 elements. Don't combine multiple large elements.

### Style Overrides Affect Space

When you use `style` overrides, the space budget shrinks:
- `font_size: "56px"` uses ~3x the space of default 18px
- `padding: "24px 32px"` adds 48px vertical
- `margin` adds to total height
- **Always account for styled elements when planning density**

### What Causes Overflow

1. **Too many bullets** — more than 5 on a content slide
2. **Too many table rows** — more than 5 total (header + 4 data)
3. **Large font + multiple elements** — a 32px heading + 5 bullets won't fit
4. **Excessive padding/margin** in style overrides
5. **Multiple body elements** — heading + bullets + text won't fit. Use ONE body element.
6. **Long bullet text that wraps** — each wrap adds ~29px. Keep bullets to one line.

### The Golden Rule

**Fewer elements, more slides.** Split content across two clean slides rather than cramming one. The audience sees what fits — everything else is lost.

## Slide Layouts

Available layouts: `title`, `content`, `section_header`, `two_column`, `blank`, `image_text`

| Purpose | Layout | Notes |
|---|---|---|
| Opening / closing | `title` | Keep it bold and minimal |
| Main content | `content` | One heading + one body element |
| Topic transitions | `section_header` | Visual breathing room between sections |
| Comparisons, side-by-side | `two_column` | Great for pros/cons, before/after |
| Metrics, custom, diagrams | `blank` | Full creative control |
| Visual + explanation | `image_text` | Image alongside text |

## Slide Elements

Types: `title`, `subtitle`, `heading`, `text`, `bullets`, `numbered_list`, `image`, `quote`, `code`, `table`, `notes`

Every element needs: `id` (e.g., `el-1`), `type`, and `content`. Optional: `style` (visual overrides), `metadata` (type-specific data).

### Element ID Convention
Use `el-{n}` pattern: `el-1`, `el-2`, `el-3`. IDs must be unique within the slide.

### Rich Text
All text supports inline markdown: `**bold**`, `*italic*`, `` `code` ``, `[link](url)`

Use **bold** to highlight key terms in bullets and text. Use sparingly — if everything is bold, nothing stands out.

## Element Styling

Any element can have an optional `style` object with visual overrides:
`font_size`, `font_weight`, `font_style`, `color`, `text_align`, `background_color`, `opacity`, `padding`, `margin`, `border_radius`, `width`, `max_width`, `line_height`

**Rule**: Style 1-2 elements per slide for emphasis. If you style everything, nothing stands out.

## Two-Column Layout

Elements default to the left column. Add `"metadata": {"column": "right"}` for right-column placement. The heading renders above both columns.

Common patterns:
- Bullets + bullets (comparisons)
- Text + image
- Bullets + table

## Reference Files

Use `ReadSkillFile` to access detailed specifications:
- `refs/layout_specs.md` — **Load when** deciding which elements work in each layout
- `refs/element_schemas.md` — **Load when** unsure about content format for any element type
- `refs/design_recipes.md` — **Load when** you need ready-to-use visual pattern examples with full JSON
- `refs/deck_templates.md` — **Load when** creating a full presentation from scratch (has standard structures for pitch decks, reports, etc.)
