---
name: data-storytelling
description: >
  Build Pyramid Principle story arc for PPTX slide deck branch. Transforms analytical
  outputs into consulting narrative with SCQA framework and story_arc.json.
  Trigger: after all analysis skills complete, output_format = "pptx".
when_to_use: "slide deck", "pptx", "presentation", "story arc", "consulting narrative"
disable-model-invocation: false
user-invocable: false
allowed-tools: Bash(python3 *), Read, Glob
model: sonnet
effort: high
version: "2.0"
---

# Skill: Data Storytelling

## Purpose
Transform raw analytical outputs into a consulting-style narrative arc for PPTX slide decks.
Builds SCQA framework, assigns findings to story positions, and produces `story_arc.json`.

**Reads:**
- `data/pipeline/{stem}/descriptive_output.json`
- `data/pipeline/{stem}/diagnostic_output.json`
- `data/pipeline/{stem}/predictive_output.json` (if exists)
- `data/pipeline/{stem}/question_frame.json` → `analysis_type` field

**Writes:** `data/pipeline/{stem}/story_arc.json`

**Read references:**
- `references/slide_structure.md` — full deck sequence (MUST READ before building)
- `references/storytelling_principles.md` — narrative rules

---

## Steps

### Step 1: Detect Analysis Type
Read `question_frame.json` → `analysis_type` field. Valid values:
- `forecasting` — Section 3: forecast_line + model_comparison_bar
- `regression` — Section 3: scatter_regression + feature_importance
- `classification` — Section 3: model_comparison_bar + feature_importance + roc_curve (optional)
- `descriptive_only` — skip Section 3

This determines how many slides Section 3 has. Read `references/slide_structure.md` for exact branching.

### Step 2: Extract Raw Material
From each analysis JSON extract:
- **descriptive_output.json**: header_kpis (exactly 3), trend findings, segment findings, SCQA draft
- **diagnostic_output.json**: root causes ranked 1–3, verdict sentence, ruled-out hypotheses
- **predictive_output.json** (if exists): forecast headline, model name, metric values, feature importances

### Step 3: Build SCQA
Construct the master SCQA governing the entire deck:

| Component | Rule | Maps to |
|-----------|------|---------|
| **S** Situation | Factual baseline, 1–2 sentences | BACKGROUND slide body |
| **C** Complication | Tension with specific magnitude ($, %, count) | First INSIGHT_CHART headline (Slide 4) |
| **Q** Question | User's original question restated | FRAMEWORK_3COL framing |
| **A** Answer | Direct resolution, no hedging | CONCLUSIONS_OVERVIEW |

### Step 4: Build Opening Hook
Cover headline — must create tension, ≤15 words, action verb, NOT the conclusion:
- GOOD: `"Customer churn accelerated 3× faster than new acquisition in 2025"`
- BAD: `"Q1 2026 Churn Analysis Results"`

### Step 5: Assign Findings to Slide Sequence
Follow the exact deck sequence from `references/slide_structure.md`:

**Section 0 — SETUP (3 slides)**
| Slide | Layout | Content |
|-------|--------|---------|
| 1 | COVER | Opening hook + 4 KPIs (period, orders, segments, suppliers) |
| 2 | BACKGROUND | Situation (left panel, include `key_question` field) + Analysis scope (right panel: 4 scope badges) |
| 3 | FRAMEWORK_3COL | 3 pillars: What Happened / Why It Happened / What's Next |

**Section 1 — WHAT HAPPENED: Descriptive (2–3 slides)**
| Slide | Layout | Content |
|-------|--------|---------|
| 4 | INSIGHT_CHART | Main KPI trend — left: trend chart, right: segment KPIs or second chart |
| 5 | INSIGHT_CHART | Segment breakdown — left: segment comparison, right: heatmap or second dim |
| 6 | INSIGHT_CHART | Secondary dimension (optional — only if strong finding warrants it) |

**Section 2 — WHY IT HAPPENED: Diagnostic (4–5 slides)**
| Slide | Layout | Content |
|-------|--------|---------|
| 7 | FINDINGS_OVERVIEW | 3 root causes as numbered cards — NO chart |
| 8 | INSIGHT_CHART | Root Cause #1 detail |
| 9 | INSIGHT_CHART | Root Cause #2 detail |
| 10 | INSIGHT_CHART | Root Cause #3 (optional) |
| 11 | FRAMEWORK_3COL | Hypotheses tested + ruled out |

**Section 3 — WHAT'S NEXT: Predictive (branch by analysis_type)**
- `forecasting`: 2 slides — forecast_line chart + model_comparison_bar
- `regression`: 2 slides — scatter_regression + feature_importance
- `classification`: 2–3 slides — model_comparison_bar + feature_importance + roc_curve (optional)
- `descriptive_only`: skip Section 3

**Section 4 — ACTION (3–4 slides)**
| Slide | Layout | Content |
|-------|--------|---------|
| N | CONCLUSIONS_OVERVIEW | 3 urgency-tiered takeouts — NO chart |
| N+1 | STRATEGY_MAPS | 3-phase roadmap |
| N+2 | RECS_TABLE | Recommendations table |
| N+3 | IMPACT_TWO_COL | Expected impact (optional) |

### Step 6: Write Slide Content
For each slide, write content obeying **hard limits** by layout. Exceeding these causes text overflow — truncate to fit.

#### Limits by Layout

**COVER**
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `opening_hook` (headline) | 15 | 100 | 1 |
| `cover_kpis[].value` | 6 | 35 | 1 |

**BACKGROUND**
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `headline` | 15 | 100 | 2 |
| `left_panel.supporting_text` | 80 | 500 | 10 |
| `left_panel.key_question` | 15 | 90 | 1 |
| `right_panel.supporting_text` | 60 | 400 | 8 |

**INSIGHT_CHART** ← most common layout — enforce strictly
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `headline` | 15 | 100 | 2 |
| `left_panel.supporting_text` | **45** | **300** | **5** |
| `right_panel.supporting_text` | **45** | **300** | **5** |
| `chart_title` (per panel) | 12 | 80 | 1 |

**FINDINGS_OVERVIEW / CONCLUSIONS_OVERVIEW**
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `headline` | 15 | 100 | 2 |
| `cards[].title` | 4 | 30 | 1 |
| `cards[].bullets[]` each string | **20** | **130** | 1–2 |
| `cards[].footer` | 10 | 60 | 1 |
(3 bullets combined per card ≈ 50 words / 350 chars / 5 lines)

**FRAMEWORK_3COL / STRATEGY_MAPS**
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `headline` | 15 | 100 | 2 |
| `cards[].title` | 4 | 30 | 1 |
| `cards[].bullets[]` each string | **20** | **130** | 1–2 |
| `cards[].footer` | 10 | 60 | 1 |
(3 bullets combined per card ≈ 50 words / 350 chars / 5 lines)

**RECS_TABLE**
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `rows[].action` | 20 | 130 | 1 |
| `rows[].expected_impact` | 10 | 60 | 1 |
| `rows[].success_metric` | 10 | 60 | 1 |

**IMPACT_TWO_COL**
| Field | Max words | Max chars | Max lines |
|-------|-----------|-----------|-----------|
| `headline` | 15 | 100 | 2 |
| `left_panel.title` | 5 | 35 | 1 |
| `left_panel.supporting_text` | 90 | 580 | 12 |
| `right_panel.title` | 5 | 35 | 1 |
| `right_panel.supporting_text` | 90 | 580 | 12 |

---

### Writing Style Reference — Learn from these exact patterns

**INSIGHT_CHART `supporting_text` — flowing prose (2–4 sentences):**
```
GOOD: "Revenue fell three consecutive quarters from the Q2 2025 peak of $136,809 down to $92,669
in Q4 2025, a -32% cumulative decline. Q1 2026 reversed course sharply, adding $38,691 (+41.8% QoQ)
to reach $131,360, the strongest single-quarter rebound in 17 months."

GOOD: "Platform surged +71.8% QoQ to $79,623, rising from 50% to 60.6% of Q1 revenue and driving 86%
of the total QoQ dollar gain. Analytics grew modestly at +36.9% to $39,413. Support declined -29.7%
to just $12,324, the only product line contracting in Q1."

BAD: "Platform: +71.8% QoQ — driving 86% of gain. Support: -29.7%"   ← short label:value format
BAD: "- Platform surged\n- Analytics grew\n- Support declined"        ← bullet list
```

**FINDINGS_OVERVIEW / CONCLUSIONS_OVERVIEW / STRATEGY_MAPS card bullets — `**The [concept]** prose` (no separator):**
```
GOOD (FINDINGS): "**The pattern** March fell -54% in both 2025 and 2026, confirming a structural seasonal trough rather than a one-off event."
GOOD (FINDINGS): "**The mechanism** B2B budget freeze at fiscal year boundary drives Enterprise and Mid-Market buyers to defer purchases."
GOOD (FINDINGS): "**The recovery signal** April recovered V-shaped both years, confirming demand is deferred, not lost."

GOOD (CONCLUSIONS): "**The pattern is structural** March's -54% decline is confirmed across two consecutive years, making it predictable and plannable."
GOOD (CONCLUSIONS): "**The action** Front-load Enterprise deals into Jan–Feb, where each order averages $2,569 in protected revenue."

GOOD (STRATEGY): "**The target** Front-load $20K+ committed Enterprise in Jan–Feb to buffer against March's structural -54% decline."
GOOD (STRATEGY): "**The leverage** Each Enterprise order averages $2,569, making early deal stacking the strongest revenue cushion available."
GOOD (STRATEGY): "**The alert** If Feb Enterprise pipeline falls below $18K, escalate immediately before the window closes."

BAD: "March fell -54% in both years — confirmed"         ← short fragment with —
BAD: "Target $20K+ committed Enterprise in Jan-Feb"      ← plain imperative, no bold prefix
BAD: "**The pattern** — March fell -54% confirmed"       ← uses — as separator after bold prefix
BAD: "**The mechanism:** B2B budget freeze..."            ← uses : as separator after bold prefix
```

**FRAMEWORK_3COL card bullets — same `**The [concept]** prose` pattern:**
```
GOOD: "**Overall performance** Q1 2026 revenue reached $131,360, up +41.8% QoQ."
GOOD: "**The March trough** March hit $25,002, a drop of -54% vs February, the sharpest single-month decline in the dataset."
GOOD: "**The hypothesis** Higher discount rates drove the March revenue drop."
GOOD: "**The evidence** Discount rate rose only +2.3pp, with a revenue impact of just -$682, representing 2.3% of the total $29,430 drop."
GOOD: "**The verdict** The higher discount rate reflects an SMB order mix shift, not price cuts. Negligible as a root cause."

BAD: "Q1 2026 revenue: $131,360 (+41.8% QoQ)"      ← label:value format
BAD: "March trough: $25,002 (-54% vs February)"     ← label:value format
BAD: "Discounts ruled out — only 2.3% impact"       ← short fragment with —
```

**IMPACT_TWO_COL `supporting_text` — section-header format with `:` inside the prose only:**
```
GOOD left panel:
"**The core mechanic:** Front-loading Enterprise pipeline in Jan–Feb is the highest-leverage near-term action available.\n\n**What each deal is worth:**\nEach Enterprise order in February = ~$2,569 in revenue\nShifting 5 deals from March to Jan/Feb recovers $10–13K of the March shortfall\nEquivalent to reducing the March drop from -54% toward -38%\n\n**Why January matters most:** January is the most efficient month to close Enterprise renewals, before the Q1/Q2 planning freeze sets in."

GOOD right panel:
"**Base case — $155.9K:** Assumes North holds above 35% revenue share and Platform QoQ growth stays positive.\n\n**Optimistic case — $179.3K (+15%):** Requires Mid-Market and North to maintain Q1 2026 pace through Q3.\n\n**Pessimistic case — $124.7K (-20%):** Models reversion to Q4 2025 growth rates.\n\n**Early warning triggers:**\nMonthly miss > 30% vs forecast\nNorth share below 25%\nPlatform QoQ turning negative"

BAD: flowing prose without section breaks       ← hard to scan
BAD: single paragraph with no structure        ← misses the information hierarchy
```

Note: In IMPACT_TWO_COL, `:` appears only inside section headers (e.g., `**The core mechanic:**`), never as a separator after a `**The X**` card bullet prefix.

---

**INSIGHT_CHART slides — Pyramid Principle (non-negotiable):**
1. `headline` = CONCLUSION — the full insight, action verb, ≤15 words, no colons/em-dashes.
2. `left_panel.supporting_text` = EVIDENCE — 2–4 flowing prose sentences. Numbers embedded naturally in the sentence. NEVER bullet list or label:value.
3. `left_panel.chart_id` + `chart_title` = PROOF — one-line data claim.
4. Same structure for `right_panel`.

**FINDINGS_OVERVIEW / CONCLUSIONS_OVERVIEW / STRATEGY_MAPS / FRAMEWORK_3COL cards:**
Each bullet: `"**The [concept]** [full prose sentence with embedded numbers]"` — bold phrase then prose immediately, NO separator character (no `:`, no `—`, no newline between them).

**RECS_TABLE rows:**
`priority` | `action` (≤20 words) | `owner` | `timeline` | `expected_impact` | `success_metric`

### Step 7: Build Chart Requirements — DRAFT ONLY & CALL ASSEMBLER (MANDATORY HYBRID ASSEMBLY)
For every chart referenced across all slides, add an entry to `chart_requirements[]` in `story_arc_draft.json`.

**CRITICAL:** You must NOT copy-paste raw numerical data arrays. Instead, define the chart structural requirements (`chart_id`, `chart_type`, `title`, `width`, `section`, `slide_order`) WITHOUT the `data` field. The Python script will dynamically inject the numbers!

After writing `story_arc_draft.json`, you MUST execute the story assembler command to automatically inject the data arrays and generate the final populated `story_arc.json` and `report_context.json`:
`python scripts/assemble_story.py --stem {stem}`

```json
{
  "chart_id": "quarterly_revenue_bar",
  "chart_type": "vertical_bar",
  "section": "descriptive",
  "slide_order": 4,
  "title": "Q4 drives ~50% of annual revenue — seasonality is structural",
  "width": "split"
}
```

---

### SWD Chart Type Selection — Decision Rule (MANDATORY)

**Core question: "Does the connection between data points mean something?"**
- YES (continuous time, trajectory is the story) → use LINE types
- NO (categorical, standalone values) → use BAR types

**Decision table — pick chart_type by what insight you're communicating:**

| Insight you want to show | chart_type | NEVER use |
|--------------------------|-----------|-----------|
| Trend / trajectory over time (story = HOW it changed) | `highlight_line` or `multi_line` | `vertical_bar` |
| Which category is biggest (story = MAGNITUDE, time order secondary) | `vertical_bar` | `highlight_line` |
| "Q4 is always the peak quarter" (seasonality = structure, not trend) | `vertical_bar` | — |
| Ranking comparison across categories | `horizontal_bar` | Line |
| Before → After direction and magnitude (2 time points, ≤5 entities) | `slopegraph` | Grouped bar |
| Contribution to a delta / bridge from A to B | `waterfall` | Stacked bar |
| Multiple series over time, one outperforms | `multi_line` (highlight=True on key series) | Grouped bar |
| Correlation between 2 continuous variables | `scatter_regression` | — |
| Pattern across 2 categorical dimensions | `heatmap` | Multiple lines |
| Historical + future uncertainty band | `forecast_line` | Bar |
| Model performance ranking | `model_comparison_bar` | Radar/Spider |
| Feature importance (what drives X most) | `feature_importance` | — |
| Classification model quality | `roc_curve` | — |
| Few categories, comparing 2 sub-groups | `grouped_bar` | — |

**CRITICAL mismatches to avoid:**
- Title says "trend" / "over time" → MUST use `highlight_line` or `multi_line`, not `vertical_bar`
- Title says "which is biggest" / "peaks at" → use `vertical_bar`, not `highlight_line`
- 2+ time points, 3-5 entities, story = directional change → `slopegraph`, not `grouped_bar`
- Never use pie, donut, 3D, radar, or dual-axis — these violate SWD principles

---

**chart_type options:** `vertical_bar` · `horizontal_bar` · `highlight_line` · `multi_line` ·
`waterfall` · `grouped_bar` · `forecast_line` · `feature_importance` · `scatter_regression` ·
`heatmap` · `slopegraph` · `model_comparison_bar` · `roc_curve`

**Data field schemas by chart_type:**

| chart_type | Required data keys |
|------------|-------------------|
| `vertical_bar` | `categories`, `values`, `highlight` (list of category names), `value_format` |
| `horizontal_bar` / `highlight_bar` | `categories`, `values`, `highlight`, `value_format` |
| `highlight_line` | `x` (labels), `y` (values), `highlight_range` ([start,end] idx), `highlight_points` (list[int]) |
| `multi_line` | `x` (labels), `series` (list of `{name, values, highlight:bool}`) |
| `waterfall` | `categories`, `values` (signed deltas), `start_value`, `value_format` |
| `grouped_bar` | `categories`, `groups` (list of `{name, values, highlight:bool}`) |
| `forecast_line` | `x` (labels), `historical`, `forecast`, `ci_low`, `ci_high`, `split_idx` |
| `feature_importance` | `features` (names), `importances` (scores), `top_n` |
| `scatter_regression` | `x`, `y`, `x_label`, `y_label`, `r_squared` |
| `heatmap` | `rows`, `cols`, `values` (2D list), `colormap` |
| `slopegraph` | `labels`, `before`, `after`, `before_label`, `after_label`, `highlight` |
| `model_comparison_bar` | `models`, `scores`, `metric_name`, `highlight` |
| `roc_curve` | `fpr`, `tpr`, `auc`, `model_name` |

Each INSIGHT_CHART slide has exactly 2 chart_ids (left + right). If only 1 chart, right panel = text callout (no chart_id).

### Step 8: Write story_arc.json

---

## Rules

**R-1:** INSIGHT_CHART headline = full insight statement (Pyramid Level 1). Never a label.
**R-2:** Text must fit within element bounds — use max limits strictly. Long text → truncate.
**R-3:** FINDINGS_OVERVIEW and CONCLUSIONS_OVERVIEW have exactly 3 cards and NO chart.
**R-4:** chart_title ≠ slide headline. chart_title = 1-line data claim. headline = narrative conclusion.
**R-5:** Ruling Out slide (FRAMEWORK_3COL in Section 2) must include ≥1 rejected hypothesis.
**R-6:** section_color drives badge, breadcrumb accent, and headline_accents color:
  - Context (Section 1): `#2554E7` blue, breadcrumb oval `#F97316` orange
  - Root Cause (Section 2): `#EF4444` red
  - Predict (Section 3): `#EF4444` red
  - Action (Section 4): `#42967A` teal, conclusions `#2554E7`
**R-7:** Every INSIGHT_CHART needs `headline_accents` — array of key phrases to bold/color in headline.
**R-8:** COVER KPIs: exactly 4 items from descriptive_output header_kpis + metadata.

---

## Output Schema

```json
{
  "report_type": "pptx",
  "analysis_type": "classification|regression|forecasting|descriptive_only",
  "generated_at": "ISO 8601",
  "opening_hook": "≤15 words tension headline",
  "scqa": {
    "situation": "1-2 sentences factual baseline",
    "complication": "tension with magnitude",
    "question": "original question restated",
    "answer": "direct resolution, no hedging"
  },
  "slides": [
    {
      "order": 1,
      "layout": "COVER|BACKGROUND|FRAMEWORK_3COL|INSIGHT_CHART|FINDINGS_OVERVIEW|CONCLUSIONS_OVERVIEW|STRATEGY_MAPS|RECS_TABLE|IMPACT_TWO_COL",
      "breadcrumb_section": "Context",
      "breadcrumb_topic": "What's Happening",
      "section_color": "#2554E7",
      "headline": "≤15 words insight",
      "headline_accents": ["key phrase to bold/color"],
      "left_panel": {
        "title": "IMPACT_TWO_COL only: panel section label (≤5 words, e.g. 'Why Front-Load Enterprise'). Omit for all other layouts.",
        "supporting_text": "INSIGHT_CHART: prose sentences (≤45 words, ≤300 chars, ≤5 lines). Bold numbers: **54%**. NEVER : or — as separators.\nIMPACT_TWO_COL: section-header format (≤90 words, ≤580 chars, ≤12 lines): '**The core mechanic:** prose\\n\\n**What each deal is worth:**\\nSub-bullet 1\\nSub-bullet 2'",
        "supporting_accents": ["bold phrases that appear in supporting_text"],
        "chart_id": "chart_key_or_null",
        "chart_title": "1-line data claim ≤12 words ≤80 chars",
        "key_question": "BACKGROUND slide only: restate the user's original question as a single crisp sentence (≤15 words). For all other layouts: omit this field or set null."
      },
      "right_panel": {
        "title": "IMPACT_TWO_COL only: panel section label (≤5 words, e.g. 'Q3 Scenario Range'). Omit for all other layouts.",
        "supporting_text": "Same rules as left_panel. INSIGHT_CHART: ≤45 words, ≤300 chars, ≤5 lines. IMPACT_TWO_COL: ≤90 words, ≤580 chars, ≤12 lines.",
        "supporting_accents": [],
        "chart_id": "chart_key_or_null",
        "chart_title": "1-line data claim"
      },
      "cards": [
        {
          "number": "01",
          "title": "≤4 words",
          "bullets": [
            "**The pattern** March fell -54% in both 2025 and 2026, confirming a structural seasonal trough rather than a one-off event.",
            "**The mechanism** B2B budget freeze at fiscal year boundary drives Enterprise and Mid-Market buyers to defer purchases.",
            "**The recovery signal** April recovered V-shaped both years, confirming demand is deferred, not lost."
          ],
          "footer": "≤10 words — bold prefix THEN prose, no : or — separator between them"
        }
      ],
      "rows": [
        {
          "priority": "P1-Now",
          "action": "≤20 words",
          "owner": "Team",
          "timeline": "30 days",
          "expected_impact": "short phrase",
          "success_metric": "short metric"
        }
      ],
      "cover_kpis": [
        {"label": "PERIOD", "value": "string"},
        {"label": "ORDERS", "value": "string"},
        {"label": "SEGMENTS", "value": "string"},
        {"label": "SUPPLIERS", "value": "string"}
      ],
      "speaker_notes": "Presenter talking points"
    }
  ],
  "chart_requirements": [
    {
      "chart_id": "string",
      "chart_type": "highlight_line|highlight_bar|waterfall|forecast_line|scatter_regression|feature_importance|model_comparison_bar|roc_curve|heatmap|slopegraph",
      "data_source": "descriptive_output|diagnostic_output|predictive_output",
      "slide_order": 4,
      "section": "descriptive|diagnostic|predictive"
    }
  ],
  "confidence": {"score": 82, "grade": "B"},
  "metadata": {
    "total_slides": 16,
    "analysis_type": "classification",
    "total_findings": 6
  }
}
```

**Notes on optional fields per layout:**
- COVER: use `cover_kpis`, skip `left_panel`/`right_panel`/`cards`/`rows`
- BACKGROUND, INSIGHT_CHART: use `left_panel` + `right_panel`, skip `cards`/`rows`
- FINDINGS_OVERVIEW, CONCLUSIONS_OVERVIEW, FRAMEWORK_3COL, STRATEGY_MAPS: use `cards`, skip `left_panel`/`right_panel`/`rows`
- RECS_TABLE: use `rows`, skip all other content fields
- IMPACT_TWO_COL: use `left_panel` + `right_panel` (text only, no charts). Each panel has a `title` field (bold label shown above the text, e.g., `"Why Front-Load Enterprise"`) and `supporting_text` structured as section headers: `"**The core mechanic:** prose\n\n**What each deal is worth:**\nSub-bullet 1\nSub-bullet 2\n\n**Why this matters:** prose"`. The `:` here is ONLY after section-header labels inside `supporting_text`, NOT as a card bullet separator.

**ABSOLUTE FORMAT RULES (apply to every layout, every field):**
- NEVER use `—` or `:` as separators between a bold phrase and its description
- NEVER write short one-liner bullets like `• Revenue grew 12%` — write prose with bold/italic markup
- ALWAYS bold key numbers: `**54%**`, `**$2.3M**`, `**Q4**`
- ALWAYS italic key concepts where meaningful: `_churn_`, `_enterprise segment_`, `_seasonality_`
- Supporting text = prose paragraphs, not a bulleted list
