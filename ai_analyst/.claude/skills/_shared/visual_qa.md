# Visual QA Checks

Run these quality checks against every chart specification after building it.

## 5 Gotcha Checks

| # | Check | What to Look For |
|---|-------|------------------|
| 1 | **Label collision** | Text overlapping other text or data points |
| 2 | **Color contrast** | Highlighted element not visually distinct from gray |
| 3 | **Axis scale** | Bar chart Y-axis not starting at zero |
| 4 | **Missing context** | Chart not standalone without narrative |
| 5 | **Annotation accuracy** | Arrow pointing at wrong data point |

## Label Collision Patterns
1. **Data-label vs data-label:** Similar bar heights → labels overlap
2. **Annotation vs data-label:** Arrow text overlaps direct labels
3. **Axis-label overlap:** Long tick labels overlap each other
4. **Title/subtitle crowding:** Annotation encroaches on title area

## Advanced Technique Checks

| # | Technique | When Required | What to Verify |
|---|-----------|--------------|---------------|
| 1 | Trendline | Time series with anomaly | Trendline present, anomaly excluded from fit |
| 2 | Stacked bars | Category contribution over time | Key category highlighted, totals shown |
| 3 | Event span | Specific time window is focus | Span marked, boundary dates labeled |
| 4 | Side-by-side | Comparing two groups | Bars side-by-side, both labeled |
| 5 | Big-number summary | Final resolution chart | 2-4 KPIs, findings, recommendation |
| 6 | Progressive zoom | Sequential charts | Each chart narrower scope than previous |

## Pre-Output Validation
- [ ] Title is insight (not label)
- [ ] Background is #FFFFFF
- [ ] No gridlines
- [ ] Only bottom + left spines
- [ ] Max 3 annotations
- [ ] Callout starts with "So what:" and has at least 1 number
- [ ] Data values are valid (no NaN, no Infinity)
- [ ] Color usage follows highlight + gray pattern
