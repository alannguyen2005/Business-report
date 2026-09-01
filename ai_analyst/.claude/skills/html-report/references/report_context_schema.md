# report_context.json Schema

This is the **only file** the `html-report` skill / `render_html.py` reads from the agent.
The agent's job is to fill this schema correctly. The script renders everything else.

---

## Top-level structure

```json
{
  "report_type": "revenue",
  "big_answer": "Revenue fell -3.6% YoY on volume alone — margin held at 33.2%",
  "verdict_sentence": "Revenue declined modestly (-3.6% YoY) on pure volume — margin intact at 33.2%, Q4 forecast $1.22M",
  "header_kpis": [...],
  "scqa": {...},
  "sections": [...],
  "confidence": {...}
}
```

---

## `header_kpis[]` — sticky verdict band (max 3 items)

```json
{
  "label": "Total Revenue",
  "value": "$8.75M",
  "delta": "-3.6% YoY",
  "status": "alert"
}
```

| Field | Type | Values |
|-------|------|--------|
| `label` | string | Short metric name (≤20 chars) |
| `value` | string | Formatted value with unit ($, %, K, M) |
| `delta` | string | YoY or MoM change, optional |
| `status` | string | `"alert"` (red) · `"good"` (green) · `"flat"` (gray) |

---

## `scqa{}` — analysis framework drawer (collapsed by default)

```json
{
  "situation": "TechWorld is a stable multi-region e-commerce retailer — $8.75M across 13,925 completed orders, 33.2% margin.",
  "complication": "Revenue declined $136K (-3.6% YoY Jan-Sep). Order count fell -3.9%. Margin held perfectly — costs are ruled out.",
  "question": "What drove this mild volume decline, which segments can recover, and what does Q4 look like?",
  "answer": "Gradual structural erosion (-1,081 units/month slope) in an 87%-Electronics portfolio. West is the only growing region. Q4 forecast $1.22M."
}
```

All fields are plain strings. ≤3 sentences each. `answer` must be conclusion-first.

---

## `sections[]` — analysis sections (1 per analytical layer)

```json
{
  "id": "descriptive",
  "title": "Revenue fell -3.6% on volume alone — margin held perfectly",
  "bridge_in": "Jan 2022 – Sep 2023 · Completed orders only · 21 monthly data points",
  "bridge_out": "Margin stability rules out cost issues — the root cause is demand volume.",
  "findings": [...],
  "charts": [...]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | `"descriptive"` · `"diagnostic"` · `"predictive"` — controls section accent color (blue/purple/green) |
| `title` | yes | Conclusion-first section headline (≤12 words) |
| `bridge_in` | no | Short subtitle / data scope line below headline |
| `bridge_out` | no | Italic transition sentence at section bottom |
| `findings` | yes | Array of finding cards (see below) |
| `charts` | yes | Array of chart_id strings to render in this section |

### Section `id` → color mapping (hardcoded in script)
| `id` | Accent color | Badge color |
|------|-------------|------------|
| `descriptive` | `#2554E7` blue | `.section-accent.blue` |
| `diagnostic` | `#9333EA` purple | `.section-accent.purple` |
| `predictive` | `#10B981` green | `.section-accent.green` |

---

## `sections[].findings[]` — finding cards

```json
{
  "tag": "Pattern",
  "title": "Volume drives 70% of variance — order count swings explain every major deviation",
  "evidence": "Correlation: orders vs revenue r=0.774, quantity vs revenue r=0.818. Price range stayed stable at $479–$539.",
  "supporting_data": "Laspeyres decomposition: volume effect 69.9%, price effect 30.1%, mix effect ~0%"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `tag` | yes | Controls badge color. Valid values: `Pattern` · `Contrast` · `Implication` · `Ruling Out` · `Root Cause` · `Emerging` · `Trend` · `Forecast` · `Anomaly` · `Segment Region` · `Model Selection` |
| `title` | yes | Conclusion-first headline (≤15 words, specific number required) |
| `evidence` | yes | 1–3 sentences of supporting evidence |
| `supporting_data` | no | Italic data footnote line |

**Max 4 findings per section.** More than 4 = split into two sections.

---

## `sections[].charts[]` — chart references

Simple array of `chart_id` strings. The script looks these up in `chart_specs.json`.

```json
"charts": ["monthly_revenue_trend", "yoy_kpi_comparison"]
```

The chart must exist in `chart_specs.json` with a populated `data` field — otherwise it renders as "No data for: {id}".

---

## `confidence{}` — footer badge

```json
{
  "grade": "B",
  "score": 82,
  "interpretation": "Grade B (82/100). Key metrics complete, 6 quality warnings. Results reliable for strategic decisions; return-rate and margin figures independently verified."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `grade` | string | `A` / `B` / `C` / `D` / `F` |
| `score` | int | 0–100 |
| `interpretation` | string | 1–2 sentences, cite key verified numbers |

---

## Complete minimal example

```json
{
  "report_type": "revenue",
  "big_answer": "Revenue is essentially flat YoY (-3.6%) on a slow structural volume trend",
  "verdict_sentence": "Revenue -3.6% YoY on volume — margin 33.2% intact — Q4 forecast $1.22M",
  "header_kpis": [
    { "label": "Total Revenue",    "value": "$8.75M",   "delta": "-3.6% YoY", "status": "alert" },
    { "label": "Net Profit",       "value": "$2.90M",   "delta": "-3.8% YoY", "status": "alert" },
    { "label": "Q4 2023 Forecast", "value": "$1.22M",   "delta": "-5.2% vs Sep", "status": "alert" }
  ],
  "scqa": {
    "situation": "TechWorld generated $8.75M from 13,925 completed orders across 4 regions and categories, with a consistent 33.2% profit margin.",
    "complication": "Revenue declined $136K (-3.6% YoY Jan–Sep). Orders fell -3.9%. But margin held perfectly — this rules out cost and pricing as causes.",
    "question": "What is driving the gradual volume decline, which segments can recover, and what should we plan for in Q4?",
    "answer": "Slow structural erosion (-1,081 units/month) amplified by 87% Electronics concentration. West is the only growing region. Q4 forecast $1.22M with high model confidence (<4% MAPE)."
  },
  "sections": [
    {
      "id": "descriptive",
      "title": "Revenue fell -3.6% on volume alone — margin held at 33.2%",
      "bridge_in": "Jan 2022 – Sep 2023 · 13,925 completed orders · 21 monthly data points",
      "bridge_out": "Costs and pricing are ruled out — root cause investigation focuses on demand volume.",
      "findings": [
        {
          "tag": "Pattern",
          "title": "Revenue -3.6% YoY with margin unchanged — a pure volume story",
          "evidence": "Jan-Sep 2022: $3.79M vs Jan-Sep 2023: $3.65M. Orders -3.9%. Net profit margin 33.2% in both years.",
          "supporting_data": "Total period revenue $8.75M across 21 months. Slope -$1,081/month."
        }
      ],
      "charts": ["monthly_revenue_trend", "yoy_kpi_comparison"]
    }
  ],
  "confidence": {
    "grade": "B",
    "score": 82,
    "interpretation": "Grade B (82/100). Primary metrics 100% complete. 6 structural warnings (non-unique Order_ID, comma-decimal numerics, 15 future-date rows). All headline numbers independently verified."
  }
}
```

---

## What the agent must NOT put in report_context.json

- Raw data arrays (those go in `chart_specs.json`)
- HTML or CSS strings
- Chart rendering instructions
- More than 3 `header_kpis`
- More than 4 `findings` per section
- Section `id` values other than `descriptive`, `diagnostic`, `predictive`
