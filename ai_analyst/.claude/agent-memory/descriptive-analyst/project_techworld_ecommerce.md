---
name: techworld-ecommerce-patterns
description: Patterns from techworld_data_sample (TechWorld electronics e-commerce, Jan 2022 - Mar 2026, includes 12 synthetic 2025 months, monthly grain)
metadata:
  type: project
---

Dataset: techworld_data_sample — TechWorld e-commerce retailer (Electronics, Audio, Accessories, Wearables), Jan 2022 to Jun 2024 (real) + 12 synthetic 2025 months + Mar 2026 fragment. 4,016 total rows; 2,786 real completed non-returned orders ($1.82M real sales); 1,108 synthetic 2025 orders ($757K synthetic sales).

**Revenue baseline (real data only):** ~$60K/month avg, $1.82M total, 33.1% NP margin. Return rate 3.04%.
**With synthetic 2025:** $2.57M total across 43 months.

**Key structural facts:**
- Electronics = 87.7% of total sales — extreme single-category concentration; consistent 87.2-88.4% in every region (Simpson's paradox confirmed absent)
- Top 2 products (Laptop Pro X + Laptop Air) = 46.5% of total — high product-level concentration
- All four regions balanced within 1.6pp (~25% each) — no regional concentration risk
- Five suppliers equally balanced (~20% each) — no supplier risk
- Traffic sources evenly spread across 6 channels (14-17% each) — no channel dependency
- Trend is statistically flat on real data (R2=0.036, p=0.316 on 30 months) despite apparent -4.1% YoY drift

**Seasonality pattern (validated on 2022-2023 real data only):**
- October: index=118.1 (+18% above avg) — peak
- January: index=113.7, December: index=111.4 — also above average
- April: index=87.8 (-12% below avg) — trough
- May/July soft: 89.6, 91.8
- Swing: ~30pp peak-to-trough

**2022 vs 2023 dynamics (both real):**
- Electronics -5.8% YoY — drove aggregate decline
- Wearables +25.6%, Accessories +9.5% YoY — growing but too small (<12% combined)
- South region weakest (-9.4%), West only growing region (+2.5%)
- NP margin locked at 33.0-33.6% every month — no compression
- AOV eroded from $672 (2022) to $614 (2024 H1) — -8.6% over 2 years

**2025 synthetic data notes:**
- 2025 fully filled with synthetic rows (is_synthetic=1); $757K / 1,108 orders
- Synthetic 2025 shows +5.8% vs 2023 full year — treat as modeled, not observed
- All trend regressions and seasonal indices MUST use real data only (is_synthetic=0)
- Monthly series includes all 43 months for visualization; statistical tests use 30 real months

**Data quality notes for forecasting:**
- Real data: 2022-01 to 2024-06 (30 months)
- 2024 truncated at June (H1 only, 551 orders)
- 2026-03 has only 14 orders (partial month) — exclude from trend fitting
- Forecast models should be fit on real 30-month series; synthetic months available as out-of-sample reference

**Simpson's paradox check results:**
- 2022-to-2023 aggregate decline (-4.1%) consistent across all regions: no paradox
- Electronics 87.7% concentration consistent across all regions (87.2-88.4%): no paradox

**Why:** Updated in descriptive re-run 2026-05-29 after 2025 synthetic data was added to cleaned file.

**How to apply:** Always separate real vs synthetic in any trend/regression work. Use 30 real months for model fitting. Flag synthetic 2025 in all report commentary. Electronics concentration and AOV erosion are the two structural risks to call out in any executive summary.
