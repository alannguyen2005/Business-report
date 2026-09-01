# Encoding Patterns Reference

> Source: predictive_agents heritage + sklearn best practices

## Purpose
Guide for encoding categorical variables into numeric format for ML models. Choice of encoding depends on cardinality, ordinality, and model type.

---

## Encoding Decision Tree

```
Is the column categorical?
├── No (numeric) → StandardScaler (or leave raw for tree models)
└── Yes
    ├── Binary (2 unique values) → Label Encode (0/1)
    ├── Ordinal (has natural order) → Ordinal Encode (mapped integers)
    ├── Low cardinality (3-10 unique) → One-Hot Encode (drop_first=True)
    ├── Medium cardinality (11-20 unique) → One-Hot Encode (consider grouping rare)
    └── High cardinality (>20 unique) → Frequency Encode (or Target Encode)
```

---

## 1. Label Encoding (Binary)

```python
def label_encode_binary(df, col):
    """
    Encode binary column as 0/1.
    Deterministic: alphabetically first value = 0.
    """
    unique_vals = sorted(df[col].dropna().unique())
    assert len(unique_vals) == 2, f"{col} is not binary: {unique_vals}"
    mapping = {unique_vals[0]: 0, unique_vals[1]: 1}
    df[col] = df[col].map(mapping)
    return df, mapping

# Examples:
# gender: {Female: 0, Male: 1}
# is_active: {False: 0, True: 1}
# plan_type: {free: 0, paid: 1}
```

**When to use:** Exactly 2 unique values. All model types.

---

## 2. Ordinal Encoding

```python
def ordinal_encode(df, col, order):
    """
    Encode ordinal column preserving natural order.
    
    Parameters:
        order: list of values from lowest to highest
        e.g., ['low', 'medium', 'high'] → [0, 1, 2]
    """
    mapping = {val: i for i, val in enumerate(order)}
    df[col] = df[col].map(mapping)
    return df, mapping

# Common ordinal mappings:
ORDINAL_MAPS = {
    "size": ["XS", "S", "M", "L", "XL", "XXL"],
    "priority": ["low", "medium", "high", "critical"],
    "satisfaction": ["very_dissatisfied", "dissatisfied", "neutral", "satisfied", "very_satisfied"],
    "education": ["high_school", "bachelors", "masters", "phd"],
    "income_band": ["<25k", "25-50k", "50-75k", "75-100k", "100k+"],
    "company_size": ["startup", "smb", "mid_market", "enterprise"]
}
```

**When to use:** Column has natural order that matters for prediction.
**Pitfall:** Never use for nominal categories (city, color) — implies false order.

---

## 3. One-Hot Encoding

```python
def one_hot_encode(df, cols, drop_first=True, max_categories=10):
    """
    One-hot encode categorical columns.
    
    Parameters:
        drop_first: True to avoid multicollinearity (N-1 dummies)
        max_categories: group rare categories into 'Other' if exceeded
    """
    for col in cols:
        if df[col].nunique() > max_categories:
            # Group rare categories
            top_cats = df[col].value_counts().nlargest(max_categories - 1).index
            df[col] = df[col].where(df[col].isin(top_cats), 'Other')
        
    df = pd.get_dummies(df, columns=cols, drop_first=drop_first, dtype=int)
    return df

# Example:
# region: [North, South, East, West]
# → region_South, region_East, region_West (North is baseline when drop_first=True)
```

**When to use:** 3-20 unique values, no natural order.
**Pitfall:** Feature explosion if >20 categories. Use `drop_first=True` for linear models.

---

## 4. Frequency Encoding

```python
def frequency_encode(df, col):
    """
    Replace each category with its frequency (proportion) in the dataset.
    Handles unseen categories in test set gracefully.
    """
    freq_map = df[col].value_counts(normalize=True).to_dict()
    df[col + '_freq'] = df[col].map(freq_map).fillna(0)  # unseen → 0
    df.drop(col, axis=1, inplace=True)
    return df, freq_map

# Example:
# product_category with 500 unique values:
# "Electronics" → 0.35 (35% of rows)
# "Books" → 0.12
# "Rare_Category_X" → 0.0001
```

**When to use:** >20 unique values, no ordinal relationship.
**Advantage:** Single column output (no feature explosion).
**Pitfall:** Two different categories with same frequency get same value. Rare in practice.

---

## 5. Target Encoding (Use with Caution)

```python
def target_encode(df_train, df_test, col, target_col, smoothing=10):
    """
    Replace category with mean target value for that category.
    Uses smoothing to prevent overfitting on rare categories.
    
    WARNING: Must be fit on train only, then applied to test.
    """
    global_mean = df_train[target_col].mean()
    cat_stats = df_train.groupby(col)[target_col].agg(['mean', 'count'])
    
    # Smoothed mean: weighted average of category mean and global mean
    smoother = cat_stats['count'] / (cat_stats['count'] + smoothing)
    cat_stats['smoothed_mean'] = smoother * cat_stats['mean'] + (1 - smoother) * global_mean
    
    encoding_map = cat_stats['smoothed_mean'].to_dict()
    
    df_train[col + '_target'] = df_train[col].map(encoding_map)
    df_test[col + '_target'] = df_test[col].map(encoding_map).fillna(global_mean)
    
    return df_train, df_test, encoding_map

# CRITICAL: Only fit encoding on TRAINING data to prevent target leakage
```

**When to use:** High cardinality + strong relationship with target.
**Pitfall:** Target leakage if fit on full data. Always use train-only fit.

---

## Model-Specific Encoding Rules

| Model Type | Recommended Encoding | Why |
|---|---|---|
| **Linear (Ridge/Lasso/LogReg)** | One-hot (drop_first=True) + StandardScaler | Needs numeric + no multicollinearity |
| **Tree (DT/RF)** | Label or Ordinal (any order) | Trees split on thresholds, order doesn't matter |
| **XGBoost** | Label or Ordinal | Handles categoricals natively (enable_categorical=True) |
| **Prophet** | Not applicable | Only uses date + target |
| **SARIMA** | Not applicable | Only uses target series |
| **LightGBM-TS** | Ordinal for categoricals | Native categorical support |

---

## Missing Value Handling Before Encoding

```python
def handle_missing_for_encoding(df, col, strategy='auto'):
    """
    Handle missing values before encoding.
    Must be done BEFORE encoding step.
    """
    if df[col].dtype in ['object', 'category']:
        if strategy == 'auto':
            # If <5% missing: fill with mode
            if df[col].isnull().mean() < 0.05:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                # Create explicit 'Missing' category
                df[col] = df[col].fillna('_MISSING_')
    else:
        # Numeric: median imputation
        df[col] = df[col].fillna(df[col].median())
    return df
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Encoding before split** | Test data influences encoding | Fit encoders on train only |
| **One-hot on high cardinality** | 500 categories → 499 columns | Use frequency or target encoding |
| **Ordinal on nominal** | Implies false order (city A < city B) | Use one-hot or frequency instead |
| **Forgetting drop_first** | Multicollinearity in linear models | Always `drop_first=True` for linear models |
| **NaN after encoding** | Unseen categories in test set | Map unseen to 0 (frequency) or global mean (target) |
