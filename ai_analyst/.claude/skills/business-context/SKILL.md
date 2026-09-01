---
name: business-context
description: >
  Browse organization knowledge: glossary, products, metrics, objectives, teams.
  Interactive browser for business context stored in knowledge/organizations/.
  Trigger: /business, "browse business context", "business terms".
when_to_use: "/business", "browse business context", "business terms", "organization context", "glossary"
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(python3 *), Read, Write, Glob
model: sonnet
effort: medium
version: "1.0"
---

# Skill: Business Context Browser

## Purpose
Interactive browser for organization knowledge. Explore terms, products, metrics, objectives, and team structure from the knowledge brain.

**Reads:** `knowledge/organizations/{org}/` · `knowledge/setup-state.yaml` · `knowledge/datasets/{active}/metrics/`
**Writes:** (read-only — does not modify business context)

**Read references:** `references/context_guide.md`

---

## Steps

### Step 1: Load Organization Context
1. Read `knowledge/setup-state.yaml` to find active organization
2. If no org configured: "No organization context found. Run `/setup` Phase 3 to configure."
3. Read `knowledge/organizations/{org}/manifest.yaml` for org name

### Step 2: Execute Subcommand

**`/business` (no args) — Overview:**
Display summary of available business context:
- Glossary: N terms defined
- Products: N products cataloged
- Metrics: N metrics specified
- Objectives: N OKRs/goals tracked
- Teams: N teams mapped

**`/business glossary` — Browse Terms:**
- Load from `business/glossary/terms.yaml`
- Sort alphabetically, show first 20
- Display: Term | Definition | Category

**`/business products` — View Products:**
- Load from `business/products/index.yaml`
- Display: Product | Category | Status | Key Metrics

**`/business metrics` — Inspect Metrics:**
- Load from `business/metrics/index.yaml`
- Cross-reference with `knowledge/datasets/{active}/metrics/` if available
- Display: Metric | Type | Formula/Definition | Owner

**`/business objectives` — Review OKRs:**
- Load from `business/objectives/index.yaml`
- Display: Objective | Key Results | Status (On Track / At Risk / Behind)

**`/business teams` — Show Teams:**
- Load from `business/teams/index.yaml`
- Display: Team | Lead | Focus Area | Analysts

**`/business lookup {term}` — Search:**
- Search across all categories (case-insensitive substring)
- Rank: exact match > starts-with > contains
- Show top 10 results with category badge

### Step 3: Handle Empty Categories
For any empty category, show helpful message with file path:
- "No glossary terms defined. Add to `knowledge/organizations/{org}/business/glossary/terms.yaml`."

### Step 4: Display Rules
- Use tables for structured data (align columns)
- Limit initial display to 20 rows; offer pagination
- Always show file paths so users know where to edit

---

## Rules

**R-1:** This skill is read-only — never modify business context files.
**R-2:** Always show file paths so users can edit directly.
**R-3:** Limit display to 20 rows; offer "show all" if more.
**R-4:** If org not configured, guide to `/setup` — don't create partial context.
**R-5:** Cross-reference business metrics with dataset metrics when both exist.

---

## Subcommands
- `/business` — overview of all categories
- `/business glossary` — browse term definitions
- `/business products` — view product catalog
- `/business metrics` — inspect metric definitions
- `/business objectives` — review OKRs/goals
- `/business teams` — show team structure
- `/business lookup {term}` — search across all categories
