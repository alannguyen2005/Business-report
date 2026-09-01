# Iterative Drill-Down Protocol

> Enriched from plugin: root-cause-investigator agent

## Purpose
Systematically narrow down from a broad signal to a specific, actionable root cause. Each level adds a dimension of analysis.

## Drill-Down Levels

### Level 1: Broad Signal
**Question:** "Is this real? Does the data support the observation?"
**Action:** Verify the signal with a simple aggregate query
**Output:** Confirmed / Not confirmed / Mixed signals

### Level 2: Segment Decomposition
**Question:** "Which segment drives the most change?"
**Action:** Break down by each dimension column, compute per-segment delta
**Output:** Segment ranked by contribution to the change

```python
# For each dimension:
for dim in dimensions:
    segment_impact = df.groupby(dim)[metric].agg(['sum', 'mean'])
    # Compare current vs prior period
    # Rank by absolute contribution to total change
```

### Level 3: Time Localization
**Question:** "When exactly did this start?"
**Action:** Narrow the time window for the top-contributing segment
**Output:** Specific period when the change began

```python
# For top segment:
segment_data = df[df[dim] == top_segment]
# Plot metric over time, identify inflection point
# Check what happened in/around that period
```

### Level 3+: Sub-Segment / Behavioral
**Question:** "What specific behavior changed?"
**Action:** Further decompose by additional dimensions, funnel steps, or behavioral metrics
**Output:** Specific mechanism driving the change

## Drill-Down Decision Tree

```
Signal detected
├── Verify signal (Level 1)
│   ├── Not confirmed → REJECTED
│   └── Confirmed → continue
│       ├── Which segment? (Level 2)
│       │   ├── One segment dominates (>50%) → focus on it
│       │   └── Multiple segments → analyze top 2-3
│       │       ├── When did it start? (Level 3)
│       │       │   ├── Specific date found → check events/changes
│       │       │   └── Gradual → trend analysis
│       │       │       ├── What behavior changed? (Level 3+)
│       │       │       │   ├── Usage pattern → Product hypothesis
│       │       │       │   ├── Data anomaly → Technical hypothesis
│       │       │       │   └── Market-wide → External hypothesis
│       │       │       └── Max 3 iterations reached → report findings
```

## Rules
- **Max 3 iterations per hypothesis** — prevent rabbit holes
- **Document each level's finding** — even dead ends are informative
- **Always have a "so what" at each level** — don't just describe, interpret
- **If Level 2 shows even distribution** — likely systemic cause, not segment-specific
