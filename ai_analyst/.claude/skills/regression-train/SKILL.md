---
name: regression-train
description: >
  Train a single regression model (param: model_type). Supports mean_baseline, ridge_lasso,
  random_forest, xgboost. Reads train/test data, trains model, predicts on test, computes MAE/RMSE/R².
  Trigger: called by predictive-trainer subagent, 4 times in PARALLEL (one per model_type).
when_to_use: "train regression", "ridge", "lasso", "random forest regression", "xgboost regression"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write
model: sonnet
effort: high
version: "1.0"
---

# Skill: Regression Train

## Purpose
Train a single regression model specified by `model_type` parameter. Called 4 times in parallel by `predictive-trainer` subagent — once per model type. Each invocation is independent and writes its own result file.

**Reads:** `data/pipeline/{stem}/train_data.json` + `data/pipeline/{stem}/test_data.json` + `model_type` param
**Writes:** `data/pipeline/{stem}/model_result_{model_type}.json`

**Read references:** `references/ridge_lasso_guide.md` · `references/random_forest_reg_guide.md` · `references/xgboost_reg_guide.md`

---

## Parameters

| Parameter | Required | Values |
|---|---|---|
| `model_type` | Yes | `mean_baseline` \| `ridge_lasso` \| `random_forest` \| `xgboost` |

---

## Steps

### Step 1: Load Data
```python
import json
import pandas as pd

with open(f"data/pipeline/{stem}/train_data.json") as f:
    train_data = json.load(f)
with open(f"data/pipeline/{stem}/test_data.json") as f:
    test_data = json.load(f)

train_df = pd.DataFrame(train_data["train_data"]["values"])
test_df = pd.DataFrame(test_data["test_data"]["values"])
target_col = train_data["train_data"]["target_column"]
feature_cols = [c for c in train_df.columns if c != target_col]

X_train, y_train = train_df[feature_cols], train_df[target_col]
X_test, y_test = test_df[feature_cols], test_df[target_col]
```

### Step 2: Train Model (dispatch by model_type)

**`mean_baseline`** — Baseline model:
```python
# Predict training set mean for all test samples
train_mean = y_train.mean()
predictions = [train_mean] * len(y_test)
model_params = {"strategy": "mean", "train_mean": train_mean}
```

**`ridge_lasso`** — Linear with L1/L2 regularization:
```python
from sklearn.linear_model import RidgeCV, LassoCV
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# Try both Ridge and Lasso, pick better one
ridge = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0], cv=5)
ridge.fit(X_train_sc, y_train)

lasso = LassoCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0], cv=5, random_state=42)
lasso.fit(X_train_sc, y_train)

# Select winner by CV score
if ridge.score(X_train_sc, y_train) >= lasso.score(X_train_sc, y_train):
    model, model_name = ridge, "Ridge"
else:
    model, model_name = lasso, "Lasso"

predictions = model.predict(X_test_sc)
coefficients = dict(zip(feature_cols, model.coef_))
```

**`random_forest`** — Ensemble of decision trees:
```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=100, max_depth=None, min_samples_split=5,
    min_samples_leaf=2, random_state=42, n_jobs=-1
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
feature_importance = dict(zip(feature_cols, model.feature_importances_))
```

**`xgboost`** — Gradient boosting:
```python
import xgboost as xgb

model = xgb.XGBRegressor(
    learning_rate=0.05, max_depth=6, n_estimators=300,
    subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1,
    reg_lambda=1.0, random_state=42, n_jobs=-1
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)],
          verbose=False)
predictions = model.predict(X_test)
feature_importance = dict(zip(feature_cols, model.feature_importances_))
```

### Step 3: Compute Metrics
```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

actuals = y_test.values

mae = mean_absolute_error(actuals, predictions)
rmse = np.sqrt(mean_squared_error(actuals, predictions))
r2 = r2_score(actuals, predictions)

metrics = {
    "mae": round(mae, 2),
    "rmse": round(rmse, 2),
    "r2": round(r2, 4)
}
```

### Step 4: Write Result
Write to `data/pipeline/{stem}/model_result_{model_type}.json`.

---

## Rules

**R-1:** Each invocation trains exactly ONE model. Do not train multiple models.
**R-2:** Primary metric is MAE. Lower MAE = better model.
**R-3:** If R² < 0, flag as "model worse than mean prediction" in metadata.
**R-4:** For ridge_lasso, try both Ridge and Lasso — report whichever has lower CV error.
**R-5:** Always use `random_state=42` for reproducibility.
**R-6:** Never modify test data — predict only.

---

## Output Schema

```json
{
  "skill_type": "regression_train",
  "model_type": "mean_baseline|ridge_lasso|random_forest|xgboost",
  "run_context": {},
  "status": "success|failed",
  "model_params": {
    "n_estimators": 100,
    "max_depth": null,
    "alpha": 1.0
  },
  "model_variant": "Ridge|Lasso|null",
  "metrics": {
    "mae": 45000.50,
    "rmse": 62000.30,
    "r2": 0.82
  },
  "predictions": [
    {"index": 0, "actual": 120000, "predicted": 115000},
    {"index": 1, "actual": 135000, "predicted": 128000}
  ],
  "feature_importance": {"feature_a": 0.35, "feature_b": 0.20},
  "coefficients": {"feature_a": 1250.5, "feature_b": -890.2},
  "residual_analysis": {
    "mean_residual": 0.02,
    "std_residual": 45000,
    "residual_skew": 0.15,
    "quality_flag": "good|acceptable|poor"
  },
  "metadata": {
    "train_size": 40000,
    "test_size": 10000,
    "n_features": 32,
    "training_time_seconds": 8.5,
    "generated_at": "ISO 8601"
  }
}
```
