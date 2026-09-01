# Feedback Capture Protocol

> Enriched from plugin: ask-question skill

## Purpose
Capture user feedback from previous analyses to improve future runs. Applied during triage to avoid repeating mistakes.

## When to Check
At triage time, before building blueprint:
1. Check `knowledge/datasets/{dataset_type}/quirks.md` for known data issues
2. Check `knowledge/history/` for past analyses of same dataset
3. Check correction logs for past mistakes on similar questions

## Feedback Types

### Explicit Corrections
User says "that was wrong" or "no, the actual cause was X":
- Log via `log-correction` skill
- Store: question, wrong answer, correct answer, category

### Implicit Signals
- User asks to re-run with different parameters → previous approach was suboptimal
- User modifies the question after seeing blueprint → original classification was wrong
- User skips predictive phase → not always needed for this type of question

## Application at Triage
If past feedback exists for this dataset type:
- Adjust default question level
- Pre-populate known domain rules
- Warn about known data quirks
- Avoid previously rejected analysis approaches
