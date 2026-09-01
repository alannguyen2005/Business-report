---
name: Ecommerce domain dataset patterns
description: observed structure and caveats for ecommerce datasets in this pipeline — covers both ecommerce_orders and techworld_data
type: project
---

## techworld_data (active as of 2026-05-29)

20,429 order-level rows, Jan 2022 – Sep 2023 (21 months). Columns: Order_Date, Sales, Net_Profit, Region, Category, Product_Name, Quantity, Unit_Price, Marketing_Cost, Shipping_Cost, Traffic_Source, Supplier, Order_Status, Return_Flag, Review_Rating.

**Why notable:** This dataset has explicit cost columns (Marketing_Cost, Shipping_Cost) enabling profit margin decomposition. Return_Flag and Order_Status must be filtered to completed orders before revenue aggregation. No churn_flag — purely transactional.

**How to apply:** For diagnostic analysis, decompose revenue change into volume (Quantity), price (Unit_Price), and cost (Marketing_Cost + Shipping_Cost) vectors. Always filter Order_Status != cancelled before aggregation. Return_Flag is a key signal for realized vs. returned revenue.

**Aggregation note:** 20,429 rows / 21 months = ~973 orders/month. Monthly aggregation yields 21 data points — sufficient for Prophet and exponential smoothing. ARIMA is feasible but borderline; communicate wide prediction intervals.

**Forecasting pattern (first seen 2026-05-29):** When a Sales forecast question is asked, the filter must be Order_Status='Completed' AND Return_Flag=0 before monthly aggregation — Returned rows show Sales=0 and inflate the count while deflating average. Forecast horizon 3 months against 21 data points is at the lower reliability bound; always surface prediction intervals. Header KPIs for forecasting questions: Monthly Sales (primary), Net Profit Margin (quality check), Avg Order Value (volume vs ticket decomposition).

---

## ecommerce_orders (prior dataset)

500 rows, Jan 2025 – Jun 2026. Columns: order_date, customer_id, segment, region, product, revenue, quantity, discount_rate, churn_flag.

**Why notable:** churn_flag is non-standard for order tables — introduces customer-level risk dimension. Surface to diagnostic-investigator even when not explicitly asked.

**Date quality flag:** Dataset date_range ends 2026-06-30 but was loaded 2026-05-20 — last ~40 days likely placeholder/future-dated rows. Flag in confidence_notes.

**Aggregation note:** 500 rows / 18 months = ~27 orders/month. Monthly aggregation = 18 data points — sufficient for exponential smoothing/Prophet but ARIMA is borderline.
