# Hypothesis Categories

> Enriched from plugin: hypothesis agent

## The 4 Categories (MECE Framework)

### 1. Product
Changes originating from the product/service/offering itself.

**Signals:**
- Feature launch/deprecation coincides with metric change
- Usage patterns shifted (adoption, engagement, retention)
- Pricing or packaging changed
- Customer feedback mentions product issues

**Common Hypotheses:**
- "Feature X change drove user behavior change"
- "New pricing tier cannibalized existing plans"
- "Onboarding flow change affected activation"
- "Product quality issue caused satisfaction drop"

### 2. Technical
Data, system, or infrastructure issues that create apparent (not real) changes.

**Signals:**
- Sudden step-change (not gradual)
- Change exactly on a deployment date
- Affects only specific data sources
- Other related metrics unaffected

**Common Hypotheses:**
- "Tracking implementation changed → apparent metric shift"
- "Data pipeline delay → missing recent data"
- "Attribution model update → same spend, different ROAS"
- "System outage → temporary drop, not real decline"

**Critical:** Always check technical hypotheses early — they invalidate all other analysis if true.

### 3. External
Market, seasonal, competitive, or macroeconomic forces.

**Signals:**
- Pattern repeats YoY (seasonal)
- Affects entire industry (check benchmarks)
- Coincides with known external event
- Internal operations unchanged

**Common Hypotheses:**
- "Seasonal effect (same pattern last year)"
- "Competitor launched competing product"
- "Macroeconomic downturn affecting entire market"
- "Regulatory change impacted customer behavior"

### 4. Mix Shift
Composition changes where the aggregate trend is misleading.

**Signals:**
- Aggregate shows improvement, but all segments declining (Simpson's)
- Fastest-growing segment has different unit economics
- New segment entered with very different baseline
- Customer acquisition mix changed (channel, geography, tier)

**Common Hypotheses:**
- "Higher-value segment shrank while lower-value grew → aggregate declined"
- "New customer cohort has lower LTV → dragging average down"
- "Channel mix shift toward lower-converting channels"

## Hypothesis Generation Checklist
For any metric change, generate at least:
- [ ] 1 Product hypothesis (something we changed)
- [ ] 1 Technical hypothesis (could data be wrong?)
- [ ] 1 External hypothesis (something the market did)
- [ ] Consider Mix Shift if segments have different characteristics

Then select the top 3-5 most plausible for testing.
