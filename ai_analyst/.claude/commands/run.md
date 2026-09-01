---
description: Start the AI Analyst pipeline with a data file and business question
---

# /run — Start Analysis Pipeline

**You are the orchestrator. Do NOT delegate to `pipeline-orchestrator`.
Orchestrate all phases yourself, calling agents in parallel batches directly.**

## Setup

1. Validate `$1` exists and is a supported format (CSV, XLSX, Parquet). If not, stop and tell user.
2. Set `stem` = filename without extension (e.g. `sales_2024.csv` → `sales_2024`)
3. Create pipeline directory: `data/pipeline/{stem}/`

---

## Phase 0 — BLUEPRINT

Invoke the `triage-report` skill with `file_path=$1`, `question=$2`, `stem`.

- **If `--bypass` flag present:** auto-confirm blueprint, proceed immediately
- **Otherwise:** show blueprint to user and wait for explicit confirmation

---

## Phase 1 — UNDERSTAND (PARALLEL)

Call **2 agents simultaneously in a single message**:

| Agent | Inputs | Output |
|-------|--------|--------|
| `question-framer` | `file_path`, `stem`, `question` | `data/pipeline/{stem}/structured_questions.json` |
| `data-profiler` | `file_path`, `stem` | `data/pipeline/{stem}/data_profile.json`, `validation_result.json` |

Wait for both to complete, then check data grade:
- Grade A/B/C → proceed
- Grade D/F + NOT bypass → **HALT**, show data quality issues to user
- Grade D/F + bypass → proceed with warnings

---

## Phase 1.5 — DATA PREP (CONDITIONAL, runs after Phase 1)

Read `data/pipeline/{stem}/validation_result.json` (written by data-profiler in Phase 1) and decide:

```
SKIP if ANY of these is true:
  (A) data/cleaned/{dataset_type}/{stem}_cleaned.xlsx already exists  → use cached cleaned file
  (B) validation grade = A  AND  zero structural/logical issues        → raw file is already clean, use as-is

RUN data-prep skill if:
  (C) cleaned file not found  AND  grade < A  OR  issues > 0
```

**Condition B detail — "raw is already clean":**
- Grade must be exactly **A** (score 90–100)
- `validation_result.issues` must be empty (zero warnings, zero blockers)
- If grade is A but has warnings → still run data-prep (warnings = fixable issues)
- Log: `"Raw file passed all quality checks (Grade A, 0 issues) — skipping data-prep"`
- Set `run_context.file_path` = original raw file path for downstream phases

**When data-prep runs (Condition C):**
```
data-prep skill reads:  data/raw/{filename}
                        data/pipeline/{stem}/data_profile.json   ← issues already known, skip re-profiling
data-prep skill writes: data/cleaned/{dataset_type}/{stem}_cleaned.xlsx
                        data/pipeline/{stem}/report_config.json
```
Set `run_context.file_path` = cleaned file path for all downstream phases.

**Why this matters:**
- Cleans data exactly once — Phase 2, 3 agents never touch `data/raw/` directly
- Prevents each agent from re-implementing the same fixes independently (comma-decimals, date parsing, future rows)
- Consistent numbers across all phases — eliminates filter/scope bugs like YoY miscalculation
- If raw is already clean, zero wasted tokens on unnecessary prep

---

## Phase 2 — ANALYZE (PARALLEL)

Call **2 agents simultaneously in a single message**:

| Agent | Inputs | Output |
|-------|--------|--------|
| `descriptive-analyst` | **cleaned file** + `data_profile.json` + `structured_questions.json` + `report_config.json` | `data/pipeline/{stem}/descriptive_output.json` |
| `diagnostic-investigator` | **cleaned file** + `data_profile.json` + `structured_questions.json` + `report_config.json` | `data/pipeline/{stem}/diagnostic_output.json` |

> **CRITICAL:** Both agents read from `data/cleaned/{dataset_type}/{stem}_cleaned.xlsx` — NOT from `data/raw/`.
> `report_config.json` tells agents the column roles, primary metric, date column, and grain — do not re-derive these.

Wait for both to complete.

---

## Phase 3 — PREDICT (CONDITIONAL)

Run **only if** `structured_questions.json` has `level: L3/L4` or `predictive_needed: true`:

| Agent | Inputs | Output |
|-------|--------|--------|
| `predictive-trainer` | **cleaned file** + `report_config.json` + all Phase 2 outputs | `data/pipeline/{stem}/predictive_output.json` |

Skip this phase if L1/L2 and no forecast requested.

---

## Phase 4 — OUTPUT (PARALLEL)

### Step 4a — Story building (PARALLEL, single message)

Call **2 agents simultaneously**:
- `story-builder` with `output_format: "html"` → writes `data/pipeline/{stem}/report_context.json`
- `story-builder` with `output_format: "pptx"` → writes `data/pipeline/{stem}/story_arc.json`

Both read from: `descriptive_output.json`, `diagnostic_output.json`, `predictive_output.json` (if exists).

### Step 4b — Rendering (PARALLEL, single message)

Call **2 tasks simultaneously** after 4a completes:

**Task 1 — HTML: fill report_context + chart specs** (if output_format includes html):
- `story-builder` fills `data/pipeline/{stem}/report_context.json` (schema: `.claude/skills/html-report/references/report_context_schema.md`)
- `chart-data` skill fills `data/pipeline/{stem}/chart_specs.json` with D3.js data arrays

**Task 2 — PPTX chart data embed + PNG render** (if output_format includes pptx):
- Invoke `data-storytelling` skill → reads all pipeline JSONs → embeds actual `data` arrays into `story_arc.json` `chart_requirements[]`
- Then invoke `chart-render` skill:
  ```
  PYTHONPATH="<project_root>/.." python scripts/render_charts_swd.py --stem {stem} --no-title
  ```
  → writes `data/pipeline/{stem}/chart_images/*.png` + `chart_images.json`

> **CRITICAL:** `chart-render` requires `story_arc.json` to have a `data` field on every `chart_requirements` entry.
> If `data` fields are missing → run `data-storytelling` first to embed them. Never skip this step.

### Step 4c — Final files (PARALLEL, single message)

**IMPORTANT: Use the deterministic scripts. NEVER write python-pptx or HTML generation code from scratch.**

Invoke **2 tasks simultaneously**:

**Task 1 — HTML report:**
```
PYTHONPATH="<project_root>/.." python scripts/render_html.py --stem {stem} --output data/reports/revenue/{stem}/report.html
```
Or invoke `html-report` skill which calls this script internally.
→ Output: `data/reports/revenue/{stem}/report.html`

**Task 2 — PPTX slide deck (2 sequential steps, run as one task):**
```
# Step A: Charts must already exist from Phase 4b — verify chart_images/ has PNGs
# Step B: Build PPTX from template
PYTHONPATH="<project_root>/.." python scripts/build_pptx_v3.py --stem {stem} --output data/reports/revenue/{stem}/slidedeck.pptx
```
Or invoke `slide-builder` skill which calls `build_pptx_v3.py` internally.
→ Output: `data/reports/revenue/{stem}/slidedeck.pptx`

> **Why scripts, not agents?** `build_pptx_v3.py` loads `templates/pptx_report/pptx_report_template.pptx` — the master template. A general agent writing python-pptx from scratch will produce a structurally different file that does not match the template design.

---

## Phase 5 — QUALITY GATE

Call `quality-reviewer` agent. It independently re-derives all numbers from the raw data.

| Result | Action |
|--------|--------|
| **PASS** | Call `present_files([report.html, slidedeck.pptx])` |
| **REVISE** | Fix issues in Phase 4 output, re-run Phase 4c only |
| **FAIL** | Halt pipeline, report issues to user |

---

## Execution Rules

1. **Each phase waits** for the previous phase to complete before starting
2. **Within a phase**, all independent agents are called in a **single message** (parallel)
3. **All data flows through disk** — `data/pipeline/{stem}/` — never through conversation
4. **Never skip Quality Gate** — not even in bypass mode
5. **`present_files()` only after Quality Gate PASS**

## Examples

```
/run data/raw/sales_2024.csv "Why did revenue drop in Q3?"
/run data/raw/customers.xlsx "Predict churn for next quarter"
/run data/raw/orders.csv "Phân tích xu hướng doanh thu theo khu vực" --bypass
```
