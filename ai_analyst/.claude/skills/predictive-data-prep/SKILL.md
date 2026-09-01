---
name: predictive-data-prep
description: >
  Transform cleaned data into ML-ready format: feature engineering, categorical encoding,
  stationarity tests (forecasting), SMOTE setup (classification), multicollinearity check.
  Trigger: called by predictive-trainer subagent after predictive-bridge.
when_to_use: "feature engineering", "ML data prep", "encoding", "stationarity", "predictive prep"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Predictive Data Prep

## Purpose
Transform cleaned data into ML-ready format. This is NOT data-prep (Skill #2) which handles raw→clean. This skill handles clean→ML-ready: feature engineering, encoding, stationarity, SMOTE setup, multicollinearity.

**Reads:** `data/cleaned/{type}/{stem}_cleaned.xlsx` + `data/pipeline/{stem}/predictive_input.json`
**Writes:** `data/pipeline/{stem}/ml_ready_data.json`

**Read references:** `references/feature_engineering.md` · `references/stationarity_tests.md` · `references/encoding_patterns.md`

---

## Steps

### Step 1: Load Data and Predictive Context
```python
import pandas as pd
import json

with open(f"data/pipeline/{stem}/predictive_input.json") as f:
    pred_input = json.load(f)

pipeline_type = pred_input["pipeline_type"]  # forecasting|regression|classification
target_col = pred_input["target_column"]
date_col = pred_input.get("date_column")
feature_cols = pred_input.get("feature_columns", [])

df = pd.read_excel(pred_input["data_path"])
```

### Step 2: Feature Engineering (pipeline-type specific)

**Forecasting features:**
| Feature Type | Examples | Code |
|---|---|---|
| Lag features | lag_1, lag_2, lag_3, lag_6, lag_12 | `df[f'lag_{k}'] = df[target].shift(k)` |
| Rolling stats | rolling_mean_3, rolling_std_3 | `df[target].rolling(k).mean()` |
| Calendar | month, quarter, day_of_week, is_weekend | `df[date_col].dt.month` |
| Trend | linear_trend | `range(len(df))` |

**Regression features:**
| Feature Type | Action |
|---|---|
| Interaction terms | Create top-2 feature interactions (if <20 features) |
| Polynomial | Square of top-correlated numeric features (max 3) |
| Domain-specific | Revenue per user, rate metrics, ratios |

**Classification features:**
| Feature Type | Action |
|---|---|
| Frequency encoding | High-cardinality categoricals (>20 unique) |
| Behavioral ratios | Activity_count / tenure, support_tickets / months |
| Recency features | Days_since_last_X from date columns |

### Step 3: Categorical Encoding
```python
# Determine encoding strategy per column
for col in categorical_cols:
    n_unique = df[col].nunique()
    if n_unique == 2:
        # Binary: label encode (0/1)
        df[col] = df[col].map({vals[0]: 0, vals[1]: 1})
    elif n_unique <= 10:
        # Low cardinality: one-hot encode (drop_first=True)
        df = pd.get_dummies(df, columns=[col], drop_first=True)
    elif has_natural_order(col):
        # Ordinal: map to integers preserving order
        df[col] = df[col].map(ordinal_mapping)
    else:
        # High cardinality: frequency encoding
        freq = df[col].value_counts(normalize=True)
        df[col + '_freq'] = df[col].map(freq)
        df.drop(col, axis=1, inplace=True)
```

### Step 4: Stationarity Tests (Forecasting Only)
```python
from statsmodels.tsa.stattools import adfuller, kpss

# ADF test: H0 = unit root (non-stationary)
adf_stat, adf_p, _, _, _, _ = adfuller(series.dropna())
adf_stationary = adf_p < 0.05

# KPSS test: H0 = stationary
kpss_stat, kpss_p, _, _ = kpss(series.dropna(), regression='c')
kpss_stationary = kpss_p > 0.05

# Decision matrix
if adf_stationary and kpss_stationary:
    differencing = 0  # Stationary
elif not adf_stationary and not kpss_stationary:
    differencing = 1  # Difference once
    # If still non-stationary after d=1, try d=2
else:
    differencing = 1  # Ambiguous → difference once to be safe
```

### Step 5: SMOTE Setup (Classification Only)
```python
class_counts = df[target_col].value_counts()
imbalance_ratio = class_counts.min() / class_counts.max()

smote_config = {
    "apply_smote": imbalance_ratio < 0.4,  # >60/40 imbalance
    "strategy": "auto",  # SMOTE default: equalize classes
    "k_neighbors": min(5, class_counts.min() - 1),
    "random_state": 42
}
# NOTE: SMOTE applied ONLY on training set, NEVER on test set
```

### Step 6: Multicollinearity Check
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

numeric_df = df[numeric_features]
vif_data = pd.DataFrame({
    "feature": numeric_df.columns,
    "VIF": [variance_inflation_factor(numeric_df.values, i)
            for i in range(numeric_df.shape[1])]
})

# Flag features with VIF > 10
high_vif = vif_data[vif_data["VIF"] > 10]
# Drop highest VIF iteratively until all < 10
while vif_data["VIF"].max() > 10:
    drop_col = vif_data.loc[vif_data["VIF"].idxmax(), "feature"]
    numeric_df = numeric_df.drop(columns=[drop_col])
    # Recalculate VIF
```

### Step 7: Scale Numeric Features
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
numeric_cols = [c for c in numeric_cols if c != target_col]

df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
# Store scaler params for inverse transform later
scaler_params = {col: {"mean": m, "std": s}
                 for col, m, s in zip(numeric_cols, scaler.mean_, scaler.scale_)}
```

### Step 8: Write ML-Ready Output
Write to `data/pipeline/{stem}/ml_ready_data.json`.

---

## Rules

**R-1:** NEVER apply SMOTE on the full dataset — only on training split (done in train-test-split skill).
**R-2:** Drop features with >50% missing values. Impute rest: median (numeric), mode (categorical).
**R-3:** Always preserve the original target column unscaled.
**R-4:** For forecasting, drop rows with NaN from lag features (beginning of series).
**R-5:** Log all dropped columns and reasons in the output metadata.
**R-6:** If VIF check removes >50% of features, WARN but proceed.

---

## Output Schema

```json
{
  "skill_type": "predictive_data_prep",
  "run_context": {},
  "pipeline_type": "forecasting|regression|classification",
  "data": {
    "rows": 45000,
    "features": 32,
    "target_column": "revenue",
    "feature_names": ["lag_1", "lag_3", "month", "..."],
    "feature_types": {"lag_1": "numeric", "segment_A": "binary"},
    "values": "...serialized DataFrame..."
  },
  "preprocessing": {
    "encoding": {
      "one_hot": ["segment", "region"],
      "ordinal": ["size_tier"],
      "frequency": ["product_category"],
      "label": ["is_active"]
    },
    "scaling": {
      "method": "StandardScaler",
      "params": {"feature_name": {"mean": 0.5, "std": 0.2}}
    },
    "stationarity": {
      "adf_p": 0.03,
      "kpss_p": 0.08,
      "differencing_order": 0,
      "is_stationary": true
    },
    "smote_config": {
      "apply_smote": true,
      "strategy": "auto",
      "k_neighbors": 5,
      "imbalance_ratio": 0.15
    },
    "multicollinearity": {
      "dropped_features": ["feature_x"],
      "reason": "VIF > 10",
      "remaining_vif_max": 4.2
    },
    "dropped_columns": [
      {"column": "notes", "reason": "78% missing"},
      {"column": "id", "reason": "identifier, not predictive"}
    ]
  },
  "metadata": {
    "original_rows": 50000,
    "rows_after_prep": 45000,
    "original_features": 25,
    "engineered_features": 32,
    "generated_at": "ISO 8601"
  }
}
```
