---
name: model-finalize
description: >
  Retrain the winning model on full data (train+test combined), perform threshold tuning
  for classification, run residual analysis, and generate final predictions with confidence intervals.
  Trigger: called by predictive-trainer subagent after model-evaluate.
when_to_use: "finalize model", "retrain winner", "threshold tuning", "final predictions"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write
model: sonnet
effort: high
version: "1.0"
---

# Skill: Model Finalize

## Purpose
Retrain the winning model on the full dataset (train + test combined) to maximize data utilization. For classification, tune the prediction threshold. Run residual analysis to verify model quality. Generate final predictions with confidence intervals.

**Reads:** `data/pipeline/{stem}/evaluation_result.json` + full dataset
**Writes:** `data/pipeline/{stem}/final_model.json`

**Read references:** `references/retrain_protocol.md` · `references/threshold_tuning.md`

---

## Steps

### Step 1: Load Evaluation Result and Data
```python
import json
import pandas as pd

with open(f"data/pipeline/{stem}/evaluation_result.json") as f:
    eval_result = json.load(f)

winner = eval_result["winner"]
model_type = winner["model_type"]
pipeline_type = eval_result["pipeline_type"]

# Load full dataset (train + test)
with open(f"data/pipeline/{stem}/train_data.json") as f:
    train = json.load(f)
with open(f"data/pipeline/{stem}/test_data.json") as f:
    test = json.load(f)

full_df = pd.concat([
    pd.DataFrame(train["train_data"]["values"]),
    pd.DataFrame(test["test_data"]["values"])
]).reset_index(drop=True)
```

### Step 2: Retrain Winner on Full Data
```python
# Use the same hyperparameters as the winning model
# from model_result_{model_type}.json
with open(f"data/pipeline/{stem}/model_result_{model_type}.json") as f:
    winner_result = json.load(f)

model_params = winner_result["model_params"]

# Retrain with full data (same code as *-train skill, but full_df instead of train_df)
# ... dispatch by pipeline_type and model_type ...
```

### Step 3: Threshold Tuning (Classification Only)
```python
if pipeline_type == "classification":
    from sklearn.metrics import f1_score, precision_recall_curve
    
    # Use cross-validation on full data for threshold selection
    from sklearn.model_selection import StratifiedKFold
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    all_probs, all_labels = [], []
    
    for train_idx, val_idx in skf.split(X_full, y_full):
        model_cv = clone_and_fit(model, X_full.iloc[train_idx], y_full.iloc[train_idx])
        probs = model_cv.predict_proba(X_full.iloc[val_idx])[:, 1]
        all_probs.extend(probs)
        all_labels.extend(y_full.iloc[val_idx])
    
    # Method 1: F1-maximizing threshold
    thresholds = np.arange(0.1, 0.9, 0.01)
    f1_scores = [f1_score(all_labels, (np.array(all_probs) >= t).astype(int)) for t in thresholds]
    optimal_threshold_f1 = thresholds[np.argmax(f1_scores)]
    
    # Method 2: Cost-based threshold (if costs provided)
    # optimal_threshold_cost = minimize_cost(all_labels, all_probs, cost_FP, cost_FN)
    
    final_threshold = optimal_threshold_f1
```

### Step 4: Residual Analysis
```python
if pipeline_type in ["forecasting", "regression"]:
    residuals = actuals - predictions
    
    residual_analysis = {
        "mean": float(np.mean(residuals)),
        "std": float(np.std(residuals)),
        "skewness": float(pd.Series(residuals).skew()),
        "kurtosis": float(pd.Series(residuals).kurtosis()),
        "normality_test_p": float(shapiro(residuals[:500])[1]),
        "autocorrelation_lag1": float(pd.Series(residuals).autocorr(lag=1)),
        "has_pattern": abs(pd.Series(residuals).autocorr(lag=1)) > 0.3,
        "quality": "good" if abs(np.mean(residuals)) < np.std(residuals) * 0.1 else "biased"
    }
```

### Step 5: Generate Final Predictions with Confidence Intervals
```python
if pipeline_type == "forecasting":
    # Confidence intervals from residual std
    ci_multiplier = 1.96  # 95% CI
    final_predictions = [{
        "date": str(date),
        "predicted": float(pred),
        "lower_95": float(pred - ci_multiplier * residual_std),
        "upper_95": float(pred + ci_multiplier * residual_std)
    } for date, pred in zip(future_dates, predictions)]

elif pipeline_type == "regression":
    final_predictions = [{
        "index": int(i),
        "predicted": float(pred),
        "lower_95": float(pred - ci_multiplier * residual_std),
        "upper_95": float(pred + ci_multiplier * residual_std)
    } for i, pred in enumerate(predictions)]

elif pipeline_type == "classification":
    final_predictions = [{
        "index": int(i),
        "probability": float(prob),
        "predicted_class": int(prob >= final_threshold),
        "threshold_used": float(final_threshold)
    } for i, prob in enumerate(probabilities)]
```

### Step 6: Write Final Model Output
Write to `data/pipeline/{stem}/final_model.json`.

---

## Rules

**R-1:** Always retrain on full data (train + test). This maximizes data utilization.
**R-2:** Use the EXACT same hyperparameters as the winning model from evaluation.
**R-3:** For classification, NEVER use default 0.5 threshold — always tune.
**R-4:** Residual analysis must check for systematic patterns (bias, autocorrelation).
**R-5:** Always include confidence intervals in predictions.
**R-6:** If residuals show strong patterns (autocorrelation > 0.3), WARN — model may be misspecified.

---

## Output Schema

```json
{
  "skill_type": "model_finalize",
  "run_context": {},
  "pipeline_type": "forecasting|regression|classification",
  "winner": {
    "model_type": "prophet",
    "primary_metric": "mape",
    "primary_value": 8.2,
    "improvement_vs_baseline": "47.4%"
  },
  "retrained_on_full_data": true,
  "full_data_size": 50000,
  "threshold": {
    "value": 0.35,
    "method": "f1_maximizing",
    "f1_at_threshold": 0.76,
    "precision_at_threshold": 0.72,
    "recall_at_threshold": 0.81
  },
  "residual_analysis": {
    "mean": 0.02,
    "std": 45000,
    "skewness": 0.15,
    "kurtosis": 2.8,
    "normality_p": 0.12,
    "autocorrelation_lag1": 0.08,
    "has_pattern": false,
    "quality": "good"
  },
  "final_predictions": [
    {
      "date": "2026-09-01",
      "predicted": 1150000,
      "lower_95": 1062000,
      "upper_95": 1238000
    }
  ],
  "feature_importance": {"lag_1": 0.35, "month": 0.20},
  "model_params": {},
  "finding_box": {
    "text": "Revenue predicted to recover to $2.1M by Q3 (Prophet, MAPE 8.2%)",
    "sub": "Based on seasonal patterns + expansion pipeline"
  },
  "metadata": {
    "retrain_time_seconds": 15.2,
    "generated_at": "ISO 8601"
  }
}
```
