# XGBoost Classification Guide

> Gradient boosting classifier — typically the best F1 for imbalanced tabular data.

## Algorithm Overview

XGBoost for classification uses the same sequential tree-building approach as regression, but optimizes log-loss (binary cross-entropy) instead of MSE:

```
Step 1: Initialize with log-odds of positive class
Step 2: Compute gradient of log-loss (pseudo-residuals)
Step 3: Fit tree to pseudo-residuals
Step 4: Update predictions with learning_rate × tree output
Step 5: Repeat until convergence or early stopping
```

For imbalanced data, XGBoost offers `scale_pos_weight` to upweight the minority class, equivalent to `class_weight` in sklearn.

---

## Implementation

```python
import xgboost as xgb
from imblearn.over_sampling import SMOTE

def train_xgboost_clf(X_train, y_train, X_test, y_test, smote_config=None):
    """
    Train XGBoost classifier with SMOTE and scale_pos_weight.
    """
    # Step 1: SMOTE (optional)
    if smote_config and smote_config.get("apply_smote", False):
        smote = SMOTE(
            sampling_strategy=smote_config.get("strategy", "auto"),
            k_neighbors=smote_config.get("k_neighbors", 5),
            random_state=42
        )
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    else:
        X_train_res, y_train_res = X_train, y_train
    
    # Step 2: Calculate scale_pos_weight from ORIGINAL data
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / pos_count
    
    # Step 3: Train
    model = xgb.XGBClassifier(
        learning_rate=0.05,
        max_depth=6,
        n_estimators=300,
        scale_pos_weight=scale_pos_weight,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    model.fit(
        X_train_res, y_train_res,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    
    importance = dict(zip(X_train.columns, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'model': model,
        'predictions': predictions,
        'probabilities': probabilities,
        'feature_importance': importance,
        'scale_pos_weight': scale_pos_weight,
        'best_iteration': model.best_iteration if hasattr(model, 'best_iteration') else 300
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `learning_rate` | 0.05 | 0.01-0.3 | Step size per round | Lower = better generalization |
| `max_depth` | 6 | 3-10 | Max tree depth | Reduce to 3-4 for small data or overfitting |
| `n_estimators` | 300 | 100-2000 | Max boosting rounds | Use early stopping |
| `scale_pos_weight` | auto | neg/pos ratio | Minority class upweight | Auto-calculate from class counts |
| `subsample` | 0.8 | 0.5-1.0 | Row sampling per tree | Lower = more regularization |
| `colsample_bytree` | 0.8 | 0.5-1.0 | Feature sampling per tree | Lower = more regularization |
| `reg_alpha` | 0.1 | 0-10 | L1 regularization | Increase if overfitting |
| `reg_lambda` | 1.0 | 0-10 | L2 regularization | Increase if overfitting |
| `min_child_weight` | 1 | 1-10 | Min sum of weights in child | Higher = more conservative |
| `gamma` | 0 | 0-5 | Min loss reduction for split | Higher = fewer splits |
| `eval_metric` | 'logloss' | 'logloss', 'auc', 'error' | Evaluation metric | 'logloss' for early stopping |

### scale_pos_weight Mechanics
```python
# Auto-calculation from class distribution:
# scale_pos_weight = count(negative) / count(positive)
#
# Example: 9500 negatives, 500 positives
# scale_pos_weight = 9500 / 500 = 19.0
#
# Effect: Each positive sample contributes 19x more to the loss
# → Model pays more attention to minority class
#
# Can also combine with SMOTE for double protection
```

### SMOTE + scale_pos_weight — When to Use Both
```
Imbalance < 10% minority:  class_weight / scale_pos_weight alone
Imbalance < 5% minority:   SMOTE + class_weight (double protection)
Imbalance < 1% minority:   SMOTE + scale_pos_weight + careful threshold tuning
```

---

## Best Practices

1. **Always early-stop on log-loss** — Not F1 (F1 depends on threshold; log-loss evaluates probability quality).
2. **Use SMOTE + scale_pos_weight for severe imbalance** — Belt-and-suspenders approach.
3. **Store probabilities** — Threshold tuning in model-finalize requires raw probabilities.
4. **Check feature importance** — Top features should make business sense.
5. **Compare with LogReg** — If XGBoost F1 is only marginally better, prefer LogReg for interpretability.

### Threshold Tuning Preview
```python
# Default threshold = 0.5 is rarely optimal for imbalanced data
# Model-finalize skill will tune threshold based on:
# 1. F1 maximization: find threshold that maximizes F1 on validation set
# 2. Cost-based: minimize business cost (FP × cost_FP + FN × cost_FN)

# Example: Churn prediction
# FP cost = $50 (unnecessary outreach to non-churner)
# FN cost = $5000 (lost customer)
# → Optimal threshold ≈ 0.05 (catch more churners, accept more FPs)
```

---

## Diagnostics

### Classification Report
```python
from sklearn.metrics import classification_report

print(classification_report(y_test, predictions, 
                             target_names=['Stay', 'Churn']))
#               precision    recall  f1-score   support
#       Stay       0.98      0.92      0.95      9500
#      Churn       0.45      0.78      0.57       500
#   accuracy                           0.91     10000
#   macro avg      0.72      0.85      0.76     10000
```

### SHAP Values (Per-Prediction Explanation)
```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# For a single prediction:
# "This customer has 85% churn probability because:
#   +0.25 days_since_login = 67 (vs avg 15)
#   +0.18 support_tickets = 5 (vs avg 1.2)
#   -0.10 monthly_spend = $120 (vs avg $85) — protective factor"
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **No scale_pos_weight** | Model ignores minority class | Auto-calculate from class ratio |
| **Early stop on accuracy** | Misleading for imbalanced data | Use `eval_metric='logloss'` |
| **Default threshold** | 0.5 is suboptimal for most cases | Tune in model-finalize |
| **SMOTE on full data** | Synthetic test samples → inflated metrics | SMOTE on training set ONLY |
| **Overfitting** | Train logloss << test logloss | Reduce max_depth, increase regularization |
| **Missing eval_set** | No early stopping → overfitting | Always provide eval_set |

---

## When XGBoost Classification Works Best

- **Imbalanced binary classification** — Best F1 achiever with proper handling
- **Tabular data with mixed types** — Handles numeric, categorical, missing natively
- **Complex non-linear boundaries** — Feature interactions and thresholds
- **Moderate to large datasets** (1K - 1M rows)

## When XGBoost Struggles

- **Very small data** (<200 rows) — Overfits easily; use LogReg
- **Extreme imbalance** (>99.9/0.1) — Even with SMOTE, F1 may be low
- **Need for interpretability** — Use Decision Tree for rules or SHAP for explanations
- **Requires probability calibration** — XGBoost probabilities may need post-hoc calibration
