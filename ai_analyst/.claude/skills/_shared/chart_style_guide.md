# Chart Style Guide — Brand Palette v3

All charts are rendered by `scripts/render_charts_swd.py`.
Colors and fonts are sourced from `themes/_base.yaml` at runtime.
**NEVER write matplotlib code directly — call the script.**

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Background | `#FFFFFF` | Figure + axes background |
| Blue (primary) | `#2B4EFF` | Descriptive highlight |
| Red (alert) | `#EF4444` | Diagnostic highlight |
| Green (positive) | `#34D399` | Predictive highlight |
| Orange (warning) | `#FF6B2B` | Event / anomaly marker |
| Gray (neutral) | `#D1D5DB` | Non-highlighted elements |
| Spine/divider | `#E2E8F0` | Axis lines |
| Title text | `#080F1E` | Chart titles |
| Body text | `#475569` | Body content |
| Muted text | `#64748B` | Axis ticks, captions |

**Rule: ONE accent color per chart. Everything else #D1D5DB.**

## Fonts

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Title | Inter | 11pt | Bold | `#080F1E` |
| Axis ticks | Inter | 8pt | Regular | `#64748B` |
| Data labels (highlight) | Inter | 8pt | Bold | accent color |
| Data labels (neutral) | Inter | 8pt | Regular | `#64748B` |
| Annotations | Inter | 8pt | Bold | accent color |

## Figure Sizes

| Slot | Size | DPI |
|------|------|-----|
| Two-col panel | `(8.0, 3.8)` | 150 |
| Full-width | `(11.0, 4.0)` | 150 |

## 23 Chart Types Available

| # | chart_type | Aliases | Use when |
|---|-----------|---------|----------|
| 1 | `vertical_bar` | | Magnitude across categories |
| 2 | `horizontal_bar` | `highlight_bar` | Ranking (long labels) |
| 3 | `highlight_line` | | Trend + anomaly highlight |
| 4 | `multi_line` | `multi_line_highlight` | Compare series trajectories |
| 5 | `waterfall` | | Bridge / delta decomposition |
| 6 | `grouped_bar` | | Groups across categories |
| 7 | `slopegraph` | `slope` | Before/after 2 time points |
| 8 | `heatmap` | | Segment x dimension (blue gradient) |
| 9 | `forecast_line` | | Historical + forecast + CI |
| 10 | `feature_importance` | | Feature ranking |
| 11 | `scatter_regression` | `scatter` | Correlation 2 vars |
| 12 | `model_comparison_bar` | `model_comparison` | Model metric ranking |
| 13 | `roc_curve` | | Classification AUC |
| 14 | `residual_plot` | | Regression error distribution |
| 15 | `stacked_bar` | | Part-to-whole composition |
| 16 | `histogram` | | Distribution shape |
| 17 | `dot_plot` | | Clean ranking (Cleveland) |
| 18 | `bullet` | `bullet_chart` | Actual vs target + ranges |
| 19 | `area` | `area_chart`, `stacked_area` | Volume + trend |
| 20 | `connected_dot` | `dumbbell` | Gap between 2 values |
| 21 | `diverging_bar` | `tornado` | Sensitivity / 2 groups |
| 22 | `box_plot` | | Distribution comparison |
| 23 | `pareto` | | 80/20 analysis |
