# Common Descriptive Analysis Errors

## Error 1: Metric Label as Chart Title
- WRONG: "Revenue by Month"
- RIGHT: "Revenue declined 3 consecutive months for the first time since 2023"
- Fix: Always title with the INSIGHT, not the data description

## Error 2: Missing "Ruling Out"
- WRONG: Only present findings that support the narrative
- RIGHT: Include at least 1 hypothesis that the data rejected
- Why: Prevents confirmation bias and builds credibility

## Error 3: Simpson's Paradox Blindness
- WRONG: "Overall conversion rate improved from 4.2% to 4.5%"
- RIGHT: Check if improvement holds at segment level (it might not!)
- Fix: Always run segment-level check on aggregate findings

## Error 4: Partial Period Distortion
- WRONG: "May revenue is only $800K vs April's $2.1M" (but May has 15 days)
- RIGHT: Normalize to per-day rate or exclude partial periods
- Fix: Check if last period is complete before including

## Error 5: Survivorship Bias
- WRONG: Analyzing only active customers shows improving metrics
- RIGHT: Include churned/inactive customers in the analysis
- Fix: Check if data includes all records or only "surviving" ones

## Error 6: Correlation as Causation
- WRONG: "Marketing spend increased → revenue increased, therefore marketing caused growth"
- RIGHT: Note correlation, but flag that causation requires controlled experiment
- Fix: Always add correlation_note to strong relationships

## Error 7: Round Number Bias
- WRONG: "Revenue dropped ~20%"
- RIGHT: "Revenue dropped 18.2% ($460K)"
- Fix: Use precise numbers. Round only in headlines (but show precision in evidence).
