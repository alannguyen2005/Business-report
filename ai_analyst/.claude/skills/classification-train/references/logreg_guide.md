# Logistic Regression Guide

> Interpretable linear classifier — the baseline every classification model must beat.

## Algorithm Overview

Logistic Regression fits a linear decision boundary, then applies the sigmoid function to produce probabilities:

```
z = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ    (linear combination)
P(y=1|x) = 1 / (1 + e^(-z))              (sigmoid → probability)
Predict: 1 if P > threshold, else 0       (default threshold = 0.5)
```

Despite its name, Logistic Regression is a **classification** algorithm, not regression.

---

## Implementation

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def train_logistic_regression(X_train, y_train, X_test):
    """
    Train Logistic Regression with balanced class weights.
    """
    # Scale features (important for logistic regression)
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    
    model = LogisticRegression(
        class_weight='balanced',  # Adjust for imbalance
        max_iter=1000,            # Ensure convergence
        random_state=42,
        solver='lbfgs',           # Good for medium datasets
        C=1.0,                    # Inverse regularization strength
        penalty='l2'              # L2 regularization (default)
    )
    
    model.fit(X_train_sc, y_train)
    
    predictions = model.predict(X_test_sc)
    probabilities = model.predict_proba(X_test_sc)[:, 1]
    
    # Coefficients — interpretable!
    coefs = pd.DataFrame({
        'feature': X_train.columns,
        'coefficient': model.coef_[0],
        'odds_ratio': np.exp(model.coef_[0])
    }).sort_values('coefficient', ascending=False)
    
    return {
        'model': model,
        'scaler': scaler,
        'predictions': predictions,
        'probabilities': probabilities,
        'coefficients': coefs,
        'intercept': float(model.intercept_[0])
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `C` | 1.0 | 0.001 - 100 | Inverse regularization (smaller = stronger regularization) |
| `penalty` | 'l2' | 'l1', 'l2', 'elasticnet' | Regularization type |
| `class_weight` | None | 'balanced' or dict | Weight adjustment for imbalanced classes |
| `solver` | 'lbfgs' | 'lbfgs', 'liblinear', 'saga' | Optimization algorithm |
| `max_iter` | 100 | 100 - 10000 | Max optimization iterations |

### class_weight='balanced' Mechanics
```python
# sklearn computes weights automatically:
# weight_class_k = n_samples / (n_classes * n_samples_class_k)
#
# Example: 95% class 0, 5% class 1
# weight_0 = 10000 / (2 * 9500) = 0.526
# weight_1 = 10000 / (2 * 500) = 10.0
# → Minority class errors penalized 19x more
```

---

## Best Practices

1. **Always use `class_weight='balanced'`** for imbalanced data — otherwise model ignores minority class.
2. **Scale features** — Coefficients are meaningless without scaling. Use `StandardScaler`.
3. **Check convergence** — If `ConvergenceWarning`, increase `max_iter` to 5000+.
4. **Interpret via odds ratios** — `exp(coefficient)` gives the multiplicative change in odds per unit increase.
5. **Use as interpretable baseline** — If LogReg F1 is close to XGBoost, prefer LogReg (simpler, explainable).

### Interpreting Coefficients
```python
# After fitting on SCALED data:
# coefficient = 1.5 for "days_since_login"
# → exp(1.5) = 4.48
# → "Each 1-std increase in days since login increases churn odds by 4.48x"

# Negative coefficient = protective factor
# coefficient = -0.8 for "monthly_usage"
# → exp(-0.8) = 0.45
# → "Each 1-std increase in usage reduces churn odds by 55%"
```

---

## Accuracy Trap Demonstration

This skill produces BOTH naive and LogReg results to demonstrate why accuracy is misleading:

```
Dataset: 97% non-churners, 3% churners

Naive (predict all 0):
  Accuracy = 97% ← looks great!
  F1 = 0.0       ← useless (misses every churner)
  
Logistic Regression (class_weight='balanced'):
  Accuracy = 78% ← looks worse!
  F1 = 0.45      ← actually useful (catches churners)
```

**Key insight:** For imbalanced data, a model that "looks less accurate" may be dramatically more useful.

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **No scaling** | Large-scale features dominate | Always StandardScaler before fitting |
| **No class_weight** | Model predicts majority class for everything | Set `class_weight='balanced'` |
| **Using accuracy** | 97% accuracy but 0% recall on minority | Use F1-Score as primary metric |
| **Non-linear relationships** | LogReg assumes linear decision boundary | Expected — this is baseline. Use tree models for non-linear |
| **Multicollinearity** | Coefficients unstable and misleading | Check VIF; use L1 penalty for feature selection |
| **Convergence failure** | max_iter too low | Increase to 5000-10000 |
