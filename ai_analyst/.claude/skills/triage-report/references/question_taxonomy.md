# Question Taxonomy

## Level Classification (L1–L4)

### L1 — Descriptive ("What happened?")
**Keywords:** show, summary, overview, KPIs, metrics, dashboard, report
**Examples:**
- "Show me last month's revenue numbers"
- "What are our current KPIs?"
- "Give me a summary of Q1 performance"

**Pipeline:** triage → data-prep → validate → descriptive → output

### L2 — Diagnostic ("Why did it happen?")
**Keywords:** why, cause, reason, explain, drop, increase, change, investigate
**Examples:**
- "Why did revenue drop in March?"
- "What caused churn to spike?"
- "Explain the decline in conversion rate"

**Pipeline:** triage → data-prep → validate → descriptive → diagnostic → output

### L3 — Predictive ("What will happen?")
**Keywords:** forecast, predict, estimate, project, next quarter, will, expect
**Examples:**
- "Forecast revenue for next quarter"
- "Predict which customers will churn"
- "What will our CAC be in 6 months?"

**Pipeline:** triage → data-prep → validate → descriptive → diagnostic → predictive → output

### L4 — Prescriptive ("What should we do?")
**Keywords:** recommend, optimize, improve, action, strategy, should, how to
**Examples:**
- "What should we do about rising churn?"
- "How can we optimize our pricing tiers?"
- "Recommend actions to hit Q2 targets"

**Pipeline:** full (all phases + experiment design + opportunity sizing)

## Ambiguity Resolution

When a question doesn't clearly map to one level:

| Signal | Resolution |
|--------|-----------|
| Contains both "what" and "why" | L2 |
| Contains "predict" + "why" | L3 (predictive subsumes diagnostic) |
| No clear signal | Default to L2 |
| User says "just show me" | L1 |
| User mentions "action" or "next steps" | L4 |

## Predictive Type Detection

| Signal in Question | Predictive Type |
|-------------------|----------------|
| "forecast", "next month/quarter", "trend" + date column | Forecasting |
| "what drives", "factors affecting" + numeric target | Regression |
| "predict churn", "classify", "which customers" + binary/categorical target | Classification |
