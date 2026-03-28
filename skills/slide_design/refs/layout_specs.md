# Layout Specifications

Detailed element recommendations for each layout type.

## `title` Layout

Primary use: Opening slide, closing slide, major section introductions.

Recommended elements:
- `title` (required) — The main presentation or section title
- `subtitle` (optional) — Tagline, author name, date, or brief description

Example:
```json
{
  "id": "slide-1",
  "layout": "title",
  "elements": [
    {"id": "el-1", "type": "title", "content": "The Future of AI"},
    {"id": "el-2", "type": "subtitle", "content": "How Artificial Intelligence is Reshaping Industries — March 2025"}
  ],
  "notes": "Welcome the audience. Set context for the presentation."
}
```

## `content` Layout

Primary use: Main body slides for delivering information.

Recommended elements:
- `heading` (required) — Slide topic
- One body element: `text`, `bullets`, `numbered_list`, `code`, `table`, or `quote`
- `notes` (optional) — Speaker notes for additional context

Tips:
- Don't combine multiple body element types on one content slide
- If you need both bullets and a table, use two slides or `two_column`

Example (with styled heading and rich text in bullets):
```json
{
  "id": "slide-3",
  "layout": "content",
  "elements": [
    {"id": "el-1", "type": "heading", "content": "Key Benefits", "style": {"color": "#e94560"}},
    {"id": "el-2", "type": "bullets", "content": ["**Increased efficiency** across all teams", "Cost reduction of *up to 40%*", "Better accuracy", "Scalability"]}
  ],
  "notes": "Emphasize the cost reduction point — it's the strongest selling point."
}
```

## `section_header` Layout

Primary use: Visual separator between major topics.

Recommended elements:
- `title` (required) — Section name
- `subtitle` (optional) — Brief description of what this section covers

Keep it minimal — section headers are visual breathers, not content-heavy slides.

## `two_column` Layout

Primary use: Comparisons, pros/cons, side-by-side data.

Recommended elements:
- `heading` (required) — Slide topic
- Two body elements: one for left column, one for right column
- Right column elements must have `"metadata": {"column": "right"}`
- Common patterns: bullets + bullets, text + image, bullets + table

Example:
```json
{
  "id": "slide-5",
  "layout": "two_column",
  "elements": [
    {"id": "el-1", "type": "heading", "content": "Cloud vs On-Premise"},
    {"id": "el-2", "type": "bullets", "content": ["Scalable", "Pay-as-you-go", "Managed services"]},
    {"id": "el-3", "type": "bullets", "content": ["Full control", "One-time cost", "Data sovereignty"], "metadata": {"column": "right"}}
  ]
}
```

## `blank` Layout

Primary use: Custom arrangements, diagrams, full-bleed images, or creative slides.

Any combination of elements is allowed. Use when standard layouts don't fit.

## `image_text` Layout

Primary use: Visual storytelling — image alongside explanatory text.

Recommended elements:
- `image` (required) — The visual element
- `text` or `bullets` (required) — Accompanying explanation
- `heading` (optional) — Slide title

Example:
```json
{
  "id": "slide-7",
  "layout": "image_text",
  "elements": [
    {"id": "el-1", "type": "heading", "content": "Our Team"},
    {"id": "el-2", "type": "image", "content": "Team photo at annual retreat", "metadata": {"alt": "Team photo"}},
    {"id": "el-3", "type": "text", "content": "A diverse team of 50+ engineers, designers, and product managers across 12 countries."}
  ]
}
```
