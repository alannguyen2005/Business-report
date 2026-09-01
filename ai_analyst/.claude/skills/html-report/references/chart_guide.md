# Chart Guide — HTML Report (D3.js)

## Chart Types

| Type | D3 Pattern | Use Case |
|------|-----------|----------|
| highlight_line | SVG path + circle markers | Time series with focus |
| highlight_bar | SVG rect (horizontal) | Category comparison |
| waterfall | SVG rect with connectors | Part-to-whole |
| histogram | SVG rect (vertical bins) | Distribution |
| scatter | SVG circle | Correlation |
| forecast_line | SVG path + fill area | Prediction with uncertainty |
| heatmap | SVG rect grid | Matrix visualization |

## Standard D3 Configuration
```javascript
const config = {
  width: container.node().getBoundingClientRect().width,
  height: 400,
  margin: {top: 60, right: 40, bottom: 50, left: 60},
  background: '#F7F6F2',
  spineColor: '#E2E8F0',
  highlightColor: '#2554E7',
  grayColor: '#D1D5DB',
  fontFamily: "'IBM Plex Sans', system-ui, sans-serif"
};
```

## Responsive Behavior
- Charts use viewBox for SVG scaling
- Window resize triggers chart re-render via responsive_resize.js
- Tooltip repositions on scroll/resize
- Min chart width: 320px
