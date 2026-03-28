# Edit Operation Examples

Concrete before/after examples for common edit operations.

## Example 1: Update a single element's content

**User request**: "Add 'Global expansion' to the strategy slide"

**Existing slide**:
```json
{
  "id": "slide-4",
  "layout": "content",
  "elements": [
    {"id": "el-1", "type": "heading", "content": "Strategic Priorities"},
    {"id": "el-2", "type": "bullets", "content": ["Product innovation", "Customer retention", "Cost optimization"]}
  ]
}
```

**Tool call** (EditElement — surgical edit of just the bullets):
```json
{
  "tool": "EditElement",
  "args": {
    "slide_id": "slide-4",
    "element_id": "el-2",
    "content": ["Product innovation", "Customer retention", "Cost optimization", "Global expansion"]
  }
}
```

## Example 2: Add an element to an existing slide

**User request**: "Add a quote at the bottom of slide 3"

**Tool call** (AddElement):
```json
{
  "tool": "AddElement",
  "args": {
    "slide_id": "slide-3",
    "element": {"id": "el-4", "type": "quote", "content": "Innovation distinguishes between a leader and a follower. — Steve Jobs"}
  }
}
```

## Example 3: Remove an element

**User request**: "Remove the image from the team slide"

**Tool call** (RemoveElement):
```json
{
  "tool": "RemoveElement",
  "args": {
    "slide_id": "slide-5",
    "element_id": "el-3"
  }
}
```

## Example 4: Insert a new slide between existing ones

**User request**: "Add a team slide after the intro"

**Existing order**: slide-1 (intro), slide-2 (agenda), slide-3 (content)

**Step 1 — CreateSlide**:
```json
{
  "tool": "CreateSlide",
  "args": {
    "id": "slide-4",
    "layout": "content",
    "elements": [
      {"id": "el-1", "type": "heading", "content": "Meet the Team"},
      {"id": "el-2", "type": "bullets", "content": ["Alice — Engineering Lead", "Bob — Product Manager", "Carol — Design Director"]}
    ]
  }
}
```

**Step 2 — ReorderSlides**:
```json
{
  "tool": "ReorderSlides",
  "args": {
    "slide_ids": ["slide-1", "slide-4", "slide-2", "slide-3"]
  }
}
```

Note: ALL slide IDs must be included in the reorder, not just the new one.

## Example 5: Delete slides and reorganize

**User request**: "Remove the Q2 and Q3 detail slides, keep only the summary"

**Tool calls** (in sequence):
```json
{"tool": "DeleteSlide", "args": {"id": "slide-5"}}
{"tool": "DeleteSlide", "args": {"id": "slide-6"}}
```

No ReorderSlides needed if the remaining slides are already in the correct order.

## Example 6: Change a slide's layout (full rewrite with EditSlide)

**User request**: "Make the comparison slide use two columns"

**Tool call**:
```json
{
  "tool": "EditSlide",
  "args": {
    "id": "slide-3",
    "layout": "two_column",
    "elements": [
      {"id": "el-1", "type": "heading", "content": "Cloud vs On-Premise"},
      {"id": "el-2", "type": "bullets", "content": ["Scalable", "Pay-as-you-go", "Managed"]},
      {"id": "el-3", "type": "bullets", "content": ["Full control", "One-time cost", "Data sovereignty"], "metadata": {"column": "right"}}
    ]
  }
}
```

Note: When changing layout, you typically need to restructure elements. For `two_column` layout, mark right-column elements with `metadata.column = "right"`.

## Example 7: Change element type

**User request**: "Convert those bullet points into a numbered list"

**Tool call** (EditElement — change type only):
```json
{
  "tool": "EditElement",
  "args": {
    "slide_id": "slide-4",
    "element_id": "el-2",
    "type": "numbered_list"
  }
}
```

The content stays the same since both bullets and numbered_list use `list[str]`.

## Example 8: Style an element

**User request**: "Make the heading on slide 2 red and centered"

**Tool call** (EditElement — style only):
```json
{
  "tool": "EditElement",
  "args": {
    "slide_id": "slide-2",
    "element_id": "el-1",
    "style": {"color": "#e94560", "text_align": "center"}
  }
}
```

Style is shallow-merged with any existing style on the element.

## Example 9: Add rich text formatting

**User request**: "Bold the first bullet point on slide 4"

**Tool call** (EditElement — content with inline markdown):
```json
{
  "tool": "EditElement",
  "args": {
    "slide_id": "slide-4",
    "element_id": "el-2",
    "content": ["**Product innovation**", "Customer retention", "Cost optimization"]
  }
}
```

Use `**bold**`, `*italic*`, `` `code` ``, and `[link](url)` in any text content.
