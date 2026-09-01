# Time Series Patterns

> Enriched from plugin: overtime-trend agent

## Pattern Detection

### Trend Patterns
| Pattern | Detection | Significance |
|---------|----------|-------------|
| **Uptrend** | 3+ consecutive positive changes | Growth phase |
| **Downtrend** | 3+ consecutive negative changes | Decline phase |
| **Plateau** | <2% change for 3+ periods | Stabilization |
| **Inflection** | Direction change after 3+ periods | Turning point |
| **Acceleration** | Increasing rate of change | Compounding growth/decline |
| **Deceleration** | Decreasing rate of change | Approaching plateau |

### Seasonal Patterns
| Pattern | Detection | Action |
|---------|----------|--------|
| **Monthly seasonality** | Consistent pattern within each year | Decompose and adjust |
| **Day-of-week effect** | Consistent weekday/weekend pattern | Note grain dependency |
| **Holiday spikes** | Spikes correlating with holidays | Exclude from trend analysis |
| **Quarter-end effect** | Spikes at quarter boundaries | Common in B2B/SaaS |

### Anomaly Patterns
| Pattern | Detection | Threshold |
|---------|----------|-----------|
| **Point anomaly** | Single period >2σ from rolling mean | Flag individual period |
| **Level shift** | Sustained change in mean | Before/after comparison |
| **Variance change** | Sustained change in volatility | F-test on rolling windows |

## Breakpoint Detection
Identify when trends change:
```python
# Simple method: rolling mean direction changes
rolling = df[metric].rolling(3).mean()
direction = np.sign(rolling.diff())
breakpoints = direction[direction != direction.shift()].index
```

## Reporting
For each time series metric, report:
1. Overall direction (up/down/flat)
2. Rate of change (accelerating/decelerating/constant)
3. Breakpoints (when did it change?)
4. Seasonality (present/absent, type)
5. Anomalies (which periods are unusual?)
