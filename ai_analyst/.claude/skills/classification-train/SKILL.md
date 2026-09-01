---
name: classification-train
description: >
  Train a single classification model (param: model_type). Supports naive_logreg, decision_tree,
  random_forest, xgboost. Handles imbalanced data via SMOTE and class_weight. Computes F1/Precision/Recall.
  Trigger: called by predictive-trainer subagent, 4 times in PARALLEL (one per model_type).
when_to_use: "train classifier", "logistic regression", "decision tree", "random forest classify", "xgboost classify", "churn prediction"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write
model: sonnet
effort: high
version: "1.0"
---

# Skill: Classification Train

## Purpose
Train a single classification model specified by `model_type` parameter. Designed for binary classification with imbalanced data (e.g., churn prediction). Called 4 times in parallel by `predictive-trainer` subagent.

**Reads:** `data/pipeline/{stem}/train_data.json` + `data/pipeline/{stem}/test_data.json` + `model_type` param
**Writes:** `data/pipeline/{stem}/model_result_{model_type}.json`

**Read references:** `references/logreg_guide.md` · `references/decision_tree_guide.md` · `references/random_forest_clf_guide.md` · `references/xgboost_clf_guide.md`

---

## Parameters

| Parameter | Required | Values |
|---|---|---|
| `model_type` | Yes | `naive_logreg` \| `decision_tree` \| `random_forest` \| `xgboost` |

---

## Steps

### Step 1: Load Data
```python
import json
import pandas as pd
import numpy as np

with open(f"data/pipeline/{stem}/train_data.json") as f:
    train_data = json.load(f)
with open(f"data/pipeline/{stem}/test_data.json") as f:
    test_data = json.load(f)

train_df = pd.DataFrame(train_data["train_data"]["values"])
test_df = pd.DataFrame(test_data["test_data"]["values"])
target_col = train_data["train_data"]["target_column"]
feature_cols = [c for c in train_df.columns if c != target_col]
smote_config = train_data.get("smote_config", {})

X_train, y_train = train_df[feature_cols], train_df[target_col]
X_test, y_test = test_df[feature_cols], test_df[target_col]
```

### Step 2: Apply SMOTE (if configured)
```python
if smote_config.get("apply_smote", False) and model_type in ["random_forest", "xgboost"]:
    from imblearn.over_sampling import SMOTE
    smote = SMOTE(
        sampling_strategy=smote_config.get("strategy", "auto"),
        k_neighbors=smote_config.get("k_neighbors", 5),
        random_state=42
    )
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
else:
    X_train_resampled, y_train_resampled = X_train, y_train
```

### Step 3: Train Model (dispatch by model_type)

**`naive_logreg`** — Baseline (All-0 prediction + Logistic Regression):
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

# Part A: Naive (all-0) — demonstrates Accuracy Trap
naive_preds = np.zeros(len(y_test))
naive_accuracy = (naive_preds == y_test).mean()
naive_f1 = f1_score(y_test, naive_preds, zero_division=0)
# Expect: high accuracy, zero F1 → proves accuracy is misleading

# Part B: Logistic Regression
model = LogisticRegression(
    class_weight='balanced', max_iter=1000, random_state=42,
    solver='lbfgs', C=1.0
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]
coefficients = dict(zip(feature_cols, model.coef_[0]))
```

**`decision_tree`** — Interpretable single tree:
```python
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(
    max_depth=5, class_weight='balanced',
    min_samples_split=10, min_samples_leaf=5,
    random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]
feature_importance = dict(zip(feature_cols, model.feature_importances_))
```

**`random_forest`** — Ensemble + SMOTE:
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100, class_weight='balanced',
    max_depth=None, min_samples_split=5, min_samples_leaf=2,
    random_state=42, n_jobs=-1
)
model.fit(X_train_resampled, y_train_resampled)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]
feature_importance = dict(zip(feature_cols, model.feature_importances_))
```

**`xgboost`** — Gradient boosting + SMOTE:
```python
import xgboost as xgb

# Auto-calculate scale_pos_weight from original (pre-SMOTE) class ratio
neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
scale_pos_weight = neg_count / pos_count

model = xgb.XGBClassifier(
    learning_rate=0.05, max_depth=6, n_estimators=300,
    scale_pos_weight=scale_pos_weight,
    subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.1, reg_lambda=1.0,
    random_state=42, n_jobs=-1, verbosity=0,
    eval_metric='logloss', use_label_encoder=False
)
model.fit(X_train_resampled, y_train_resampled,
          eval_set=[(X_test, y_test)], verbose=False)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]
feature_importance = dict(zip(feature_cols, model.feature_importances_))
```

### Step 4: Compute Metrics
```python
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix, roc_auc_score

f1 = f1_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
accuracy = (predictions == y_test).mean()
auc_roc = roc_auc_score(y_test, probabilities) if probabilities is not None else None
cm = confusion_matrix(y_test, predictions)

metrics = {
    "f1": round(f1, 4),
    "precision": round(precision, 4),
    "recall": round(recall, 4),
    "accuracy": round(accuracy, 4),
    "auc_roc": round(auc_roc, 4) if auc_roc else None,
    "confusion_matrix": {
        "tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
        "fn": int(cm[1, 0]), "tp": int(cm[1, 1])
    }
}
```

### Step 5: Write Result
Write to `data/pipeline/{stem}/model_result_{model_type}.json`.

---

## Rules

**R-1:** Primary metric is F1-Score. NEVER use Accuracy for imbalanced data (Accuracy Trap!).
**R-2:** Apply SMOTE ONLY on training set. NEVER on test set.
**R-3:** Always use `class_weight='balanced'` for sklearn models.
**R-4:** For naive_logreg, report BOTH naive (all-0) metrics AND logistic regression metrics to demonstrate the Accuracy Trap.
**R-5:** Always output predicted probabilities for threshold tuning in model-finalize.
**R-6:** If F1 = 0 for any model, flag as "model failed to learn" in metadata.

---

## Output Schema

```json
{
  "skill_type": "classification_train",
  "model_type": "naive_logreg|decision_tree|random_forest|xgboost",
  "run_context": {},
  "status": "success|failed",
  "model_params": {
    "max_depth": 5,
    "class_weight": "balanced",
    "n_estimators": 100,
    "smote_applied": true
  },
  "metrics": {
    "f1": 0.72,
    "precision": 0.68,
    "recall": 0.76,
    "accuracy": 0.85,
    "auc_roc": 0.81,
    "confusion_matrix": {"tn": 8500, "fp": 320, "fn": 180, "tp": 1000}
  },
  "naive_baseline": {
    "accuracy": 0.97,
    "f1": 0.0,
    "note": "Accuracy Trap: 97% accurate but misses ALL positive cases"
  },
  "predictions": [
    {"index": 0, "actual": 1, "predicted": 1, "probability": 0.82},
    {"index": 1, "actual": 0, "predicted": 0, "probability": 0.15}
  ],
  "feature_importance": {"days_since_login": 0.25, "support_tickets": 0.18},
  "coefficients": {"days_since_login": 1.25, "support_tickets": 0.89},
  "class_distribution": {
    "train_original": {"0": 38000, "1": 2000},
    "train_after_smote": {"0": 38000, "1": 38000},
    "test": {"0": 9500, "1": 500}
  },
  "metadata": {
    "train_size": 40000,
    "test_size": 10000,
    "n_features": 32,
    "training_time_seconds": 6.2,
    "generated_at": "ISO 8601"
  }
}
```
