# Simpson's Paradox Detection

> Enriched from plugin: descriptive-analytics agent

## What is Simpson's Paradox?
A trend that appears in aggregate data but reverses when data is split by segments.

Example:
- Overall conversion rate: Q1 4.2% → Q2 4.5% (improved!)
- Segment A: 5.0% → 4.8% (declined)
- Segment B: 3.0% → 2.8% (declined)
- Both segments declined, but overall improved because Segment A (higher rate) grew in proportion

## Why It Matters
If you report "conversion improved" without checking segments, your analysis is **misleading**. The business might celebrate a metric that is actually declining in every segment.

## Detection Algorithm

```python
def check_simpsons(df, metric_col, dimension_col, time_col):
    """Check if aggregate trend reverses at segment level."""

    # Overall trend
    overall = df.groupby(time_col)[metric_col].mean()
    overall_direction = "up" if overall.iloc[-1] > overall.iloc[0] else "down"

    # Segment trends
    reversals = []
    for segment in df[dimension_col].unique():
        seg_data = df[df[dimension_col] == segment]
        seg_trend = seg_data.groupby(time_col)[metric_col].mean()
        seg_direction = "up" if seg_trend.iloc[-1] > seg_trend.iloc[0] else "down"

        if seg_direction != overall_direction:
            reversals.append({
                "segment": segment,
                "segment_direction": seg_direction,
                "overall_direction": overall_direction
            })

    return {
        "paradox_detected": len(reversals) > len(df[dimension_col].unique()) / 2,
        "reversals": reversals
    }
```

## Severity
| Condition | Severity |
|-----------|----------|
| No reversals | none |
| Reversal in <50% of segments, non-primary metric | low |
| Reversal in >50% of segments, non-primary metric | medium |
| Reversal in primary metric, any number of segments | **high** (BLOCKER) |

## What to Do
1. **low:** Note in findings as "Caveat: aggregate trend driven by mix shift"
2. **medium:** Prominent warning in findings, show both views
3. **high:** Lead with segment-level story, explicitly flag the paradox

## Mandatory Check Points
- Run on ALL primary metric findings
- Run on at least the top 2 segmentation dimensions
- Cannot be skipped, even if data "looks clean"
