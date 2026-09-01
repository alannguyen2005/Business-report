---
name: size-opportunity
description: >
  Estimate business impact and financial value of an opportunity with
  sensitivity analysis, scenario modeling, and prioritization scoring.
  Trigger: /size-opportunity, "how much is this worth", "business impact".
when_to_use: "/size-opportunity", "size the opportunity", "business impact", "how much is this worth", "ROI analysis"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Size Opportunity

## Purpose
Estimate the business impact and financial value of an opportunity. Produces an impact model with sensitivity analysis, scenario modeling, and prioritization scoring.

**Reads:** `knowledge/active.yaml` · `knowledge/datasets/{active}/schema.md` · `knowledge/datasets/{active}/metrics/` · `data/pipeline/{stem}/`
**Writes:** `working/opportunity-sizing/{name}_{DATE}.md`

**Read references:** `references/sizing_guide.md`

---

## Steps

### Step 1: Parse the Opportunity Brief
Extract:
1. **What is the opportunity?** — new feature, performance fix, retention lever, new market
2. **Who benefits?** — user segment, customer tier, geography
3. **Current state** — baseline metric/revenue (query from data if available)
4. **Proposed improvement** — what changes
5. **Timeline** — launch date, time to maturity

### Step 2: Build Impact Model
Core formula: `Impact = Users Affected × Improvement Rate × Value per Unit`

For each component:
- **Users Affected** — count from dataset, filter to eligible segment
- **Improvement Rate** — from analysis results, benchmarks, or assumptions
- **Value per Unit** — from dataset or assumptions

Handle compound models:
- Direct impact (primary metric improvement)
- Cost avoidance (resources saved)
- Indirect impact (second-order effects — flag as lower confidence)

Annualize unless time-bounded.

### Step 3: Compute Base Case
1. Pull actuals from dataset for each model component
2. Estimate improvement: use analysis results (quantified excess), benchmarks, or assumptions
3. Calculate: `Base Case = Users × Improvement (midpoint) × Value per Unit`
4. Express in multiple units: revenue ($), cost savings ($), users impacted, time saved

### Step 4: Sensitivity Analysis
1. Rank assumptions by uncertainty (confidence × leverage)
2. One-variable sensitivity: vary top 2-3 assumptions at -50%, -25%, base, +25%, +50%
3. Break-even analysis: find threshold where opportunity is not worth pursuing

### Step 5: Scenario Analysis
Three scenarios:

| Scenario | Approach | Use |
|----------|----------|-----|
| Pessimistic | Lowest plausible values | Downside risk |
| Base case | Best-estimate values | Decision basis |
| Optimistic | Highest plausible values | Upside potential |

Compute expected value if probabilities can be estimated.

### Step 6: Prioritization Score
```
Priority Score = (Impact × Confidence) / Effort
```
- Impact: annual base case ($)
- Confidence: HIGH=0.8, MEDIUM=0.5, LOW=0.3
- Effort: from user or flagged as TBD

### Step 7: Output Sizing Report
Save to `working/opportunity-sizing/{name}_{DATE}.md` with sections:
- Bottom line (annual impact, confidence, key risk, recommendation)
- Impact model (formula, components, multi-channel if applicable)
- Sensitivity analysis (tables, break-even points)
- Scenario analysis (pessimistic/base/optimistic)
- Prioritization score
- Data sources and caveats

### Step 8: Interactive Follow-Up
Offer:
- "Want to compare this against other opportunities?"
- "Want to validate assumptions with a pilot?"
- "Want to design an experiment to test impact claims?"

---

## Rules

**R-1:** Never use a single point estimate — always show range with sensitivity.
**R-2:** Never ignore adoption ramp — few features reach full penetration immediately.
**R-3:** Never assume immediate impact — account for measurement lag and ramp time.
**R-4:** Never forget cannibalization — new offering may shift existing revenue.
**R-5:** Every assumption must be labeled as "data-backed" or "assumption".
**R-6:** Impact model formula must be explicit with named variables and values.
**R-7:** If >3 key variables are assumptions, confidence must be LOW.
**R-8:** Apply order-of-magnitude check — >10% of company revenue is likely wrong.

---

## Subcommands
- `/size-opportunity` — full sizing wizard
- `/size-opportunity --template {type}` — use template (product, retention, efficiency, expansion)
- `/size-opportunity --sensitivity` — focus on sensitivity analysis
