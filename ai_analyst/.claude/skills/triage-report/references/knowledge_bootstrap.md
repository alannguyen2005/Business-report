# Knowledge Bootstrap Protocol

> Enriched from plugin: ask-question skill

## Purpose
Bootstrap domain knowledge at the start of each analysis to provide better context for all subsequent steps.

## Bootstrap Steps

### 1. Check Active Dataset
Read `knowledge/active.yaml`:
```yaml
active_dataset:
  id: "orders_2026"
  type: "ecommerce"
  path: "data/raw/orders_2026-01-01_to_2026-03-31.csv"
  last_analyzed: "2026-04-10T14:30:00Z"
```

### 2. Load Dataset Knowledge (if exists)
From `knowledge/datasets/{id}/`:
- `schema.md` — Column documentation (types, meanings, relationships)
- `quirks.md` — Known data issues, gotchas, workarounds
- `metrics.yaml` — Standardized KPI definitions for this dataset

### 3. Load Domain Rules (if exists)
From `config/domains/domain_rules.md`:
- Domain-specific KPIs and their expected ranges
- Waterfall structure for this domain
- Segment dimensions that matter
- Business rules for validation

### 4. Check Run History
From `knowledge/history/`:
- Past analyses of the same dataset
- What questions were asked before
- What findings were significant
- Any corrections or feedback

## Output
Enriches the `run_context` with:
```json
{
  "knowledge": {
    "has_schema": true,
    "has_quirks": true,
    "has_metrics": true,
    "has_domain_rules": true,
    "past_runs": 3,
    "last_correction": null
  }
}
```

## Rules
- **Never fail** if knowledge doesn't exist — it's optional enrichment
- First analysis of a new dataset will have no knowledge → that's fine
- After analysis completes, knowledge should be updated for next time
