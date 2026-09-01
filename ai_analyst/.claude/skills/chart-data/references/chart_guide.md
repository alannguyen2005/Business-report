# Chart Guide — D3.js Specifications

## Chart Type Selection

| Data Relationship | Chart Type | When to Use |
|-------------------|-----------|-------------|
| Change over time | `highlight_line` | Time series with 4-50 data points |
| Comparison | `highlight_bar` | ≤12 categories, horizontal bars |
| Part-to-whole | `waterfall` | Bridge decomposition (start → end) |
| Distribution | `histogram` | Single numeric variable |
| Correlation | `scatter` | Two numeric variables |
| Before/after | `slope` | Two time points comparison |
| Composition over time | `stacked_area` | 2-5 categories over time |
| Forecast | `forecast_line` | Historical + projected with confidence |
| Matrix | `heatmap` | Two dimensions, one metric |

## Color System

| Role | Color | Hex |
|------|-------|-----|
| Highlight | Blue | `#2554E7` |
| Comparison | Gray | `#D1D5DB` |
| Alert | Red | `#EF4444` |
| Positive | Green | `#10B981` |
| Event marker | Orange | `#F97316` |
| Zone fill | Any+0.08 | `rgba(X,X,X,0.08)` |

## Categorical Palette (colorblind-safe, 8 colors)
1. `#2554E7` Blue
2. `#F97316` Orange
3. `#10B981` Green
4. `#9333EA` Purple
5. `#EF4444` Red
6. `#06B6D4` Cyan
7. `#F59E0B` Amber
8. `#6366F1` Indigo

**Rule:** If ≤3 series, use highlight + gray pattern instead of multiple colors.

## Standard Configuration
```json
{
  "width": "100%",
  "height": 400,
  "background": "#F7F6F2",
  "margin": {"top": 60, "right": 40, "bottom": 50, "left": 60},
  "show_gridlines": false,
  "spine_color": "#E2E8F0",
  "spines": ["bottom", "left"],
  "font_family": "'IBM Plex Sans', system-ui, sans-serif",
  "title_font": "'Outfit', sans-serif",
  "title_size": 16,
  "label_size": 11,
  "axis_size": 10,
  "tooltip": true
}
```
