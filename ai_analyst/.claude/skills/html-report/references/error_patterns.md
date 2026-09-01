# HTML Report Error Patterns

## Layout Errors

### LE-1: Side-by-Side Charts
- **Wrong:** Two charts in a grid row (`chart-grid-2`)
- **Right:** Each chart full-width, stacked vertically

### LE-2: Insight Cards
- **Wrong:** Small card grid showing metrics (`insight-cards`)
- **Right:** KPIs in verdict band, findings in finding-boxes
- **Rule:** insight-cards is banned (CB-11)

### LE-3: SCQA as Summary
- **Wrong:** 4-quadrant "Executive Summary" always visible
- **Right:** Collapsible `<details>` drawer, closed by default

## Rendering Errors

### RE-1: White Background
- **Wrong:** #FFFFFF background
- **Right:** Page #F5F5F0, charts #F7F6F2

### RE-2: External File Dependencies
- **Wrong:** `<script src="chart.js">`
- **Right:** All CSS and JS inline
- **Exception:** Google Fonts and D3.js CDN allowed

### RE-3: Missing present_files()
- **Wrong:** Writing HTML without calling present_files()
- **Right:** Always call present_files() after writing report.html

## Interaction Errors

### IE-1: No Tooltip
- **Wrong:** Chart without hover interaction
- **Right:** setupTooltip() for every D3 chart

### IE-2: Non-Responsive
- **Wrong:** Fixed-width charts
- **Right:** viewBox-based SVG + resize listener
