---
name: define-metric
description: >
  Define a metric with standardized spec: formula, components, segmentation,
  thresholds, limitations. Auto-registers in metric dictionary.
  Trigger: /define-metric, "define a metric", "specify metric".
when_to_use: "/define-metric", "define a metric", "specify metric", "create KPI", "metric definition"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Define Metric

## Purpose
Define any metric clearly and completely using a standardized template so there is no ambiguity about what is being measured, how it's calculated, or how to interpret it. Auto-registers the metric in the active dataset's metric dictionary.

**Reads:** `knowledge/active.yaml` · `knowledge/datasets/{active}/metrics/index.yaml` · `knowledge/datasets/{active}/schema.md`
**Writes:** `knowledge/datasets/{active}/metrics/{id}.yaml` · `knowledge/datasets/{active}/metrics/index.yaml`

**Read references:** `references/metric_spec_template.md` · `references/sql_patterns.md`

---

## Steps

### Step 1: Gather Metric Details
Extract from conversation or ask the user:
1. **Name** — plain English name (e.g., "Checkout Conversion Rate")
2. **Plain English definition** — one sentence a non-technical person understands
3. **Formula** — exact calculation
4. **Components** — numerator, denominator (if ratio), unit of analysis
5. **Segmentation dimensions** — how to slice this metric
6. **Data source** — primary table, key columns, refresh cadence
7. **Thresholds** — healthy/watch/investigate/alert levels (based on historical data)
8. **Known limitations** — caveats, exclusions, edge cases

If any required field is unclear, ask the user. Do not guess thresholds without data.

### Step 2: Validate Completeness
Apply writing rules:
- Definition must be unambiguous — two analysts should write the same SQL
- Always specify the denominator for ratios
- Always specify the time window
- Always specify exclusions (test accounts, bots, internal users)
- Thresholds must be based on historical data, not gut feel

### Step 3: Generate Metric Spec
Build the full spec using the template from `references/metric_spec_template.md`:
- Metric header with definition and formula
- Components table (numerator, denominator, unit)
- Segmentation dimensions with rationale
- Data source with refresh cadence
- Thresholds with action triggers
- Known limitations
- Related metrics (upstream, downstream, alternative)
- Driver decomposition (optional, for key business metrics)

### Step 4: Auto-Register in Dictionary
1. Read `knowledge/active.yaml` to get active dataset ID
2. Generate metric `id` from name (lowercase, hyphens)
3. Check `knowledge/datasets/{active}/metrics/index.yaml` — update if exists, append if new
4. Write metric YAML to `knowledge/datasets/{active}/metrics/{id}.yaml`:
   - `definition.formula` ← formula from spec
   - `definition.unit` ← infer from formula (%, count, currency, ratio)
   - `definition.direction` ← infer from thresholds (higher_is_better / lower_is_better)
   - `source.tables` ← primary table
   - `source.sql` ← reference query if provided
   - `dimensions` ← segmentation column names
   - `guardrails` ← threshold values
5. Update `index.yaml` with new/updated entry

### Step 5: Confirm
Present the complete metric spec to the user. Offer:
- "Want to validate this metric against current data?"
- "Want to define related metrics?"
- "Want to add a driver decomposition?"

---

## Rules

**R-1:** Never define a metric without specifying the denominator for ratios.
**R-2:** Never use a metric name that means different things to different teams — create separate specs.
**R-3:** Never set thresholds without historical data — state the basis for every threshold.
**R-4:** Never skip the "known limitations" section — every metric has caveats.
**R-5:** Never use a ratio without understanding numerator vs denominator independence.
**R-6:** Always auto-register after writing the spec — the dictionary must stay in sync.
**R-7:** SQL in reference queries must use the active dataset's schema prefix.

---

## Subcommands
- `/define-metric` — start metric definition wizard
- `/define-metric --quick` — define with minimal fields (name, formula, table)
