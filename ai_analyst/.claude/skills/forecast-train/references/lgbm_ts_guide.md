# LightGBM Time Series Guide

> Gradient boosting for time series — treats forecasting as supervised regression on lag features.

## Algorithm Overview

LightGBM-TS is NOT a traditional time series method. Instead, it converts the forecasting problem into a supervised learning problem:

1. Create lag features (past values) and calendar features as inputs (X)
2. Use the target value as the label (y)
3. Train a gradient boosting model: X → y
4. At prediction time, use the latest known values as lag features

```
Traditional TS:  y(t) = f(y(t-1), y(t-2), ..., seasonality, trend)
LightGBM-TS:     y(t) = gbm(lag_1, lag_3, lag_6, lag_12, month, quarter, rolling_mean_3, ...)
```

---

## Implementation

```python
import lightgbm as lgb
import numpy as np
import pandas as pd

def train_lgbm_ts(train_df, test_df, target_col, date_col, feature_cols):
    """
    Train LightGBM for time series forecasting.
    
    Parameters:
        train_df: DataFrame with features + target (features already engineered)
        test_df: DataFrame with features (same columns as train)
        target_col: name of target column
        date_col: name of date column (excluded from features)
        feature_cols: list of feature column names
    
    Returns:
        model, predictions, feature_importance
    """
    # Prepare datasets
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_test = test_df[feature_cols]
    
    # LightGBM dataset
    dtrain = lgb.Dataset(X_train, label=y_train)
    
    # Parameters
    params = {
        'objective': 'regression',
        'metric': 'mae',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Train with early stopping via CV
    cv_results = lgb.cv(
        params, dtrain,
        num_boost_round=500,
        nfold=3,  # Time series CV would be better but sklearn CV is fine for features
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
    )
    best_rounds = len(cv_results['valid mae-mean'])
    
    # Train final model
    model = lgb.train(params, dtrain, num_boost_round=best_rounds)
    
    # Predict
    predictions = model.predict(X_test)
    
    # Feature importance
    importance = dict(zip(feature_cols, model.feature_importance(importance_type='gain')))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    return model, predictions, importance
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `num_leaves` | 31 | 15-63 | Max leaves per tree | Higher = more complex. Start with 31. Reduce if overfitting |
| `learning_rate` | 0.05 | 0.01-0.1 | Step size per boosting round | Lower = more rounds needed but better generalization. 0.05 is good default |
| `n_estimators` | 200 | 100-1000 | Number of boosting rounds | Use early stopping to determine optimal |
| `max_depth` | -1 (no limit) | 3-10 or -1 | Max tree depth | -1 lets num_leaves control complexity. Set 5-7 if overfitting |
| `feature_fraction` | 0.8 | 0.5-1.0 | Fraction of features per tree | Lower = more regularization. 0.8 is good default |
| `bagging_fraction` | 0.8 | 0.5-1.0 | Fraction of data per tree | Lower = more regularization |
| `bagging_freq` | 5 | 1-10 | Perform bagging every k rounds | 5 is standard |
| `min_child_samples` | 20 | 5-100 | Min samples in leaf | Higher = prevents overfitting on small groups |
| `reg_alpha` | 0 | 0-10 | L1 regularization | Add 0.1-1.0 if overfitting |
| `reg_lambda` | 0 | 0-10 | L2 regularization | Add 0.1-1.0 if overfitting |

### Feature Engineering Recap

The quality of LightGBM-TS depends heavily on feature engineering:

```python
# Essential features for time series
FEATURE_TEMPLATE = {
    'lags': [1, 2, 3, 6, 12],           # Autoregressive signal
    'rolling_mean': [3, 6, 12],          # Trend signal
    'rolling_std': [3, 6],               # Volatility signal
    'calendar': ['month', 'quarter',     # Seasonality signal
                 'day_of_week', 'is_weekend',
                 'is_month_end'],
    'trend': ['linear_trend'],           # Linear growth signal
}

# For monthly data, top features are usually:
# 1. lag_1 (most recent value)
# 2. lag_12 (same month last year)  
# 3. rolling_mean_3 (recent trend)
# 4. month (seasonality)
```

---

## Best Practices

1. **Always create lag features** — Without lags, LightGBM has no autoregressive signal and will underperform.
2. **Use early stopping** — Prevents overfitting by stopping when validation loss plateaus.
3. **Feature importance for interpretability** — Check that top features make business sense.
4. **Avoid data leakage in lags** — Use `.shift(1)` on rolling features so they use only past data.
5. **Combine with cross-validation** — TimeSeriesSplit for more robust evaluation.

### Handling Prediction with Lag Dependencies

When predicting multiple steps ahead, lag features for future periods depend on predictions themselves:

```python
def recursive_predict(model, last_known, feature_cols, steps, seasonal_period=12):
    """
    Recursive multi-step prediction.
    Each prediction becomes input for the next step.
    
    WARNING: Error compounds with each step. 
    Reliable for ~1-3 steps, degrades after.
    """
    predictions = []
    history = list(last_known)
    
    for step in range(steps):
        # Build features from history
        features = {}
        for lag in [1, 2, 3, 6, 12]:
            if len(history) >= lag:
                features[f'lag_{lag}'] = history[-lag]
            else:
                features[f'lag_{lag}'] = np.nan
        
        features['rolling_mean_3'] = np.mean(history[-3:]) if len(history) >= 3 else np.nan
        features['rolling_mean_6'] = np.mean(history[-6:]) if len(history) >= 6 else np.nan
        # ... add calendar features based on next date
        
        X = pd.DataFrame([features])[feature_cols]
        pred = model.predict(X)[0]
        predictions.append(pred)
        history.append(pred)
    
    return np.array(predictions)
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **No lag features** | Model has no temporal signal | Always include lag_1 at minimum |
| **Leaky rolling features** | Rolling window includes current/future values | Use `.shift(1)` before `.rolling()` |
| **Overfitting on calendar** | Month/quarter memorized instead of generalized | Reduce num_leaves; add regularization |
| **Recursive error compounding** | Multi-step forecasts degrade quickly | Use direct multi-output or limit horizon |
| **Ignoring feature importance** | Black-box predictions | Always check — top features should be interpretable |
| **Too many features** | Noise features dilute signal | Use feature_fraction=0.6, reduce feature count |

---

## When LightGBM-TS Works Best

- **Non-linear seasonal patterns** — Seasonality that changes shape or amplitude
- **Many exogenous features** — Marketing spend, promotions, weather, etc.
- **Large datasets** (> 500 data points) — More data = better gradient boosting performance
- **Complex interactions** — E.g., weekend + holiday interaction effects

## When LightGBM-TS Struggles

- **Very short series** (< 50 points) — Not enough data for gradient boosting
- **Pure linear trend + seasonality** — Prophet/SARIMA are simpler and sufficient
- **Interpretability requirements** — Tree-based models are harder to explain than SARIMA
- **Long forecast horizons** — Recursive prediction error compounds rapidly

## Comparison with Other Models

| Aspect | LightGBM-TS | Prophet | SARIMA |
|--------|------------|---------|--------|
| Non-linearity | Excellent | Limited | None |
| Exogenous features | Excellent | Good (regressors) | Limited |
| Small data | Poor | Good | Good |
| Interpretability | Moderate (feature importance) | Good (components) | Good (orders) |
| Speed | Fast | Moderate | Slow (auto_arima) |
| Multi-seasonality | Good (via features) | Excellent | Poor |
