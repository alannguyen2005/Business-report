---
name: Ecommerce Q3 2026 Forecast Run
description: Q3 2026 monthly revenue forecast for ecommerce_orders dataset — winner model, key metrics, and forecast outcomes
type: project
---

Run completed 2026-05-20. Dataset: ecommerce_orders_2025-01-01_to_2026-06-30.

Training series: 17 months Jan 2025 – May 2026 (June 2026 excluded as partial).
Split: train Jan 2025 – Feb 2026 (14 months), holdout Mar–May 2026 (3 months).

Winner: holt_winters_manual (period=6, alpha=0.4, beta=0.2, gamma=0.1)
Holdout MAPE: 8.27% | MAE: $4,728 | Beats naive seasonal baseline by 41.5%

Q3 2026 forecast:
- Jul 2026: $54,680 [95% CI: $38,560–$70,800]
- Aug 2026: $62,349 [95% CI: $46,229–$78,469]
- Sep 2026: $38,840 [95% CI: $22,720–$54,960]
- Q3 base: $155,869 | Optimistic: $179,250 | Pessimistic: $124,695
- Q3 2025 actual: $100,191 → implied +55.6% YoY

**Why:** Holt-Winters period=6 (biannual) was the only feasible seasonal model given only 14 training months (period=12 needs 24+ points for initialization). It correctly captured the recurring March trough and April/May recovery pattern.

**How to apply:** For this dataset's next forecast refresh, reuse period=6 HW unless training length exceeds 24 months (then period=12 becomes viable). Wide CIs (~$32K/month at 95%) are expected — flag to stakeholders as directional.
