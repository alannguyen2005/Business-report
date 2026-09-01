---
name: dataset-techworld-quirks
description: Known data quirks and quality patterns for techworld_data_sample.csv
metadata:
  type: project
---

Dataset: techworld_data_sample.csv (3015 rows x 20 columns, ecommerce/electronics domain)

**Comma-decimal columns:** Shipping_Cost (1444 rows), Net_Profit (8 rows), Marketing_Cost (4 rows) use comma as decimal separator (e.g. "5,6" means 5.6). Fix: `.str.replace(",", ".")` before casting to float.

**Duplicate Order_IDs:** 136 duplicates / 133 unique IDs appear more than once (269 rows total). Not exact row duplicates — same Order_ID with different field values. Likely data entry or upsert issue.

**Returned orders have Sales=0:** Sales column is set to 0 for all 101 Returned orders. This is intentional (revenue reversal), not a data error. One Completed order also has Sales=0 — that one is anomalous.

**Corrupt record Order_ID 20422:** Single row with Unit_Price=0, Sales=0, Net_Profit=0, missing Region/Category/Product_Name. Should be dropped during cleaning.

**Temporal gap:** 2025 is entirely absent. 2024 has only 600 rows (half the 2022/2023 volume of 1200 each). 15 rows from early 2026. Likely a partial/truncated extract — confirm with data source.

**Net_Profit, Marketing_Cost, Shipping_Cost stored as object dtype** (not numeric). Must cast during data-prep. The Net_Profit_Flag inconsistency (10 rows) is a downstream symptom of the comma-decimal issue.

**Confidence grade on first run:** C (74/100) — proceed_with_warnings. Primary blocker for upgrade to B is resolving comma-decimals and duplicate Order_IDs.

**Why:** Observed on first profiling run 2026-05-29.
**How to apply:** Skip re-detecting these issues on subsequent runs; go straight to data-prep fixes.
