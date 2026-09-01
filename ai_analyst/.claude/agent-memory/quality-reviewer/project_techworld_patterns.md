---
name: project-techworld-patterns
description: Known data patterns and QA learnings from the TechWorld dataset pipeline run (2026-05-29)
metadata:
  type: project
---

## TechWorld Dataset — QA Learnings

**Dataset:** `techworld_data_sample_cleaned.xlsx`, 2878 rows, Jan 2022–Mar 2026.

**Why:** First full pipeline run. All 11 KPIs verified clean.

### Key structural facts (verified 2026-05-29)
- Return_Flag=1 rows (92 orders) have **Sales=0 and negative Net_Profit** in the cleaned file. This means filtering on Return_Flag=0 is equivalent to filtering on Sales>0 for revenue, but return cost shows up in Net_Profit only.
- 2025 is structurally absent (0 rows). This is a data extract issue, not a business gap.
- 2024 contains Jan–Jun only (551 completed orders).
- 2026 contains only 14 rows (March partial, new SKU catalog).

### Return rate denominator
Return rate = 92 / 2878 = 3.197% — denominator is **all rows (including returns)**, not just completed orders.

### Known non-issues (confirmed PASS)
- Net Profit Margin is stable at exactly 33.07% (no margin erosion).
- Seasonal indices derived from 2022–2023 full years only — correct approach given partial years elsewhere.
- Trend slope uses 30 monthly points (Jan 2022–Jun 2024), excludes 2026-03 partial month — correct.
- Q2 2026 forecast of ~$152,022 is arithmetic sum of 3 point forecasts — verified to the cent.

### How to apply
- For future TechWorld runs: skip re-checking the returns Sales=0 pattern — it is confirmed structural.
- Watch for: any new data appended beyond 2026-03 that might change the trend baseline.
- The 2025 gap inflates forecast CIs substantially (22–24 months ahead); always flag this in reports.
