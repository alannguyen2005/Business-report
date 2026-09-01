# Structural Validation Rules

## Schema Checks
| Check | Pass Condition | Severity |
|-------|---------------|----------|
| No unnamed columns | All columns have names (no "Unnamed: 0") | WARNING |
| No all-null columns | Every column has ≥1 non-null value | BLOCKER |
| Consistent dtypes | No mixed types in same column (e.g., "123" and 123) | WARNING |
| Expected columns present | Domain-required columns exist (if domain detected) | WARNING |

## Primary Key Checks
| Check | Pass Condition | Severity |
|-------|---------------|----------|
| PK identified | At least 1 column with 100% unique values | INFO |
| PK no nulls | PK column has 0 null values | BLOCKER |
| PK uniqueness | No duplicate PK values | BLOCKER |

## Completeness Checks
| Check | Pass Condition | Severity |
|-------|---------------|----------|
| Primary metric | <20% null | BLOCKER if >20% |
| Other metrics | <5% null | WARNING if 5-20% |
| Dimensions | <1% null | WARNING |
| Date column | 0% null | BLOCKER |

## Value Domain Checks
| Data Type | Valid Range | Severity |
|-----------|-----------|----------|
| Rate/ratio | 0.0 to 1.0 (or 0 to 100 if percentage) | WARNING |
| Revenue/amount | > 0 (unless refunds expected) | WARNING |
| Count | ≥ 0, integer values | WARNING |
| Date | Not in future, not before 2000 | WARNING |
| Percentage | 0 to 100 | WARNING |
