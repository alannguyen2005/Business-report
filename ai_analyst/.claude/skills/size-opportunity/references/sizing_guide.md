# Opportunity Sizing Guide

## Core Formula

```
Impact = Users Affected × Improvement Rate × Value per Unit
```

All opportunity sizing follows this structure, regardless of domain.

## Impact Channels

| Channel | Description | Confidence |
|---------|-------------|------------|
| Direct revenue | Primary metric improvement → revenue gain | HIGH (if data-backed) |
| Cost avoidance | Resources saved (tickets, hours, infrastructure) | MEDIUM |
| Indirect (retention) | Better experience → lower churn → more LTV | LOW — requires extra assumptions |

## Sizing Templates

### Product Feature
```
Addressable = Total active users × will-use-feature% × will-upgrade%
Impact = Addressable × incremental ARPU × adoption ramp
```

### Retention / Churn Reduction
```
Addressable = Churn rate × Total users
Impact = Addressable × save rate% × LTV per user
```

### Efficiency / Cost Reduction
```
Addressable = Current opex × % improvable
Impact = Addressable × efficiency gain%
Payback = Implementation cost / Annual impact
```

### Geographic / Segment Expansion
```
Addressable = New market size × penetration% × ARPU
Impact = Addressable - overlap with existing segment
```

## Sensitivity Analysis Method

### Step 1: Rank assumptions
For each assumption, rate:
- **Confidence:** data-backed (HIGH) / estimated (MEDIUM) / guessed (LOW)
- **Leverage:** how much output changes if assumption varies ±25%

Focus on: LOW confidence × HIGH leverage assumptions.

### Step 2: One-variable tables
Vary assumption at 5 points: -50%, -25%, base, +25%, +50%.

### Step 3: Break-even
Find the threshold where the opportunity is no longer worth pursuing.
- "Worth pursuing if adoption rate > X%"
- "Breaks even at ARPU lift of $Y"

## Scenario Framework

| Scenario | Assumption Strategy | Typical Range |
|----------|-------------------|---------------|
| Pessimistic | All uncertain assumptions at low end | 25th percentile |
| Base case | Best-estimate values | 50th percentile |
| Optimistic | All uncertain assumptions at high end | 75th percentile |

Use ±25-50% variation, not ±5% — scenarios must be meaningfully different.

## Prioritization Score

```
Priority = (Annual Impact × Confidence Multiplier) / Effort
```

| Confidence Level | Multiplier | Criteria |
|-----------------|------------|----------|
| HIGH | 0.8 | Most variables data-backed, <2 assumptions |
| MEDIUM | 0.5 | Mix of data and estimates, 2-3 assumptions |
| LOW | 0.3 | Mostly assumptions, >3 key unknowns |

## Recommendation Rules

| Condition | Recommendation |
|-----------|---------------|
| HIGH confidence + positive base case | Pursue |
| MEDIUM confidence + positive base case | Investigate further → validate assumptions |
| LOW confidence + positive base case | Investigate further → need more data |
| Any confidence + negative base case | Pass |
| Pessimistic scenario still positive | Strong pursue — robust opportunity |
| Scenarios diverge widely | Investigate — result depends on assumptions |

## Validation Checks

1. Impact model is explicit (formula with named variables)
2. Every assumption is labeled (data-backed vs assumption)
3. Sensitivity covers riskiest assumptions (low confidence × high leverage)
4. Break-even is computed for at least one assumption
5. Scenarios are meaningfully different (±25-50%, not ±5%)
6. Units are consistent (same currency, same time period)
7. Impact passes order-of-magnitude check
8. Recommendation matches evidence quality
