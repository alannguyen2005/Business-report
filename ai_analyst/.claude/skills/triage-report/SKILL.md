---
name: triage-report
description: >
  Entry point for all analyses. Classify user question, build run_context, detect domain,
  create execution blueprint, and WAIT for user confirmation before proceeding.
  Trigger: user uploads data file + asks analytical question.
when_to_use: "analyze", "run analysis", "what happened", "why did", "forecast", "predict", "upload data"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Glob, Grep
model: sonnet
effort: high
version: "1.0"
---

# Skill: Triage Report

## Purpose
Entry point for AI Analyst pipeline. Classify the user's question, build a run_context object, detect the data domain, construct an execution blueprint, and WAIT for user confirmation.

**Reads:** User question + data file path
**Writes:** `run_context` (in-memory, carried through pipeline) + `data/pipeline/{stem}/pipeline_state.json`

**Read references:** `references/question_taxonomy.md` · `references/data_prep_rules.md` · `references/feedback_capture.md` · `references/knowledge_bootstrap.md`

---

## Steps

### Step 1: Resolve Filename
```
Pattern: {dataset_type}_{YYYY-MM-DD_to_YYYY-MM-DD}.xlsx
Fallback: {dataset_type}_as_of_{today}.xlsx
Extract: dataset_type, range_slug, stem
```

Verify file exists in `data/raw/` or at the user-provided path. If file not found, ask user.

### Step 2: Build run_context
```json
{
  "project_root": "/absolute/path/to/ai_analyst",
  "dataset_type": "orders|churn|revenue|...",
  "stem": "orders_2026-04-01_to_2026-04-30",
  "question": "user's original question",
  "output_format": "html|pptx|ask",
  "execution_plan": "full|analysis_only|predict_only|describe_only",
  "confidence_grade": null,
  "skills_completed": [],
  "started_at": "ISO 8601"
}
```

### Step 3: Classify Question (L1–L4)
| Level | Pattern | Execution Plan |
|-------|---------|---------------|
| L1 | "What happened?" "Show KPIs" | descriptive only |
| L2 | "Why did X change?" "What caused Y?" | descriptive + diagnostic |
| L3 | "What will happen?" "Forecast/predict" | descriptive + diagnostic + predictive |
| L4 | "What should we do?" "Optimize" | full pipeline |

When ambiguous → default to L2 (most common business need).

### Step 4: Detect Output Format
| Signal | Format |
|--------|--------|
| "--both", "both", "html and pptx", "pptx and html" | `both` |
| "slide deck", "pptx", "presentation", "powerpoint" | `pptx` |
| "html report", "web report", "interactive", "report" | `html` |
| None detected | `ask` (present both options) |

`output_format: "both"` → pipeline produces HTML report AND PPTX slide deck in parallel (Phase 4 runs two output chains simultaneously).

### Step 4b: Detect Predictive Type (if L3/L4)
| Signal | Predictive Type |
|--------|----------------|
| Date column + numeric target + time-related question | `forecasting` |
| Numeric target + "what drives" / "factors" / "relationship" | `regression` |
| Binary/categorical target + "predict" / "classify" / "which" | `classification` |
| No clear signal | `null` (ask user) |

### Step 5: Show Blueprint and PAUSE
```
═══════════════════════════════════════════════════════
 ANALYSIS BLUEPRINT
═══════════════════════════════════════════════════════
 Question: "[precise restatement]"
 Analysis: [layers: descriptive + diagnostic + predictive]
 Output: [HTML Report / PPTX Slide Deck]
 Data: [N rows · date range · grain · domain]
 Confidence: [will be calculated after validation]

 Pipeline:
   1. Data Prep    → clean & profile
   2. Validate     → 4-layer DQ + confidence score
   3. Descriptive  → KPIs, trends, segments
   4. Diagnostic   → root cause, hypotheses
   5. Predictive   → [forecasting/regression/classification]
   6. Report       → [HTML/PPTX]

 Output paths:
   Cleaned   → data/cleaned/{type}/{stem}_cleaned.xlsx
   Pipeline  → data/pipeline/{stem}/*.json
   HTML      → data/reports/{type}/{stem}/report.html        [if html or both]
   PPTX      → data/reports/{type}/{stem}/slidedeck.pptx     [if pptx or both]
═══════════════════════════════════════════════════════
 Reply "yes" to start, or tell me what to adjust.
```

### Step 6: Wait for User Confirmation
- "yes" or "yes html" → proceed with HTML chain
- "yes pptx" → proceed with PPTX chain
- Other → revise blueprint based on feedback

### Bypass Mode

If user message contains "bypass" or "--bypass":
1. Auto-confirm blueprint (skip Step 6 wait)
2. If no format detected → default `output_format: "both"` (generate HTML + PPTX)
3. If `--both` also present → `output_format: "both"`
4. Set `bypass: true` in run_context — downstream skills will:
   - Relax halt threshold from D to F (only halt on grade F)
   - Skip audience adaptation prompts in story-builder
   - Quality gate runs but doesn't block on REVISE verdict
5. Print `[BYPASS MODE]` in blueprint banner

```json
// run_context additions in bypass mode
{
  "bypass": true,
  "output_format": "both",
  "halt_on_confidence": "F"
}
```

---

## Rules

**R-1:** ALWAYS show blueprint and WAIT. Never skip user confirmation (unless bypass mode).
**R-2:** run_context must be passed to EVERY subsequent skill call.
**R-3:** If file not found, ask user — never guess.
**R-4:** If question is ambiguous, default to L2.
**R-5:** Check `knowledge/datasets/{dataset_type}/` for existing domain knowledge (via knowledge_bootstrap reference).
**R-6:** If user previously gave feedback on a similar question, apply it (via feedback_capture reference).
**R-7:** This skill replaces the old `router` skill — all classification logic lives here now.
