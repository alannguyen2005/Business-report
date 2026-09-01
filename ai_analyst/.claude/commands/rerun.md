---
description: Re-run the last analysis pipeline from a specific phase or from the beginning
---

# /rerun — Re-run Analysis

Re-execute the most recent analysis pipeline, optionally from a specific phase.

## Usage
```
/rerun [phase]
```

## Behavior
1. Read `data/pipeline/` to find the most recent run (by modification time)
2. Load `pipeline_state.json` from that run
3. If `$1` is provided, resume from that phase (0-5)
4. If no argument, re-run from Phase 0 (full re-run)
5. Delegate to `pipeline-orchestrator` with the recovered `run_context`

## Examples
```
/rerun          # Full re-run of last analysis
/rerun 4        # Re-run from Phase 4 (Output) with existing analysis results
/rerun 2        # Re-run from Phase 2 (Analyze) — useful after data corrections
```

## Phase Reference
- 0: Blueprint
- 1: Understand (question-framer + data-profiler)
- 2: Analyze (descriptive + diagnostic)
- 3: Predict (ML pipeline)
- 4: Output (story + visuals)
- 5: Quality Gate
