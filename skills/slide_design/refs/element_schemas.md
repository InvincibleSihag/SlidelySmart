# Element Content Schemas

Detailed format specifications for each element type.

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
- **content**: `list[string]` — Each string is one bullet point
- **metadata**: not used
- Rules:
  - Maximum 6 bullets per slide
  - Each bullet should be one line (no sub-bullets)
  - Start each bullet with an action verb or key noun

Example content: `["Increased revenue by 25%", "Reduced churn to 3%", "Expanded to 5 new markets"]`

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
  "type": "code",
  "content": "def hello():\n    print('Hello, world!')",
  "metadata": {"language": "python"}
}
```

## `table`
- **content**: `list[list[string]]` — 2D array where the first row is the header
- **metadata**: not used
- Rules:
  - First row is always treated as the header
  - All rows must have the same number of columns
  - Keep tables small (max 5 columns, 6-8 data rows)

Example content:
```json
[
  ["Metric", "Q1", "Q2", "Q3"],
  ["Revenue", "$1.2M", "$1.5M", "$1.8M"],
  ["Users", "10K", "15K", "22K"]
]
```

## `notes`
- **content**: `string` — Speaker notes (not displayed on the slide itself)
- **metadata**: not used
- Alternative: Use the `notes` field on the slide object directly
