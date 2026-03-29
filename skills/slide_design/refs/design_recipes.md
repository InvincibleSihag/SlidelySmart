# Design Recipes

Ready-to-use slide patterns. Each recipe shows the complete CreateSlide arguments for a specific visual effect. Adapt the accent colors to match your active theme (see SKILL.md for theme color values).

## Recipe 1: Hero Metric Slide

Use when a key number or statistic is the main point. Makes the metric impossible to miss.

**Layout**: `blank`

```json
{
  "id": "slide-X",
  "layout": "blank",
  "elements": [
    {
      "id": "el-1",
      "type": "text",
      "content": "47%",
      "style": {
        "font_size": "64px",
        "font_weight": "bold",
        "color": "#2563eb",
        "text_align": "center",
        "margin": "40px 0 16px 0"
      }
    },
    {
      "id": "el-2",
      "type": "text",
      "content": "Reduction in customer churn since Q1",
      "style": {
        "font_size": "20px",
        "text_align": "center",
        "color": "#475569"
      }
    }
  ],
  "notes": "This is our strongest result this quarter. Churn dropped from 8.2% to 4.3% after we launched the retention program in January."
}
```

**Why it works**: The oversized, accent-colored number creates an instant focal point. The subtle label below provides context without competing for attention.

## Recipe 2: Compelling Opening Slide

Use for the first slide. Sets the tone and hooks the audience.

**Layout**: `title`

```json
{
  "id": "slide-1",
  "layout": "title",
  "elements": [
    {
      "id": "el-1",
      "type": "title",
      "content": "The Quarter That Changed Everything"
    },
    {
      "id": "el-2",
      "type": "subtitle",
      "content": "Q3 2025 Performance Review — Engineering Division"
    }
  ],
  "notes": "Open with energy. This quarter saw our biggest launch in two years. Set the stage for the metrics that follow."
}
```

**Why it works**: The title hooks with a story ("Changed Everything") instead of being generic ("Q3 Report"). The subtitle provides the factual context.

## Recipe 3: Clean Comparison (Two-Column)

Use for comparing two options, before/after, or pros/cons.

**Layout**: `two_column`

```json
{
  "id": "slide-X",
  "layout": "two_column",
  "elements": [
    {
      "id": "el-1",
      "type": "heading",
      "content": "Cloud vs On-Premise",
      "style": {"color": "#2563eb"}
    },
    {
      "id": "el-2",
      "type": "bullets",
      "content": [
        "**Scalability** — Auto-scales with demand",
        "**Cost** — Pay only for what you use",
        "**Speed** — Deploy in minutes, not weeks"
      ]
    },
    {
      "id": "el-3",
      "type": "bullets",
      "content": [
        "**Control** — Full infrastructure ownership",
        "**Compliance** — Data never leaves your network",
        "**Predictability** — Fixed monthly costs"
      ],
      "metadata": {"column": "right"}
    }
  ],
  "notes": "Walk through each column. Acknowledge both sides have merit — the right choice depends on the use case."
}
```

**Why it works**: Bold lead words make each point scannable. The accent-colored heading signals this is an important comparison. Parallel structure between columns aids comprehension.

## Recipe 4: Key Insight Card

Use when a single important takeaway deserves visual emphasis.

**Layout**: `content`

```json
{
  "id": "slide-X",
  "layout": "content",
  "elements": [
    {
      "id": "el-1",
      "type": "heading",
      "content": "The Core Insight"
    },
    {
      "id": "el-2",
      "type": "text",
      "content": "Teams that adopted the new workflow shipped **2.3x faster** with **40% fewer bugs** — without increasing headcount.",
      "style": {
        "background_color": "#eff6ff",
        "padding": "28px 36px",
        "border_radius": "12px",
        "font_size": "22px",
        "line_height": "1.6"
      }
    }
  ],
  "notes": "Pause here. Let this sink in. The key selling point is that speed AND quality improved simultaneously — usually these are trade-offs."
}
```

**Why it works**: The card background creates a visual container that says "this is important." The larger font and generous padding make it feel like a callout, not just another paragraph.

## Recipe 5: Section Transition

Use between major topics. Provides visual breathing room and resets attention.

**Layout**: `section_header`

```json
{
  "id": "slide-X",
  "layout": "section_header",
  "elements": [
    {
      "id": "el-1",
      "type": "title",
      "content": "Traction & Results"
    },
    {
      "id": "el-2",
      "type": "subtitle",
      "content": "What we've achieved in the first 6 months"
    }
  ],
  "notes": "Transition: 'Now that we've covered the problem and our approach, let me show you the results.' Pause briefly before advancing."
}
```

**Why it works**: Minimal content lets the audience reset. The subtitle previews what's coming, creating anticipation.

## Recipe 6: Data Table with Context

Use when presenting tabular data. The heading tells the story; the table proves it.

**Layout**: `content`

```json
{
  "id": "slide-X",
  "layout": "content",
  "elements": [
    {
      "id": "el-1",
      "type": "heading",
      "content": "Engineering Velocity Doubled in Q3"
    },
    {
      "id": "el-2",
      "type": "table",
      "table_data": [
        ["Metric", "Q1", "Q2", "**Q3**"],
        ["PRs Merged/Week", "42", "58", "**94**"],
        ["Deploy Frequency", "Weekly", "2x/week", "**Daily**"],
        ["Incident Rate", "4.2/mo", "3.1/mo", "**1.8/mo**"]
      ]
    }
  ],
  "notes": "Point out that Q3 numbers (bolded) show improvement across all three metrics. The deploy frequency shift from weekly to daily was the biggest unlock."
}
```

**Why it works**: The heading tells the conclusion upfront ("Doubled") so the audience knows what to look for in the table. Bold formatting on the Q3 column draws the eye to the proof.

## Recipe 7: Quote + Attribution

Use for testimonials, expert opinions, or memorable statements.

**Layout**: `content`

```json
{
  "id": "slide-X",
  "layout": "content",
  "elements": [
    {
      "id": "el-1",
      "type": "heading",
      "content": "What Our Users Say"
    },
    {
      "id": "el-2",
      "type": "quote",
      "content": "This tool cut our onboarding time from two weeks to two days. I wish we'd found it sooner. — Sarah Chen, VP of Engineering at Acme Corp"
    }
  ],
  "notes": "Let the quote speak for itself. Sarah is a well-known figure in the industry — mention her background briefly if the audience doesn't know her."
}
```

**Why it works**: Quotes provide social proof and a human voice. The theme's quote styling (accent border, italic, background) makes it visually distinct from regular text.

## Recipe 8: Three-Point Summary

Use to wrap up a section or the whole deck with key takeaways.

**Layout**: `content`

```json
{
  "id": "slide-X",
  "layout": "content",
  "elements": [
    {
      "id": "el-1",
      "type": "heading",
      "content": "Key Takeaways"
    },
    {
      "id": "el-2",
      "type": "numbered_list",
      "content": [
        "**Velocity doubled** — Daily deploys with fewer incidents",
        "**Costs down 35%** — Cloud migration paid for itself in 4 months",
        "**Team morale up** — eNPS improved from 32 to 67"
      ]
    }
  ],
  "notes": "Recap these three points slowly. Each one maps to a section of the presentation. Ask if there are questions before moving to the closing slide."
}
```

**Why it works**: Three points is the sweet spot — memorable without overwhelming. Bold lead phrases make each takeaway scannable. Numbered list implies priority/order.

## Recipe 9: Strong Closing Slide

Use for the final slide. Leave a lasting impression with a clear call to action.

**Layout**: `title`

```json
{
  "id": "slide-X",
  "layout": "title",
  "elements": [
    {
      "id": "el-1",
      "type": "title",
      "content": "Ready to Ship Faster?"
    },
    {
      "id": "el-2",
      "type": "subtitle",
      "content": "Let's discuss next steps — reach out at team@example.com"
    }
  ],
  "notes": "End with confidence. Reiterate the main value proposition and make the next step obvious. Don't end with 'Questions?' — invite them to engage directly."
}
```

**Why it works**: A question as the title creates engagement. The subtitle provides a concrete next step. Much stronger than a generic "Thank You" or "Questions?" slide.

---

## Anti-Patterns to Avoid

### Wall of Bullets
More than 5 bullets on one slide. Audience tunes out after 3-4. **Fix**: Split into two slides, or promote the most important points and move the rest to speaker notes.

### Generic Headings
"Overview", "Details", "Summary", "Results". These headings say nothing. **Fix**: Be specific about what the slide communicates: "Revenue Grew 40% YoY", "Three Bottlenecks We Eliminated", "What Users Actually Want".

### Uniform Layouts
Five `content` slides in a row creates visual monotony. **Fix**: Insert `two_column`, `image_text`, `blank` (hero metric), or `section_header` slides to create rhythm.

### Style Overload
Styling every element on every slide — custom fonts, colors, sizes everywhere. **Fix**: Let the theme do the heavy lifting. Reserve `style` overrides for 1-2 emphasis elements per slide.

### Missing Speaker Notes
Slides without notes force presenters to either improvise or cram too much text on the slide. **Fix**: Write notes on every content slide. The slide shows the headline; the notes contain the story.

### Sentence-Heavy Slides
Full paragraphs on slides. People read ahead and stop listening. **Fix**: Shorten to punchy fragments. Move the full explanation to speaker notes.
