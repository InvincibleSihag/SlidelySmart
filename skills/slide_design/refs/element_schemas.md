# Element Content Schemas

> **Tip**: For visual design patterns using these elements (big metrics, card callouts, accent headings), see `refs/design_recipes.md`.

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
- `padding` — e.g. `"16px"`, `"10px 20px"`
- `margin` — e.g. `"12px 0"`, `"0 auto"`
- `border_radius` — e.g. `"8px"`, `"50%"`
- `width` — e.g. `"80%"`, `"400px"`
- `max_width` — e.g. `"600px"`, `"100%"`
- `line_height` — e.g. `"1.6"`, `"28px"`

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
- **content**: `string` — Paragraph text. Max ~150 chars (1-2 short sentences).
- **metadata**: not used
- Tip: Anything longer belongs in speaker notes, not on the slide

## `bullets`
- **content**: `list[string]` — Each item is a bullet point.
- **metadata**: not used (except `{"column": "right"}` for two_column layout)
- Rules:
  - Maximum **5 bullets** per element (3 per column in two_column)
  - Each bullet under ~80 chars — must fit on one line
  - Start each bullet with an action verb or key noun

Example: `["Revenue up 25%", "Churn down to 3%", "5 new markets"]`

## `numbered_list`
- **content**: `list[string]` — Each string is one numbered item
- **metadata**: not used
- Use when: Order matters (steps, rankings, priorities)

## `image`
- **content**: `string` — The image URL. Call **SearchImage** first to get a real URL, then place it here. Never make up URLs.
- **metadata**: `{"alt": "string"}`
  - `alt`: Accessibility text describing the image

**Workflow**: Call `SearchImage(query="...")` → get back a real URL → put that URL in `content`.

Example:
```json
{
  "id": "el-3",
  "type": "image",
  "content": "<url from SearchImage>",
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
  - Max **4 data rows** + 1 header row, max **4 columns**
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
