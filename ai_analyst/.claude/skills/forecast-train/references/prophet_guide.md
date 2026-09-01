# Prophet Forecasting Guide

> Facebook's decomposable time series model — handles seasonality, trends, and holidays.

## Algorithm Overview

Prophet decomposes a time series into three additive (or multiplicative) components:

```
y(t) = g(t) + s(t) + h(t) + ε(t)
Where:
  g(t) = trend (piecewise linear or logistic growth)
  s(t) = seasonality (Fourier series)
  h(t) = holidays/events (user-specified)
  ε(t) = error term
```

Prophet uses a Bayesian approach with Stan backend. It's robust to missing data, trend shifts, and outliers.

---

## Implementation

```python
from prophet import Prophet
import pandas as pd

def train_prophet(train_df, date_col, target_col, test_size, freq='MS'):
    """
    Train Prophet model and generate forecasts.
    
    Parameters:
        train_df: DataFrame with date and target columns
        date_col: name of date column
        target_col: name of target column
        test_size: number of periods to forecast
        freq: 'MS' (monthly), 'W' (weekly), 'D' (daily)
    
    Returns:
        model, forecast_df, predictions
    """
    # Prophet requires columns named 'ds' and 'y'
    prophet_df = train_df[[date_col, target_col]].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    
    # Initialize model
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_mode='multiplicative',
        yearly_seasonality=True,
        weekly_seasonality='auto',
        daily_seasonality=False,
        interval_width=0.95
    )
    
    # Fit
    model.fit(prophet_df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=test_size, freq=freq)
    forecast = model.predict(future)
    
    # Extract predictions for test period
    predictions = forecast.tail(test_size)['yhat'].values
    lower = forecast.tail(test_size)['yhat_lower'].values
    upper = forecast.tail(test_size)['yhat_upper'].values
    
    return model, forecast, predictions, lower, upper
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `changepoint_prior_scale` | 0.05 | 0.001 - 0.5 | Flexibility of trend changes | Higher = more flexible trend. Lower = smoother trend. Start with 0.05, increase if underfitting trend shifts |
| `seasonality_mode` | 'additive' | 'additive' \| 'multiplicative' | How seasonality scales with trend | Multiplicative if seasonal amplitude grows with level (e.g., revenue). Additive if constant amplitude |
| `seasonality_prior_scale` | 10 | 0.01 - 10 | Strength of seasonality fitting | Lower = dampen seasonality. Increase if seasonality is clearly strong |
| `holidays_prior_scale` | 10 | 0.01 - 10 | Strength of holiday effects | Lower if holiday effects are noisy |
| `changepoint_range` | 0.8 | 0.5 - 0.95 | Fraction of history for changepoints | 0.8 means changepoints only in first 80% of data |
| `n_changepoints` | 25 | 10 - 50 | Number of potential changepoints | More = finer trend detection. Too many = overfitting |
| `yearly_seasonality` | 'auto' | True/False/'auto'/int | Yearly seasonal component | True for monthly/weekly data with >2 years. int = Fourier order |
| `weekly_seasonality` | 'auto' | True/False/'auto' | Weekly seasonal component | True for daily data |
| `interval_width` | 0.80 | 0.50 - 0.99 | Width of uncertainty interval | 0.95 for conservative intervals |

### Decision Logic for Key Parameters

```python
def auto_configure_prophet(series, freq):
    """Auto-select Prophet hyperparameters based on data characteristics."""
    config = {}
    
    # Seasonality mode: multiplicative if variance increases with level
    cv = series.rolling(12).std() / series.rolling(12).mean()
    if cv.std() > 0.1:
        config['seasonality_mode'] = 'multiplicative'
    else:
        config['seasonality_mode'] = 'additive'
    
    # Changepoint flexibility: higher for volatile data
    volatility = series.pct_change().std()
    if volatility > 0.2:
        config['changepoint_prior_scale'] = 0.1
    elif volatility > 0.1:
        config['changepoint_prior_scale'] = 0.05
    else:
        config['changepoint_prior_scale'] = 0.01
    
    # Yearly seasonality
    if freq in ['MS', 'M', 'W'] and len(series) >= 24:
        config['yearly_seasonality'] = True
    else:
        config['yearly_seasonality'] = False
    
    return config
```

---

## Best Practices

1. **Use multiplicative seasonality for business metrics** — Revenue, orders, users typically scale with level.
2. **Add holidays for retail/e-commerce** — Black Friday, Christmas, etc. significantly impact forecasts.
3. **Set interval_width=0.95** for business reporting — wider intervals communicate uncertainty honestly.
4. **Check component plots** — `model.plot_components(forecast)` reveals what Prophet learned.
5. **Use `make_future_dataframe` with correct freq** — 'MS' for month-start, 'W' for weekly, 'D' for daily.

### Adding Custom Seasonality
```python
# Example: quarterly seasonality for data with fiscal quarter patterns
model.add_seasonality(name='quarterly', period=91.25, fourier_order=5)

# Example: custom holidays
holidays = pd.DataFrame({
    'holiday': 'black_friday',
    'ds': pd.to_datetime(['2024-11-29', '2025-11-28', '2026-11-27']),
    'lower_window': -1,  # 1 day before
    'upper_window': 1    # 1 day after
})
model = Prophet(holidays=holidays)
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Short data** | < 2 years for yearly seasonality | Set `yearly_seasonality=False` |
| **Flat forecast** | `changepoint_prior_scale` too low | Increase to 0.1 or 0.2 |
| **Overfitting** | Wild forecast oscillations | Decrease `changepoint_prior_scale` to 0.01 |
| **Wrong freq** | Misaligned future dates | Match freq to data: 'MS', 'W-MON', 'D' |
| **Negative forecasts** | Unconstrained prediction | Set `floor=0` in dataframe for non-negative metrics |
| **Timezone issues** | Prophet warns about timezones | Remove timezone info: `df['ds'] = df['ds'].dt.tz_localize(None)` |
| **Convergence warnings** | Stan backend issues | Try `model.fit(df, algorithm='Newton')` or increase `mcmc_samples` |

---

## Diagnostics

```python
from prophet.diagnostics import cross_validation, performance_metrics

# Cross-validation (built-in)
cv_results = cross_validation(
    model, 
    initial='730 days',   # training window
    period='180 days',    # forecast every 6 months
    horizon='365 days'    # forecast 1 year ahead
)

# Performance metrics
metrics = performance_metrics(cv_results)
print(f"MAPE: {metrics['mape'].mean():.2%}")
print(f"MAE: {metrics['mae'].mean():.0f}")
```
