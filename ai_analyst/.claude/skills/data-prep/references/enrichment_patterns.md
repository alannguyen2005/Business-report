# Data Enrichment Patterns

## Derived Columns
After cleaning, create useful derived columns:

### Time-Based Enrichment
| Derived Column | Formula | When |
|---------------|---------|------|
| `year` | `df[date_col].dt.year` | Always if date exists |
| `month` | `df[date_col].dt.month` | Always if date exists |
| `quarter` | `df[date_col].dt.quarter` | Always if date exists |
| `day_of_week` | `df[date_col].dt.dayofweek` | Daily grain data |
| `is_weekend` | `day_of_week >= 5` | Daily grain data |
| `is_month_end` | `df[date_col].dt.is_month_end` | Daily grain data |

### Metric Enrichment
| Derived Column | Formula | When |
|---------------|---------|------|
| `{metric}_pct_change` | `df[metric].pct_change()` | Time series metrics |
| `{metric}_rolling_avg_3` | `df[metric].rolling(3).mean()` | Smoothing trends |
| `{metric}_yoy` | Compare to same period prior year | ≥13 months of data |

### Segment Enrichment
| Derived Column | Formula | When |
|---------------|---------|------|
| `{metric}_rank` | `df.groupby(dim)[metric].rank()` | Segment ranking |
| `{metric}_pct_of_total` | `value / group_total * 100` | Contribution analysis |

## Rules
- Never overwrite original columns — always create new derived columns
- Name derived columns with clear suffixes: `_pct_change`, `_rolling_avg_3`, `_rank`
- Log all enrichment in report_config.json `enrichment_log`
