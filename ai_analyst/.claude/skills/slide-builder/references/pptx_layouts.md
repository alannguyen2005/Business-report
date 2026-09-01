# PPTX Slide Layouts — Extracted from slidedeck_template.pptx

## Universal Header (all content slides, y < 1.5")

```
Background rect:  (0.00, 0.00) 13.33"×7.50"  fill=#F5F5F0
Breadcrumb text:  (0.89, 0.41) variable width, h=0.27"
                  Format: "Section  |  Topic"
                  "Section": Calibri 10pt #94A3B8
                  "  |  Topic": Calibri 10pt bold, section accent color
Headline text:    (0.89, 0.68) w=11.56", h=0.44–0.77"
                  Calibri 20pt bold #111827
Slide number:     (12.3, 7.10) Calibri 9pt #94A3B8  (skip slide 1)
```

---

## Layout 1: COVER

Used for: Title slide only.

```
Background:       (0.00, 0.00) 13.33"×7.50"  fill=#0F1729
Project label:    (0.89, 0.38) Calibri 10pt #475569  → "PROJECT  ·  ANALYSIS TITLE"
Accent bar:       (0.89, 1.95) 0.55"×0.05"  fill=#2554E7
Headline:         (0.89, 2.05) 8.50"×0.40"  Calibri 28pt bold #FFFFFF
Subtitle:         (0.89, 4.70) 9.00"×0.40"  Calibri 13pt #64748B

KPI separator lines (vertical):
  x=[3.19, 5.50, 7.82, 10.13]  y=6.25  0.01"×1.00"  fill=#1E293B

KPI labels row:   y=6.33  Calibri 9pt #334155
  x=[0.89, 3.20, 5.51, 7.83, 10.14]  w=2.31"  h=0.22"
  Labels: PERIOD | ORDERS ANALYSED | PRODUCTS | SUPPLIERS | PREPARED BY

KPI values row:   y=6.57  Calibri 16pt bold #94A3B8
  Same x positions
```

---

## Layout 2: BACKGROUND

Used for: Context slide (Slide 2 — "Business Context & Analysis Scope").

```
[Standard header]
Panel titles above panels (not inside):
  Left title:  (0.97, 1.48) w=1.81" h=0.34"  Calibri 14pt bold #111827
  Right title: (6.98, 1.48) w=1.81" h=0.34"  Calibri 14pt bold #111827

Left panel:  (0.89, 1.59) 5.55"×5.10"  fill=#FFFFFF  corner_radius=100000
  Body text: (0.97, 1.89) w=5.30" h=0.71"  Calibri 12pt regular #374151
             3 lines: situation text, "What happened?", "Why now?"

  KEY QUESTION box at bottom:
    (1.06, 5.63) 5.21"×0.85"  fill=#2554E7  corner_radius=80000
    Label: (1.15, 5.78) Calibri 10.5pt regular #FFFFFF → "KEY QUESTION"
           ← text appears white on blue background (color extracted as #2554E7 due to theme)
    Text:  (1.15, 6.05) Calibri 11pt regular #FFFFFF → question text

Right panel: (6.89, 1.59) 5.55"×5.10"  fill=#FFFFFF  corner_radius=100000
  4 scope item rows at y: [2.07, 3.03, 3.98, 4.94]
  Each item:
    Container rect: (7.12, row_y) w=5.08" h=0.62"  no fill, rounded corner
    Badge:          (7.28, row_y+0.14) 0.35"×0.35"  fill=#2554E7  rounded
    Label text:     (7.78, row_y+0.06) Calibri 9pt bold #334155 UPPERCASE
                    e.g. "DATA PERIOD" / "RECORDS ANALYZED" / "DIMENSIONS" / "METHODS"
    Value text:     (7.78, row_y+0.26) Calibri 12pt regular #111827
```

---

## Layout 3: INSIGHT_CHART  ← PRIMARY ANALYSIS LAYOUT

Used for: ALL descriptive, diagnostic, predictive slides that have charts.
Implements **Pyramid Principle**: Conclusion → Evidence → Data.

```
[Standard header]
HEADLINE (0.89, 0.68) w=11.56" h=0.77":  ← LEVEL 1: Main Insight/Conclusion
  Calibri 20pt bold #111827
  Key numbers/phrases: inline colored runs (section accent color)
  This IS the insight statement (e.g. "Supplier_X lost 26% of orders while competitors grew")

Left panel:  (0.89, 1.64) 5.55"×5.26"  fill=#FFFFFF rounded
Right panel: (6.89, 1.64) 5.55"×5.26"  fill=#FFFFFF rounded

Inside each panel:
  Quote badge (oval):  (panel_x+0.16, 1.83) 0.26"×0.26"  fill=section_color
                       Text: "  (quote mark)" Calibri 12pt white
  Supporting text:     (panel_x+0.16, 2.14) 5.23"×0.90"  ← LEVEL 2: Supporting Evidence
                       Calibri 12pt #374151
                       Bold key phrases in section accent color (e.g. #EF4444)
  Chart container:     (panel_x+0.16, 3.23) 5.23"×3.47"  ← LEVEL 3: Data/Proof
                       Rounded rect, no fill (transparent), corner_radius=60000
    Chart title text:  (panel_x+0.29, 3.35) 4.93"×0.28"  Calibri 10.5pt bold #374151
    Chart PNG picture: (panel_x+0.29, 3.74) 4.93"×2.78"
```

**PYRAMID PRINCIPLE ORDER (mandatory for INSIGHT_CHART):**
1. Top: Big headline = the conclusion (what we know)
2. Panel top: Supporting insight text = why/how (evidence)
3. Panel bottom: Chart = the data proof (supporting detail)

**Section accent colors for INSIGHT_CHART:**
- Context slides: #F97316 (orange)
- Root Cause / Diagnostic: #EF4444 (red)
- Predictive: #EF4444 (red) — template shows red; can use #22C55E green for positive findings
- Conclusions: #2554E7 (blue)

---

## Layout 4: FINDINGS_OVERVIEW

Used for: "Findings | Overview" — 3 findings summary, NO chart.

```
[Standard header]

3 white panels at y=1.65", h=5.25":
  Col 1: (0.89, 1.65) w=3.68"
  Col 2: (5.00, 1.65) w=3.68"
  Col 3: (9.10, 1.65) w=3.68"

Each panel:
  Badge bg:    (panel_x+0.16, 1.91) 0.42"×0.42"  fill=#FFF5F5  corner_radius=80000
  Badge num:   (panel_x+0.17, 1.99) 0.42"×0.25"  Calibri 9pt bold #EF4444  → "01" "02" "03"
  Title text:  (panel_x+0.66, 1.94) w≈2.94" h=0.34"  Calibri 14pt bold #111827
  Divider:     (panel_x+0.16, 2.54) 3.36"×0.01"  fill=#E2E8F0
  Body bullets: 3 items at fixed y positions:
    Bullet 1: (panel_x+0.16, 2.83) w=3.35" h=0.30"  Calibri 12pt regular #374151  "- ..."
    Bullet 2: (panel_x+0.16, 3.79) w=3.35" h=0.30"  Calibri 12pt regular #374151  "- ..."
    Bullet 3: (panel_x+0.16, 4.77) w=3.35" h=0.30"  Calibri 12pt regular #374151  "- ..."
    ← y spacing = 0.96" between bullets
  Footer bar: (panel_x+0.16, 6.07) 3.36"×0.42"  fill=#FFF5F5  corner_radius=60000
              Calibri 9pt #EF4444 italic text  (implication / "→ takeaway")
```

---

## Layout 5: FRAMEWORK_3COL

Used for: "Analysis Framework" — 3 pillars/approaches.

```
[Standard header]

3 white panels at y=1.73", h=5.11":
  Col 1: (0.89, 1.73) w=3.53"
  Col 2: (5.00, 1.73) w=3.53"
  Col 3: (9.10, 1.73) w=3.53"

Each panel:
  Badge:      (panel_x+0.27, 1.96) 0.48"×0.45"  fill=#2554E7  rounded
              Calibri 12pt bold white → "01" "02" "03"  (Inter fallback: Calibri)
  Title:      (panel_x+0.22, 2.54) w≈3.10", h=0.34"  Calibri 14pt bold #111827
  Body:       (panel_x+0.22, 2.99) w≈3.10"  Calibri 12pt #374151
  Footer:     (panel_x+0.22, 6.15) w≈3.10", h=0.47"  Calibri 11pt #94A3B8
              Format: "→ outcome text"
```

---

## Layout 6: FOUR_2x2

Used for: Methodology — 4 topic panels in 2×2 grid.

```
[Standard header]

4 white panels:
  Top-left:     (0.89, 1.59) 5.60"×2.43"
  Top-right:    (6.80, 1.59) 5.64"×2.43"
  Bottom-left:  (0.89, 4.26) 5.60"×2.43"
  Bottom-right: (6.80, 4.26) 5.64"×2.43"

Each panel (left panels x=1.03, right x=6.94):
  Section label: (panel_text_x, panel_y+0.18) Calibri 9.5pt bold #2554E7
  Title:         (panel_text_x, panel_y+0.43) Calibri 12.5pt bold #111827
  Body:          (panel_text_x, panel_y+0.74) Calibri 11pt #374151
  Footer:        (panel_text_x, panel_y+2.04) Calibri 11pt #94A3B8 → "→ ..."
```

---

## Layout 7: CONCLUSIONS_OVERVIEW

Used for: "Conclusions | Overview Key takeouts" — 3 urgency-tiered findings.
Same structure as FINDINGS_OVERVIEW but with blue badges and urgency labels.

```
[Same structure as FINDINGS_OVERVIEW — same positions and sizes — except:]
  Badge bg:    fill=#EEF2FF (light blue)  corner_radius=80000
  Badge num:   (panel_x+0.17, 1.99) Calibri 9pt bold #2554E7
  Title text:  (panel_x+0.66, 1.97) Calibri 12pt regular #2554E7
               ← NOT bold, color = #2554E7, e.g. "Critical · Immediate"
  Divider:     (panel_x+0.16, 2.54) fill=#E2E8F0  ← same
  Body bullets: same y positions (2.83, 3.79, 4.77) Calibri 12pt #374151
  Footer bar:  fill=#EEF2FF  Calibri 9pt #2554E7 italic
```

---

## Layout 8: STRATEGY_MAPS

Used for: "Action | Strategy Maps" — 3 phase timeline cards.
Same structure as FINDINGS_OVERVIEW but with teal (#42967A) badges.

```
[Same structure as FINDINGS_OVERVIEW — same positions and sizes — except:]
  Badge bg:    fill=#42967A  corner_radius=80000
  Badge num:   (panel_x+0.17, 1.99) Calibri 9pt bold #42967A
               ← number text color matches section, not white
  Title text:  (panel_x+0.66, 1.97) Calibri 12pt regular #42967A
               ← e.g. "Phase 1 · Days 1–30"
  Divider:     (panel_x+0.16, 2.54) fill=#E2E8F0
  Body bullets: same y positions (2.83, 3.79, 4.77) Calibri 12pt #374151
  Footer bar:  fill=#E6F5EF  Calibri 9pt #42967A italic
```

---

## Layout 9: RECS_TABLE

Used for: "Action | Recommendation" — full-width table.

```
[Standard header]

White panel: (0.89, 1.58) 11.89"×5.41"  fill=#FFFFFF rounded
Table:       (1.05, 1.76) 11.56"×5.02"

Columns: PRIORITY | ACTION | OWNER | TIMELINE | EXPECTED IMPACT | SUCCESS METRIC
Column widths: 1.2" | 4.0" | 1.5" | 1.2" | 2.0" | 1.66"

Header row: fill=#42967A (dark teal)  Calibri 10pt bold #FFFFFF uppercase
Body rows: alternating #FFFFFF / #F5F5F0  Calibri 10pt #374151

Priority cell colors (text only, bold):
  P1-Now:  fill=#EF4444 (red)  text=#FFFFFF
  P1-30d:  fill=#F97316 (orange)  text=#FFFFFF
  P1-60d:  text=#111827 plain
  P2-30d:  text=#94A3B8 muted
```

---

## Layout 10: IMPACT_TWO_COL

Used for: "Action | Expected Impact" — 2-col outcome panels.
Same as FINDINGS_OVERVIEW but 2 columns with teal badges.

```
[Standard header]

2 white panels:
  Left:  (0.90, 1.65) 5.62"×5.25"
  Right: (6.82, 1.65) 5.62"×5.25"

Each panel (same structure as STRATEGY_MAPS card):
  Badge:   (panel_x+0.15, 1.91) 0.42"×0.42"  fill=#42967A
  Number:  Calibri 9pt bold #FFFFFF
  Title:   (panel_x+0.49, 1.97) Calibri 14pt bold #42967A
  Divider: (panel_x+0.18, 2.54) w≈4.92"  fill=#E2E8F0
  Bullets: y from 2.83", spacing 0.96"  Calibri 12pt #374151
           Format: "- ..."
```

---

## Section Color Map

| Slide section | Breadcrumb accent | Badge / oval color | Headline key phrase color |
|---------------|-------------------|--------------------|--------------------------|
| Context       | #2554E7 blue      | #F97316 orange     | #F97316 orange           |
| Root Cause    | #EF4444 red       | #EF4444 red        | #EF4444 red              |
| Findings      | #EF4444 red       | #FFF5F5/#EF4444    | #EF4444 red              |
| Predictive    | #EF4444 red       | #EF4444 red        | #EF4444 red              |
| Conclusions   | #2554E7 blue      | #2554E7 blue       | #2554E7 blue             |
| Action        | #42967A teal      | #42967A teal       | #42967A teal             |
