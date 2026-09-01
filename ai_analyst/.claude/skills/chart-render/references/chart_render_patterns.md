# Chart Render Patterns (Matplotlib)

## Global Setup — Apply Once Per Script

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

plt.rcParams.update({
    'figure.facecolor': '#FFFFFF',
    'axes.facecolor': '#FFFFFF',
    'savefig.facecolor': '#FFFFFF',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#E2E8F0',
    'axes.linewidth': 0.8,
    'axes.grid': False,
    'xtick.color': '#64748B',
    'ytick.color': '#64748B',
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.labelsize': 9,
    'axes.labelcolor': '#64748B',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Calibri', 'Arial', 'DejaVu Sans'],
    'figure.dpi': 150,
    'savefig.dpi': 150,
})

FIGSIZE_SPLIT = (8.0, 3.8)   # two-col panel: 4.93"×2.78" slot
FIGSIZE_FULL  = (11.0, 4.0)  # full-width panel

def save_chart(fig, path):
    fig.tight_layout(pad=1.2)
    fig.savefig(path, dpi=150, facecolor='white', edgecolor='none')
    plt.close(fig)
```

---

## Descriptive Patterns

### highlight_bar — rankings, category comparisons
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
colors = ['#2B4EFF' if v == max(values) else '#D1D5DB' for v in values]
bars = ax.barh(labels, values, color=colors, height=0.55, edgecolor='none')
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9, fontweight='bold', color='#080F1E')
ax.xaxis.set_visible(False)
ax.set_xlim(0, max(values) * 1.25)
ax.set_title("Insight headline here", fontsize=11, fontweight='bold',
             loc='left', color='#080F1E', pad=10)
save_chart(fig, path)
```

### vertical_bar — time periods, few categories
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
colors = ['#EF4444' if lbl in highlight_labels else '#D1D5DB' for lbl in labels]
ax.bar(range(len(labels)), values, color=colors, width=0.6, edgecolor='none')
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=9)
for i, v in enumerate(values):
    ax.text(i, v + max(values)*0.01, f'{v:.1f}%', ha='center',
            fontsize=9, fontweight='bold', color='#080F1E')
ax.yaxis.set_visible(False)
save_chart(fig, path)
```

### highlight_line — trends over time
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
# Comparison lines first (behind)
for label, y_vals in comparisons.items():
    ax.plot(x, y_vals, color='#D1D5DB', linewidth=1.5, zorder=2)
    ax.text(x[-1], y_vals[-1], f'  {label}', va='center', fontsize=9, color='#64748B')
# Highlight line
ax.plot(x, y_primary, color='#2B4EFF', linewidth=2.5, zorder=3)
ax.text(x[-1], y_primary[-1], f'  {primary_label}', va='center',
        fontsize=9, fontweight='bold', color='#2B4EFF')
# Event zone (optional)
ax.axvspan(crisis_start, crisis_end, alpha=0.08, color='#FF6B2B', zorder=1)
save_chart(fig, path)
```

### waterfall — contribution decomposition
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
running = 0
for i, (lbl, val) in enumerate(items):
    if i == 0 or i == len(items) - 1:
        color = '#080F1E'  # start/end totals
    else:
        color = '#34D399' if val > 0 else '#EF4444'
    ax.bar(i, abs(val), bottom=min(running, running+val),
           color=color, width=0.6, edgecolor='none')
    ax.text(i, running + val + offset, f'{val:+.0f}', ha='center',
            fontsize=9, fontweight='bold', color=color)
    running += val
ax.set_xticks(range(len(items)))
ax.set_xticklabels([lbl for lbl, _ in items], fontsize=9)
save_chart(fig, path)
```

### grouped_bar — compare 2 series across categories
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
x = np.arange(len(labels))
w = 0.35
ax.bar(x - w/2, series_a, width=w, color='#D1D5DB', edgecolor='none', label='Prior')
ax.bar(x + w/2, series_b, width=w, color='#2B4EFF', edgecolor='none', label='Current')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9)
# Direct labels (no legend)
for xi, (a, b) in zip(x, zip(series_a, series_b)):
    ax.text(xi - w/2, a + offset, f'{a:.0f}', ha='center', fontsize=8, color='#64748B')
    ax.text(xi + w/2, b + offset, f'{b:.0f}', ha='center', fontsize=8,
            fontweight='bold', color='#2B4EFF')
save_chart(fig, path)
```

### heatmap — segment × dimension matrix
```python
import seaborn as sns
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
cmap = sns.light_palette('#2B4EFF', as_cmap=True)
sns.heatmap(data_df, annot=True, fmt='.1f', cmap=cmap,
            linewidths=0.5, linecolor='#E2E8F0',
            annot_kws={'size': 9, 'weight': 'bold', 'color': '#080F1E'},
            cbar=False, ax=ax)
ax.tick_params(labelsize=9)
save_chart(fig, path)
```

---

## Diagnostic Patterns

### multi_line_highlight — compare entity vs peers
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
for label, y_vals in peers.items():
    ax.plot(x, y_vals, color='#D1D5DB', linewidth=1.2, zorder=2)
ax.plot(x, subject_vals, color='#EF4444', linewidth=2.5, zorder=3)
ax.text(x[-1], subject_vals[-1], f'  {subject_label}', va='center',
        fontsize=9, fontweight='bold', color='#EF4444')
save_chart(fig, path)
```

### slopegraph — change between 2 time points
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
for label, (val_a, val_b) in data.items():
    color = '#EF4444' if label == highlight_label else '#D1D5DB'
    lw = 2.5 if label == highlight_label else 1.2
    ax.plot([0, 1], [val_a, val_b], color=color, linewidth=lw, marker='o',
            markersize=5, markerfacecolor=color, markeredgewidth=0)
    ax.text(-0.05, val_a, f'{label}: {val_a:.1f}', ha='right', fontsize=9, color=color)
    ax.text(1.05, val_b, f'{val_b:.1f}', ha='left', fontsize=9, color=color)
ax.set_xlim(-0.3, 1.3)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Before', 'After'], fontsize=9)
save_chart(fig, path)
```

---

## Predictive Patterns

### forecast_line — time series forecast (Forecasting)
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
ax.plot(hist_x, hist_y, color='#2B4EFF', linewidth=2.5, label='Actual')
ax.plot(fore_x, fore_y, color='#2B4EFF', linewidth=2.0, linestyle='--', label='Forecast')
ax.fill_between(fore_x, lower_ci, upper_ci, alpha=0.12, color='#2B4EFF')
ax.axvline(x=split_x, color='#E2E8F0', linewidth=1.2, linestyle='--')
ax.text(split_x + 0.1, ax.get_ylim()[1] * 0.95, 'Forecast →',
        fontsize=8, color='#64748B')
save_chart(fig, path)
```

### scatter_regression — predicted vs actual (Regression)
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
ax.scatter(y_actual, y_pred, color='#2B4EFF', s=25, alpha=0.6, edgecolors='none')
# Perfect prediction line
lims = [min(min(y_actual), min(y_pred)), max(max(y_actual), max(y_pred))]
ax.plot(lims, lims, color='#D1D5DB', linewidth=1.2, linestyle='--')
ax.set_xlabel('Actual', fontsize=9)
ax.set_ylabel('Predicted', fontsize=9)
save_chart(fig, path)
```

### residual_plot — error distribution (Regression)
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
residuals = y_pred - y_actual
ax.scatter(y_pred, residuals, color='#2B4EFF', s=25, alpha=0.6, edgecolors='none')
ax.axhline(0, color='#EF4444', linewidth=1.2, linestyle='--')
ax.set_xlabel('Predicted', fontsize=9)
ax.set_ylabel('Residual', fontsize=9)
save_chart(fig, path)
```

### roc_curve — model performance (Classification)
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
ax.plot(fpr, tpr, color='#2B4EFF', linewidth=2.5)
ax.plot([0, 1], [0, 1], color='#D1D5DB', linewidth=1.2, linestyle='--')
ax.fill_between(fpr, tpr, alpha=0.08, color='#2B4EFF')
ax.text(0.55, 0.30, f'AUC = {auc:.3f}', fontsize=11,
        fontweight='bold', color='#2B4EFF')
ax.set_xlabel('False Positive Rate', fontsize=9)
ax.set_ylabel('True Positive Rate', fontsize=9)
save_chart(fig, path)
```

### feature_importance — top drivers (Classification + Regression)
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
sorted_idx = np.argsort(importances)
colors = ['#2B4EFF' if i >= len(importances) - 3 else '#D1D5DB'
          for i in range(len(importances))]
ax.barh([features[i] for i in sorted_idx],
        [importances[i] for i in sorted_idx],
        color=[colors[i] for i in sorted_idx], height=0.55, edgecolor='none')
for i, (idx, val) in enumerate(zip(sorted_idx, [importances[i] for i in sorted_idx])):
    ax.text(val + 0.002, i, f'{val:.1%}', va='center', fontsize=9,
            fontweight='bold', color='#080F1E')
ax.xaxis.set_visible(False)
save_chart(fig, path)
```

### model_comparison_bar — compare models (All prediction types)
```python
fig, ax = plt.subplots(figsize=FIGSIZE_SPLIT)
colors = ['#2B4EFF' if m == winner else '#D1D5DB' for m in model_names]
bars = ax.barh(model_names, metric_values, color=colors, height=0.55, edgecolor='none')
for bar, val in zip(bars, metric_values):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=9,
            fontweight='bold' if bar.get_facecolor() == '#2B4EFF' else 'normal',
            color='#080F1E')
ax.xaxis.set_visible(False)
save_chart(fig, path)
```

---

## Chart Type → Pattern Mapping

| Analysis type | Chart need | Pattern |
|--------------|-----------|---------|
| Descriptive | Trend over time | `highlight_line` |
| Descriptive | Segment ranking | `highlight_bar` |
| Descriptive | Period comparison | `vertical_bar` or `grouped_bar` |
| Descriptive | Part-to-whole | `highlight_bar` (horizontal, NOT pie) |
| Descriptive | Contribution | `waterfall` |
| Descriptive | Segment × dimension | `heatmap` |
| Diagnostic | Entity vs peers | `multi_line_highlight` |
| Diagnostic | Before/after change | `slopegraph` |
| Predictive: Forecasting | Future projection | `forecast_line` |
| Predictive: Regression | Fit quality | `scatter_regression` + `residual_plot` |
| Predictive: Regression | Error dist | `residual_plot` |
| Predictive: Classification | Model performance | `roc_curve` |
| Predictive: All | Feature drivers | `feature_importance` |
| Predictive: All | Model comparison | `model_comparison_bar` |

---

## D3.js HTML Renderer Rules (`scripts/render_html.py`)

These rules apply to the inline D3 charts rendered inside `report.html`.
**Do NOT modify `D3_RENDERER_JS` in `render_html.py` unless you are certain of the impact.**

### SVG sizing — always use this pattern in `mkSvg`
```javascript
function mkSvg(el, W, H) {
  return d3.select(el).append('svg')
    .attr('viewBox', '0 0 ' + W + ' ' + H)
    .attr('width', W).attr('height', H)          // required for correct aspect ratio
    .attr('preserveAspectRatio', 'xMinYMin meet') // top-left align, no vertical centering
    .style('width', '100%').style('height', 'auto');
}
```
**Why:** Without `width`/`height` attributes alongside `viewBox`, some browsers default SVG height
to 150px. `xMidYMid` causes vertical centering when the container is taller than the SVG,
creating visible blank space above/below the chart.

### Chart container — no fixed height
```python
# CORRECT
f'<div id="chart-{chart_id}" class="chart-svg"></div>'

# WRONG — fixed height causes misalignment when SVG intrinsic height differs
f'<div id="chart-{chart_id}" class="chart-svg" style="height:320px;"></div>'
```

### No gridlines — enforce in every renderer
```javascript
// WRONG — never add gridlines
var grd = d3.axisLeft(ys).ticks(5).tickSize(-w).tickFormat('');
g.append('g').call(grd).selectAll('line').attr('stroke', '#E2E8F0');

// CORRECT — remove domain line, no grid
g.select('.domain').remove();
```
Applies to: `renderHighlightLine`, `renderHighlightBar`, `renderGroupedBar`,
`renderWaterfall`, `renderForecastLine`.

### Patch scripts are DELETED — do not recreate
`scripts/_patch_render_html.py` and `scripts/_fix_d3_renderers.py` were one-time migration
scripts. They have been deleted. **Do not recreate them.** Edit `render_html.py` directly.
