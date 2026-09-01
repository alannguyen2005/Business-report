---
name: Pipeline inheritance conventions
description: question-framer must inherit level/format/predictive_type from triage-report run_context without re-classifying
type: feedback
---

Always inherit `level`, `output_format`, `predictive_type`, and `bypass` from the `run_context` written by triage-report to `pipeline_state.json`. Do not re-classify these fields.

**Why:** triage-report is the authoritative classifier. Re-classifying downstream creates divergence in the pipeline state and can cause downstream skills to receive contradictory signals.

**How to apply:** Read `data/pipeline/{stem}/pipeline_state.json` first. If `run_context.question_level` is set, copy it directly into `structured_questions.json` under both `level` and `inherited_from_triage`. Same for `output_format`, `predictive_type`, `bypass`, `pipeline_id`.
