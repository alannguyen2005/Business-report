---
name: feedback_assembler_forecast_schema
description: assemble_story.py forecast_line handler crashes when predictive_output.forecast is a list (new schema) instead of a dict (old schema) — patch required before running assembler
metadata:
  type: feedback
---

The `helpers/story_assembler.py` `_map_chart_data` method for `forecast_line` and `model_comparison_bar` was written for a legacy schema that does not match the current `predictive_output.json` format.

**Why:** The current forecasting pipeline writes `predictive_output.json` with `forecast` as a list of monthly objects `[{month, point_forecast, ci_80_lower, ...}]` and `models_trained` as a list of model objects. The old assembler expected `forecast` as a dict with keys `x`, `historical`, `forecast`, `ci_low`, `ci_high`, `split_idx` and `model_comparison` as a dict with `models` and `scores` arrays.

**How to apply:** Before running `assemble_story.py` on a forecasting pipeline run, verify that `helpers/story_assembler.py` handles both schemas. The fix (applied 2026-05-29) adds isinstance checks:
- For `forecast_line`: if `forecast` is a list, extract months/values from the list objects and build the combined historical+forecast arrays from `monthly_series_used`.
- For `model_comparison_bar`: if `model_comparison` dict is absent, fall back to `models_trained` list extracting `model_type` and `metrics.mape_pct`.

See the patch at lines ~194-240 of `helpers/story_assembler.py`.
