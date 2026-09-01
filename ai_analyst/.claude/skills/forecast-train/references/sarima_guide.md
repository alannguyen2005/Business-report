# SARIMA Forecasting Guide

> Seasonal AutoRegressive Integrated Moving Average — classical statistical forecasting.

## Algorithm Overview

SARIMA models a time series using autoregressive (past values), differencing (stationarity), and moving average (past errors) components, both for non-seasonal and seasonal parts.

```
SARIMA(p, d, q)(P, D, Q, m)

Non-seasonal:
  p = AR order (how many past values to use)
  d = differencing order (how many times to difference for stationarity)
  q = MA order (how many past errors to use)

Seasonal (period = m):
  P = seasonal AR order
  D = seasonal differencing order
  Q = seasonal MA order
  m = seasonal period (12 for monthly, 7 for daily, 4 for quarterly)
```

### Equation
```
(1 - Σφ_i B^i)(1 - ΣΦ_j B^(jm))(1 - B)^d (1 - B^m)^D y_t 
    = (1 + Σθ_i B^i)(1 + ΣΘ_j B^(jm)) ε_t
```

---

## Implementation

```python
import pmdarima as pm
import numpy as np

def train_sarima(train_series, test_size, seasonal_period):
    """
    Train SARIMA using auto_arima for automatic order selection.
    
    Parameters:
        train_series: pd.Series of target values (sorted by time)
        test_size: int, number of periods to forecast
        seasonal_period: int (m parameter)
    
    Returns:
        model, predictions, confidence_intervals, order, seasonal_order
    """
    model = pm.auto_arima(
        train_series,
        
        # Seasonal configuration
        seasonal=True,
        m=seasonal_period,
        
        # Search bounds
        start_p=1, max_p=3,
        start_q=1, max_q=3,
        start_P=0, max_P=2,
        start_Q=0, max_Q=2,
        max_d=2, max_D=1,
        max_order=5,
        
        # Search strategy
        stepwise=True,          # Faster than exhaustive grid search
        information_criterion='aic',  # AIC for model selection
        
        # Robustness
        suppress_warnings=True,
        error_action='ignore',  # Skip invalid models
        
        # Stationarity
        test='adf',             # Use ADF test for d
        seasonal_test='ocsb',   # Use OCSB test for D
        
        trace=False             # Set True for debugging
    )
    
    # Forecast
    predictions, conf_int = model.predict(
        n_periods=test_size, 
        return_conf_int=True,
        alpha=0.05  # 95% CI
    )
    
    return {
        'model': model,
        'predictions': predictions,
        'conf_lower': conf_int[:, 0],
        'conf_upper': conf_int[:, 1],
        'order': model.order,            # (p, d, q)
        'seasonal_order': model.seasonal_order,  # (P, D, Q, m)
        'aic': model.aic(),
        'bic': model.bic()
    }
```

---

## Hyperparameters

| Parameter | Range | Description | Auto-Selected By |
|---|---|---|---|
| `p` (AR) | 0-3 | Autoregressive terms | `auto_arima` via AIC |
| `d` (I) | 0-2 | Differencing order | ADF test |
| `q` (MA) | 0-3 | Moving average terms | `auto_arima` via AIC |
| `P` (Seasonal AR) | 0-2 | Seasonal autoregressive | `auto_arima` via AIC |
| `D` (Seasonal I) | 0-1 | Seasonal differencing | OCSB test |
| `Q` (Seasonal MA) | 0-2 | Seasonal moving average | `auto_arima` via AIC |
| `m` (Period) | 4/7/12/52 | Seasonal period | Domain knowledge / auto-detect |

### How auto_arima Selects Orders

1. Test stationarity → determine d (ADF test)
2. Test seasonal stationarity → determine D (OCSB test)
3. Stepwise search over (p, q, P, Q) → minimize AIC
4. AIC = 2k - 2ln(L) where k = parameters, L = likelihood
5. Lower AIC = better model (balances fit vs complexity)

### Manual Order Selection (ACF/PACF)
```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# After differencing d times:
# ACF cuts off at lag q → MA order
# PACF cuts off at lag p → AR order
# Seasonal spikes at lag m, 2m → seasonal orders

# Example interpretation:
# PACF significant at lags 1, 2 → p = 2
# ACF significant at lag 1 → q = 1
# PACF spike at lag 12 → P = 1
# ACF spike at lag 12 → Q = 1
```

---

## Best Practices

1. **Always use `auto_arima`** — Manual order selection is error-prone. Let the algorithm search.
2. **Set `stepwise=True`** — Much faster than exhaustive search, usually finds the same model.
3. **Check residuals** — Good model should have white noise residuals (no pattern).
4. **Use `information_criterion='aic'`** — AIC balances fit and complexity well for forecasting.
5. **Limit max orders** — `max_p=3, max_q=3` prevents overfitting. SARIMA with too many params overfits fast.
6. **Handle non-stationarity** — If d=2 required, data might need log transform instead.

### Residual Diagnostics
```python
def check_residuals(model):
    """
    Check if residuals behave like white noise.
    Good model: residuals are ~N(0, σ²) with no autocorrelation.
    """
    residuals = model.resid()
    
    # 1. Ljung-Box test: H0 = residuals are white noise
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb_test = acorr_ljungbox(residuals, lags=[10], return_df=True)
    is_white_noise = lb_test['lb_pvalue'].values[0] > 0.05
    
    # 2. Normality: Shapiro-Wilk
    from scipy.stats import shapiro
    _, p_normal = shapiro(residuals[:500])  # limit to 500 for performance
    is_normal = p_normal > 0.05
    
    # 3. Mean near zero
    mean_near_zero = abs(residuals.mean()) < residuals.std() * 0.1
    
    return {
        "white_noise": is_white_noise,
        "normal": is_normal,
        "mean_near_zero": mean_near_zero,
        "residual_mean": float(residuals.mean()),
        "residual_std": float(residuals.std()),
        "ljung_box_p": float(lb_test['lb_pvalue'].values[0])
    }
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Non-stationary data** | Model fails or gives wild forecasts | Check stationarity before fitting; use d=1 or log transform |
| **Wrong seasonal period** | Model captures wrong cycle | Verify with ACF plot; m=12 for monthly, m=7 for daily |
| **Over-differencing** | d=2 when d=1 is enough → overdamped forecast | Let auto_arima decide via ADF test |
| **Too many parameters** | Overfitting (good fit, bad forecast) | Keep max_order=5, max_p=3, max_q=3 |
| **Long computation time** | Exhaustive search with high bounds | Use `stepwise=True`, reduce max bounds |
| **Convergence failure** | Model doesn't converge | Try `method='nm'` (Nelder-Mead), reduce max orders |
| **Missing values** | SARIMA can't handle NaN | Interpolate or forward-fill before fitting |

---

## When SARIMA Works Best

- **Data with clear seasonality and trend** — Monthly revenue, quarterly sales
- **Moderate data size** (50-500 data points) — enough to estimate params, not so much that ML wins
- **Linear patterns** — SARIMA assumes linearity; non-linear patterns favor LightGBM
- **Interpretability needed** — SARIMA orders are interpretable (AR=momentum, MA=shock response)

## When SARIMA Struggles

- **Multiple seasonalities** — Daily data with both weekly and yearly patterns (use Prophet instead)
- **Non-linear relationships** — Complex interactions (use LightGBM)
- **Structural breaks** — Sudden regime changes (SARIMA assumes stationarity)
- **Very long series** (> 1000 points) — Computation grows; ML alternatives scale better
