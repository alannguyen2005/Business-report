---
name: project_techworld_diagnostic
description: Diagnostic findings for techworld_data_sample — TechWorld e-commerce electronics retailer, Jan 2022 to Mar 2026; 2025 now covered by synthetic data (is_synthetic=1)
metadata:
  type: project
---

## Confirmed Root Causes

**H1 CONFIRMED (real data):** Smartphone Alpha structural demand decline is the primary driver (~55% impact). Orders fell -23.3% FY2022→FY2023 and -60.9% in H1 2023→2024 across all 4 regions simultaneously. Unit price unchanged at $700 — purely volume contraction. Laptop Air (+7.5%) and Smartphone Z (+13%) grew in same period — product substitution active.

**H2 CONFIRMED (real data):** South region disproportionate contraction (-20.4% H1 2022→2024) vs North +26.1%. South had highest Smartphone Alpha concentration (31 orders H1 2022 → 6 H1 2024) with no premium replacement. North offset via Laptop Pro X growth ($18K → $25.5K H1). Impact attribution: ~20%.

**H3 PARTIALLY CONFIRMED (synthetic projection):** Laptop Pro X and Smartphone Z projected to absorb Alpha gap in 2025 (syn: LPX +$60K, SZ +$33K vs FY2023). 2026 Mar real data validates premium SKU refresh (iPhone 15 Pro, MacBook Pro 14). Confirm with real 2025 data.

**Why:** Product lifecycle decline of a single SKU (Smartphone Alpha) cascading across all geographies. South over-indexed on Alpha with no offset product.
**How to apply:** Smartphone Alpha is effectively exiting the portfolio by 2025. South is the risk region. North is self-correcting. LPX and Smartphone Z are the growth candidates.

## Rejected Hypotheses (Ruling Out)

- Pricing erosion: All unit prices identical 2022-2025. AOV decline is 100% mix effect ($33/order mix, ~$0 price effect).
- Category mix shift: Electronics held 87-89% share. Traffic channels stable within 2-3% YOY.
- Return rate: 2.5-4.7% range — within normal bounds, immaterial.
- Margin compression: NPM stable 33.0-33.1% across all real years.
- Marketing budget cuts: Marketing spend flat 2022-2023 (-0.3%), proportional to revenue in 2024.

## Data Caveats

- 2025 is SYNTHETIC (is_synthetic=1, 1,138 rows). All 2025 insights are projections, not confirmed findings.
- 2024 has H1 only (Jan-Jun, 578 rows). All YOY comparisons must use H1-aligned periods.
- October 2022 is an anomalous spike (z=2.69) inflating FY2022 baseline by ~$13,950.
- 2026 has only 14 orders (Mar 2026) with new premium SKUs — AOV $1,126 not comparable to prior years.

## Key Numbers

- FY2022 Sales: 746,010 | FY2023: 715,450 | H1 2024: 338,470 | FY2025 (syn): 757,050
- H1 trend: H1 2022: 363,680 | H1 2023: 341,230 (-6.2%) | H1 2024: 338,470 (-0.8%) | H1 2025 (syn): 351,770 (+3.9%)
- FY NPM: 33.1% (all real years, stable)
- Smartphone Alpha: 109,900 (2022) → 76,300 (2023) → 27,300 H1 2024 → 18,900 (syn 2025). Cumulative -82.8%.
- AOV: 672 (2022) → 644 (2023) → 614 (H1 2024) → 683 (syn 2025, LPX/SZ mix recovery)

Related: [[project_ecommerce_diagnostic]] [[project_retail_diagnostic]]
