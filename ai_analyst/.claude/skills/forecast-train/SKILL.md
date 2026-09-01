---
name: forecast-train
description: >
  Train a single forecasting model (param: model_type). Supports seasonal_naive, prophet,
  sarima, lgbm_ts. Reads train/test data, trains model, predicts on test, computes MAPE/MAE/RMSE.
  Trigger: called by predictive-trainer subagent, 4 times in PARALLEL (one per model_type).
when_to_use: "train forecast", "prophet", "sarima", "lgbm forecast", "time series model"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write
model: sonnet
effort: high
version: "1.0"
---

# Skill: Forecast Train

## Purpose
Train a single forecasting model specified by `model_type` parameter. Called 4 times in parallel by `predictive-trainer` subagent — once per model type. Each invocation is independent and writes its own result file.

**Reads:** `data/pipeline/{stem}/train_data.json` + `data/pipeline/{stem}/test_data.json` + `model_type` param
**Writes:** `data/pipeline/{stem}/model_result_{model_type}.json`

**Read references:** `references/seasonal_naive_guide.md` · `references/prophet_guide.md` · `references/sarima_guide.md` · `references/lgbm_ts_guide.md`

---

## Parameters

| Parameter | Required | Values |
|---|---|---|
| `model_type` | Yes | `seasonal_naive` \| `prophet` \| `sarima` \| `lgbm_ts` |

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
date_col = train_data.get("date_column")
```

### Step 2: Train Model (dispatch by model_type)

**`seasonal_naive`** — Baseline model:
```python
season_length = detected_seasonal_period  # 12 for monthly, 7 for daily
predictions = []
for i in range(len(test_df)):
    # Predict: same value from one season ago
    idx = len(train_df) - season_length + (i % season_length)
    predictions.append(train_df[target_col].iloc[idx])
```

**`prophet`** — Facebook Prophet:
```python
from prophet import Prophet
model = Prophet(
    changepoint_prior_scale=0.05,
    seasonality_mode='multiplicative',  # or 'additive'
    yearly_seasonality=True,
    weekly_seasonality='auto',
    daily_seasonality=False
)
prophet_df = train_df.rename(columns={date_col: 'ds', target_col: 'y'})
model.fit(prophet_df)
future = model.make_future_dataframe(periods=len(test_df), freq=freq)
forecast = model.predict(future)
predictions = forecast.tail(len(test_df))['yhat'].values
```

**`sarima`** — Auto SARIMA:
```python
import pmdarima as pm
model = pm.auto_arima(
    train_df[target_col],
    seasonal=True, m=seasonal_period,
    stepwise=True, suppress_warnings=True,
    error_action='ignore',
    max_order=5, max_p=3, max_q=3,
    max_P=2, max_Q=2, max_D=1
)
predictions = model.predict(n_periods=len(test_df))
order = model.order        # (p, d, q)
seasonal = model.seasonal_order  # (P, D, Q, m)
```

**`lgbm_ts`** — LightGBM with lag features:
```python
import lightgbm as lgb
feature_cols = [c for c in train_df.columns if c not in [target_col, date_col]]
dtrain = lgb.Dataset(train_df[feature_cols], label=train_df[target_col])
params = {
    'objective': 'regression',
    'metric': 'mae',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'n_estimators': 200,
    'verbose': -1,
    'random_state': 42
}
model = lgb.train(params, dtrain, num_boost_round=200)
predictions = model.predict(test_df[feature_cols])
feature_importance = dict(zip(feature_cols, model.feature_importance()))
```

### Step 3: Compute Metrics
```python
import numpy as np

actuals = test_df[target_col].values

# MAPE (primary metric for forecasting)
mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100

# MAE
mae = np.mean(np.abs(actuals - predictions))

# RMSE
rmse = np.sqrt(np.mean((actuals - predictions) ** 2))

metrics = {
    "mape": round(mape, 2),
    "mae": round(mae, 2),
    "rmse": round(rmse, 2)
}
```

### Step 4: Write Result
Write to `data/pipeline/{stem}/model_result_{model_type}.json`.

---

## Rules

**R-1:** Each invocation trains exactly ONE model. Do not train multiple models.
**R-2:** Primary metric is MAPE. Lower MAPE = better forecast.
**R-3:** If MAPE > 50%, flag as "poor forecast quality" in metadata.
**R-4:** If Prophet/SARIMA fails to converge, catch exception and write result with `status: "failed"`.
**R-5:** Always use `random_state=42` where applicable.
**R-6:** Never modify test data — predict only.

---

## Output Schema

```json
{
  "skill_type": "forecast_train",
  "model_type": "prophet|sarima|lgbm_ts|seasonal_naive",
  "run_context": {},
  "status": "success|failed",
  "model_params": {
    "changepoint_prior_scale": 0.05,
    "seasonality_mode": "multiplicative"
  },
  "metrics": {
    "mape": 8.2,
    "mae": 45000,
    "rmse": 62000
  },
  "predictions": [
    {"date": "2026-09-01", "actual": 1200000, "predicted": 1150000},
    {"date": "2026-10-01", "actual": 1350000, "predicted": 1280000}
  ],
  "feature_importance": {"lag_1": 0.35, "month": 0.20},
  "confidence_interval": {
    "lower": [1100000, 1220000],
    "upper": [1200000, 1340000]
  },
  "diagnostics": {
    "convergence": true,
    "residual_mean": 0.02,
    "residual_std": 45000,
    "quality_flag": "good|acceptable|poor"
  },
  "metadata": {
    "train_size": 40000,
    "test_size": 10000,
    "training_time_seconds": 12.5,
    "generated_at": "ISO 8601"
  }
}
```
