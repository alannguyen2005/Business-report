# Business Rules Template

## How to Use
Business rules are domain-specific. Load from `knowledge/datasets/{id}/metrics.yaml` if available, otherwise use these generic templates.

## Generic Business Rules
| Rule | Check | Severity |
|------|-------|----------|
| Revenue positive | `revenue > 0` (unless refund column exists) | WARNING |
| Counts non-negative | `count >= 0` for all count columns | BLOCKER |
| Rates bounded | `0 <= rate <= 1` or `0 <= pct <= 100` | WARNING |
| YoY change bounded | `abs(yoy_change) < 500%` | WARNING |
| No zero denominators | Columns used as divisors have no zeros | BLOCKER |

## Domain-Specific Rules

### SaaS
| Rule | Check | Alert |
|------|-------|-------|
| MRR positive | `mrr > 0` | BLOCKER |
| Churn rate bounded | `0 <= churn_rate <= 1` | WARNING |
| NRR realistic | `0.5 <= nrr <= 2.0` | WARNING |
| Expansion < Revenue | `expansion_mrr <= total_mrr` | WARNING |

### E-commerce
| Rule | Check | Alert |
|------|-------|-------|
| AOV positive | `aov > 0` | WARNING |
| Conversion bounded | `0 < conversion_rate < 1` | WARNING |
| Orders = integer | `orders == int(orders)` | WARNING |

### Marketing
| Rule | Check | Alert |
|------|-------|-------|
| Spend non-negative | `spend >= 0` | BLOCKER |
| ROAS non-negative | `roas >= 0` | WARNING |
| Impressions ≥ Clicks | `impressions >= clicks` | BLOCKER |
| Clicks ≥ Conversions | `clicks >= conversions` | BLOCKER |

## Custom Rule Loading
If `knowledge/datasets/{id}/metrics.yaml` exists, load custom rules:
```yaml
business_rules:
  - column: "revenue"
    check: "value > 0"
    severity: "BLOCKER"
    message: "Revenue must be positive"
  - column: "churn_rate"
    check: "0 <= value <= 0.5"
    severity: "WARNING"
    message: "Churn rate above 50% is unusual"
```
