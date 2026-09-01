# Random Forest Regression Guide

> Ensemble of decision trees — robust, non-linear, resistant to outliers.

## Algorithm Overview

Random Forest builds N independent decision trees, each trained on:
- A bootstrap sample (random subset of rows with replacement)
- A random subset of features at each split

Final prediction = average of all tree predictions (reduces variance).

```
Tree 1: train on 63% of data, random features → prediction_1
Tree 2: train on 63% of data, random features → prediction_2
...
Tree N: train on 63% of data, random features → prediction_N

Final = mean(prediction_1, prediction_2, ..., prediction_N)
```

---

## Implementation

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import numpy as np

def train_random_forest_reg(X_train, y_train, X_test):
    """
    Train Random Forest regressor with reasonable defaults.
    """
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=None,          # Grow full trees
        min_samples_split=5,     # At least 5 samples to split
        min_samples_leaf=2,      # At least 2 samples in leaf
        max_features='sqrt',     # sqrt(n_features) per split
        random_state=42,
        n_jobs=-1
    )
    
    # Cross-validation on training set
    cv_scores = cross_val_score(model, X_train, y_train, cv=5,
                                 scoring='neg_mean_absolute_error')
    cv_mae = -cv_scores.mean()
    
    # Fit final model on full training set
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    # Feature importance (mean decrease in impurity)
    importance = dict(zip(X_train.columns, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'model': model,
        'predictions': predictions,
        'feature_importance': importance,
        'cv_mae': cv_mae,
        'n_estimators': 100,
        'oob_score': model.oob_score_ if hasattr(model, 'oob_score_') else None
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `n_estimators` | 100 | 50-500 | Number of trees | More trees = better (diminishing returns after ~200). Rarely need >500 |
| `max_depth` | None | 5-30 or None | Max depth per tree | None = fully grown. Set 10-20 if overfitting |
| `min_samples_split` | 5 | 2-20 | Min samples to split a node | Higher = more regularization |
| `min_samples_leaf` | 2 | 1-10 | Min samples in a leaf node | Higher = smoother predictions |
| `max_features` | 'sqrt' | 'sqrt', 'log2', 0.3-1.0 | Features considered per split | 'sqrt' for high-dim, 1.0 for low-dim |
| `bootstrap` | True | True/False | Use bootstrap sampling | True enables OOB score; False = use all data |
| `oob_score` | False | True/False | Out-of-bag evaluation | Set True for free validation estimate |

### Quick Tuning Strategy
```python
from sklearn.model_selection import RandomizedSearchCV

param_dist = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2', 0.5]
}

search = RandomizedSearchCV(
    RandomForestRegressor(random_state=42),
    param_dist, n_iter=20, cv=5,
    scoring='neg_mean_absolute_error',
    random_state=42, n_jobs=-1
)
search.fit(X_train, y_train)
best_model = search.best_estimator_
```

---

## Best Practices

1. **Start with defaults** — `n_estimators=100, max_depth=None` is a strong baseline.
2. **No scaling needed** — Trees are scale-invariant. Don't waste time on StandardScaler.
3. **Check OOB score** — Set `oob_score=True` for free validation without holdout.
4. **Feature importance is approximate** — Use permutation importance for more reliable ranking.
5. **Watch for overfitting** — If train MAE << test MAE, reduce max_depth or increase min_samples_leaf.

### Permutation Importance (More Reliable)
```python
from sklearn.inspection import permutation_importance

perm_imp = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
sorted_idx = perm_imp.importances_mean.argsort()[::-1]

for i in sorted_idx[:10]:
    print(f"{X_test.columns[i]}: {perm_imp.importances_mean[i]:.4f} ± {perm_imp.importances_std[i]:.4f}")
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Can't extrapolate** | RF predictions bounded by training range | Expected limitation — flag if test has out-of-range values |
| **Slow with large data** | 100 trees × 1M rows = slow | Reduce n_estimators or subsample data |
| **Overfitting** | Train MAE = 0 but test MAE high | Increase `min_samples_leaf` to 5-10, set `max_depth=15` |
| **Misleading importance** | MDI biases toward high-cardinality features | Use permutation importance on test set |
| **Correlated features** | Importance split between correlated features | VIF check before training; drop redundant features |
| **Memory usage** | Deep trees consume memory | Set `max_depth=20` for large datasets |

---

## When Random Forest Works Best

- **Non-linear relationships** — Complex patterns that linear models miss
- **Robustness needed** — Outlier-resistant, no scaling required
- **Feature importance needed** — Quick way to identify important predictors
- **Moderate data size** (1K - 100K rows) — Good performance without tuning

## When Random Forest Struggles

- **Extrapolation** — Cannot predict outside training range (linear model is better for trends)
- **Very high dimensions** (>1000 features) — Slow, consider XGBoost or feature selection
- **Strong linear relationships** — Ridge/Lasso will be simpler and equivalent
- **Small data** (<200 rows) — Overfitting risk even with regularization
