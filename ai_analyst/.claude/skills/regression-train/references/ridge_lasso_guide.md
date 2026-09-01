# Ridge & Lasso Regression Guide

> Linear models with regularization — interpretable baselines for regression.

## Algorithm Overview

Both Ridge and Lasso are linear regression with a penalty term to prevent overfitting:

```
Ridge (L2): minimize ||y - Xβ||² + α||β||²
  → Shrinks coefficients toward zero, but never exactly zero
  → All features kept, just dampened

Lasso (L1): minimize ||y - Xβ||² + α||β||₁  
  → Can set coefficients to exactly zero
  → Performs automatic feature selection

ElasticNet (L1+L2): minimize ||y - Xβ||² + α₁||β||₁ + α₂||β||²
  → Combines both penalties
```

---

## Implementation

```python
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler

def train_ridge_lasso(X_train, y_train, X_test):
    """
    Train both Ridge and Lasso with cross-validated alpha selection.
    Returns the better model.
    """
    # CRITICAL: Scale features before regularization
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    
    # Alpha candidates (log scale)
    alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
    
    # Ridge with 5-fold CV
    ridge = RidgeCV(alphas=alphas, cv=5, scoring='neg_mean_absolute_error')
    ridge.fit(X_train_sc, y_train)
    ridge_score = -ridge.score(X_train_sc, y_train)  # negative MAE → positive
    
    # Lasso with 5-fold CV
    lasso = LassoCV(alphas=alphas, cv=5, random_state=42, max_iter=10000)
    lasso.fit(X_train_sc, y_train)
    lasso_score = lasso.score(X_train_sc, y_train)
    
    # Compare on training CV score
    ridge_mae = -np.mean(np.abs(y_train - ridge.predict(X_train_sc)))
    lasso_mae = -np.mean(np.abs(y_train - lasso.predict(X_train_sc)))
    
    if ridge_mae >= lasso_mae:
        best_model = ridge
        variant = "Ridge"
        best_alpha = ridge.alpha_
    else:
        best_model = lasso
        variant = "Lasso"
        best_alpha = lasso.alpha_
    
    predictions = best_model.predict(X_test_sc)
    
    return {
        'model': best_model,
        'scaler': scaler,
        'variant': variant,
        'alpha': best_alpha,
        'predictions': predictions,
        'coefficients': dict(zip(X_train.columns, best_model.coef_)),
        'intercept': float(best_model.intercept_)
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `alpha` | 1.0 | 0.001 - 1000 | Regularization strength. Higher = more shrinkage |
| `cv` | 5 | 3-10 | Cross-validation folds for alpha selection |
| `max_iter` | 1000 | 1000-10000 | Max iterations (Lasso). Increase if not converging |
| `tol` | 1e-4 | 1e-6 - 1e-3 | Convergence tolerance |
| `fit_intercept` | True | True/False | Whether to fit intercept term |

### How Alpha Works
```
α = 0:      No regularization → ordinary least squares (may overfit)
α = small:  Mild regularization → most coefficients active
α = large:  Strong regularization → most coefficients ≈ 0
α = ∞:      All coefficients = 0 (predict intercept only)
```

### When to Choose Ridge vs Lasso

| Scenario | Prefer | Why |
|----------|--------|-----|
| Many correlated features | Ridge | Ridge handles multicollinearity; Lasso drops one arbitrarily |
| Want feature selection | Lasso | Lasso zeros out irrelevant features |
| > 100 features | Lasso | Automatic dimensionality reduction |
| All features important | Ridge | Ridge preserves all features with damping |
| Uncertain | Try both | RidgeCV + LassoCV, compare MAE |

---

## Best Practices

1. **ALWAYS StandardScale before fitting** — Regularization penalizes large coefficients. Without scaling, features on larger scales get penalized more, which is unfair.
2. **Use CV for alpha selection** — Never hand-pick alpha. Let `RidgeCV`/`LassoCV` search.
3. **Check coefficient signs** — If a coefficient has an unexpected sign, the model may have collinearity issues.
4. **Report top features** — Sort coefficients by absolute value. Top features = most influential.
5. **Lasso convergence** — If `ConvergenceWarning`, increase `max_iter` to 10000.

### Interpreting Coefficients
```python
def interpret_coefficients(model, feature_names, scaler):
    """
    Convert scaled coefficients to original-scale impact.
    """
    coefs = pd.DataFrame({
        'feature': feature_names,
        'coefficient': model.coef_,
        'abs_coefficient': np.abs(model.coef_)
    }).sort_values('abs_coefficient', ascending=False)
    
    # Interpretation: "1 std increase in feature X → coefficient change in y"
    # For original scale: coefficient / scaler.scale_[i]
    coefs['original_scale_impact'] = model.coef_ / scaler.scale_
    
    return coefs
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **No scaling** | Regularization unfairly penalizes large-scale features | Always `StandardScaler` before fitting |
| **Wrong alpha** | Too small → overfit, too large → underfit | Use `RidgeCV`/`LassoCV` with wide alpha range |
| **Lasso instability** | Different features selected on different data subsets | Use Ridge if stability matters, or ElasticNet |
| **Non-linear relationships** | Linear model can't capture curves | Consider polynomial features or switch to tree model |
| **High multicollinearity** | Lasso drops one of correlated pair randomly | Use Ridge or VIF check before Lasso |
| **Extrapolation** | Linear models extrapolate dangerously beyond training range | Flag predictions outside training feature range |
