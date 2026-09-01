---
name: descriptive
description: >
  Descriptive analytics — compute KPIs, trends, segments, distributions, waterfall
  decomposition, and findings. Screen for Simpson's Paradox. Draft SCQA narrative.
  Trigger: after validate passes (grade A/B/C).
when_to_use: "what happened", "KPIs", "trends", "segments", "descriptive analysis"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Descriptive

## Purpose
Answer "What happened?" — compute KPIs, analyze trends, segment data, build waterfall, generate findings with SCQA draft.

**Reads:** Cleaned data + `data/pipeline/{stem}/report_config.json`
**Writes:** `data/pipeline/{stem}/descriptive_output.json`

**Read references:** `references/domain_rules.md` · `references/principles.md` · `references/error_patterns.md` · `references/cohort_patterns.md` · `references/time_series_patterns.md` · `references/simpsons_paradox.md`

---

## Steps

### Step 1: Compute KPIs
Select exactly **3 header KPIs** based on domain and question:
- Primary metric (from report_config)
- 2 supporting metrics (complementary, not redundant)

Each KPI:
```json
{
  "id": "kpi_1",
  "label": "Revenue",          // ≤20 chars
  "value": "$2.1M",
  "delta": "-18%",
  "delta_abs": "-$460K",
  "prior_value": "$2.56M",
  "status": "alert",           // alert|good|flat
  "direction": "down_is_bad",
  "trend_series": [2.4, 2.5, 2.56, 2.1]  // 4-12 data points
}
```

### Step 2: Trend Analysis
- Compute period-over-period changes (auto-detect granularity)
- Identify inflection points (where trend changes direction)
- Flag anomalous periods (>2σ from rolling mean)
- If multiple segments: trends per segment

### Step 3: Segment Analysis
For each dimension column:
- Rank segments by primary metric
- Compute contribution % (segment value / total)
- Compute delta % per segment
- Assign verdict: `healthy` | `alert` | `root_cause_candidate`
- Flag concentration (top segment > 50% of total)

### Step 4: Waterfall Decomposition
If domain has `waterfall_structure` in config:
- Build waterfall from start to end metric
- Each bridge item: label + value + type (positive/negative/total)
- Highlight largest contributors

### Step 5: Cohort Analysis (if applicable)
If data has date + customer/entity identifier:
- Build retention cohort matrix
- Compute cohort-level KPIs
- Identify best/worst cohorts

### Step 6: Simpson's Paradox Screen
**Mandatory.** For each key finding:
1. Test if finding reverses when grouped by top 2 dimensions
2. If reversal detected → tag finding with `[PARADOX]`
3. Adjust insight to reflect true segment-level pattern

### Step 7: Generate Findings
Produce **≥3 findings**, each tagged:

| Tag | Meaning | Mandatory? |
|-----|---------|-----------|
| **Pattern** | Trend, seasonality, recurring behavior | At least 1 |
| **Contrast** | Unexpected difference between segments/periods | Optional |
| **Implication** | Business consequence | Optional |
| **Ruling Out** | Hypothesis explicitly rejected | **At least 1** |

Finding format:
```json
{
  "id": "F1",
  "type": "Contrast",
  "headline": "Mid-Market is the only segment declining (-22%) while Enterprise grew +12%",
  "evidence": "Mid-Market revenue: $800K→$624K. Enterprise: $1.2M→$1.34M",
  "confidence": "high",
  "chart_id": "segment_bar_01"
}
```

### Step 8: Draft SCQA
```json
{
  "situation": "Factual baseline (1-2 sentences)",
  "complication": "What changed — MUST include magnitude ($, %)",
  "question": "Natural question arising from complication",
  "answer": "Direct answer — conclusion first"
}
```

---

## Rules

**R-1:** Conclusion-first — every finding headline leads with insight, not metric label.
**R-2:** ≥1 "Ruling Out" finding — always include rejected hypotheses.
**R-3:** Simpson's Paradox screen is mandatory — never skip.
**R-4:** Exactly 3 header KPIs — no more, no less.
**R-5:** SCQA "Answer" must directly answer the "Question" — no hedging.
**R-6:** Chart titles are INSIGHTS ("Revenue fell 23% in Q3") not labels ("Revenue by Month").

---

## Output Schema

```json
{
  "skill_type": "descriptive",
  "run_context": {},
  "header_kpis": [],
  "trends": [],
  "segments": [],
  "cohorts": null,
  "waterfall": null,
  "findings": [],
  "scqa_draft": {
    "situation": "...",
    "complication": "...",
    "question": "...",
    "answer": "..."
  },
  "simpsons_paradox_checks": [],
  "metadata": {
    "generated_at": "ISO 8601"
  }
}
```
