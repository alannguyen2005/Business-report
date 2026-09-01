# Column Classifier

## Role Detection Rules

### Date Columns
- dtype is `datetime64`
- Column name contains: `date`, `time`, `timestamp`, `created_at`, `updated_at`, `period`, `month`, `year`, `quarter`
- String values are parseable as dates (>80% success rate)

### Metric Columns (numeric, continuous)
- dtype is `int64` or `float64`
- >20 unique values
- Column name contains: `revenue`, `amount`, `count`, `rate`, `score`, `total`, `sum`, `avg`, `cost`, `price`, `value`
- NOT an identifier (not unique per row)

### Dimension Columns (categorical)
- dtype is `object` or `category`
- <20 unique values (or <1% of row count)
- Column name contains: `segment`, `region`, `category`, `type`, `status`, `group`, `tier`, `channel`, `plan`

### Identifier Columns
- Unique per row (nunique == nrows)
- Column name contains: `id`, `key`, `code`, `uuid`, `identifier`
- These are used for joins but NOT for analysis

### Target Columns (for predictive)
- Binary: exactly 2 unique values (0/1, True/False, yes/no)
- Specified explicitly by user in question

## Domain-Specific Column Mapping

### SaaS/Revenue
| Column Pattern | Role | Domain KPI |
|---------------|------|-----------|
| `mrr`, `monthly_recurring_revenue` | metric | Primary KPI |
| `arr` | metric | Annual equivalent |
| `churn_rate`, `churn` | metric | Health indicator |
| `ltv`, `lifetime_value` | metric | Unit economics |
| `nrr`, `net_revenue_retention` | metric | Growth quality |
| `customer_segment`, `plan_tier` | dimension | Primary segment |

### E-commerce
| Column Pattern | Role | Domain KPI |
|---------------|------|-----------|
| `revenue`, `gmv` | metric | Primary KPI |
| `orders`, `order_count` | metric | Volume |
| `aov`, `average_order_value` | metric | Unit economics |
| `conversion_rate` | metric | Funnel efficiency |
| `category`, `product_type` | dimension | Product segment |

### Marketing
| Column Pattern | Role | Domain KPI |
|---------------|------|-----------|
| `spend`, `budget` | metric | Investment |
| `cac`, `cost_per_acquisition` | metric | Efficiency |
| `roas` | metric | Return |
| `channel`, `campaign` | dimension | Attribution |
