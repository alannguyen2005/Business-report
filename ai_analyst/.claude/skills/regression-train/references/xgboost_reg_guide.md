# XGBoost Regression Guide

> Gradient boosting — typically the top performer for structured/tabular data.

## Algorithm Overview

XGBoost builds trees sequentially, where each new tree corrects the errors of the previous ensemble:

```
Step 1: Predict with initial value (mean)
Step 2: Compute residuals (errors)
Step 3: Train tree to predict residuals
Step 4: Add tree prediction × learning_rate to ensemble
Step 5: Repeat from Step 2 with updated residuals
```

Key innovations over vanilla gradient boosting:
- L1 + L2 regularization on leaf weights
- Column subsampling (like Random Forest)
- Built-in handling of missing values
- Histogram-based splitting (fast)

---

## Implementation

```python
import xgboost as xgb
import numpy as np

def train_xgboost_reg(X_train, y_train, X_test, y_test):
    """
    Train XGBoost regressor with early stopping.
    """
    model = xgb.XGBRegressor(
        learning_rate=0.05,
        max_depth=6,
        n_estimators=300,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,       # L1 regularization
        reg_lambda=1.0,      # L2 regularization
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )
    
    # Train with early stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    predictions = model.predict(X_test)
    
    # Feature importance
    importance = dict(zip(X_train.columns, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'model': model,
        'predictions': predictions,
        'feature_importance': importance,
        'best_iteration': model.best_iteration if hasattr(model, 'best_iteration') else 300,
        'best_score': model.best_score if hasattr(model, 'best_score') else None
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `learning_rate` (eta) | 0.05 | 0.01-0.3 | Step size per round | Lower = better generalization but need more rounds. 0.05 is safe default |
| `max_depth` | 6 | 3-10 | Max tree depth | Higher = more complex. 6 is good default. Reduce to 3-4 if overfitting |
| `n_estimators` | 300 | 100-2000 | Max boosting rounds | Use early stopping. Set high and let early stop find optimal |
| `subsample` | 0.8 | 0.5-1.0 | Row sampling ratio | Lower = more regularization. 0.8 is standard |
| `colsample_bytree` | 0.8 | 0.5-1.0 | Feature sampling per tree | Lower = more regularization. 0.8 is standard |
| `reg_alpha` | 0.1 | 0-10 | L1 regularization on weights | Increase if overfitting |
| `reg_lambda` | 1.0 | 0-10 | L2 regularization on weights | Increase if overfitting |
| `min_child_weight` | 1 | 1-10 | Min sum of instance weight in child | Higher = more conservative. Increase for noisy data |
| `gamma` | 0 | 0-5 | Min loss reduction for split | Higher = fewer splits. Add 0.1-1.0 if overfitting |

### Tuning Strategy (3 Steps)

```python
# Step 1: Fix learning_rate=0.1, find optimal n_estimators via early stopping
model = xgb.XGBRegressor(learning_rate=0.1, n_estimators=1000, ...)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
          early_stopping_rounds=50, verbose=False)
best_n = model.best_iteration

# Step 2: Grid search max_depth and min_child_weight
from sklearn.model_selection import GridSearchCV
param_grid = {
    'max_depth': [3, 5, 7, 9],
    'min_child_weight': [1, 3, 5]
}
grid = GridSearchCV(xgb.XGBRegressor(n_estimators=best_n, learning_rate=0.1),
                     param_grid, cv=5, scoring='neg_mean_absolute_error')
grid.fit(X_train, y_train)

# Step 3: Lower learning_rate, increase n_estimators proportionally
# lr=0.1 with 200 rounds ≈ lr=0.05 with 400 rounds
final_model = xgb.XGBRegressor(
    learning_rate=0.05,
    n_estimators=best_n * 2,
    **grid.best_params_
)
```

---

## Best Practices

1. **Always use early stopping** — Prevents overfitting and finds optimal n_estimators automatically.
2. **No scaling needed** — Tree-based; scale-invariant.
3. **Handle missing values** — XGBoost handles NaN natively. Don't impute unless you have domain knowledge.
4. **Check learning curves** — Plot train vs test error to diagnose over/underfitting.
5. **Use `importance_type='gain'`** — More reliable than 'weight' (split count).

### Learning Curve Diagnostics
```python
def plot_learning_curve(model):
    """
    Diagnose overfitting from evaluation results.
    """
    results = model.evals_result()
    train_loss = results['validation_0']['rmse']
    test_loss = results['validation_1']['rmse']
    
    # Interpretation:
    # - Both decreasing: underfitting (more rounds or increase complexity)
    # - Train decreasing, test increasing: overfitting
    # - Both flat: converged (good)
    # - Large gap: overfitting (reduce depth, increase regularization)
    
    gap = test_loss[-1] - train_loss[-1]
    if gap > 0.1 * test_loss[-1]:
        return "overfitting — reduce max_depth or increase reg_lambda"
    elif test_loss[-1] > train_loss[-1] * 1.5:
        return "significant overfitting — major regularization needed"
    else:
        return "good fit"
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **No early stopping** | Overfitting with too many rounds | Always set `early_stopping_rounds=50` |
| **Learning rate too high** | Fast convergence but poor generalization | Use 0.01-0.05 for final model |
| **Max depth too high** | Overfitting on noise | Start with 6, reduce to 3-4 for small data |
| **Ignoring feature importance** | Using all features blindly | Remove features with 0 importance |
| **Data leakage in eval_set** | Using test data for early stopping | Acceptable for single-model training; use validation split for production |
| **Extrapolation** | Same limitation as all tree models | Cannot predict beyond training range |

---

## When XGBoost Works Best

- **Tabular/structured data** — XGBoost is consistently top performer on tabular data
- **Non-linear relationships** — Complex interactions and thresholds
- **Mixed feature types** — Handles numeric + categorical + missing natively
- **Moderate to large datasets** (1K - 1M rows) — Scales well with histogram binning

## When XGBoost Struggles

- **Very small data** (<200 rows) — Overfitting risk; try Ridge/Lasso instead
- **Strong linear signal** — Simpler Ridge may match XGBoost with better interpretability
- **Extrapolation needed** — Cannot predict outside training range (use linear model)
- **Real-time inference** — Slower than linear models (but fast enough for batch)

## Comparison with Random Forest

| Aspect | XGBoost | Random Forest |
|--------|---------|---------------|
| Training | Sequential (slower) | Parallel (faster) |
| Overfitting risk | Higher (needs regularization) | Lower (bagging reduces variance) |
| Accuracy | Usually better | Usually good, rarely best |
| Hyperparameter sensitivity | High (needs tuning) | Low (good defaults) |
| Missing values | Handles natively | Requires imputation |
