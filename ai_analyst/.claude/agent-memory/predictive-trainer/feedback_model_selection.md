---
name: feedback-model-selection
description: Guidance on Holt-Winters period selection and model choice for monthly series of varying length
metadata:
  type: feedback
---

**Rule:** Match HW seasonal period to data length — period=6 for <24 months, period=12 for 24+ months.

**Why:** On the ecommerce dataset (14 training months), manual HW period=6 achieved 8.3% MAPE vs statsmodels ETS 24.9%. On TechWorld Q2 2026 run (27 training months), HW period=12 achieved 6.06% MAPE vs period=6 at 12.10% — a 2x improvement from using the correct period. The statsmodels optimizer can converge to degenerate parameters on short series.

**How to apply:**
- < 16 months: manual HW period=6 with grid search over alpha/beta/gamma
- 16–23 months: HW period=6 with statsmodels optimized=True (monitor for degenerate params)
- 24+ months: try HW period=12 and period=6, select by holdout MAPE
- At 30 months: linear trend + seasonal adjustment can outperform HW if trend is dominant (confirmed TechWorld 2026: 3.24% MAPE vs 6.06% for HW p=12)

**Also:** For flat-trend regimes with clear seasonality (like TechWorld), linear+seasonal deseasonalization is fast, interpretable, and competitive with Holt-Winters at 24+ points.
