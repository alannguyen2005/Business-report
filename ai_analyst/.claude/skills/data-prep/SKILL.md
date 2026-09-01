---
name: data-prep
description: >
  Clean raw data files: fix types, handle missing values, remove duplicates, detect outliers,
  classify column roles, detect domain, and produce report_config.json.
  Trigger: after triage-report approved, raw data file ready for cleaning.
when_to_use: "clean data", "prepare data", "data prep", "fix data", "after triage"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: high
version: "1.0"
---

# Skill: Data Prep

## Purpose
Transform raw data into clean, analysis-ready format. Profile columns, fix issues, classify roles, detect domain, and write configuration for downstream skills.

**Reads:** `data/raw/{filename}`
**Writes:** `data/cleaned/{type}/{stem}_cleaned.xlsx` + `data/pipeline/{stem}/report_config.json`

**Read references:** `references/cleaning_helpers.py` · `references/column_classifier.md` · `references/enrichment_patterns.md` · `references/schema_discovery.md` · `references/gap_analysis.md`

---

## Steps

### Step 1: Profile Raw Data
```python
import pandas as pd
df = pd.read_csv(file_path)  # or read_excel

profile = {
    "rows": len(df),
    "columns": len(df.columns),
    "dtypes": df.dtypes.to_dict(),
    "null_pcts": (df.isnull().sum() / len(df) * 100).to_dict(),
    "unique_counts": df.nunique().to_dict(),
    "memory_mb": df.memory_usage(deep=True).sum() / 1e6
}
```

### Step 2: Detect and Fix Issues
| Issue | Detection | Fix |
|-------|----------|-----|
| **Duplicate rows** | `df.duplicated()` | Drop exact dupes, flag fuzzy dupes |
| **Missing values** | `df.isnull().sum()` | Numeric: median. Categorical: mode. Date: interpolate. >50% null: drop column |
| **Wrong types** | Detect numeric stored as string | `pd.to_numeric()`, `pd.to_datetime()` |
| **Outliers** | IQR method: Q1-1.5*IQR to Q3+1.5*IQR | Flag but do NOT remove (analyst decides) |
| **Leading/trailing spaces** | `.str.strip()` | Clean all string columns |
| **Inconsistent categories** | Case variations, typos | Standardize (lowercase, map common typos) |

### Step 3: Classify Column Roles
| Role | Detection Criteria |
|------|-------------------|
| **date** | datetime dtype, or parseable date strings |
| **metric** | numeric, continuous, >20 unique values |
| **dimension** | categorical, <20 unique values |
| **identifier** | unique per row (potential PK) |
| **target** | binary flag for classification, or specified by user |

### Step 4: Detect Domain
Match column names against domain signals (see `references/column_classifier.md`).
Requires ≥2 column matches for assignment.

### Step 5: Write Outputs
1. Save cleaned data: `data/cleaned/{type}/{stem}_cleaned.xlsx`
2. Write report_config.json:
```json
{
  "stem": "...",
  "dataset_type": "...",
  "domain": "saas_revenue|ecommerce|...",
  "date_column": "order_date",
  "primary_metric": "revenue",
  "dimensions": ["segment", "region"],
  "grain": "monthly|weekly|daily",
  "date_range": {"start": "...", "end": "..."},
  "row_count": 50000,
  "column_roles": {"col_name": "metric|dimension|date|identifier"},
  "issues_found": [{"type": "...", "column": "...", "severity": "...", "action": "..."}],
  "cleaning_log": ["removed 42 duplicates", "imputed 3% missing in revenue"]
}
```

---

## Rules

**R-1:** HALT and ask user if primary_metric has >20% missing values.
**R-2:** Never delete data without logging the action.
**R-3:** Never modify `data/raw/` — raw data is SACRED (read-only).
**R-4:** Flag outliers but do NOT remove them automatically.
**R-5:** If data has <10 rows, warn: "Sample too small for reliable analysis."
