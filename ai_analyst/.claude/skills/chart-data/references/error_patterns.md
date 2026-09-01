# Chart Data Error Patterns

## E-1: Label as Title
- **Wrong:** "Monthly Revenue" or "Revenue by Segment"
- **Right:** "Revenue fell 18% in Q1 — first decline in 6 quarters"

## E-2: Rainbow Charts
- **Wrong:** Each bar/line a different color (6+ colors)
- **Right:** ONE highlighted element, everything else gray

## E-3: Missing Callout
- **Wrong:** Chart with no "So what:" text
- **Right:** "So what: At current rate, Q2 target missed by $300K"

## E-4: Opaque Annotation Background
- **Wrong:** Solid color annotation box (fill: #EF4444)
- **Right:** Transparent annotation (fill: rgba(239,68,68,0.08))

## E-5: Gridlines Present
- **Wrong:** Any visible gridlines
- **Right:** No gridlines, only bottom + left spines in #E2E8F0

## E-6: Legend Box
- **Wrong:** Separate legend box
- **Right:** Direct labels on the data series

## E-7: White Background
- **Wrong:** Chart background #FFFFFF
- **Right:** Chart background #F7F6F2

## E-8: Over-Annotation
- **Wrong:** >3 annotations on a single chart
- **Right:** ≤3 focused annotations

## E-9: Misleading Axis
- **Wrong:** Bar chart Y-axis not starting at zero
- **Right:** Bar charts always start at zero

## E-10: Low Contrast Annotation
- **Wrong:** Annotation text in #94A3B8 (light gray)
- **Right:** Text in #EF4444, #10B981, or #1A202C — weight ≥600, size ≥11px
