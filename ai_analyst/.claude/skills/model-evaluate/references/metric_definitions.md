# Metric Definitions Reference

> Complete definitions for all evaluation metrics used in the predictive pipeline.

## Forecasting Metrics

### MAPE — Mean Absolute Percentage Error (Primary)
```
MAPE = (1/n) × Σ |actual - predicted| / |actual| × 100

Interpretation:
  MAPE = 5%  → predictions are off by 5% on average (excellent)
  MAPE = 10% → predictions are off by 10% on average (good)
  MAPE = 20% → predictions are off by 20% on average (acceptable)
  MAPE = 50% → predictions are off by 50% on average (poor)
```

```python
import numpy as np

def mape(actual, predicted):
    """Mean Absolute Percentage Error."""
    actual, predicted = np.array(actual), np.array(predicted)
    # Avoid division by zero
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
```

**Advantages:** Scale-independent (comparable across datasets), intuitive interpretation.
**Limitations:** Undefined when actual = 0. Asymmetric (penalizes over-prediction less than under-prediction). Use sMAPE if actuals near zero.

### MAE — Mean Absolute Error
```
MAE = (1/n) × Σ |actual - predicted|

Interpretation: Average error in original units (e.g., dollars, users)
```

```python
def mae(actual, predicted):
    """Mean Absolute Error."""
    return np.mean(np.abs(np.array(actual) - np.array(predicted)))
```

**When to use over MAPE:** When actuals can be zero or negative, or when absolute error is more meaningful than percentage.

### RMSE — Root Mean Squared Error
```
RMSE = √((1/n) × Σ (actual - predicted)²)

Interpretation: Like MAE but penalizes large errors more.
RMSE ≥ MAE always. RMSE = MAE when all errors are equal.
```

```python
def rmse(actual, predicted):
    """Root Mean Squared Error."""
    return np.sqrt(np.mean((np.array(actual) - np.array(predicted)) ** 2))
```

**When RMSE >> MAE:** A few predictions have very large errors (outlier sensitivity).

---

## Regression Metrics

### MAE — Mean Absolute Error (Primary)
Same as forecasting MAE above. Used as primary because it's robust to outliers and interpretable.

### RMSE — Root Mean Squared Error
Same as above. Secondary metric — useful for detecting large-error predictions.

### R² — Coefficient of Determination
```
R² = 1 - (SS_res / SS_tot)
   = 1 - Σ(actual - predicted)² / Σ(actual - mean(actual))²

Interpretation:
  R² = 1.0 → perfect prediction
  R² = 0.8 → model explains 80% of variance
  R² = 0.0 → model is no better than predicting the mean
  R² < 0   → model is WORSE than predicting the mean
```

```python
from sklearn.metrics import r2_score

r2 = r2_score(actual, predicted)
```

**Key insight:** R² < 0 means the model is actively harmful — predicting the mean would be better.

---

## Classification Metrics

### F1-Score (Primary)
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)

F1 is the harmonic mean of Precision and Recall.
Harmonic mean penalizes extreme imbalance (high precision + low recall = low F1).

Interpretation:
  F1 = 0.80 → excellent balance of precision and recall
  F1 = 0.50 → decent but room for improvement
  F1 = 0.20 → poor — model is struggling
  F1 = 0.00 → model predicts only one class
```

```python
from sklearn.metrics import f1_score

f1 = f1_score(y_true, y_pred)  # Binary default: pos_label=1
```

### Precision
```
Precision = TP / (TP + FP)
"Of all predicted positives, how many are actually positive?"

High precision = few false alarms
Example: Precision = 0.90 → 90% of predicted churners actually churned
```

### Recall (Sensitivity)
```
Recall = TP / (TP + FN)
"Of all actual positives, how many did we catch?"

High recall = few missed cases
Example: Recall = 0.80 → we caught 80% of actual churners
```

### Precision-Recall Trade-off
```
Lower threshold → more predicted positives → higher recall, lower precision
Higher threshold → fewer predicted positives → lower recall, higher precision

Business decides the trade-off:
  - Churn: prefer high recall (don't miss churners) → lower threshold
  - Fraud: prefer high precision (don't block legitimate users) → higher threshold
```

### Confusion Matrix
```
                    Predicted
                    Neg    Pos
Actual  Neg    [ TN     FP ]
        Pos    [ FN     TP ]

TN: True Negative  — correctly predicted negative
FP: False Positive — false alarm (predicted positive, actually negative)
FN: False Negative — missed case (predicted negative, actually positive)
TP: True Positive  — correctly predicted positive
```

### AUC-ROC — Area Under ROC Curve
```
AUC = probability that model ranks a random positive higher than a random negative

AUC = 0.5 → no better than random
AUC = 0.7 → acceptable
AUC = 0.8 → good
AUC = 0.9 → excellent
AUC = 1.0 → perfect ranking
```

**Why NOT primary metric:** AUC evaluates ranking ability across all thresholds. F1 evaluates performance at a specific threshold — more actionable for business decisions.

---

## The Accuracy Trap

```
Dataset: 97% negative, 3% positive

Model A (predict all negative):
  Accuracy = 97%     ← looks great!
  F1 = 0.0           ← useless
  
Model B (balanced classifier):
  Accuracy = 80%     ← looks worse!
  F1 = 0.45          ← actually useful

LESSON: NEVER use accuracy as primary metric for imbalanced data.
```

---

## Metric Selection Summary

| Pipeline | Primary | Secondary | Direction | Why |
|----------|---------|-----------|-----------|-----|
| Forecasting | MAPE | MAE, RMSE | Lower better | Scale-independent, intuitive |
| Regression | MAE | RMSE, R² | Lower better (MAE/RMSE) | Robust to outliers |
| Classification | F1 | Precision, Recall, AUC | Higher better | Balanced precision-recall |
