# Diagnostic Domain Rules

## Domain-Specific Root Cause Patterns

### SaaS / Revenue
| Common Root Cause | Category | Detection |
|------------------|----------|----------|
| Feature deprecation/change | Product | Usage metrics dropped for affected feature users |
| Pricing change impact | Product | Plan migration patterns changed after pricing update |
| Competitor launch | External | Churn spike coincides with competitor event |
| Seasonal budget cycle | External | Pattern repeats YoY at same months |
| Customer mix shift | Mix Shift | Enterprise/SMB ratio changed significantly |
| Onboarding degradation | Product | Time-to-value increased for recent cohorts |

### E-commerce
| Common Root Cause | Category | Detection |
|------------------|----------|----------|
| Promotion dependency | Product | Revenue drops when promos end |
| Shipping cost change | Product | Cart abandonment rate increased |
| SEO/algorithm change | Technical | Organic traffic dropped on specific date |
| Market seasonality | External | Pattern matches known retail calendar |
| Category mix shift | Mix Shift | High-margin categories shrank vs low-margin grew |

### Marketing
| Common Root Cause | Category | Detection |
|------------------|----------|----------|
| Channel saturation | External | Diminishing returns on increased spend |
| Creative fatigue | Product | CTR declining while impressions stable |
| Attribution model change | Technical | Same spend, different reported ROAS |
| Audience overlap | Technical | Multiple campaigns targeting same users |

## Cross-Domain Investigation Order
1. **Time drill first** — When exactly did the change start?
2. **Segment drill** — Which segment drives most of the change?
3. **Funnel drill** — Where in the process does the breakdown occur?
4. **Correlation** — What other metrics moved at the same time?
