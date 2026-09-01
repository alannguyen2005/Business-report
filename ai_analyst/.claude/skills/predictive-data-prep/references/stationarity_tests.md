# Stationarity Tests Reference

> Source: predictive_agents heritage + statistical methods

## Purpose
Determine if a time series is stationary (constant mean, variance over time) before applying forecasting models. SARIMA requires stationarity; Prophet handles non-stationarity internally.

---

## Why Stationarity Matters

| Model | Requires Stationarity? | Action if Non-Stationary |
|-------|----------------------|--------------------------|
| **Seasonal Naive** | No | N/A — uses raw values |
| **Prophet** | No | Handles internally (piecewise trends) |
| **SARIMA** | Yes | Difference series (d parameter) |
| **LightGBM-TS** | No | Lag features work on raw values |

---

## Test 1: Augmented Dickey-Fuller (ADF)

**Hypothesis:**
- H0: Unit root exists (series is NON-stationary)
- H1: No unit root (series IS stationary)

```python
from statsmodels.tsa.stattools import adfuller

def run_adf_test(series, significance=0.05):
    """
    Run ADF test for stationarity.
    
    Returns:
        dict with test results and interpretation
    """
    series_clean = series.dropna()
    result = adfuller(series_clean, autolag='AIC')
    
    return {
        "test": "ADF",
        "statistic": round(result[0], 4),
        "p_value": round(result[1], 4),
        "lags_used": result[2],
        "n_observations": result[3],
        "critical_values": {k: round(v, 4) for k, v in result[4].items()},
        "is_stationary": result[1] < significance,
        "interpretation": (
            f"p={result[1]:.4f} {'<' if result[1] < significance else '>='} {significance} "
            f"→ {'Reject' if result[1] < significance else 'Fail to reject'} H0 "
            f"→ Series {'IS' if result[1] < significance else 'is NOT'} stationary"
        )
    }
```

**Interpreting ADF Results:**
| p-value | Decision | Action |
|---------|----------|--------|
| p < 0.01 | Strong evidence of stationarity | No differencing needed |
| 0.01 ≤ p < 0.05 | Moderate evidence | No differencing needed |
| 0.05 ≤ p < 0.10 | Weak evidence | Consider differencing |
| p ≥ 0.10 | Non-stationary | Difference the series |

---

## Test 2: KPSS (Kwiatkowski-Phillips-Schmidt-Shin)

**Hypothesis (reversed from ADF):**
- H0: Series IS stationary
- H1: Series is NOT stationary

```python
from statsmodels.tsa.stattools import kpss

def run_kpss_test(series, regression='c', significance=0.05):
    """
    Run KPSS test for stationarity.
    regression='c' tests level stationarity.
    regression='ct' tests trend stationarity.
    
    Returns:
        dict with test results and interpretation
    """
    series_clean = series.dropna()
    stat, p_value, n_lags, critical_values = kpss(series_clean, regression=regression)
    
    return {
        "test": "KPSS",
        "statistic": round(stat, 4),
        "p_value": round(p_value, 4),
        "lags_used": n_lags,
        "regression": regression,
        "critical_values": {k: round(v, 4) for k, v in critical_values.items()},
        "is_stationary": p_value > significance,
        "interpretation": (
            f"p={p_value:.4f} {'>' if p_value > significance else '<='} {significance} "
            f"→ {'Fail to reject' if p_value > significance else 'Reject'} H0 "
            f"→ Series {'IS' if p_value > significance else 'is NOT'} stationary"
        )
    }
```

---

## Decision Matrix (Combined ADF + KPSS)

| ADF Result | KPSS Result | Conclusion | Action |
|------------|-------------|------------|--------|
| Stationary (p < 0.05) | Stationary (p > 0.05) | **Stationary** | d=0, no differencing |
| Non-stationary (p ≥ 0.05) | Non-stationary (p ≤ 0.05) | **Non-stationary** | d=1, difference once |
| Stationary | Non-stationary | **Trend-stationary** | d=1 (or detrend) |
| Non-stationary | Stationary | **Difference-stationary** | d=1 to be safe |

```python
def determine_differencing(series):
    """
    Combined ADF + KPSS to determine differencing order.
    Returns: differencing_order (0, 1, or 2)
    """
    adf = run_adf_test(series)
    kpss_result = run_kpss_test(series)
    
    if adf["is_stationary"] and kpss_result["is_stationary"]:
        return 0  # Stationary
    
    # Non-stationary: try d=1
    diff1 = series.diff().dropna()
    adf1 = run_adf_test(diff1)
    kpss1 = run_kpss_test(diff1)
    
    if adf1["is_stationary"] and kpss1["is_stationary"]:
        return 1  # One difference sufficient
    
    # Rare: try d=2
    diff2 = diff1.diff().dropna()
    adf2 = run_adf_test(diff2)
    if adf2["is_stationary"]:
        return 2
    
    # If d=2 still not stationary, log warning and use d=1
    return 1  # Fallback
```

---

## Seasonal Stationarity

For seasonal data, also check seasonal differencing:

```python
def check_seasonal_stationarity(series, seasonal_period):
    """
    Check if seasonal differencing is needed.
    Seasonal difference: y_t - y_{t-m} where m = seasonal period
    """
    seasonal_diff = series - series.shift(seasonal_period)
    seasonal_diff = seasonal_diff.dropna()
    
    adf = run_adf_test(seasonal_diff)
    return {
        "seasonal_period": seasonal_period,
        "needs_seasonal_diff": not adf["is_stationary"],
        "D": 0 if adf["is_stationary"] else 1
    }
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Over-differencing** | d=2 when d=1 sufficient → introduces MA structure | Always test d=1 before trying d=2 |
| **Ignoring seasonality** | ADF passes but seasonal pattern remains | Test seasonal differencing separately |
| **Small sample** | ADF has low power with <30 observations | Use KPSS as confirmation; be conservative |
| **Structural breaks** | Break point makes ADF unreliable | Visual inspection + Chow test if suspected |
| **NaN in series** | Both tests fail on NaN | Always `.dropna()` before testing |
