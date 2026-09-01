# Seasonal Naive Forecasting Guide

> Baseline model — every other model must beat this to be considered useful.

## Algorithm Overview

The Seasonal Naive model predicts future values by repeating the value from the same period in the previous cycle. It captures seasonality perfectly but assumes no trend change.

```
Prediction: ŷ(t+h) = y(t + h - m)
Where: m = seasonal period (12 for monthly, 7 for daily, 4 for quarterly)
```

### Visual Example (Monthly Data)
```
Historical:  Jan=100, Feb=90, Mar=110, ..., Dec=120
                                                      ↓ repeat
Forecast:    Jan=100, Feb=90, Mar=110, ..., Dec=120
```

---

## Implementation

```python
def seasonal_naive_forecast(train_series, test_size, seasonal_period):
    """
    Forecast by repeating the last seasonal cycle.
    
    Parameters:
        train_series: pd.Series of training values (sorted by time)
        test_size: int, number of periods to forecast
        seasonal_period: int (7=daily/weekly, 12=monthly, 4=quarterly)
    
    Returns:
        np.array of predictions
    """
    import numpy as np
    
    # Get the last full seasonal cycle from training data
    last_cycle = train_series.values[-seasonal_period:]
    
    # Repeat the cycle to cover the test period
    predictions = np.tile(last_cycle, (test_size // seasonal_period) + 1)[:test_size]
    
    return predictions
```

---

## Hyperparameters

| Parameter | Description | How to Set |
|---|---|---|
| `seasonal_period` | Length of one seasonal cycle | Auto-detect or domain knowledge |

### Auto-Detecting Seasonal Period
```python
from statsmodels.tsa.seasonal import seasonal_decompose

def detect_seasonal_period(series, candidates=[4, 7, 12, 52]):
    """
    Try multiple seasonal periods, pick the one with strongest seasonality.
    """
    best_period = candidates[0]
    best_strength = 0
    
    for period in candidates:
        if len(series) < 2 * period:
            continue
        try:
            decomp = seasonal_decompose(series, period=period, model='additive')
            seasonal_var = decomp.seasonal.var()
            residual_var = decomp.resid.dropna().var()
            strength = 1 - (residual_var / (seasonal_var + residual_var + 1e-10))
            if strength > best_strength:
                best_strength = strength
                best_period = period
        except:
            continue
    
    return best_period, best_strength
```

---

## Best Practices

1. **Always include as baseline** — If a complex model can't beat seasonal naive, it's adding noise, not signal.
2. **Use domain knowledge for period** — Monthly revenue → period=12. Daily web traffic → period=7.
3. **Check if trend exists** — Seasonal naive assumes flat trend. If data has strong upward/downward trend, seasonal naive will systematically under/over-predict.
4. **Confidence interval** — Use standard deviation of residuals from the last cycle:
   ```python
   residuals = train_series.values[-seasonal_period:] - train_series.values[-2*seasonal_period:-seasonal_period]
   ci_width = 1.96 * np.std(residuals)  # 95% CI
   ```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Wrong period** | Using period=12 on daily data | Match period to data frequency |
| **Incomplete last cycle** | Last season has missing months | Pad or use second-to-last cycle |
| **Strong trend** | Naive repeats old level, misses growth | Expected — this is why we train other models |
| **Short history** | < 2 full cycles | Cannot use seasonal naive; fall back to last-value naive |

---

## When Seasonal Naive Wins

Seasonal naive often wins when:
- Data has very strong, stable seasonality
- Limited training data (< 3 years monthly)
- High noise-to-signal ratio (complex models overfit)
- No clear trend or structural changes

**Interpret this as:** "The data is too noisy or too short for ML to add value. Use simpler methods and collect more data."
