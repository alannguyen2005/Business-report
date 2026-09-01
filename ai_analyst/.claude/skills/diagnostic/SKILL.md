---
name: diagnostic
description: >
  Root cause analysis — form hypotheses (min 3), test with data evidence, rank root causes
  by impact, include "ruling out" findings. Iterative drill-down to Level 3+.
  Trigger: after descriptive, when plan includes diagnostic (L2+).
when_to_use: "why did", "root cause", "what caused", "explain the change", "diagnostic"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Diagnostic

## Purpose
Answer "Why did it happen?" — form hypotheses, test with evidence, rank root causes, and produce a verdict. Iterative drill-down ensures depth beyond surface-level observations.

**Reads:** `data/pipeline/{stem}/descriptive_output.json` + cleaned data
**Writes:** `data/pipeline/{stem}/diagnostic_output.json`

**Read references:** `references/domain_rules.md` · `references/principles.md` · `references/error_patterns.md` · `references/drill_down_protocol.md` · `references/hypothesis_categories.md`

---

## Steps

### Step 1: Extract Signals
Read `descriptive_output.json` and identify anomalies:
- Metrics with significant delta (>10% or >2σ)
- Segments flagged as `root_cause_candidate`
- Trend inflection points
- Findings tagged "Contrast" or "Pattern"

### Step 2: Generate Hypotheses
Produce **≥3 hypotheses** across **≥2 of 4 categories**:

| Category | Focus | Example |
|----------|-------|---------|
| **Product** | Product/service changes | "New pricing tier cannibalized existing plans" |
| **Technical** | Data/system issues | "Tracking pixel dropped → apparent decline" |
| **External** | Market/seasonal forces | "Competitor launched free tier" |
| **Mix Shift** | Composition changes | "Enterprise grew but SMB shrank → net flat" |

Each hypothesis:
```json
{
  "id": "H1",
  "statement": "Falsifiable claim",
  "category": "Product|Technical|External|Mix Shift",
  "confirming_evidence": "What pattern would confirm this",
  "rejecting_evidence": "What pattern would reject this",
  "data_requirements": ["columns needed"]
}
```

### Step 3: Test Hypotheses (Iterative Drill-Down)
For each hypothesis, up to 3 iterations:

**Level 1:** Broad test (overall data supports or contradicts?)
**Level 2:** Segment drill (which segment drives the pattern?)
**Level 3:** Time drill (when exactly did it start?)
**Level 3+:** Sub-segment / funnel step / correlation analysis

```
Iteration loop:
  1. Identify the data cut needed
  2. Run analysis (filter, group, compare)
  3. Evaluate evidence → confirm | reject | partial
  4. If partial → drill deeper (add dimension, narrow time)
  5. Max 3 iterations per hypothesis
```

### Step 4: Assign Verdicts
| Verdict | Criteria |
|---------|---------|
| **CONFIRMED** | Strong evidence, 3+ data points, 0 contradictions |
| **PARTIALLY CONFIRMED** | Some support, but not conclusive |
| **REJECTED** | Evidence contradicts → becomes "Ruling Out" finding |
| **INCONCLUSIVE** | Insufficient data to determine |

### Step 5: Rank Root Causes
Rank by: impact_magnitude × confidence × actionability

| Factor | Assessment |
|--------|-----------|
| Impact | % of total metric change explained |
| Confidence | high (3+ sources) / medium (2) / low (1) |
| Actionability | Can business act on this? yes/no/partially |

**Impact attributions should sum to ~100%** (account for entire change).

### Step 6: Build Verdict
One-sentence verdict: direct, ≤35 words, no hedging.
- GOOD: "Mid-Market churn from Feature X deprecation accounts for 60% of revenue decline — recoverable in 8 weeks via rollback"
- BAD: "It appears that there may have been some factors contributing to the decline"

---

## Rules

**R-1:** Minimum 3 hypotheses, across ≥2 categories.
**R-2:** Always include ≥1 REJECTED hypothesis (Ruling Out prevents confirmation bias).
**R-3:** Max 3 drill-down iterations per hypothesis — avoid rabbit holes.
**R-4:** Impact attributions must sum to ~100%.
**R-5:** Correlation ≠ causation — add `correlation_note` to every confirmed root cause.
**R-6:** Verdict sentence ≤35 words, no hedging.

---

## Output Schema

```json
{
  "skill_type": "diagnostic",
  "run_context": {},
  "signals": [],
  "hypotheses": [
    {
      "id": "H1",
      "statement": "...",
      "category": "Product",
      "verdict": "CONFIRMED",
      "evidence": ["data point 1", "data point 2"],
      "impact_attribution": "60%",
      "confidence": "high",
      "correlation_note": "Mechanism: Feature X removed → usage dropped → churn increased",
      "drill_down_path": ["Overall → Mid-Market → Feature X users → March cohort"]
    }
  ],
  "root_causes_ranked": [
    {"hypothesis_id": "H1", "rank": 1, "impact_pct": 60, "actionable": true}
  ],
  "ruling_out": [
    {"hypothesis_id": "H3", "reason": "Data shows acquisition metrics stable"}
  ],
  "verdict_sentence": "≤35 words summary",
  "metadata": {"generated_at": "ISO 8601"}
}
```
