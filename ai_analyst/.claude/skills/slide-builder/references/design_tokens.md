# PPTX Design Tokens
## Extracted from slidedeck_template.pptx (user's reference template)

## Dimensions
- Slide: 13.33" x 7.5" (16:9)
- Left margin: 0.89"
- Breadcrumb row: y=0.41", height=0.27"
- Headline row: y=0.68", height=0.44–0.77"
- Content panels start: y=1.59–1.73"
- Footer/slide number: y=7.1", bottom-right

## Colors — Backgrounds

| Element | Hex |
|---------|-----|
| Cover background | #0F1729 |
| Content slide background | #F5F5F0 |
| Content panel | #FFFFFF |
| KPI card / separator bg | #1E293B |
| Alert badge bg | #FFF5F5 |
| Divider line | #E2E8F0 |

## Colors — Text

| Element | Hex |
|---------|-----|
| Primary text | #111827 |
| Body text | #374151 |
| Secondary / subtitle | #64748B |
| Muted / breadcrumb | #94A3B8 |
| Cover breadcrumb | #475569 |
| KPI label | #334155 |
| KPI value | #94A3B8 |

## Colors — Accent

| Section / Use | Hex |
|---------------|-----|
| Primary blue (Descriptive / Context) | #2554E7 |
| Orange (warning / highlight) | #F97316 |
| Red (Root Cause / alert) | #EF4444 |
| Green (positive / predictive) | #22C55E |

## Typography

| Element | Font | Size (pt) | Weight |
|---------|------|-----------|--------|
| Cover headline | League Spartan (or Calibri fallback) | 28–32 | Bold |
| Slide headline (large) | League Spartan Medium | 20 | Bold |
| Panel / section title | League Spartan | 14 | Bold |
| Body text | League Spartan Light | 12 | Regular |
| Supporting bullets | League Spartan Light | 10.5–11 | Regular (key numbers bold) |
| Breadcrumb label | League Spartan Light | 10 | Regular, colored section word bold |
| Number badge | Inter | 9–12 | Bold |
| Cover breadcrumb | Calibri | 10 | Regular |
| KPI label | Calibri | 9 | Regular |
| KPI value | Calibri | 16 | Bold |
| Slide number | Calibri | 9 | Regular, #94A3B8 |

> **Fallback rule:** If League Spartan is unavailable, use Calibri throughout.
> If Inter is unavailable, use Calibri for number badges.

## Layout — Cover Slide

- Full background rect: (0,0) 13.33×7.50 fill=#0F1729
- Breadcrumb / project name: (0.89, 0.38) Calibri 10pt #475569 → "PROJECT_NAME  ·  ANALYSIS TITLE"
- Blue accent bar: (0.89, 1.95) 0.55"×0.05" fill=#2554E7
- Headline: (0.89, 2.10) League Spartan Bold 28pt #FFFFFF
- Subtitle: (0.89, 2.90) Calibri 13pt #64748B
- Bottom KPI row at y≈6.25": Calibri 9pt #334155 label + 16pt Bold #94A3B8 value
- KPI vertical separators: #1E293B 0.01"×1.00" at x=3.19, 5.50, 7.82, 10.13

## Layout — Content Slides (all non-cover)

- Full background rect: (0,0) 13.33×7.50 fill=#F5F5F0
- Breadcrumb row: (0.89, 0.41) w=variable h=0.27 → "Section  |  Topic" (muted base, colored keyword)
- Headline row: (0.89, 0.68) w=11.56 h=0.44–0.77 → League Spartan Medium 20pt bold
- Content panels: #FFFFFF rounded rectangles starting at y≈1.59–1.73"

## Layout — Column Grids

| Grid | Column positions & widths |
|------|--------------------------|
| Two-col | Left (0.89, w=5.55) · Right (6.89, w=5.55) |
| Three-col | Col1 (0.89, w=3.53) · Col2 (5.00, w=3.53) · Col3 (9.10, w=3.53) |
| Four-card | Col1 (0.89, w=5.60) · Col2 (6.80, w=5.64) — top/bottom stacked |
| Full-width | (0.89, w=11.56) |

## Shape Styles

| Shape | Fill | Border | Notes |
|-------|------|--------|-------|
| Content panel | #FFFFFF | none | Rounded corners 0.1–0.15" |
| Divider line | #E2E8F0 | none | 0.01" tall, full panel width |
| Number badge | #2554E7 or #EF4444 | none | Rounded 0.35–0.48" sq, white text |
| Accent dot/circle | section color | none | 0.26–0.42" sq, white text |
| KPI separator | #1E293B | none | 0.01"×1.00" vertical |
| Callout box | #F5F5F0 | dashed #F97316 | Insight/So What callout |
