---
name: chart-data
description: >
  Generate D3.js-ready chart specifications for HTML reports. Maps chart_ids from
  report_context to chart types, extracts data series, builds annotations (AV-1 to AV-4),
  and produces chart_specs.json.
  Trigger: after context-builder, output_format = "html".
when_to_use: "D3 charts", "chart specs", "chart data", "html charts"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Chart Data

## Purpose
Generate D3.js-ready chart specifications for HTML reports. Maps each chart_id from report_context to the appropriate chart type, extracts data series, builds annotations following AV-1 through AV-4 rules, and writes chart_specs.json.

**Reads:** `data/pipeline/{stem}/report_context.json` · `data/pipeline/{stem}/descriptive_output.json` · `data/pipeline/{stem}/diagnostic_output.json` · `data/pipeline/{stem}/predictive_output.json` (if exists) · cleaned data file
**Writes:** `data/pipeline/{stem}/chart_specs.json`

**Read references:** `references/chart_guide.md` · `references/error_patterns.md` · `_shared/swd_checklist.md` · `_shared/visual_qa.md`

---

## Steps

### Step 1: Inventory Charts
Read `report_context.json` → extract all `chart_id` references from sections.

### Step 2: Map Chart Types
For each chart_id, determine the D3.js chart type based on data relationship:

| Data Relationship | Chart Type | D3 Implementation |
|-------------------|-----------|-------------------|
| Change over time | `highlight_line` | Line chart with highlight |
| Comparison (few categories) | `highlight_bar` | Horizontal bar with highlight |
| Part-to-whole | `waterfall` | Waterfall/bridge chart |
| Distribution | `histogram` | Binned histogram |
| Correlation | `scatter` | Scatter plot |
| Before/after | `slope` | Slope chart |
| Composition over time | `stacked_area` | Stacked area chart |
| Forecast with uncertainty | `forecast_line` | Line + confidence band |
| Heatmap/matrix | `heatmap` | D3 heatmap grid |

### Step 3: Extract Data Series
For each chart, query the appropriate source and build data arrays:
- Numeric values: round to meaningful precision (currency: 2 decimals, percentages: 1 decimal)
- Date labels: human-readable format (Jan, Feb... not 2026-01-01)
- Sort: chronological for time series, descending by value for bars
- Max 8 categories for bar charts, max 12 data points for line charts in small view

### Step 4: Build Annotations
Apply annotation rules AV-1 through AV-4 for each chart:

| Rule | Requirement |
|------|------------|
| **AV-1** | No opaque backgrounds — use `rgba(color, 0.08)` |
| **AV-2** | Offset ≥40px from data point, connected via arrow |
| **AV-3** | Uniform style within chart (fontSize, fontWeight, offset direction) |
| **AV-4** | High contrast: color in {#EF4444, #10B981, #1A202C}, weight ≥600, size ≥11px |

Max 3 annotations per chart.

### Step 5: Build Callout Text
For each chart, write the "So what:" callout:
- Prefix: always "So what:"
- Must include ≥1 specific number
- ≤20 words, 1 sentence

### Step 6: Assemble Chart Spec
For each chart, combine type, data, annotations, callout, and config:
```json
{
  "chart_id": "string",
  "chart_type": "string",
  "title": "string (insight, not label)",
  "subtitle": "string (data context)",
  "data": {"labels": [], "series": []},
  "annotations": [],
  "callout": "So what: ...",
  "config": {
    "width": "100%",
    "height": 400,
    "background": "#F7F6F2",
    "margin": {"top": 60, "right": 40, "bottom": 50, "left": 60},
    "show_gridlines": false,
    "spine_color": "#E2E8F0",
    "spines": ["bottom", "left"],
    "tooltip": true
  }
}
```

### Step 7: Write chart_specs.json
Write to `data/pipeline/{stem}/chart_specs.json`.

---

## Rules

**R-1:** Title = insight, not label. "Revenue fell 3 months" not "Monthly Revenue".
**R-2:** Background always `#F7F6F2` — never `#FFFFFF`.
**R-3:** Max 1 highlight color + gray for everything else. No rainbows.
**R-4:** Max 3 annotations per chart.
**R-5:** Callout starts with "So what:" and includes ≥1 number.
**R-6:** No gridlines. Only bottom + left spines visible, colored `#E2E8F0`.
**R-7:** Direct labels on data — no separate legend boxes.
**R-8:** All annotation backgrounds are rgba with 0.08 opacity (AV-1).
**R-9:** Run swd_checklist against every chart spec before writing output.
**R-10:** Run visual_qa checks — flag any label collision, contrast issue, or misleading axis.

---

## Output Schema

```json
{
  "generated_at": "ISO 8601",
  "total_charts": "int",
  "charts": [
    {
      "chart_id": "string",
      "chart_type": "highlight_line|highlight_bar|waterfall|histogram|scatter|slope|stacked_area|forecast_line|heatmap",
      "title": "string (insight)",
      "subtitle": "string (data context)",
      "data": {"labels": [], "series": [{"name": "string", "values": [], "highlight": "bool", "color": "hex"}]},
      "annotations": [{"type": "point|span|line", "data_index": "int", "text": "string", "style": {}}],
      "callout": "string (So what: ...)",
      "config": {}
    }
  ]
}
```
