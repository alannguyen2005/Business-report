---
name: Sales Orders 2023-2026 Analysis Run
description: Completed L3 full pipeline run (descriptive + diagnostic + predictive + both outputs) on sales_orders_2023_2026.csv. Key findings: APAC GP margin decline, Q3 2025 collapse, H2 2026 forecast.
type: project
---

Completed full pipeline run on 2026-05-19 for sales_orders_2023_2026.csv.

Pipeline ID: sales_orders_2023_2026_20260519
Data: 6,601 orders, 2023-01-27 to 2026-06-30, zero nulls (grade A quality).
Question level: L3 (descriptive + diagnostic + predictive).
Output: HTML report + PPTX slide deck (both), Vietnamese language.

**Key findings:**
- Revenue 2025: $23.06M (+56.4% YoY). GP margin: 49.8%.
- APAC grew fastest (+74.5%) but GP margin dropped -3.9 pp (51.9% to 48.0%).
- Root causes: Hardware mix shift (36% of APAC revenue, 27.3% margin), Q3 2025 collapse (-50%, only 31 orders).
- Forecast H2 2026: $18.7M (Q3: $8.0M +106% YoY, Q4: $10.7M -8% YoY). Full 2026: $29.6M.
- Quality gate: PASS, 10/10 checks verified independently.

**Why:** User asked in Vietnamese, --bypass mode, wanted APAC root cause + 2-quarter forecast.
**How to apply:** If user asks to re-run or extend this analysis, resume from pipeline_state.json checkpoint. All intermediate JSON files exist in data/pipeline/sales_orders_2023_2026/.

Outputs:
- HTML: data/reports/descriptive/sales_orders_2023_2026/report.html
- PPTX: data/reports/descriptive/sales_orders_2023_2026/slidedeck.pptx
