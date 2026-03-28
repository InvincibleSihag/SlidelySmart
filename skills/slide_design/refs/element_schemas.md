# Element Content Schemas

Detailed format specifications for each element type.

Every element must have an `id` (unique within the slide, e.g. `el-1`), a `type`, and `content`.

## Rich Text (Inline Markdown)

All text content supports inline markdown formatting:
- `**bold text**` → renders as **bold**
- `*italic text*` → renders as *italic*
- `` `inline code` `` → renders as `code`
- `[link text](url)` → renders as a clickable link

Use rich text naturally in any string content — titles, headings, text, bullets, quotes, table cells.

## Element Style

Any element can have an optional `style` object for visual overrides:

```json
{
  "id": "el-1",
  "type": "heading",
  "content": "Key Results",
  "style": {
    "font_size": "32px",
    "font_weight": "bold",
    "color": "#e94560",
    "text_align": "center"
  }
}
```

Available style properties:
- `font_size` — e.g. `"24px"`, `"1.5em"`
- `font_weight` — e.g. `"bold"`, `"normal"`, `"600"`
- `font_style` — e.g. `"italic"`, `"normal"`
- `color` — text color, e.g. `"#ff0000"`
- `text_align` — e.g. `"left"`, `"center"`, `"right"`
- `background_color` — element background color
- `opacity` — `0.0` to `1.0`

Style is optional. When omitted, theme defaults apply.

## `title`
- **content**: `string` — The main title text
- **metadata**: not used
- Usage: One per slide, typically the first element

## `subtitle`
- **content**: `string` — Secondary text below the title
- **metadata**: not used
- Usage: Paired with `title` on title/section_header layouts

## `heading`
- **content**: `string` — Slide heading/topic
- **metadata**: not used
- Usage: Used on content, two_column, image_text layouts instead of `title`

## `text`
- **content**: `string` — Paragraph text. Keep concise (1-3 sentences).
- **metadata**: not used
- Tip: If you need more than 3 sentences, use speaker notes for the overflow

## `bullets`
- **content**: `list[string]` — Each item is a bullet point.
- **metadata**: not used (except `{"column": "right"}` for two_column layout)
- Rules:
  - Maximum 6 bullets per slide
  - Each bullet should be one line
  - Start each bullet with an action verb or key noun

Example: `["Revenue up 25%", "Churn down to 3%", "5 new markets"]`

## `numbered_list`
- **content**: `list[string]` — Each string is one numbered item
- **metadata**: not used
- Use when: Order matters (steps, rankings, priorities)

## `image`
- **content**: `string` — Description of the image (used as placeholder text)
- **metadata**: `{"url": "string (optional)", "alt": "string"}`
  - `url`: Direct image URL if available, otherwise omit
  - `alt`: Accessibility text describing the image

Example:
```json
{
  "id": "el-3",
  "type": "image",
  "content": "Bar chart showing quarterly revenue growth",
  "metadata": {"alt": "Revenue growth Q1-Q4 2024"}
}
```

## `quote`
- **content**: `string` — The quote text, optionally with attribution
- **metadata**: not used
- Format: `"Quote text here" — Attribution`

## `code`
- **content**: `string` — The code snippet
- **metadata**: `{"language": "string"}` — Programming language for syntax highlighting
- Supported languages: python, javascript, typescript, java, go, rust, sql, bash, html, css, json, yaml, and more

Example:
```json
{
  "id": "el-2",
  "type": "code",
  "content": "def hello():\n    print('Hello, world!')",
  "metadata": {"language": "python"}
}
```

## `table`
- **content**: not used (set to `null` or omit)
- **table_data**: `list[list[string]]` — 2D array where the first row is the header
- **metadata**: not used
- Rules:
  - First row is always treated as the header
  - All rows must have the same number of columns
  - Keep tables small (max 5 columns, 6-8 data rows)
  - Cell text supports inline markdown (bold, italic, etc.)

Example:
```json
{
  "id": "el-2",
  "type": "table",
  "table_data": [
    ["Metric", "Q1", "Q2", "Q3"],
    ["Revenue", "$1.2M", "**$1.5M**", "$1.8M"],
    ["Users", "10K", "15K", "*22K*"]
  ]
}
```

## `notes`
- **content**: `string` — Speaker notes (not displayed on the slide itself)
- **metadata**: not used
- Alternative: Use the `notes` field on the slide object directly
