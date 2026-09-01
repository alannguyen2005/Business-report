# Diagnostic Analysis Principles

## 1. Multiple Hypotheses, Multiple Categories
Never investigate only one theory. Minimum 3 hypotheses across ≥2 categories prevents tunnel vision. The most obvious hypothesis is often NOT the root cause.

## 2. Falsifiability
Every hypothesis must be testable with available data:
- "The market declined" → Need external benchmark or multi-company data
- "Segment X churned" → Can verify with internal data
- Prefer hypotheses you can definitively confirm OR reject

## 3. Ruling Out is as Valuable as Confirming
A rejected hypothesis tells the business what NOT to worry about:
- "Acquisition is fine" → Don't waste resources fixing top-of-funnel
- "Pricing isn't the issue" → Don't rush a pricing change
- Always include ≥1 Ruling Out in findings

## 4. Impact Attribution Must Sum to ~100%
If revenue dropped $460K:
- Root Cause 1 accounts for $280K (60%)
- Root Cause 2 accounts for $115K (25%)
- Unexplained: $65K (15%) — note this explicitly

Never leave >30% unexplained without flagging it.

## 5. Correlation ≠ Causation
For every confirmed root cause, check:
- **Mechanism:** Is there a logical path from cause → effect?
- **Timing:** Did cause precede effect?
- **Confounders:** Is there a third variable driving both?
- Always add `correlation_note` to the finding

## 6. Depth Over Breadth
Better to deeply investigate 3 hypotheses than superficially scan 10:
- Level 1: Does the data support this? (yes/no/maybe)
- Level 2: Which segment shows it most? (narrow the scope)
- Level 3: When exactly did it start? (pinpoint the trigger)

## 7. Confidence Calibration
| Level | Evidence Required | Presentation |
|-------|------------------|-------------|
| **high** | 3+ independent data points, 0 contradictions | Present as conclusion |
| **medium** | 2 data points, or 1 + mechanism makes sense | Present with qualifier |
| **low** | 1 data point only, or conflicting signals | Present as hypothesis only |
