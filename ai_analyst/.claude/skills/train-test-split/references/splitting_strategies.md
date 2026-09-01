# Splitting Strategies Reference

> Source: predictive_agents heritage + sklearn best practices

## Purpose
Detailed guide for train/test splitting strategies by pipeline type, including edge cases and validation checks.

---

## 1. Time-Based Split (Forecasting)

### How It Works
```
Timeline: ──────────────────────────────────────────►
Data:     [Jan] [Feb] [Mar] [Apr] [May] [Jun] [Jul] [Aug] [Sep] [Oct]
          ├──────────── TRAIN (80%) ──────────────┤├── TEST (20%) ──┤
          Jan - Aug                                  Sep - Oct
```

### Implementation
```python
def time_based_split(df, date_col, test_ratio=0.2):
    """
    Split time series by temporal cutoff.
    Train = earliest periods, Test = latest periods.
    """
    df = df.sort_values(date_col).reset_index(drop=True)
    cutoff_idx = int(len(df) * (1 - test_ratio))
    
    train = df.iloc[:cutoff_idx].copy()
    test = df.iloc[cutoff_idx:].copy()
    
    # Verify no date overlap
    max_train_date = train[date_col].max()
    min_test_date = test[date_col].min()
    assert max_train_date < min_test_date, \
        f"Date overlap: train ends {max_train_date}, test starts {min_test_date}"
    
    return train, test
```

### Key Rules
- **NEVER shuffle** — temporal order must be preserved
- Test set = most recent data (simulates real forecasting scenario)
- If data has gaps, split by date threshold (not by row count)
- Minimum test size: 2 full seasonal cycles (e.g., 2 months for monthly seasonality)

### Expanding Window Validation (Optional)
For more robust evaluation, use expanding window cross-validation:
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(df):
    train_fold = df.iloc[train_idx]
    test_fold = df.iloc[test_idx]
    # Train and evaluate on each fold
```

### Edge Cases
| Scenario | Action |
|----------|--------|
| < 30 data points | Use 70/30 split (more test data for reliability) |
| Multiple seasonalities | Test set must cover at least the longest seasonal period |
| Irregular frequency | Split by date threshold, not row count |
| Missing dates in test period | Warn — forecast accuracy metrics may be misleading |

---

## 2. Stratified Split (Classification)

### How It Works
```
Full dataset:    [Class 0: 95%] [Class 1: 5%]
                        ↓ stratified split
Train (80%):     [Class 0: 95%] [Class 1: 5%]  ← same ratio
Test  (20%):     [Class 0: 95%] [Class 1: 5%]  ← same ratio
```

### Implementation
```python
from sklearn.model_selection import train_test_split

def stratified_split(df, target_col, test_ratio=0.2, random_state=42):
    """
    Split preserving class distribution in both sets.
    """
    train, test = train_test_split(
        df, 
        test_size=test_ratio,
        random_state=random_state,
        stratify=df[target_col]
    )
    
    # Validate class ratios
    train_dist = train[target_col].value_counts(normalize=True)
    test_dist = test[target_col].value_counts(normalize=True)
    
    for cls in train_dist.index:
        ratio_diff = abs(train_dist[cls] - test_dist[cls])
        assert ratio_diff < 0.02, \
            f"Class {cls} ratio differs by {ratio_diff:.3f} between train/test"
    
    return train, test
```

### Key Rules
- **Always stratify** — random split on imbalanced data can put 0 minority samples in test
- `stratify=df[target_col]` in sklearn handles this automatically
- Verify class counts (not just ratios) — minority class needs ≥30 samples in test for reliable F1
- SMOTE is applied AFTER splitting, ONLY on training set

### Edge Cases
| Scenario | Action |
|----------|--------|
| Minority class < 50 total | Use 60/40 split to get enough test samples |
| Minority class < 10 total | WARN: not enough data for reliable classification |
| Multi-class (>2 classes) | Still stratify; verify each class has ≥10 test samples |
| Class with 1 sample | Cannot stratify — merge with nearest class or collect more data |

---

## 3. Random Split (Regression)

### How It Works
```python
from sklearn.model_selection import train_test_split

def random_split(df, target_col, test_ratio=0.2, random_state=42):
    """
    Simple random split for regression problems.
    No temporal or class-balance constraints.
    """
    train, test = train_test_split(
        df,
        test_size=test_ratio,
        random_state=random_state
    )
    
    # Validate target distribution similarity
    train_mean = train[target_col].mean()
    test_mean = test[target_col].mean()
    overall_mean = df[target_col].mean()
    
    pct_diff = abs(train_mean - test_mean) / overall_mean * 100
    if pct_diff > 5:
        print(f"WARNING: Target mean differs by {pct_diff:.1f}% between train/test")
    
    return train, test
```

### Key Rules
- Shuffle is OK — no temporal dependency
- Verify target distribution is similar in both sets (mean, std)
- If data has groups (e.g., customers), consider GroupShuffleSplit to prevent leakage

### Group-Aware Split (When Applicable)
```python
from sklearn.model_selection import GroupShuffleSplit

def group_split(df, target_col, group_col, test_ratio=0.2):
    """
    Split ensuring all rows from same group stay in same set.
    Prevents data leakage from repeated measurements.
    """
    gss = GroupShuffleSplit(n_splits=1, test_size=test_ratio, random_state=42)
    train_idx, test_idx = next(gss.split(df, df[target_col], groups=df[group_col]))
    return df.iloc[train_idx], df.iloc[test_idx]

# Use when: multiple rows per customer/product/store
# Example: predict store revenue — all rows from store X in same set
```

---

## Validation Checklist (All Strategies)

| Check | Pass Criteria | Action if Fail |
|-------|--------------|----------------|
| Train/test size ratio | Within 2% of target ratio | Adjust split |
| No data overlap | Zero shared indices | Debug split logic |
| Target distribution | Mean within 5% between sets | Re-split or stratify |
| Feature distributions | No dramatic shifts (KS test p > 0.05) | Investigate data ordering |
| Minimum test samples | ≥ 30 rows for regression, ≥ 30 per class for classification | Use larger test ratio |
| Temporal integrity | No future dates in train (forecasting only) | Re-sort and re-split |
