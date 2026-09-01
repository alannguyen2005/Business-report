# HTML Report Structure

## Component Hierarchy

```
report.html
├── <verdict-band> (≤100px, navy background)
│   ├── verdict_sentence (≤35 words)
│   └── 3x <kpi-badge> (label, value, delta, status)
├── <scqa-drawer> (collapsed default)
│   ├── Situation · Complication · Question · Answer
├── <section type="descriptive" color="#2554E7">
│   ├── <section-header> "1 · What happened?"
│   ├── <finding-box> (tagged: Pattern|Contrast|Implication|Ruling Out)
│   └── <chart> (full-width, single column)
├── <section type="diagnostic" color="#9333EA">
│   ├── <section-header> "2 · Why did it happen?"
│   ├── <finding-box> · <chart>
│   └── <verdict-panel>
│       ├── root_cause_1, root_cause_2 (≤30 words)
│       ├── implication (≤25 words, with number)
│       └── next_action (≤25 words, with timeline)
├── <section type="predictive" color="#10B981"> (if applicable)
│   ├── <section-header> "3 · What will happen?"
│   ├── <chart> (forecast with confidence band)
│   └── <model-summary>
└── <confidence-footer>
    ├── Score + Grade · Interpretation · Caveats
```

## Layout Rules
- Single column: max-width 1200px, centered
- Section gap: 48px · Card gap: 24px · Chart height: 400px
- Charts ALWAYS full-width (100% of container)
- NEVER use grid layouts for charts
- NEVER use insight-cards component

## Section Colors
| Section | Color |
|---------|-------|
| Descriptive | `#2554E7` (blue) |
| Diagnostic | `#9333EA` (purple) |
| Predictive | `#10B981` (green) |
