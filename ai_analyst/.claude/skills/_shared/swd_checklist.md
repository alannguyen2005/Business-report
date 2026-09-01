# SWD 6 Principles Checklist (Cole Nussbaumer Knaflic)

## Chart Type Selection

| Data relationship | Chart type | Never use |
|-------------------|-----------|-----------|
| Single number | Bold text (no chart) | -- |
| Trend over continuous time | `highlight_line` / `multi_line` | bar chart |
| Change between 2 time points | `slopegraph` | grouped bar |
| Comparison across categories | `vertical_bar` / `horizontal_bar` | pie, donut |
| Part-to-whole composition | `stacked_bar` | pie chart |
| Sequential change (bridge) | `waterfall` | stacked bar |
| Correlation 2 continuous vars | `scatter_regression` | -- |
| Magnitude + trend | `area` / `stacked_area` | -- |
| Segment x dimension pattern | `heatmap` | multiple lines |
| Historical + forecast + CI | `forecast_line` | bar |
| Model performance ranking | `model_comparison_bar` | radar |
| Feature importance | `feature_importance` | -- |
| Classification AUC | `roc_curve` | -- |
| Regression residuals | `residual_plot` | -- |
| Distribution shape | `histogram` / `box_plot` | -- |
| Ranking (many categories) | `dot_plot` | -- |
| Actual vs target | `bullet` | -- |
| Gap between 2 values | `connected_dot` | -- |
| Sensitivity / 2 groups | `diverging_bar` | -- |
| 80/20 analysis | `pareto` | -- |

**BANNED:** pie, donut, 3D, dual-axis, radar/spider

## Pre-flight QA (20 checks)

```
CONTEXT
[ ] Chart serves exactly ONE finding
[ ] Title = insight sentence (action verb + number, not a label)

VISUAL TYPE
[ ] Chart type matches data relationship (table above)
[ ] No pie, donut, 3D, dual-axis, radar

CLUTTER
[ ] No gridlines
[ ] No top/right spines
[ ] Left + bottom spines: #E2E8F0, linewidth 0.8
[ ] No legend box -- direct labels used
[ ] No rotated axis labels

FOCUS
[ ] MAX 1 highlight color -- everything else #D1D5DB
[ ] Highlight color encodes meaning (see palette below)
[ ] Max 3 annotations

DESIGN
[ ] Background = #FFFFFF (white)
[ ] Font = Inter (fallback: Calibri, Segoe UI)
[ ] Figure size = (8.0, 3.8) split or (11.0, 4.0) full
[ ] DPI = 150
[ ] tight_layout(pad=1.2) applied
[ ] Bar Y-axis starts at zero

STORY
[ ] Title answers "so what?" for the audience
[ ] Key annotation adds context (not just the number)
```

## Highlight Color by Section

| Section | Color | Hex |
|---------|-------|-----|
| Descriptive (What happened) | Blue | `#2B4EFF` |
| Diagnostic (Why it happened) | Red | `#EF4444` |
| Predictive (What's next) | Green | `#34D399` |
| Event / anomaly marker | Orange | `#FF6B2B` |
| Non-highlighted | Gray | `#D1D5DB` |
