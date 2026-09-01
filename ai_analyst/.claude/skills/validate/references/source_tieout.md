# Source Tie-Out Protocol

> Enriched from plugin: source-tieout agent

## Purpose
Cross-validate data against independent sources to verify accuracy. This is the most reliable validation layer because it uses external reference points.

## When to Apply
- When user provides reference totals ("revenue should be $5.2M")
- When multiple data sources exist for same metrics
- When knowledge/datasets has historical benchmarks

## Tie-Out Steps

### 1. Identify Reference Points
Sources of truth (in priority order):
1. User-provided totals in the question
2. Previous analysis results for same dataset
3. Knowledge base benchmarks (`knowledge/datasets/{id}/metrics.yaml`)
4. Industry benchmarks (if domain detected)

### 2. Compare Key Totals
For each reference point:
```
Discrepancy = abs(our_value - reference_value) / reference_value * 100

| Discrepancy | Status |
|-------------|--------|
| < 0.1%      | MATCH (rounding difference) |
| 0.1% - 1%   | CLOSE (minor discrepancy, note it) |
| 1% - 5%     | WARNING (investigate cause) |
| > 5%        | BLOCKER (data may be wrong) |
```

### 3. Investigate Discrepancies
Common causes:
- Different time zones (data cut at different times)
- Different filters (one source excludes refunds, other doesn't)
- Different aggregation levels (one is pre-tax, other post-tax)
- Data staleness (one source is more recent)
- Currency differences

### 4. Document Results
Add to validation_result.json:
```json
{
  "source_tieout": {
    "status": "MATCH|CLOSE|WARNING|BLOCKER",
    "comparisons": [
      {
        "metric": "total_revenue",
        "our_value": 5180000,
        "reference_value": 5200000,
        "discrepancy_pct": 0.38,
        "status": "CLOSE",
        "explanation": "Likely rounding in reference"
      }
    ]
  }
}
```
