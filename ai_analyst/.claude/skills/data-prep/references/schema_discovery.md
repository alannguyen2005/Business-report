# Schema Discovery Protocol

> Enriched from plugin: data-explorer agent

## Purpose
Automatically discover the schema and structure of an unknown dataset. Run before column classification to understand what we're working with.

## Discovery Steps

### 1. Shape Analysis
- Row count, column count
- Memory footprint
- Sparse vs dense (% fill rate)

### 2. Type Inference
For each column, test in order:
1. Boolean? (only 2 unique values: true/false, yes/no, 0/1)
2. Date? (parseable with pd.to_datetime, >80% success)
3. Numeric? (parseable with pd.to_numeric, >80% success)
4. Low-cardinality categorical? (<20 unique values)
5. High-cardinality categorical? (20-1000 unique values)
6. Free text? (>1000 unique values, avg length > 20 chars)
7. Identifier? (all unique, looks like ID/code)

### 3. Relationship Detection
- Primary key candidates: columns with 100% uniqueness
- Foreign key candidates: columns matching PK patterns of other tables
- Hierarchical dimensions: columns where one is a parent of another (e.g., category → subcategory)
- Date granularity: daily, weekly, monthly, quarterly

### 4. Pattern Recognition
- Sequential IDs (monotonically increasing integers)
- Currency values (contains $, €, commas in numbers)
- Percentage values (0-100 range or 0-1 range)
- Geographic data (country codes, state abbreviations, lat/long)
- Email/phone patterns

## Output
Enriches report_config.json with `schema_discovery` section:
```json
{
  "schema_discovery": {
    "pk_candidates": ["order_id"],
    "hierarchies": [{"parent": "category", "child": "subcategory"}],
    "granularity": "monthly",
    "special_columns": {"currency": ["revenue"], "pct": ["conversion_rate"]}
  }
}
```
