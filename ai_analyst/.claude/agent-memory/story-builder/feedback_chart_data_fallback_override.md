---
name: feedback_chart_data_fallback_override
description: assemble_story.py dynamic mappings miss domain-specific chart IDs — manually override fallback data with real values extracted from analysis outputs
metadata:
  type: feedback
---

The `assemble_story.py` assembler has a generic chart ID matching library that only knows a limited set of pre-defined chart IDs. For domain-specific chart IDs (e.g., `category_bar_share`, `product_bar_top10`, `seasonality_chart`, `region_slopegraph`, etc.) it emits `[warning] Dynamic mapping missed` and provides placeholder fallback data (e.g., `["A","B","C"]` with values `[10,20,30]`).

**Why:** The assembler was built with a fixed set of chart IDs from prior runs. New analysis runs with new chart ID names will always miss unless the assembler's mapping table is extended.

**How to apply:** After running `assemble_story.py`, always check the output for `[warning] Dynamic mapping missed` entries. For each missed chart:
1. Read the relevant analysis output (`descriptive_output.json`, `diagnostic_output.json`, or `predictive_output.json`)
2. Extract the correct data arrays manually
3. Apply `Edit` tool patches directly to the final `story_arc.json` to replace placeholder data with real values

This is a one-time patch per run — the draft file remains unchanged and the assembler will again produce fallbacks on re-run. Consider adding the domain-specific chart IDs to the assembler's `_map_chart_data` method for future runs on the same domain.
