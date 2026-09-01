# Slide Structure — AI Analyst PPTX

## Standard Deck Sequence (16–20 slides)

```
SECTION 0 — SETUP (3 slides, section_color=#2554E7)
  Slide 1  COVER                Dark navy, opening hook + 4 KPIs
  Slide 2  BACKGROUND           Business context + Analysis scope
  Slide 3  FRAMEWORK_3COL       3 layers: Descriptive / Diagnostic / Predictive

SECTION 1 — WHAT HAPPENED: Descriptive (2–3 slides, oval=#F97316)
  Slide 4  INSIGHT_CHART        Main KPI trend
  Slide 5  INSIGHT_CHART        Segment breakdown
  Slide 6  INSIGHT_CHART        Secondary dimension (optional)

SECTION 2 — WHY IT HAPPENED: Diagnostic (4–5 slides, section_color=#EF4444)
  Slide 7  FINDINGS_OVERVIEW    3 root causes summary — NO chart
  Slide 8  INSIGHT_CHART        Root Cause #1
  Slide 9  INSIGHT_CHART        Root Cause #2
  Slide 10 INSIGHT_CHART        Root Cause #3 (optional)
  Slide 11 FRAMEWORK_3COL       Hypotheses rejected

SECTION 3 — WHAT'S NEXT: Predictive (2–4 slides, section_color=#EF4444)
  Read analysis_type from question_frame.json → branch:

  FORECASTING:
    Slide 12  INSIGHT_CHART     Forecast + confidence band
    Slide 13  INSIGHT_CHART     Model comparison

  REGRESSION:
    Slide 12  INSIGHT_CHART     Predicted vs actual + model comparison
    Slide 13  INSIGHT_CHART     Feature importance (top drivers)

  CLASSIFICATION:
    Slide 12  INSIGHT_CHART     Model comparison (AUC/Precision)
    Slide 13  INSIGHT_CHART     Feature importance + at-risk list
    Slide 14  INSIGHT_CHART     ROC curve (optional)

  NO PREDICTIVE → skip Section 3

SECTION 4 — ACTION (3–4 slides, section_color=#42967A)
  Slide N    CONCLUSIONS_OVERVIEW  3 urgency-tiered takeouts — NO chart
  Slide N+1  STRATEGY_MAPS         Roadmap 3 phases
  Slide N+2  RECS_TABLE            Recommendation table
  Slide N+3  IMPACT_TWO_COL        Expected impact (optional)
```

---

## Layout → Breadcrumb + Colors

| Layout | Breadcrumb | Oval/badge |
|--------|-----------|-----------|
| BACKGROUND | "Context \| Business Context & Analysis Scope" | #2554E7 |
| FRAMEWORK_3COL (setup) | "Approach \| Analysis Framework" | #2554E7 |
| INSIGHT_CHART (descriptive) | "Context \| What's Happening" | #F97316 |
| FINDINGS_OVERVIEW | "Findings \| Overview" | #EF4444 |
| INSIGHT_CHART (diagnostic) | "Root Cause #N \| [Topic]" | #EF4444 |
| FRAMEWORK_3COL (ruled out) | "Approach \| Hypotheses Tested" | #EF4444 |
| INSIGHT_CHART (predictive) | "Predict \| [Topic]" | #EF4444 |
| CONCLUSIONS_OVERVIEW | "Conclusions \| Key Takeouts" | #2554E7 |
| STRATEGY_MAPS | "Action \| Strategy Maps" | #42967A |
| RECS_TABLE | "Action \| Recommendation" | #42967A |
| IMPACT_TWO_COL | "Action \| Expected Impact" | #42967A |

---

## Text Length Rules — Prevent Overflow

| Element | Max | Notes |
|---------|-----|-------|
| Slide headline | 15 words | Max 2 lines. Avoid `:` or `—`. |
| Supporting text per panel | 45 words | Max 5 lines. Avoid `:` or `—`. |
| Bullet in card | 45 words | Max 5 lines. Must start with a bold noun phrase prefix starting with an article (e.g. *The target*, *The leverage*). Avoid `:` or `—`. |
| Card title | 4 words | Max 1 line. |
| Footer implication | 10 words | Max 1 line. |
| Recommendation action | 20 words | Max 1 line. |
| Cover subtitle | 15 words | Max 2 lines. |

**Strictly respect word limits and lines to avoid text box overflows.**

---

## INSIGHT_CHART Content (Pyramid Principle)

```
headline (full width)           ← CONCLUSION
left_panel:
  supporting_text (≤4 sentences) ← EVIDENCE
  chart_title (1 line)
  chart_image                   ← PROOF
right_panel:
  supporting_text (≤4 sentences)
  chart_title (1 line)
  chart_image
```

Each INSIGHT_CHART = exactly 2 chart_ids (left + right).
If only 1 chart → left panel only, right panel = text callout.
