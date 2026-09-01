# Data Prep Rules (Quick Reference for Triage)

## Supported File Formats
- `.csv` — comma/semicolon/tab delimited
- `.xlsx` / `.xls` — Excel workbooks (first sheet by default)
- `.parquet` — Apache Parquet columnar format

## Filename Convention
```
{dataset_type}_{date_range}.{ext}
Examples:
  orders_2026-01-01_to_2026-03-31.csv
  churn_data_as_of_2026-04-15.xlsx
  revenue_monthly.parquet
```

## Quick Validation at Triage
Before showing blueprint, do a fast sanity check:
1. File exists and is readable
2. Has >0 rows (not empty)
3. Has >1 column (not just an index)
4. File size < 500MB (warn if larger)

## Domain Detection Signals
| Domain | Key Column Patterns |
|--------|-------------------|
| `saas_revenue` | mrr, arr, churn_rate, ltv, nrr |
| `ecommerce` | orders, revenue, aov, cart_value, conversion |
| `marketing` | cac, cpl, roas, impressions, spend |
| `finance` | net_profit, gross_margin, opex, ebitda |
| `ops_logistics` | fulfillment_time, shipping_cost, on_time |
| `product` | dau, mau, retention_rate, session_duration |
| `hr_people` | headcount, attrition_rate, tenure, salary |
| `generic` | fallback when no domain detected |

Detection rule: ≥2 column names match a domain → assign that domain.
