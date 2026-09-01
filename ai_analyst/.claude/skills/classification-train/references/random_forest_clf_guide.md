# Random Forest Classification Guide

> Ensemble of decision trees + SMOTE — robust classifier for imbalanced data.

## Algorithm Overview

Random Forest Classification builds N independent decision trees, each trained on a bootstrap sample with random feature subsets. Final prediction = majority vote (or averaged probability).

For imbalanced data, we combine:
1. **SMOTE** (Synthetic Minority Oversampling) on training data
2. **class_weight='balanced'** in the model
3. **F1-Score** as evaluation metric

```
Training: SMOTE → balanced training data → 100 trees on bootstrapped samples
Prediction: Average probabilities across all trees → apply threshold
```

---

## Implementation

```python
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

def train_random_forest_clf(X_train, y_train, X_test, smote_config=None):
    """
    Train Random Forest classifier with SMOTE for imbalanced data.
    """
    # Step 1: Apply SMOTE on training data only
    if smote_config and smote_config.get("apply_smote", False):
        smote = SMOTE(
            sampling_strategy=smote_config.get("strategy", "auto"),
            k_neighbors=smote_config.get("k_neighbors", 5),
            random_state=42
        )
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    else:
        X_train_res, y_train_res = X_train, y_train
    
    # Step 2: Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_res, y_train_res)
    
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    
    importance = dict(zip(X_train.columns, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'model': model,
        'predictions': predictions,
        'probabilities': probabilities,
        'feature_importance': importance,
        'smote_applied': smote_config.get("apply_smote", False) if smote_config else False,
        'class_distribution': {
            'before_smote': dict(pd.Series(y_train).value_counts()),
            'after_smote': dict(pd.Series(y_train_res).value_counts())
        }
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `n_estimators` | 100 | 50-500 | Number of trees | More is better (diminishing returns >200) |
| `max_depth` | None | 5-30, None | Max depth per tree | None = fully grown. Reduce if overfitting |
| `min_samples_split` | 5 | 2-20 | Min samples to split | Higher = more regularization |
| `min_samples_leaf` | 2 | 1-10 | Min samples in leaf | Higher = smoother probabilities |
| `max_features` | 'sqrt' | 'sqrt', 'log2', float | Features per split | 'sqrt' is standard for classification |
| `class_weight` | 'balanced' | 'balanced', dict | Class weights | Always 'balanced' for imbalanced data |

---

## SMOTE Details

### How SMOTE Works
```
1. For each minority sample, find k nearest neighbors (in feature space)
2. Create synthetic sample = original + random_fraction × (neighbor - original)
3. Repeat until minority class equals majority class

Before SMOTE: Class 0 = 9500, Class 1 = 500
After SMOTE:  Class 0 = 9500, Class 1 = 9500 (synthetic minority samples created)
```

### SMOTE Rules
- **ONLY on training set** — NEVER on test set (would create data leakage)
- **k_neighbors** — Must be < minority class size. Default 5; reduce for very small minority
- **Check quality** — Synthetic samples should be plausible (check feature ranges)

### When NOT to Use SMOTE
| Scenario | Why Skip SMOTE | Alternative |
|----------|---------------|-------------|
| Minority class < 10 | Not enough neighbors for meaningful synthesis | Collect more data |
| Very high dimensionality | SMOTE creates noise in sparse space | class_weight only |
| class_weight='balanced' is sufficient | F1 already good without SMOTE | Keep it simple |

---

## Best Practices

1. **SMOTE + class_weight = double protection** — Use both for severely imbalanced data (<5% minority).
2. **Check class distribution** — Report before/after SMOTE counts in output.
3. **Permutation importance over MDI** — Mean Decrease Impurity biases toward high-cardinality features.
4. **Probability calibration** — RF probabilities may need calibration via `CalibratedClassifierCV`.
5. **OOB score** — Set `oob_score=True` for free validation estimate.

### Probability Calibration
```python
from sklearn.calibration import CalibratedClassifierCV

# RF probabilities are often poorly calibrated
calibrated_model = CalibratedClassifierCV(model, cv=5, method='isotonic')
calibrated_model.fit(X_train_res, y_train_res)
calibrated_probs = calibrated_model.predict_proba(X_test)[:, 1]
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **SMOTE on test set** | Artificial samples in test → inflated metrics | SMOTE ONLY on training set |
| **SMOTE before split** | Synthetic samples leak into test | Split first, then SMOTE |
| **Ignoring probabilities** | Using default 0.5 threshold | Tune threshold in model-finalize step |
| **Too many trees** | Diminishing returns + slow prediction | 100-200 trees is usually sufficient |
| **Wrong importance method** | MDI biased toward high-cardinality | Use permutation importance on test set |

---

## When Random Forest Classification Works Best

- **Imbalanced binary classification** — SMOTE + balanced weights + F1 evaluation
- **Non-linear decision boundaries** — Complex feature interactions
- **Robustness over accuracy** — Less prone to overfitting than XGBoost
- **Feature importance needed** — Quick identification of discriminative features

## When Random Forest Struggles

- **Very high imbalance** (>99/1) — Even with SMOTE, may struggle
- **Linear separability** — LogReg is simpler and equivalent
- **Very large datasets** (>1M rows) — Slow training; consider XGBoost
