# Data Triangulation Protocol

> Enriched from plugin: triangulation skill

## Purpose
Cross-validate findings by checking them from multiple angles. Prevents single-method bias.

## Triangulation Methods

### 1. Method Triangulation
Verify the same finding using different calculation methods:
- Calculate KPI using raw aggregation AND derived formula
- Compare top-down (total ÷ segments) vs bottom-up (sum segments)
- If results diverge >1% → investigate

### 2. Source Triangulation
Check the finding against independent data points:
- Compare metric trend with related metrics (revenue ↓ → should orders ↓ or AOV ↓?)
- Check if pattern is consistent across related dimensions
- If pattern appears in only one cut of data → lower confidence

### 3. Temporal Triangulation
Verify the finding is not an artifact of time window:
- Does the pattern hold if you extend the time window?
- Does it hold if you shift the window by 1 period?
- Is it a seasonal effect being misread as a trend?

### 4. Statistical Triangulation
Apply statistical tests to confirm:
- Is the change statistically significant? (p < 0.05)
- Is the effect size meaningful? (Cohen's d > 0.2)
- Does the confidence interval exclude zero?

## Confidence Boost
Each successful triangulation method increases finding confidence:
- 1 method confirmed → low confidence
- 2 methods confirmed → medium confidence
- 3+ methods confirmed → high confidence
- Any method contradicts → downgrade to low, flag for review

## Application
Run triangulation on:
- Every finding tagged as "Pattern" or "Contrast"
- The primary root cause in diagnostic
- Any metric change >20%
