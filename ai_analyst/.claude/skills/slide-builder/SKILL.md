---
name: slide-builder
description: >
  Build PPTX consulting slide deck via python-pptx. Assembles cover, context, findings,
  conclusions, recommendations, and impact slides from story_arc.json + chart images.
  Calls present_files() at end.
  Trigger: after chart-render, output_format = "pptx".
when_to_use: "slide deck", "pptx", "presentation", "build slides"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: high
version: "3.0"
---

# Skill: Slide Builder

## Purpose
Build a consulting-quality PPTX slide deck using python-pptx. Faithfully replicates the user's design template: `pptx_report_template.pptx`.

**Reads:** `data/pipeline/{stem}/story_arc.json` · `data/pipeline/{stem}/chart_images.json` · `data/pipeline/{stem}/chart_images/*.png`
**Writes:** `data/reports/{type}/{stem}/slidedeck.pptx`

**MUST READ before building:**
- `references/pptx_layouts.md` — exact positions, sizes, colors for every layout
- `templates/pptx_report/slide_template_config.json` — dimensions, fonts, color tokens
- `templates/pptx_report/pptx_report_template.pptx` — **the master template file** (loaded as base, not read)

---

## Steps

### Step 1: Verify story_arc.json exists
Check that `data/pipeline/{stem}/story_arc.json` has been written by data-storytelling.
If it does not exist, error out — do NOT write python-pptx code by hand.

### Step 2: Run the deterministic builder — ONE COMMAND
```bash
python3 scripts/build_pptx_v3.py --stem {stem} --output data/reports/{type}/{stem}/slidedeck.pptx
```

**That is the entire skill.** The script handles all slide building.
Do NOT write python-pptx code. The script is the source of truth.

### Step 3: Verify output
Check the file was created. Call `present_files([output_path])`.

---

## CRITICAL RULE
**NEVER write python-pptx code directly.** Always call `scripts/build_pptx_v3.py`.
The script:
- Always loads `pptx_report_template.pptx` via `Presentation(TEMPLATE_PATH)` — correct font/theme
- Has all 10 layout positions hardcoded from `pptx_layouts.md`
- Produces consistent output regardless of session context

---

## Legacy reference (DO NOT USE — kept for layout specs only)

### Initialize Presentation — TEMPLATE-BASED APPROACH (reference only)

**Always load the master template file, never create from scratch.**

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import copy, os, json, shutil

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))  # adjust to actual skill path
TEMPLATE_PATH = "templates/pptx_report/pptx_report_template.pptx"

def rgb(hex_str):
    h = hex_str.lstrip('#')
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

# Load template — this inherits ALL fonts, theme, color scheme from template
prs = Presentation(TEMPLATE_PATH)

# Remove all existing slides (keep slide layouts/masters intact)
xml_slides = prs.slides._sldIdLst
for i in range(len(prs.slides) - 1, -1, -1):
    rId = prs.slides._sldIdLst[i].get('r:id')
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[i]

# Use blank layout for all new slides
BLANK_LAYOUT = prs.slide_layouts[6]
```

**Why template-based:** Loading `pptx_report_template.pptx` inherits the Office theme (colors, fonts, corner radius). The builder strips all template slides and builds from scratch via `build_pptx_v3.py`.

### Step 3: Font Resolution
All text uses **Calibri** throughout (the theme's fallback font). No League Spartan.
- Headers/bold: `Calibri` bold
- Body/supporting: `Calibri Light` (simulated via bold=False + Calibri)

### Step 4: Build Each Slide

Read `story_arc.slides[]` and apply the layout specified in each slide's `layout` field.
Full layout specs are in `references/pptx_layouts.md`. Summary below:

---

#### COVER
Dark navy slide. See pptx_layouts.md Layout 1.
- Full #0F1729 background
- Blue accent bar at y=1.95"
- Headline: Calibri 28pt bold #FFFFFF
- Subtitle: Calibri 13pt #64748B
- Bottom KPI row: 5 items (PERIOD, ORDERS, SEGMENTS/PRODUCTS, SUPPLIERS, PREPARED BY)

---

#### BACKGROUND
Context + scope two-col slide. See pptx_layouts.md Layout 2.
- Left panel: business situation text + KEY QUESTION blue box at bottom
- Right panel: 4 scope items with blue badges (DATA PERIOD, RECORDS, DIMENSIONS, METHODS)

---

#### INSIGHT_CHART  ← PRIMARY ANALYSIS LAYOUT — PYRAMID PRINCIPLE
**This is the most important layout. Used for ALL insight slides with charts.**

Structure (from pptx_layouts.md Layout 3):
```
HEADLINE (0.89, 0.68) 11.56"×0.77"           ← LEVEL 1: CONCLUSION
  Calibri 20pt bold #111827
  Key numbers/phrases → section accent color bold runs (e.g. #EF4444)
  This IS the insight. Write the full finding here.

Left panel  (0.89, 1.64) 5.55"×5.26" #FFFFFF
Right panel (6.89, 1.64) 5.55"×5.26" #FFFFFF

Inside each panel:
  Quote oval  (panel_left+0.16, 1.83) 0.26"×0.26" fill=section_color  text='"' white 12pt
  
  Supporting text (panel_left+0.16, 2.14) 5.23"×0.90"    ← LEVEL 2: EVIDENCE
    Calibri 12pt #374151
    Key phrases → Calibri 12pt bold section_color
  
  Chart container (panel_left+0.16, 3.23) 5.23"×3.47" transparent rounded  ← LEVEL 3: DATA
    Chart title: (panel_left+0.29, 3.35) Calibri 9pt bold #374151
    Chart PNG:   (panel_left+0.29, 3.74) ~4.93"×2.78"
```

**PYRAMID PRINCIPLE — non-negotiable order:**
1. Headline = the conclusion the audience should remember
2. Supporting text = why/how (evidence, comparisons)
3. Chart = the data that proves it

---

#### FINDINGS_OVERVIEW
3-col cards, NO chart. See pptx_layouts.md Layout 4.
- 3 panels: (0.89) (5.00) (9.10) y=1.65" each 3.68"×5.25"
- Red badge #FFF5F5 bg + #EF4444 number + title + divider + bullets + footer bar #FFF5F5

---

#### FRAMEWORK_3COL
3-col pillar cards. See pptx_layouts.md Layout 5.
- Blue #2554E7 badges (0.48"×0.45") + title + body + footer "→ outcome"

---

#### FOUR_2x2
2×2 grid. See pptx_layouts.md Layout 6.
- 4 panels (top-left, top-right, bottom-left, bottom-right)
- Each: section label + title + body + footer

---

#### CONCLUSIONS_OVERVIEW
3-col urgency cards. See pptx_layouts.md Layout 7.
- Same as FINDINGS_OVERVIEW but blue badges
- Card titles: "Critical · Immediate" / "High · 30 Days" / "Structural · 90 Days"

---

#### STRATEGY_MAPS
3-col phase timeline. See pptx_layouts.md Layout 8.
- Same structure, teal #42967A badges
- "Phase 1 · Days 1–30" / "Phase 2 · Days 31–60" / "Phase 3 · Days 61–90"

---

#### RECS_TABLE
Full-width recommendations table. See pptx_layouts.md Layout 9.
- Columns: PRIORITY | ACTION | OWNER | TIMELINE | EXPECTED IMPACT | SUCCESS METRIC
- Header: dark teal #42967A fill, white text
- Priority cells: P1-Now=#EF4444, P1-30d=#F97316, others plain

---

#### IMPACT_TWO_COL
2-col outcome panels. See pptx_layouts.md Layout 10.
- Teal #42967A badges, bullet points per panel

---

### Step 5: Add Slide Numbers
All slides except cover (slide 1): add slide number at (12.3, 7.10) Calibri 9pt #94A3B8.

### Step 6: Bold Key Numbers
In all body text runs, detect numbers (%, $, K, M) → apply bold.

### Step 7: Add Speaker Notes
Add `story_arc.slides[].speaker_notes` to each slide's notes placeholder.

### Step 8: Save and Present
```python
os.makedirs(os.path.dirname(output_path), exist_ok=True)
prs.save(output_path)
print(f"Saved: {output_path} ({os.path.getsize(output_path)/1024:.1f} KB)")
present_files([output_path])
```

---

## Rules

**R-1:** INSIGHT_CHART headline = full insight statement (Pyramid Level 1). Key numbers in section accent color. NOT a label.
**R-2:** BACKGROUND, FINDINGS_OVERVIEW, FRAMEWORK_3COL, CONCLUSIONS_OVERVIEW, STRATEGY_MAPS — NO chart images. Text + shapes only.
**R-3:** Content slides background = #F5F5F0 (warm off-white). Cover background = #0F1729 (navy).
**R-4:** All fonts → Calibri. Bold = League Spartan weight simulation.
**R-5:** Quote oval badge on INSIGHT_CHART panels: 0.26"×0.26" circle, section accent color fill.
**R-6:** Chart container in INSIGHT_CHART: transparent rounded rect at (panel_x+0.16, 3.23) 5.23"×3.47".
**R-7:** Panel height always 5.26" (content) or 5.10–5.25" (card layouts). Panels start at y≈1.59–1.73".
**R-8:** Section colors — read from pptx_layouts.md Section Color Map. Apply to badge, headline accent, breadcrumb.
**R-9:** Breadcrumb: "Section  |  Topic" — section word #94A3B8, "  |  Topic" in section accent color bold.
**R-10:** 16:9 ratio (13.33" × 7.5"). Always.
**R-11:** `present_files()` MANDATORY at end.
**R-12:** Read `references/pptx_layouts.md` before building — do not rely on memory for dimensions.

---

## story_arc.json Expected Fields per Slide

```json
{
  "slide_number": 5,
  "layout": "INSIGHT_CHART",
  "breadcrumb_section": "Root Cause #1",
  "breadcrumb_topic": "Order Volume Collapse",
  "section_color": "#EF4444",
  "headline": "Supplier_X lost 26% of Laptop Pro X orders in 2023 — while every competitor held or grew volume on the same SKU",
  "headline_accents": ["26%", "every competitor"],
  "left_panel": {
    "supporting_text": "Supplier_X Laptop Pro X orders collapsed...",
    "supporting_accents": ["collapsed 26%", "Supplier_A grew"],
    "chart_id": "order_volume_chart",
    "chart_title": "Order volume by supplier 2022–2023"
  },
  "right_panel": {
    "supporting_text": "Smartphone Alpha followed the same pattern...",
    "supporting_accents": ["same pattern"],
    "chart_id": "smartphone_chart",
    "chart_title": "Supplier_X drove more than 100% of profit decline"
  },
  "speaker_notes": "Notes for presenter..."
}
```

---

## Output Schema

Single file: `data/reports/{type}/{stem}/slidedeck.pptx`
Python-pptx native editable shapes + embedded PNG chart images. 16:9.
