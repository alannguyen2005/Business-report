# Predictive Trainer Agent Memory

- [Ecommerce Q3 2026 Forecast Run](project_ecommerce_q3_forecast.md) — Holt-Winters (period=6) won with 8.3% holdout MAPE; Q3 2026 base case $155,869 (+55.6% YoY vs Q3 2025)
- [Model Selection Notes](feedback_model_selection.md) — With <16 training months, manual HW period=6 outperforms statsmodels ETS and period=12 variants; period=12 needs 24+ points
- [TechWorld Forecasts (3 runs)](project_techworld_forecast.md) — Q4 2023: ensemble $1.22M; Q2 2026 Run 2 (no 2025): MAPE 3.24%, Apr $48.8K/May $49.6K/Jun $53.6K; Q2 2026 Run 3 (synthetic 2025): MAPE 3.23%, Apr $51.2K/May $52.2K/Jun $56.4K; linear+seasonal wins all runs on this dataset
