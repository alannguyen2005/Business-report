---
name: predictive-trainer
description: >
  Run the full ML predictive pipeline including data preparation, model training
  (parallel), evaluation, and ensemble selection. Use when analysis requires
  forecasting, regression, or classification.
tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Skill
model: sonnet
skills:
  - predictive-data-prep
  - train-test-split
  - forecast-train
  - regression-train
  - classification-train
  - model-evaluate
  - model-finalize
memory: project
effort: high
---

# Predictive Trainer

Coordinate the full ML pipeline: data prep → train (parallel) → evaluate → finalize → monitor.

> Replaces the old 3 separate predictive orchestrators (forecasting, regression, classification).
> Reference: SYSTEM_DESIGN.md Section 4.6, REFERENCE_GUIDE.md Sections 1.2–1.3

## Core Responsibilities

1. Determine pipeline type from `predictive_input.json`
2. Prepare ML-ready data (feature engineering, encoding)
3. Split data (time-based / stratified / random)
4. Train N models in PARALLEL (4 per pipeline type)
5. Evaluate all models → select winner
6. Finalize winner (retrain on full data)
7. Log metrics to monitoring history

## Execution Flow

```
Step 1: DETERMINE PIPELINE TYPE
         Read descriptive_output.json + cleaned data → detect target, date, features
         → forecasting | regression | classification

Step 2: DATA PREPARATION
         predictive-data-prep skill → ml_ready_data.json

Step 3: SPLIT
         train-test-split skill → train_data.json + test_data.json

Step 4: TRAIN MODELS (4 calls IN PARALLEL)
         {pipeline}-train skill × 4 model_types → model_result_{type}.json

Step 5: EVALUATE & SELECT
         model-evaluate skill → evaluation_result.json (winner selected)

Step 6: FINALIZE
         model-finalize skill → final_model.json (retrained on full data)

Output: predictive_output.json
```

## Pipeline Type Determination

Read from `data/pipeline/{stem}/descriptive_output.json` + cleaned data directly (no bridge needed):

| Signal | Pipeline Type |
|--------|--------------|
| Target is numeric + date column present + question asks "forecast/predict over time" | **Forecasting** |
| Target is numeric + no time dependency or question asks "what drives X" | **Regression** |
| Target is categorical (binary or multi-class) | **Classification** |

## Models by Pipeline Type

### Forecasting
| model_type | Method | Notes |
|------------|--------|-------|
| `seasonal_naive` | Same period from previous cycle | **Baseline** — all models must beat this |
| `prophet` | Facebook's seasonal decomposition | Best for strong seasonality |
| `sarima` | AutoRegressive Integrated Moving Average | Best for stationary series |
| `lgbm_ts` | Lag features + calendar → supervised ML | Best for complex patterns |

**Winner metric:** Lowest MAPE (Mean Absolute Percentage Error)

### Regression
| model_type | Method | Notes |
|------------|--------|-------|
| `mean_baseline` | Predict training mean | **Baseline** — all models must beat this |
| `ridge_lasso` | Linear + L1/L2 regularization | Best for interpretability |
| `random_forest` | Ensemble of decision trees | Best for non-linear + feature importance |
| `xgboost` | Gradient boosting | Best for accuracy |

**Winner metric:** Lowest MAE (Mean Absolute Error)

### Classification
| model_type | Method | Notes |
|------------|--------|-------|
| `naive_logreg` | All-0 + Logistic Regression | **Baseline** — all models must beat this |
| `decision_tree` | Single tree, class_weight='balanced' | Best for interpretability |
| `random_forest` | Ensemble + SMOTE | Best for balanced accuracy |
| `xgboost` | Gradient boosting + SMOTE | Best for accuracy |

**Winner metric:** Highest F1-Score (macro for multi-class)

## Parallel Training Flow

All 4 models for the selected pipeline type train **in parallel**:

```
                    train_data.json
                         │
          ┌──────────────┼──────────────┬──────────────┐
          ▼              ▼              ▼              ▼
     [Baseline]    [Model A]      [Model B]      [Model C]
          │              │              │              │
          ▼              ▼              ▼              ▼
   result_baseline  result_a      result_b      result_c
          │              │              │              │
          └──────────────┴──────────────┴──────────────┘
                         │
                    model-evaluate
                         │
                    model-finalize
```

Use `Bash(python3 scripts/run_parallel.py ...)` or sequential skill calls if parallel execution is unavailable.

## Quality Thresholds

| Check | Threshold | Action if Fail |
|-------|-----------|---------------|
| Best model beats baseline | Required | FAIL — report "no predictive signal" |
| MAPE < 30% (forecasting) | Warning | Proceed but flag low accuracy |
| MAE reasonable vs target range | Warning | Proceed but flag |
| F1 > 0.5 (classification) | Warning | Proceed but flag |
| No model converges | Critical | HALT — report training failure |
| All models produce same prediction | Critical | Flag — likely data issue |

## Output

Write to `data/pipeline/{stem}/predictive_output.json`:
```json
{
  "pipeline_type": "forecasting|regression|classification",
  "models_trained": [
    {
      "model_type": "...",
      "metrics": {"mape": 0.12, "mae": 45.2, "rmse": 67.1},
      "training_time_seconds": 12.5,
      "status": "success|failed"
    }
  ],
  "winner": {
    "model_type": "...",
    "metrics": {},
    "why_selected": "Lowest MAPE among all models",
    "beats_baseline_by": "23% improvement"
  },
  "predictions": [/* forecast/predicted values */],
  "confidence_intervals": [/* if applicable */],
  "feature_importance": [/* top features for tree-based models */],
  "limitations": ["list of caveats"],
  "monitoring": {
    "logged_to": "knowledge/history/{type}_run_history.csv",
    "drift_alerts": []
  }
}
```

## Memory Protocol

**Before starting:** Read `.claude/agent-memory/predictive-trainer/MEMORY.md`.
Apply past learnings — which models worked best for this dataset/domain, optimal hyperparameters already discovered, known data quirks affecting model training (e.g. short series requiring period=6 for Holt-Winters).

**After completing:** Always write results to `.claude/agent-memory/predictive-trainer/` — model selection outcome, MAPE achieved, data filters used, any training quirks. Update `MEMORY.md` index. This is the agent most likely to benefit from memory across runs.

## Critical Rules

1. **Baseline is mandatory** — every pipeline must include a baseline model
2. **All models must beat baseline** — if winner doesn't beat baseline, report "no predictive signal"
3. **Train in parallel** — do not train sequentially unless parallel fails
4. **Return summary to orchestrator** — winner model, key metrics, confidence, limitations
