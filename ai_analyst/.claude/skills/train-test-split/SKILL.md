---
name: train-test-split
description: >
  Split ML-ready data into train/test sets based on pipeline type:
  time-based (forecasting), stratified (classification), or random (regression).
  Trigger: called by predictive-trainer subagent after predictive-data-prep.
when_to_use: "train test split", "split data", "holdout set", "time series split"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Write
model: sonnet
effort: medium
version: "1.0"
---

# Skill: Train-Test Split

## Purpose
Split ML-ready data into train and test sets using the appropriate strategy for the pipeline type. Each strategy ensures no data leakage and preserves the statistical properties needed for valid model evaluation.

**Reads:** `data/pipeline/{stem}/ml_ready_data.json`
**Writes:** `data/pipeline/{stem}/train_data.json` + `data/pipeline/{stem}/test_data.json`

**Read references:** `references/splitting_strategies.md`

---

## Steps

### Step 1: Load ML-Ready Data
```python
import json
import pandas as pd

with open(f"data/pipeline/{stem}/ml_ready_data.json") as f:
    ml_data = json.load(f)

pipeline_type = ml_data["pipeline_type"]
target_col = ml_data["data"]["target_column"]
df = pd.DataFrame(ml_data["data"]["values"])
```

### Step 2: Select Split Strategy

| Pipeline Type | Strategy | Ratio | Rationale |
|---|---|---|---|
| **Forecasting** | Time-based cutoff | Last 20% of periods = test | Preserves temporal order; no future leakage |
| **Regression** | Random shuffle | 80/20 train/test | No temporal dependency; maximize train diversity |
| **Classification** | Stratified random | 80/20 train/test | Preserve class ratio in both sets |

### Step 3: Execute Split

**Forecasting (time-based):**
```python
# Sort by date, use last N periods as test
df = df.sort_values(date_col).reset_index(drop=True)
cutoff_idx = int(len(df) * 0.8)
train_df = df.iloc[:cutoff_idx]
test_df = df.iloc[cutoff_idx:]

# Verify: no overlap in dates
assert train_df[date_col].max() < test_df[date_col].min()
```

**Regression (random):**
```python
from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(
    df, test_size=0.2, random_state=42
)
```

**Classification (stratified):**
```python
from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(
    df, test_size=0.2, random_state=42,
    stratify=df[target_col]
)

# Verify class ratios preserved
train_ratio = train_df[target_col].mean()
test_ratio = test_df[target_col].mean()
assert abs(train_ratio - test_ratio) < 0.02, "Class ratio drift > 2%"
```

### Step 4: Validate Split Quality
```python
validation = {
    "train_size": len(train_df),
    "test_size": len(test_df),
    "train_pct": round(len(train_df) / len(df) * 100, 1),
    "test_pct": round(len(test_df) / len(df) * 100, 1),
    "target_stats": {
        "train_mean": train_df[target_col].mean(),
        "test_mean": test_df[target_col].mean(),
        "train_std": train_df[target_col].std(),
        "test_std": test_df[target_col].std()
    }
}

# Classification: verify class balance
if pipeline_type == "classification":
    validation["class_distribution"] = {
        "train": train_df[target_col].value_counts(normalize=True).to_dict(),
        "test": test_df[target_col].value_counts(normalize=True).to_dict()
    }

# Forecasting: verify temporal integrity
if pipeline_type == "forecasting":
    validation["date_range"] = {
        "train": {"start": str(train_df[date_col].min()), "end": str(train_df[date_col].max())},
        "test": {"start": str(test_df[date_col].min()), "end": str(test_df[date_col].max())}
    }
```

### Step 5: Write Outputs
Write `train_data.json` and `test_data.json` with data + metadata.

---

## Rules

**R-1:** NEVER shuffle time series data — forecasting splits must respect temporal order.
**R-2:** NEVER apply SMOTE before splitting — apply SMOTE on training set only (done in classification-train skill).
**R-3:** Always use `random_state=42` for reproducibility.
**R-4:** If dataset < 500 rows, use 70/30 split (more test data for reliable evaluation).
**R-5:** If classification minority class has < 50 samples in test set, WARN — metrics may be unreliable.
**R-6:** Store split indices so the exact split is reproducible.

---

## Output Schema

```json
{
  "skill_type": "train_test_split",
  "run_context": {},
  "pipeline_type": "forecasting|regression|classification",
  "split_strategy": "time_based|random|stratified",
  "train_data": {
    "rows": 40000,
    "columns": 32,
    "target_column": "revenue",
    "feature_names": ["lag_1", "lag_3", "..."],
    "values": "...serialized DataFrame..."
  },
  "test_data": {
    "rows": 10000,
    "columns": 32,
    "target_column": "revenue",
    "feature_names": ["lag_1", "lag_3", "..."],
    "values": "...serialized DataFrame..."
  },
  "split_validation": {
    "train_pct": 80.0,
    "test_pct": 20.0,
    "target_stats": {
      "train_mean": 1250.50,
      "test_mean": 1245.80,
      "train_std": 450.20,
      "test_std": 460.10
    },
    "class_distribution": {},
    "date_range": {}
  },
  "smote_config": {
    "apply_smote": true,
    "strategy": "auto",
    "k_neighbors": 5
  },
  "preprocessing_params": {
    "scaler_params": {},
    "encoding_maps": {}
  },
  "metadata": {
    "random_state": 42,
    "split_index": 40000,
    "generated_at": "ISO 8601"
  }
}
```
