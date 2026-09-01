---
name: model-evaluate
description: >
  Compare N model results, rank by primary metric (MAPE/MAE/F1), select winner,
  verify winner beats baseline. Produces evaluation_result.json with comparison table.
  Trigger: called by predictive-trainer subagent after all model training completes.
when_to_use: "compare models", "evaluate models", "model selection", "pick best model"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: medium
version: "1.0"
---

# Skill: Model Evaluate

## Purpose
Compare all trained model results, rank by primary metric, select the winner, and verify it beats the baseline. Consolidates individual `model_result_{type}.json` files into a unified evaluation.

**Reads:** `data/pipeline/{stem}/model_result_*.json` (all 4) + `data/pipeline/{stem}/test_data.json`
**Writes:** `data/pipeline/{stem}/evaluation_result.json`

**Read references:** `references/metric_definitions.md` · `references/comparison_rules.md`

---

## Steps

### Step 1: Collect All Model Results
```python
import json
import glob

results = {}
for path in glob.glob(f"data/pipeline/{stem}/model_result_*.json"):
    with open(path) as f:
        result = json.load(f)
    model_type = result["model_type"]
    results[model_type] = result
```

### Step 2: Determine Pipeline Type and Primary Metric
| Pipeline Type | Primary Metric | Direction | Baseline Model |
|---|---|---|---|
| Forecasting | MAPE | Lower is better | seasonal_naive |
| Regression | MAE | Lower is better | mean_baseline |
| Classification | F1-Score | Higher is better | naive_logreg |

### Step 3: Build Comparison Table
```python
comparison = []
for model_type, result in results.items():
    if result["status"] == "failed":
        comparison.append({
            "model_type": model_type,
            "status": "failed",
            "primary_metric": None,
            "rank": None
        })
        continue
    
    metrics = result["metrics"]
    comparison.append({
        "model_type": model_type,
        "status": "success",
        "primary_metric": metrics[primary_metric_name],
        "all_metrics": metrics,
        "training_time": result["metadata"]["training_time_seconds"]
    })

# Sort by primary metric
if direction == "lower_is_better":
    comparison.sort(key=lambda x: x["primary_metric"] if x["primary_metric"] is not None else float('inf'))
else:
    comparison.sort(key=lambda x: x["primary_metric"] if x["primary_metric"] is not None else -1, reverse=True)

# Assign ranks
for i, entry in enumerate(comparison):
    if entry["status"] == "success":
        entry["rank"] = i + 1
```

### Step 4: Verify Winner Beats Baseline
```python
winner = comparison[0]
baseline = next(c for c in comparison if c["model_type"] == baseline_model)

if direction == "lower_is_better":
    beats_baseline = winner["primary_metric"] < baseline["primary_metric"]
    improvement = ((baseline["primary_metric"] - winner["primary_metric"]) / baseline["primary_metric"]) * 100
else:
    beats_baseline = winner["primary_metric"] > baseline["primary_metric"]
    improvement = ((winner["primary_metric"] - baseline["primary_metric"]) / baseline["primary_metric"]) * 100

if not beats_baseline:
    # WARNING: Best model doesn't beat baseline
    verdict = "NO_IMPROVEMENT"
    recommendation = "No model improves over baseline. Consider: more data, better features, or different approach."
else:
    verdict = "WINNER_SELECTED"
    recommendation = f"{winner['model_type']} improves {improvement:.1f}% over baseline."
```

### Step 5: Generate Summary
```python
evaluation = {
    "winner": {
        "model_type": winner["model_type"],
        "primary_metric": primary_metric_name,
        "primary_value": winner["primary_metric"],
        "baseline_value": baseline["primary_metric"],
        "improvement_pct": round(improvement, 1),
        "beats_baseline": beats_baseline
    },
    "comparison_table": comparison,
    "verdict": verdict,
    "recommendation": recommendation
}
```

### Step 6: Write Result
Write to `data/pipeline/{stem}/evaluation_result.json`.

---

## Rules

**R-1:** Winner = model with best primary metric (MAPE/MAE/F1). If tie, prefer simpler model.
**R-2:** Winner MUST beat baseline. If no model beats baseline → verdict = "NO_IMPROVEMENT".
**R-3:** Failed models (status="failed") receive rank=null and are excluded from winner selection.
**R-4:** Always report improvement percentage vs baseline.
**R-5:** If only 1 model succeeded (others failed), it still must beat baseline to be selected.
**R-6:** Metric direction: MAPE/MAE = lower is better. F1 = higher is better.

---

## Output Schema

```json
{
  "skill_type": "model_evaluate",
  "run_context": {},
  "pipeline_type": "forecasting|regression|classification",
  "winner": {
    "model_type": "prophet",
    "primary_metric": "mape",
    "primary_value": 8.2,
    "baseline_model": "seasonal_naive",
    "baseline_value": 15.6,
    "improvement_pct": 47.4,
    "beats_baseline": true
  },
  "comparison_table": [
    {
      "rank": 1,
      "model_type": "prophet",
      "status": "success",
      "mape": 8.2,
      "mae": 45000,
      "rmse": 62000,
      "training_time": 12.5
    },
    {
      "rank": 2,
      "model_type": "lgbm_ts",
      "status": "success",
      "mape": 9.1,
      "mae": 48000,
      "rmse": 65000,
      "training_time": 3.2
    },
    {
      "rank": 3,
      "model_type": "sarima",
      "status": "success",
      "mape": 11.5,
      "mae": 55000,
      "rmse": 72000,
      "training_time": 25.0
    },
    {
      "rank": 4,
      "model_type": "seasonal_naive",
      "status": "success",
      "mape": 15.6,
      "mae": 70000,
      "rmse": 85000,
      "training_time": 0.1
    }
  ],
  "verdict": "WINNER_SELECTED|NO_IMPROVEMENT",
  "recommendation": "Prophet improves 47.4% over baseline (seasonal_naive).",
  "all_models_summary": {
    "total": 4,
    "succeeded": 4,
    "failed": 0,
    "beat_baseline": 3
  },
  "metadata": {
    "primary_metric": "mape",
    "metric_direction": "lower_is_better",
    "generated_at": "ISO 8601"
  }
}
```
