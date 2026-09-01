# Model Comparison Rules

> Rules for fair model comparison, winner selection, and tie-breaking.

## Core Comparison Rules

### Rule 1: Single Primary Metric
Each pipeline type has exactly ONE primary metric for ranking:

| Pipeline | Primary Metric | Direction |
|----------|---------------|-----------|
| Forecasting | MAPE | Lower is better |
| Regression | MAE | Lower is better |
| Classification | F1-Score | Higher is better |

**Never mix metrics.** Rank ONLY by primary metric. Secondary metrics are for diagnostic purposes.

### Rule 2: Baseline Requirement
Every model MUST be compared against the baseline:

| Pipeline | Baseline Model | Baseline Strategy |
|----------|---------------|-------------------|
| Forecasting | seasonal_naive | Repeat last seasonal cycle |
| Regression | mean_baseline | Predict training mean |
| Classification | naive_logreg | All-0 prediction (Accuracy Trap demo) |

**Winner must beat baseline.** If no model beats baseline → verdict = "NO_IMPROVEMENT".

### Rule 3: Failed Models
- Models with `status: "failed"` are excluded from ranking
- They receive `rank: null` in the comparison table
- If all models fail → verdict = "ALL_FAILED", recommend debugging

---

## Tie-Breaking Rules

When two or more models have identical primary metric values:

### Tie-Break Priority Order
1. **Simpler model wins** — fewer parameters, easier to interpret
2. **Faster training wins** — lower `training_time_seconds`
3. **Better secondary metric wins** — check secondary metrics

### Simplicity Ranking (from simplest to most complex)

**Forecasting:**
1. seasonal_naive (simplest)
2. sarima
3. prophet
4. lgbm_ts (most complex)

**Regression:**
1. mean_baseline (simplest)
2. ridge_lasso
3. random_forest
4. xgboost (most complex)

**Classification:**
1. naive_logreg (simplest)
2. decision_tree
3. random_forest
4. xgboost (most complex)

```python
SIMPLICITY_ORDER = {
    "forecasting": ["seasonal_naive", "sarima", "prophet", "lgbm_ts"],
    "regression": ["mean_baseline", "ridge_lasso", "random_forest", "xgboost"],
    "classification": ["naive_logreg", "decision_tree", "random_forest", "xgboost"]
}

def break_tie(model_a, model_b, pipeline_type):
    """Prefer simpler model when primary metrics are equal."""
    order = SIMPLICITY_ORDER[pipeline_type]
    return model_a if order.index(model_a) < order.index(model_b) else model_b
```

---

## Improvement Calculation

```python
def calculate_improvement(winner_metric, baseline_metric, direction):
    """
    Calculate percentage improvement over baseline.
    
    For lower-is-better (MAPE, MAE):
      improvement = (baseline - winner) / baseline × 100
      
    For higher-is-better (F1):
      improvement = (winner - baseline) / baseline × 100
    """
    if direction == "lower_is_better":
        return ((baseline_metric - winner_metric) / baseline_metric) * 100
    else:
        if baseline_metric == 0:
            return float('inf')  # Any improvement over 0 is infinite
        return ((winner_metric - baseline_metric) / baseline_metric) * 100
```

---

## Quality Flags

| Condition | Flag | Meaning |
|-----------|------|---------|
| Winner MAPE < 10% | `quality: "excellent"` | Very accurate forecasts |
| Winner MAPE 10-20% | `quality: "good"` | Reliable for business decisions |
| Winner MAPE 20-50% | `quality: "acceptable"` | Use with caveats |
| Winner MAPE > 50% | `quality: "poor"` | Forecasts unreliable |
| Winner MAE < 10% of mean | `quality: "excellent"` | Tight predictions |
| Winner F1 > 0.80 | `quality: "excellent"` | Strong classification |
| Winner F1 0.50-0.80 | `quality: "good"` | Useful classification |
| Winner F1 < 0.50 | `quality: "acceptable"` | Use with caution |
| No model beats baseline | `quality: "none"` | No ML value added |

---

## Comparison Table Format

The comparison table should include all models, sorted by rank:

```
┌──────┬──────────────────┬────────┬──────────┬────────┬────────┬──────────────┐
│ Rank │ Model            │ Status │ MAPE (%) │ MAE    │ RMSE   │ Train Time   │
├──────┼──────────────────┼────────┼──────────┼────────┼────────┼──────────────┤
│ 1 ★  │ Prophet          │ ✓      │ 8.2      │ 45,000 │ 62,000 │ 12.5s        │
│ 2    │ LightGBM-TS      │ ✓      │ 9.1      │ 48,000 │ 65,000 │ 3.2s         │
│ 3    │ SARIMA           │ ✓      │ 11.5     │ 55,000 │ 72,000 │ 25.0s        │
│ 4    │ Seasonal Naive   │ ✓      │ 15.6     │ 70,000 │ 85,000 │ 0.1s         │
└──────┴──────────────────┴────────┴──────────┴────────┴────────┴──────────────┘

★ Winner: Prophet — MAPE 8.2% (47.4% improvement over baseline)
```

---

## Edge Cases

| Scenario | Action |
|----------|--------|
| All models fail | `verdict: "ALL_FAILED"`, log errors, recommend investigation |
| Only baseline succeeds | `verdict: "BASELINE_ONLY"`, no winner — models need debugging |
| Winner barely beats baseline (<5% improvement) | Flag as marginal improvement, suggest more data |
| Two models tie | Apply tie-breaking rules (simpler wins) |
| Baseline fails | `verdict: "BASELINE_FAILED"`, compare remaining models without baseline reference |
