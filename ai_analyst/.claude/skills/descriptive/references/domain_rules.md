# Domain Rules for Descriptive Analysis

## Domain-Specific KPI Selection

### SaaS / Revenue
| Priority | KPI | Formula | Direction |
|----------|-----|---------|-----------|
| 1 | MRR | Sum of monthly recurring revenue | up_is_good |
| 2 | Churn Rate | Churned MRR / Beginning MRR | down_is_good |
| 3 | NRR | (Beginning + Expansion - Contraction - Churn) / Beginning | up_is_good |

Waterfall: Baseline MRR → New Business → Expansion → Contraction → Churned → Net MRR

Segments: customer_segment (Enterprise/Mid-Market/SMB), plan_tier, cohort_tenure

### E-commerce
| Priority | KPI | Formula | Direction |
|----------|-----|---------|-----------|
| 1 | Revenue | Sum of order values | up_is_good |
| 2 | Orders | Count of transactions | up_is_good |
| 3 | AOV | Revenue / Orders | up_is_good |

Waterfall: Revenue = Orders × AOV (decompose changes)

Segments: category, channel, region, customer_type (new/returning)

### Marketing
| Priority | KPI | Formula | Direction |
|----------|-----|---------|-----------|
| 1 | CAC | Total spend / New customers | down_is_good |
| 2 | ROAS | Revenue / Ad spend | up_is_good |
| 3 | Conversion Rate | Conversions / Clicks | up_is_good |

Segments: channel, campaign, audience_type

### Generic (no domain detected)
Use the top 3 numeric columns by variance as KPIs. Primary = the column mentioned in the user's question.

## Grain Detection
| Date Patterns | Grain |
|--------------|-------|
| Consecutive days | daily |
| ~7 day gaps | weekly |
| ~30 day gaps | monthly |
| ~90 day gaps | quarterly |
| ~365 day gaps | yearly |
