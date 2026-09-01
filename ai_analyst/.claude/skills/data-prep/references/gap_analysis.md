# Gap Analysis Protocol

> Enriched from plugin: data-explorer agent

## Purpose
Identify gaps in the data that could affect analysis quality. Run after profiling, before validation.

## Gap Types

### Temporal Gaps
- Missing dates in time series (e.g., no data for February)
- Inconsistent granularity (some months have daily data, others weekly)
- Truncated periods (current month has only partial data)

**Detection:**
```python
date_range = pd.date_range(df[date_col].min(), df[date_col].max(), freq=detected_freq)
missing_dates = date_range.difference(df[date_col].unique())
```

### Coverage Gaps
- Segments with too few records for reliable analysis (<30 records)
- New segments appearing mid-series (recently added product category)
- Segments disappearing mid-series (discontinued products)

### Metric Gaps
- Metrics that should exist but don't (e.g., SaaS data without churn_rate)
- Metrics with suspicious patterns (all zeros, all same value, constant)
- Metrics with different scales than expected (revenue in cents vs dollars)

### Cross-Column Gaps
- Rows where dimension exists but metric is null
- Metric columns that are always null for specific segments
- Inconsistent nulls (column A is null IFF column B is null)

## Severity Classification

| Severity | Impact | Action |
|----------|--------|--------|
| **BLOCKER** | Analysis will be wrong | HALT — ask user |
| **WARNING** | Analysis less reliable | Proceed with caveat in report |
| **INFO** | Minor, no impact | Log for transparency |

## Common Blockers
- Primary metric >20% missing → BLOCKER
- Date column has >10% gaps → BLOCKER (for time series)
- <30 data points per segment → WARNING
- Current period has <50% of expected records → WARNING (partial period)

## Output
Add to report_config.json:
```json
{
  "gaps": [
    {"type": "temporal", "severity": "WARNING", "detail": "Missing data for 2026-02"},
    {"type": "coverage", "severity": "INFO", "detail": "Segment 'Enterprise' has only 25 records"}
  ]
}
```
