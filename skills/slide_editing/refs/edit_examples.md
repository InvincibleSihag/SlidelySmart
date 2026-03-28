# Edit Operation Examples

Concrete before/after examples for common edit operations.

## Example 1: Update bullet points on a slide

**User request**: "Add 'Global expansion' to the strategy slide"

**Existing slide**:
```json
{
  "id": "slide-4",
  "layout": "content",
  "elements": [
    {"type": "heading", "content": "Strategic Priorities"},
    {"type": "bullets", "content": ["Product innovation", "Customer retention", "Cost optimization"]}
  ]
}
```

**Tool call**:
```json
{
  "tool": "EditSlide",
  "args": {
    "id": "slide-4",
    "elements": [
      {"type": "heading", "content": "Strategic Priorities"},
      {"type": "bullets", "content": ["Product innovation", "Customer retention", "Cost optimization", "Global expansion"]}
    ]
  }
}
```

Note: The full elements array is provided, including unchanged elements.

## Example 2: Insert a new slide between existing ones

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
      {"type": "heading", "content": "Meet the Team"},
      {"type": "bullets", "content": ["Alice — Engineering Lead", "Bob — Product Manager", "Carol — Design Director"]}
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

## Example 3: Delete slides and reorganize

**User request**: "Remove the Q2 and Q3 detail slides, keep only the summary"

**Tool calls** (in sequence):
```json
{"tool": "DeleteSlide", "args": {"id": "slide-5"}}
{"tool": "DeleteSlide", "args": {"id": "slide-6"}}
```

No ReorderSlides needed if the remaining slides are already in the correct order.

## Example 4: Change a slide's layout

**User request**: "Make the comparison slide use two columns"

**Tool call**:
```json
{
  "tool": "EditSlide",
  "args": {
    "id": "slide-3",
    "layout": "two_column",
    "elements": [
      {"type": "heading", "content": "Cloud vs On-Premise"},
      {"type": "bullets", "content": ["Scalable", "Pay-as-you-go", "Managed"]},
      {"type": "bullets", "content": ["Full control", "One-time cost", "Data sovereignty"]}
    ]
  }
}
```

Note: When changing layout, you typically need to restructure elements to match the new layout.
