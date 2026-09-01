# Cohort Analysis Patterns

> Enriched from plugin: cohort-analysis agent

## When to Run Cohort Analysis
- Data has both a date dimension and a customer/entity identifier
- Question involves retention, lifetime value, or behavior over time
- Domain is SaaS, subscription, or product analytics

## Cohort Construction

### Time-Based Cohorts
Group customers by signup/first-purchase month:
```python
df['cohort'] = df.groupby('customer_id')['date'].transform('min').dt.to_period('M')
```

### Activity Cohorts
Track activity in subsequent periods:
```python
df['period_number'] = ((df['date'].dt.to_period('M') - df['cohort']).apply(lambda x: x.n))
```

## Metrics to Compute Per Cohort

| Metric | Formula | Meaning |
|--------|---------|---------|
| Retention Rate | Active in period N / Active in period 0 | % still active |
| Revenue per Cohort | Sum revenue in period N for cohort | Monetization over time |
| LTV (cumulative) | Cumulative revenue per customer | Lifetime value curve |
| Churn Rate | 1 - Retention Rate | % lost per period |

## Patterns to Look For

### Healthy Patterns
- Retention curves flatten (stabilize after initial drop)
- Later cohorts retain better than earlier ones (product improving)
- LTV curves continue to grow (expansion revenue)

### Warning Patterns
- Retention curves keep declining without flattening
- Later cohorts retain worse (product-market fit eroding)
- Steeper early drop in recent cohorts (onboarding problem)

### Actionable Insights
- Period with biggest drop → focus onboarding/engagement there
- Best-performing cohort → what was different? (feature launch, pricing change)
- Worst-performing cohort → what went wrong? (bug, competition)

## Visualization
- Heatmap: cohorts (rows) × periods (columns), colored by retention %
- Line chart: retention curves overlaid by cohort
- Bar chart: cumulative LTV by cohort at fixed period (e.g., 6-month LTV)
