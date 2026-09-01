---
name: html-report
description: >
  Render the final interactive HTML report with D3.js charts. Builds verdict band,
  SCQA drawer, analysis sections, charts, verdict panel, and confidence footer.
  Calls present_files() at end.
  Trigger: after chart-data, output_format = "html".
when_to_use: "html report", "interactive report", "web report", "render html"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: high
version: "2.0"
---

# Skill: HTML Report

## Purpose
Fill `report_context.json` with analysis content, then run `scripts/render_html.py` to produce the HTML report. The agent fills data into a schema — the script owns all layout, CSS, and D3.js rendering.

**Agent fills:** `data/pipeline/{stem}/report_context.json`
**Agent must NOT write:** HTML, CSS, JavaScript, or D3.js code
**Script reads:** `report_context.json` + `chart_specs.json`
**Script writes:** `data/reports/{type}/{stem}/report.html`

**Template files (owned by script, do NOT modify):**
```
templates/html_report/style.css          ← all CSS
templates/html_report/d3_renderer.js     ← all chart rendering
templates/html_report/tooltip_helper.js
templates/html_report/text_wrap_helper.js
templates/html_report/responsive_resize.js
templates/html_report/design_tokens.json
```

**Read before filling:** `references/report_context_schema.md` — exact field names, types, and constraints.

---

## Steps

### Step 1: Read the schema
Read `references/report_context_schema.md` to understand every field the script expects.

### Step 2: Verify inputs exist
- `data/pipeline/{stem}/descriptive_output.json` ✓
- `data/pipeline/{stem}/diagnostic_output.json` ✓
- `data/pipeline/{stem}/predictive_output.json` ✓ (if L3/L4)
- `data/pipeline/{stem}/chart_specs.json` ✓ (charts have `data` field populated)

### Step 3: Fill report_context.json
Build and write `data/pipeline/{stem}/report_context.json` following the schema exactly:

```json
{
  "report_type": "revenue|churn|operations|...",
  "big_answer": "One-sentence conclusion-first answer to the business question",
  "verdict_sentence": "≤35 words, sticky band sentence, conclusion-first with a number",
  "header_kpis": [
    { "label": "...", "value": "$X.XM", "delta": "±X% YoY", "status": "alert|good|flat" }
  ],
  "scqa": {
    "situation": "...", "complication": "...", "question": "...", "answer": "..."
  },
  "sections": [
    {
      "id": "descriptive|diagnostic|predictive",
      "title": "Conclusion-first section headline",
      "bridge_in": "Data scope / period note",
      "bridge_out": "Transition to next section",
      "findings": [
        { "tag": "Pattern|Contrast|Root Cause|Ruling Out|Implication|Forecast|Trend|Anomaly",
          "title": "Conclusion-first headline with number",
          "evidence": "1-3 sentences of supporting evidence",
          "supporting_data": "Optional italic footnote" }
      ],
      "charts": ["chart_id_1", "chart_id_2"]
    }
  ],
  "confidence": { "grade": "A|B|C|D|F", "score": 82, "interpretation": "..." }
}
```

**Constraints (enforced by schema, not script — agent must respect):**
- `header_kpis`: max 3 items
- `sections[].findings`: max 4 per section
- `sections[].id`: only `descriptive`, `diagnostic`, `predictive`
- All `title` fields: conclusion-first, include ≥1 specific number
- Do NOT put data arrays here — those belong in `chart_specs.json`

### Step 4: Run the deterministic renderer — ONE COMMAND
```powershell
$env:PYTHONPATH = "<repo_root>"
python scripts/render_html.py --stem {stem} --output data/reports/{type}/{stem}/report.html
```

On Windows, always set PYTHONPATH before running. `<repo_root>` is one level above `ai_analyst/`.

**That is the entire rendering step.** Do NOT write HTML.

### Step 5: Verify output
Check the file was created. Print path + size. Call `present_files([output_path])`.

---

## CRITICAL RULES

**R-1:** NEVER write HTML, CSS, or JavaScript. Always call `scripts/render_html.py`.
**R-2:** report_context.json is the ONLY file the agent writes for this skill.
**R-3:** chart_specs.json must have `data` populated before running the script — if not, run `chart-data` skill first.
**R-4:** section `id` must be exactly `descriptive`, `diagnostic`, or `predictive` — these map to hardcoded accent colors.
**R-5:** `present_files()` is MANDATORY after writing report.html.

---

## Legacy steps (DO NOT USE — kept for reference only)

### Step 3: Render Verdict Band
Height ≤100px. Navy background. Contains:
- Verdict sentence (white text, ≤35 words)
- 3 KPI badges (status-colored: alert/good/flat)

### Step 4: Render SCQA Drawer
Collapsible `<details>` element, collapsed by default.
- S: situation text
- C: complication with magnitude
- Q: question
- A: answer (conclusion first)

### Step 5: Render Analysis Sections
For each section (descriptive/blue, diagnostic/purple, predictive/green):
- Section header with colored left border
- Finding boxes (tagged: Pattern|Contrast|Implication|Ruling Out)
- Charts: full-width, single column, D3.js rendered
- Diagnostic section includes verdict panel

**CRITICAL:** Single column layout. No `chart-grid-2`. No `insight-cards`.

### Step 6: Render Verdict Panel (Diagnostic Section)
- Root Cause #1 (≤30 words)
- Root Cause #2 (≤30 words)
- Implication (≤25 words, with number)
- Next Action (≤25 words, with timeline)

### Step 7: Render D3.js Charts
For each chart in chart_specs.json, generate D3.js rendering code. All charts:
- Use viewBox for responsive SVG
- Include tooltip via setupTooltip()
- Register with resizeAllCharts()

### Step 8: Embed Helper Scripts
Inline the three scripts: tooltip_helper.js, text_wrap_helper.js, responsive_resize.js.

### Step 9: Render Confidence Footer
Badge with score/grade, interpretation text, and caveat list.

### Step 10: Write and Present
Write to `data/reports/{type}/{stem}/report.html`.
**MANDATORY:** Call `present_files()` after writing.

---

## Rules

**R-1:** Single column layout — ALL charts full-width. No side-by-side grids.
**R-2:** No `chart-grid-2` class. Explicitly banned.
**R-3:** No `insight-cards` class. Explicitly banned (CB-11).
**R-4:** SCQA drawer collapsed by default.
**R-5:** Verdict band ≤100px height.
**R-6:** D3.js loaded from CDN — no local copy.
**R-7:** All CSS and JS inline — single self-contained HTML file.
**R-8:** Charts resize on window change (responsive_resize.js).
**R-9:** Tooltip on hover for all interactive charts (tooltip_helper.js).
**R-10:** `present_files()` is MANDATORY after writing report.html.
**R-11:** Design tokens from `assets/design_tokens.json` — no hardcoded values.

---

## Output Schema

Single file: `data/reports/{type}/{stem}/report.html`

Self-contained HTML with inline CSS + JS. External deps: Google Fonts CDN + D3.js CDN.
