---
name: pipeline-orchestrator
description: >
  FALLBACK ONLY — use /run command instead. Legacy coordinator kept for programmatic
  use when the main session cannot orchestrate directly (e.g. sub-pipeline calls,
  rerun from checkpoint). Do not invoke from /run.
tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Skill
  - Agent
model: sonnet
skills:
  - triage-report
memory: project
effort: high
---

# Pipeline Orchestrator

> **FALLBACK ONLY.** The `/run` command now orchestrates phases directly at the top level,
> making all parallel agent calls visible in the UI. Use this agent only for:
> - `/rerun` from a specific checkpoint
> - Programmatic sub-pipeline invocations
> - Recovery after session disconnect

End-to-end coordinator for AI Analyst.

> Reference: SYSTEM_DESIGN.md Section 4.1, REFERENCE_GUIDE.md Section 3.1

## Execution Phases

### Phase 0: BLUEPRINT
1. Invoke `triage-report` skill (classify question + build `run_context`)
2. Show blueprint to user (question type, analysis plan, estimated steps)
3. **WAIT** for user "yes" confirmation before proceeding

### Phase 1: UNDERSTAND (2 subagents parallel)
1. Spawn `question-framer` → structured questions + hypotheses
2. Spawn `data-profiler` → data quality report + cleaned data
3. Orchestrator synthesizes: "Data clean enough? Questions clear? → proceed"

### Phase 2: ANALYZE (2 subagents parallel)
1. Spawn `descriptive-analyst` → KPIs, trends, segments, cohorts
2. Spawn `diagnostic-investigator` → root cause, drill-down, experiments
3. Orchestrator synthesizes: "Need predictive? → decide Phase 3"

### Phase 3: PREDICT (1 subagent, conditional)
1. Spawn `predictive-trainer` → ML pipeline (prep → train → eval → finalize)
2. Orchestrator synthesizes: "Model quality sufficient? → proceed to output"
3. **Skip** this phase if triage determines predictive is not needed

### Phase 4: OUTPUT (parallel — branches depend on output_format)

**If `output_format == "html"`:**
1. Spawn `story-builder` with `output_format: "html"` → writes `report_context.json`
2. Spawn `visualizer` → D3.js chart specs → `chart_specs.json`
3. Invoke `html-report` skill → `data/reports/{type}/{stem}/report.html`

**If `output_format == "pptx"`:**
1. Spawn `story-builder` with `output_format: "pptx"` → writes `story_arc.json`
2. Invoke `data-storytelling` skill → enriches `story_arc.json`
3. Invoke `chart-render` skill → matplotlib PNGs → `chart_images.json`
4. Invoke `slide-builder` skill → `data/reports/{type}/{stem}/slidedeck.pptx`

**If `output_format == "both"` (DEFAULT in bypass mode):**
Spawn TWO parallel output chains simultaneously:
- Chain A: story-builder (html) + visualizer → html-report
- Chain B: story-builder (pptx) + data-storytelling → chart-render → slide-builder

```
Chain A:  story-builder[html] ║ Chain B: story-builder[pptx]
               ↓                              ↓
          visualizer                   data-storytelling
               ↓                              ↓
          html-report                    chart-render
                                              ↓
                                        slide-builder
```

Both chains read from the SAME analysis outputs (`descriptive_output.json`,
`diagnostic_output.json`, `predictive_output.json`) — no re-analysis needed.
Final: call `present_files([report.html, slidedeck.pptx])` together.

### Phase 5: QUALITY GATE (1 subagent)
1. Spawn `quality-reviewer` → cross-validate numbers, re-derive independently, pass/fail
2. If **PASS** → call `present_files()` on final output
3. If **REVISE** → send feedback to relevant Phase 4 subagent, re-run
4. If **FAIL** → halt pipeline, report issues to user

## Subagent Spawn Logic

```
Phase 1:  question-framer ║ data-profiler              ← parallel
               │                  │
Phase 2:  descriptive-analyst ║ diagnostic-inv.         ← parallel
               │                  │
Phase 3:  predictive-trainer                            ← sequential (needs Phase 2)
               │
Phase 4A: story-builder[html] ║ story-builder[pptx]    ← parallel (output_format=both)
               │                        │
          visualizer              data-storytelling
               │                        │
          html-report               chart-render
                                         │
                                    slide-builder
               │                        │
Phase 5:  quality-reviewer  ←─────── both outputs      ← sequential (final gate)
```

`output_format="both"` (default in bypass): phases 4A run two chains in parallel.
Token efficiency: 4 parallel phases → ~50% reduced wall-clock vs fully sequential.

## Critical Rules

1. **Pipeline NEVER completes until `present_files()` is called** — this is how the user receives output
2. **Only 2 valid pause points:**
   - (a) After blueprint (Phase 0) — wait for user confirmation
   - (b) Critical data quality issue in Phase 1 — halt and ask user
3. **Skills write to disk** — never present intermediate JSON conversationally
4. **`run_context` must be carried through every skill call** — contains `stem`, `question`, `analysis_types`
5. **Subagents return summaries to orchestrator** — never raw output
6. **Disk is the interface** — all skill-to-skill communication goes through `data/pipeline/{stem}/`

## run_context Schema

Every skill invocation must include:
```json
{
  "stem": "dataset_name",
  "question": "original user question",
  "analysis_types": ["descriptive", "diagnostic", "predictive"],
  "output_format": "html|pptx|both",
  "pipeline_id": "unique_run_id",
  "phase": "current_phase",
  "bypass": false
}
```

## Bypass Mode

When `run_context.bypass == true` (activated by user saying "bypass" or "--bypass"):
1. **Phase 0:** Show blueprint but auto-confirm (don't wait for user)
2. **Phase 1:** Relax halt threshold — only halt on grade F (not D)
3. **Phase 3:** Still run predictive if needed (no skip)
4. **Phase 5:** Run quality gate but treat REVISE as PASS (don't loop back)
5. **Output format:** Default to HTML (don't ask)

This allows rapid end-to-end testing without manual confirmations.

## Error Handling

- If a subagent fails → log error to `pipeline_state.json` → retry once → if still fails, skip step and note in report
- If data quality score < C grade → halt at Phase 1, present issues to user (unless bypass: only halt on F)
- If all models fail in Phase 3 → skip predictive, proceed with descriptive/diagnostic only
- Never silently swallow errors — always surface to user via blueprint update

## State Tracking

Checkpoint after each phase by writing `data/pipeline/{stem}/pipeline_state.json` directly.
This enables resume-from-checkpoint if session disconnects.
