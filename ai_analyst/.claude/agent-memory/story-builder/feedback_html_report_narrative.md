---
name: feedback_html_report_narrative
description: Lessons from first TechWorld HTML report_context.json build — schema reconciliation and narrative patterns that worked
metadata:
  type: feedback
---

**HTML report_context.json embeds chart_specs inside the same file.** The report_context_schema.md says charts go in a separate chart_specs.json, but the task instructions explicitly ask for chart_specs as an array inside report_context.json. Follow the task instruction over the schema reference when they conflict.

**Why:** The render_html.py script reads chart data from whichever location the agent writes it. The task-level prompt is the authoritative spec.

**How to apply:** For HTML output, always write chart_specs[] as a top-level array inside report_context.json with full data arrays populated. Do not create a separate chart_specs.json file.

---

**Sections must use only ids: descriptive, diagnostic, predictive.** The schema enforces this — section id controls the accent color (blue/purple/green). Custom ids like "overview", "trends", "diagnosis", "forecast", "recommendations" are not valid.

**Why:** The render_html.py script has hardcoded color logic keyed to these three ids.

**How to apply:** Always map: what-happened → descriptive, why-it-happened → diagnostic, what-will-happen → predictive. Put recommendations inside the predictive section bridge_out or as a standalone recommendations object at top level.

---

**For flat/stationary revenue datasets, lead the verdict with the non-event.** When revenue is statistically flat (R² < 0.1, p > 0.2), the big answer should open with "Revenue is flat — the -X% drift is statistically insignificant" before naming the root cause. This prevents the report from overstating deterioration severity.

**Why:** TechWorld case confirmed — the headline -4.1% YoY decline was real but statistically insignificant noise. Framing it as structural decline misleads management into unnecessary alarm.

**How to apply:** Always check trend p-value and R². If p > 0.15 and R² < 0.1, open the verdict with the flat-line framing, then name the concentrated driver.

---

**Smartphone Alpha / product lifecycle root cause pattern for e-commerce datasets:** When a single product loses volume uniformly across all geographies with stable pricing, the root cause is product lifecycle/competitive displacement — not regional execution failure, channel weakness, or pricing. Confirm by: (1) checking if unit price is unchanged, (2) verifying the decline is geographically proportional, (3) checking if substitute products are growing in the same period.
