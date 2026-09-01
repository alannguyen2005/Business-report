---
name: validate
description: >
  4-layer data validation (structural, logical, business rules, Simpson's Paradox)
  with confidence scoring (0-100 → grade A-F). HALT pipeline if grade D/F.
  Trigger: after data-prep complete, before any analysis begins.
when_to_use: "validate data", "check data quality", "data validation", "confidence score"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Validate

## Purpose
Verify data integrity through 4 validation layers before analysis begins. Produce confidence score and grade. HALT pipeline if data quality is insufficient.

**Reads:** Cleaned data + `data/pipeline/{stem}/report_config.json`
**Writes:** `data/pipeline/{stem}/validation_result.json`

**Read references:** `references/structural_rules.md` · `references/logical_rules.md` · `references/business_rules_template.md` · `references/source_tieout.md` · `references/triangulation.md`

---

## Steps

### Step 1: Layer 1 — Structural Validation
- Schema conformance (expected columns present, correct dtypes)
- Primary key integrity (no duplicates in PK)
- Completeness: null rates per column
  - BLOCKER: >20% null in primary metric
  - WARNING: >5% null in any metric column
- Date range coverage (no unexpected gaps)
- Value domain (rates 0–1, revenue >0, percentages 0–100)

### Step 2: Layer 2 — Logical Validation
- Aggregation consistency (detail rows sum to totals ±0.1%)
- Trend continuity (no sudden 10× jumps without explanation)
- Percentage sums = 100% (where applicable, ±1% tolerance)
- Temporal consistency (no future dates, no reverse chronology)
- Segment exhaustiveness (all segments account for total ±1%)

### Step 3: Layer 3 — Business Rules
- Load rules from `knowledge/datasets/{id}/metrics.yaml` (if exists)
- Load domain rules from `config/domains/domain_rules.md` (if exists)
- Check plausibility (revenue within expected range, churn rate reasonable)
- Flag values outside historical norms (>3σ)
- Check domain-specific constraints

### Step 4: Layer 4 — Simpson's Paradox Detection
For each (dimension × metric) combination:
1. Compute overall trend direction
2. Compute per-segment trend directions
3. Flag if overall direction ≠ majority of segment directions

| Severity | Condition |
|----------|----------|
| **none** | No reversals detected |
| **low** | Reversal in non-primary metric |
| **medium** | Reversal in secondary metric |
| **high** | Reversal in primary metric → BLOCKER |

### Step 5: Confidence Scoring
Calculate 7-factor score:

| Factor | Max Score | What It Measures |
|--------|-----------|-----------------|
| Data completeness | 15 | % non-null in key columns |
| Structural integrity | 15 | PK uniqueness, dtype consistency |
| Aggregation consistency | 15 | Parts sum to whole |
| Temporal consistency | 15 | No gaps, no future dates |
| Business plausibility | 15 | Values within expected range |
| Simpson's Paradox risk | 15 | No aggregate-segment reversals |
| Sample size | 10 | Enough data points for analysis |

**Grade mapping:**
| Grade | Score | Decision |
|-------|-------|----------|
| A | 90–100 | Proceed with confidence |
| B | 75–89 | Proceed, note minor issues |
| C | 60–74 | Proceed with caveats (embed in report) |
| D | 40–59 | **HALT** — present issues to user |
| F | 0–39 | **HALT** — data unusable |

---

## Rules

**R-1:** HALT pipeline on grade D or F. Present issues clearly to user.
**R-2:** Never skip Layer 4 (Simpson's) — even if data looks clean.
**R-3:** Confidence grade must be embedded in final report header.
**R-4:** All BLOCKER issues must be resolved before proceeding.
**R-5:** WARNING issues are logged but don't stop pipeline.

---

## Output Schema

```json
{
  "skill_type": "validation",
  "run_context": {},
  "layers": {
    "structural": {
      "status": "PASS|WARNING|BLOCKER",
      "issues": [{"field": "...", "severity": "...", "detail": "..."}]
    },
    "logical": {
      "status": "PASS|WARNING|BLOCKER",
      "issues": []
    },
    "business_rules": {
      "status": "PASS|WARNING|BLOCKER",
      "issues": []
    },
    "simpsons_paradox": {
      "status": "PASS|WARNING|BLOCKER",
      "paradoxes_found": [{"dimension": "...", "metric": "...", "severity": "..."}]
    }
  },
  "confidence": {
    "score": 82,
    "grade": "B",
    "factors": {
      "data_completeness": {"score": 12, "max": 15},
      "structural_integrity": {"score": 15, "max": 15},
      "aggregation_consistency": {"score": 12, "max": 15},
      "temporal_consistency": {"score": 15, "max": 15},
      "business_plausibility": {"score": 10, "max": 15},
      "simpsons_paradox_risk": {"score": 15, "max": 15},
      "sample_size": {"score": 8, "max": 10}
    },
    "interpretation": "MODERATE CONFIDENCE — present with caveats",
    "blockers": []
  },
  "decision": "proceed|proceed_with_caveats|halt",
  "metadata": {
    "rows_validated": 50000,
    "columns_validated": 25,
    "duration_seconds": 3.2,
    "generated_at": "ISO 8601"
  }
}
```
