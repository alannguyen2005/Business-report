# Logical Validation Rules

## Aggregation Consistency
- Parts must sum to whole (±0.1% tolerance for rounding)
- Example: segment revenues should sum to total revenue
- Example: monthly values should sum to quarterly values
- If mismatch >1%: WARNING. If >5%: BLOCKER.

## Trend Continuity
- No sudden 10× jumps in metric values between consecutive periods
- Detect: `abs(pct_change) > 900%` → flag
- Exception: first period (no prior reference)
- Severity: WARNING (could be legitimate spike, needs investigation)

## Percentage Validation
- Columns identified as percentages must sum to ~100% within groups
- Tolerance: ±1%
- Example: market share by segment should sum to 100%

## Temporal Consistency
- No future dates (dates beyond today → WARNING)
- Chronological order (earlier dates before later dates)
- Consistent granularity (all daily, or all monthly — not mixed)
- No duplicate dates within same group

## Segment Exhaustiveness
- All segments in a dimension should account for 100% of the total metric
- Missing segments → WARNING
- "Other" category acceptable if explicitly present

## Cross-Column Consistency
- start_date ≤ end_date (if both exist)
- quantity × price ≈ revenue (if all three exist, ±1% tolerance)
- Derived metrics match raw calculation
