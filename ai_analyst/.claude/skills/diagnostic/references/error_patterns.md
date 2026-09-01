# Common Diagnostic Errors

## Error 1: Anchoring on First Hypothesis
- WRONG: "Revenue dropped → must be churn" (only investigated churn)
- RIGHT: Generate multiple hypotheses across categories before investigating any
- Fix: Write all hypotheses FIRST, then test them

## Error 2: Confirmation Bias
- WRONG: Only looking for evidence that supports the hypothesis
- RIGHT: Actively seek disconfirming evidence
- Fix: For each hypothesis, explicitly define what would REJECT it

## Error 3: Confusing Correlation with Causation
- WRONG: "Marketing spend increased in same month → marketing caused growth"
- RIGHT: Check mechanism, timing, and confounders
- Fix: Always include correlation_note in findings

## Error 4: Stopping Too Early
- WRONG: "Mid-Market churn increased" (Level 1 finding only)
- RIGHT: "Mid-Market churn increased 40% because Feature X deprecation affected 47 accounts that used it daily" (Level 3)
- Fix: Always drill to at least Level 2 for primary root cause

## Error 5: Unexplained Residual
- WRONG: Root causes explain 50% of the change, other 50% ignored
- RIGHT: Explicitly note unexplained portion and investigate further
- Fix: Impact attributions must sum to ~100%, with explicit "unexplained" category if needed

## Error 6: Hindsight Bias
- WRONG: "Obviously Feature X would cause churn" (only obvious after knowing the answer)
- RIGHT: Acknowledge that this was one of multiple plausible explanations
- Fix: Include the Ruling Out findings to show other paths were considered

## Error 7: Ecological Fallacy
- WRONG: "Enterprise customers are happy (overall NPS = 65)" 
- RIGHT: Check NPS by sub-segment (Enterprise product users vs Enterprise service users)
- Fix: Always check if aggregate hides sub-group variation
