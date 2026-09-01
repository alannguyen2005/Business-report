# Feature Engineering Reference

> Source: predictive_agents heritage + AI Analyst design

## Purpose
Guide for creating predictive features from cleaned data, organized by pipeline type.

---

## Forecasting Features

### Lag Features
Create historical value references for the target variable.

```python
def create_lag_features(df, target_col, lags=[1, 2, 3, 6, 12]):
    """
    Create lag features for time series forecasting.
    
    Parameters:
        df: DataFrame sorted by date
        target_col: column to create lags from
        lags: list of lag periods
    
    Returns:
        DataFrame with lag columns added
    """
    for lag in lags:
        df[f'lag_{lag}'] = df[target_col].shift(lag)
    
    # Drop rows where lags create NaN (beginning of series)
    # max_lag rows will be lost
    return df

# Best practices:
# - Always include lag_1 (most recent value)
# - For monthly data: lag_1, lag_3, lag_6, lag_12
# - For weekly data: lag_1, lag_4, lag_13, lag_52
# - For daily data: lag_1, lag_7, lag_14, lag_28
```

### Rolling Statistics
Capture trends and volatility over windows.

```python
def create_rolling_features(df, target_col, windows=[3, 6, 12]):
    """
    Create rolling mean, std, min, max features.
    """
    for w in windows:
        df[f'rolling_mean_{w}'] = df[target_col].rolling(w).mean()
        df[f'rolling_std_{w}'] = df[target_col].rolling(w).std()
        df[f'rolling_min_{w}'] = df[target_col].rolling(w).min()
        df[f'rolling_max_{w}'] = df[target_col].rolling(w).max()
    return df

# Best practices:
# - Window size should be <= 1/3 of total data length
# - rolling_std captures volatility (useful for confidence intervals)
# - Use .shift(1) on rolling features to avoid data leakage
```

### Calendar Features
Extract temporal patterns from date columns.

```python
def create_calendar_features(df, date_col):
    """
    Extract calendar features from date column.
    """
    dt = pd.to_datetime(df[date_col])
    df['month'] = dt.dt.month
    df['quarter'] = dt.dt.quarter
    df['day_of_week'] = dt.dt.dayofweek
    df['day_of_month'] = dt.dt.day
    df['week_of_year'] = dt.dt.isocalendar().week.astype(int)
    df['is_weekend'] = (dt.dt.dayofweek >= 5).astype(int)
    df['is_month_start'] = dt.dt.is_month_start.astype(int)
    df['is_month_end'] = dt.dt.is_month_end.astype(int)
    df['is_quarter_end'] = dt.dt.is_quarter_end.astype(int)
    df['days_in_month'] = dt.dt.days_in_month
    return df

# Best practices:
# - Cyclical encoding for month: sin(2π*month/12), cos(2π*month/12)
# - Avoid: year as feature (linear trend is better)
# - Add: is_holiday if holiday calendar available
```

### Trend Feature
```python
df['linear_trend'] = range(len(df))
# Captures linear growth/decline independent of seasonality
```

---

## Regression Features

### Interaction Terms
```python
from sklearn.preprocessing import PolynomialFeatures

def create_interactions(df, features, degree=2, interaction_only=True):
    """
    Create interaction terms between top features.
    Only create if total features < 20 (avoid feature explosion).
    """
    if len(features) > 20:
        # Select top 5 by correlation with target
        features = top_corr_features(df, target_col, n=5)
    
    poly = PolynomialFeatures(degree=degree, interaction_only=interaction_only,
                               include_bias=False)
    interactions = poly.fit_transform(df[features])
    feature_names = poly.get_feature_names_out(features)
    return pd.DataFrame(interactions, columns=feature_names, index=df.index)

# Best practices:
# - Only create interactions for features with individual signal
# - Max degree=2 (higher degrees → overfitting)
# - interaction_only=True avoids x^2 terms unless explicitly needed
```

### Domain-Specific Ratios
```python
# SaaS domain
df['revenue_per_user'] = df['revenue'] / df['active_users'].clip(lower=1)
df['arpu'] = df['mrr'] / df['subscribers'].clip(lower=1)
df['churn_rate'] = df['churned'] / df['total_customers'].clip(lower=1)

# E-commerce domain  
df['aov'] = df['revenue'] / df['orders'].clip(lower=1)
df['conversion_rate'] = df['orders'] / df['sessions'].clip(lower=1)
df['cart_abandonment'] = 1 - df['completed_carts'] / df['initiated_carts'].clip(lower=1)

# General
df['growth_rate'] = df[metric].pct_change()
df['yoy_change'] = df[metric] / df[metric].shift(12) - 1
```

---

## Classification Features

### Behavioral Ratios
```python
# Activity intensity
df['actions_per_day'] = df['total_actions'] / df['days_active'].clip(lower=1)
df['support_rate'] = df['support_tickets'] / df['months_active'].clip(lower=1)

# Engagement decay
df['recent_vs_total'] = df['last_30d_actions'] / df['total_actions'].clip(lower=1)
df['engagement_trend'] = df['last_30d_actions'] - df['prev_30d_actions']
```

### Recency Features
```python
from datetime import datetime

reference_date = df[date_col].max()
df['days_since_last_login'] = (reference_date - pd.to_datetime(df['last_login'])).dt.days
df['days_since_last_purchase'] = (reference_date - pd.to_datetime(df['last_purchase'])).dt.days
df['days_since_signup'] = (reference_date - pd.to_datetime(df['signup_date'])).dt.days

# Recency bins
df['recency_tier'] = pd.cut(df['days_since_last_login'],
                             bins=[0, 7, 30, 90, 365, float('inf')],
                             labels=['1w', '1m', '3m', '1y', '1y+'])
```

### Frequency Encoding for High-Cardinality Categoricals
```python
def frequency_encode(df, col):
    """Replace category values with their frequency in the dataset."""
    freq = df[col].value_counts(normalize=True)
    df[col + '_freq'] = df[col].map(freq)
    df.drop(col, axis=1, inplace=True)
    return df

# When to use:
# - Column has >20 unique values (too many for one-hot)
# - No natural ordinal relationship
# - Examples: product_category (500 values), city (200 values)
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Data leakage** | Using future data to predict past | Always `.shift(1)` rolling features; split before SMOTE |
| **Feature explosion** | Too many one-hot columns | Frequency encode if >10 categories |
| **Target leakage** | Feature derived from target | Never include direct derivatives of target |
| **Scale mismatch** | Revenue (millions) vs count (tens) | StandardScaler before training |
| **Missing lag rows** | NaN from shift operations | Drop first `max_lag` rows, document row loss |
