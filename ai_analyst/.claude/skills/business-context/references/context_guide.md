# Business Context Guide

## Organization Knowledge Structure

```
knowledge/organizations/{org}/
├── manifest.yaml          # Org name, domain, config
├── business/
│   ├── glossary/
│   │   └── terms.yaml     # Business term definitions
│   ├── products/
│   │   └── index.yaml     # Product catalog
│   ├── metrics/
│   │   └── index.yaml     # Business-level metric definitions
│   ├── objectives/
│   │   └── index.yaml     # OKRs and goals
│   └── teams/
│       └── index.yaml     # Team structure
```

## Category Schemas

### Glossary (terms.yaml)
```yaml
terms:
  - term: "Active User"
    definition: "User with ≥1 session in last 30 days"
    category: "Engagement"
    aliases: ["AU", "active"]
    
  - term: "Churn"
    definition: "No activity for 60+ days"
    category: "Retention"
    related_metrics: ["churn_rate", "retention_d30"]
```

### Products (index.yaml)
```yaml
products:
  - name: "Core Platform"
    category: "SaaS"
    status: "Active"
    key_metrics: ["MAU", "Revenue", "NPS"]
    description: "Main product offering"
```

### Metrics (index.yaml)
```yaml
metrics:
  - name: "Conversion Rate"
    type: "Ratio"
    formula: "signups / visitors"
    owner: "Growth Team"
    category: "Acquisition"
```

### Objectives (index.yaml)
```yaml
objectives:
  - objective: "Increase activation rate"
    key_results:
      - "Activation +15% by Q2"
      - "Onboarding completion >80%"
    status: "On Track"
    owner: "Product Team"
    quarter: "Q2 2026"
```

### Teams (index.yaml)
```yaml
teams:
  - name: "Growth"
    lead: "Jane D."
    focus: "Acquisition & Activation"
    analysts: 2
    key_metrics: ["signup_rate", "activation_rate"]
```

## Search Algorithm

1. Exact match (case-insensitive) → highest rank
2. Starts-with match → medium rank
3. Contains match → lower rank
4. Search across: term names, product names, metric names, objective text, team names
5. Return top 10 results with category badge

## Display Conventions

| Element | Format |
|---------|--------|
| Tables | Aligned columns, max 20 rows |
| Empty category | "No {items} defined. Add to `{path}`." |
| File paths | Always shown for editability |
| Status indicators | On Track / At Risk / Behind |
| Pagination | "Showing 20 of {N}. Type 'show all' for complete list." |

## Cross-Referencing

When business metrics exist alongside dataset metrics:
- Show both side by side
- Flag misalignments (different formulas for same metric name)
- Business metrics = intended definition
- Dataset metrics = actual implementation
- Discrepancy = potential data quality issue
