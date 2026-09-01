# Metric Spec Template

## Structure

```markdown
## Metric: [Name]

### Definition
**Plain English:** [One sentence a non-technical person can understand]
**Formula:** [Exact calculation]

### Components
| Component | Definition | Source |
|-----------|-----------|--------|
| **Numerator** | [What's being counted/summed] | [Table.column] |
| **Denominator** | [What's in the bottom (if ratio)] | [Table.column] |
| **Unit of analysis** | [What one row represents] | [per user, per session, per order] |

### Segmentation Dimensions
| Dimension | Values | Why |
|-----------|--------|-----|
| [e.g., Device type] | [mobile, desktop, tablet] | [Different UX → different conversion] |
| [e.g., Channel] | [organic, paid, referral] | [Different intent → different behavior] |

### Data Source
- **Primary table:** [schema.table_name]
- **Key columns:** [list]
- **Refresh cadence:** [real-time / hourly / daily / weekly]
- **Latency:** [how delayed is the data?]
- **Reference query:** [SQL that computes this metric]

### Thresholds
| Condition | Value | Action |
|-----------|-------|--------|
| **Healthy** | [e.g., >3.5%] | No action needed |
| **Watch** | [e.g., 2.5-3.5%] | Monitor weekly |
| **Investigate** | [e.g., <2.5%] | Root cause analysis within 48h |
| **Alert** | [e.g., <1.5%] | Escalate immediately |

### Known Limitations
- [Limitation 1]
- [Limitation 2]

### Related Metrics
- [Upstream: what drives this metric?]
- [Downstream: what does this metric drive?]
- [Alternative: other ways to measure the same concept]

### Driver Decomposition (Optional)
**Decomposition type:** [Multiplicative / Additive]

| Driver | Formula | Relationship | Data Source |
|--------|---------|-------------|-------------|
| [driver 1] | [formula] | [× / +] | [table.column] |

**Diagnostic rule:** If [parent metric] drops, check drivers in order:
1. [driver 1] — [why most likely]
2. [driver 2] — [what changes look like]

**Verification:** [parent] = [driver 1] × [driver 2] × [driver 3]
```

## Writing Rules

1. **Unambiguous** — two analysts reading the spec should write the same SQL
2. **Always specify denominator** — "conversion rate" needs context
3. **Always specify time window** — DAU daily ≠ DAU as 7-day average
4. **Always specify exclusions** — test accounts, bots, internal users
5. **Thresholds from data** — state the basis: "Based on 6-month average of 3.8% ± 0.4%"

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| No denominator | "Conversion rate" is meaningless | Specify: visitors? sessions? users? |
| Ambiguous name | Marketing's "conversion" ≠ Product's | Create separate specs |
| Gut-feel thresholds | False alarms or missed problems | Base on historical distribution |
| Missing limitations | Hidden caveats erode trust | Document every caveat |
| Ratio without decomposition | Can't diagnose changes | Understand numerator vs denominator independently |
