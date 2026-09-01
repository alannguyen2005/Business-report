---
name: chart-render
description: >
  Render matplotlib PNG chart images for PPTX slide decks. Maps chart references from
  story_arc.json chart_requirements[], applies SWD 6 principles strictly, and outputs
  production-quality PNGs with a manifest file.
  Trigger: after data-storytelling, output_format = "pptx".
when_to_use: "chart images", "render PNG", "matplotlib charts", "pptx charts"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Glob, Write
model: sonnet
effort: high
version: "4.0"
---

# Skill: Chart Render

## Purpose
Render SWD-compliant matplotlib PNG chart images for PPTX slide decks.
All SWD rules are enforced **in code** by `scripts/render_charts_swd.py`.

**Reads:** `data/pipeline/{stem}/story_arc.json` -> `chart_requirements[]` (must have `data` field)
**Writes:** `data/pipeline/{stem}/chart_images/*.png` + `chart_images.json`

## Steps

### Step 1: Verify chart_requirements exist with data
Check that `story_arc.json` has `chart_requirements[]` and each entry contains a `data` field.
If `data` fields are missing -> run `data-storytelling` first.

### Step 2: Run the deterministic renderer
```bash
python3 scripts/render_charts_swd.py --stem {stem} --no-title
```
**That is the entire skill.** The script enforces all SWD rules in code.
`--no-title` suppresses chart titles from PNGs — slide builder adds titles as separate text boxes.

### Step 3: Verify output
Check `chart_images.json` manifest. Print total charts and any failures.

## Critical Rule
**NEVER write matplotlib code directly.** Always call `scripts/render_charts_swd.py`.

## References
- Chart type catalog + palette: `.claude/skills/_shared/chart_style_guide.md`
- SWD checklist + pre-flight QA: `.claude/skills/_shared/swd_checklist.md`
- Visual QA checks: `.claude/skills/_shared/visual_qa.md`
- Render patterns (unique): `references/chart_render_patterns.md`

## 23 Chart Types Available
See `_shared/chart_style_guide.md` for full table. Script supports:
vertical_bar, horizontal_bar, highlight_line, multi_line, waterfall, grouped_bar,
slopegraph, heatmap, forecast_line, feature_importance, scatter_regression,
model_comparison_bar, roc_curve, residual_plot, stacked_bar, histogram, dot_plot,
bullet, area, connected_dot, diverging_bar, box_plot, pareto

## Highlight Color by Section

| Section | Color | Hex |
|---------|-------|-----|
| Descriptive | Blue | `#2B4EFF` |
| Diagnostic | Red | `#EF4444` |
| Predictive | Green | `#34D399` |
| Event/anomaly | Orange | `#FF6B2B` |

## Output Schema

```json
{
  "generated_at": "ISO 8601",
  "total_charts": 8,
  "output_dir": "data/pipeline/{stem}/chart_images/",
  "charts": [
    {
      "chart_id": "monthly_trend",
      "filename": "monthly_trend.png",
      "chart_type": "highlight_line",
      "slide_order": 4,
      "title": "Crisis period Jul-Nov drove churn to 56.7% peak",
      "width_px": 1200,
      "height_px": 570,
      "dpi": 150
    }
  ]
}
```
