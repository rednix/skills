---
name: poly-tradebot
description: Automated news analysis pipeline that fetches CNBC world news, classifies articles by topic (geopolitics vs macroeconomics), and invokes specialized skills (geopolitics-expert or the_fed_agent) to produce structured trading analysis. Use when you need systematic news-to-trading-signal workflow for Iran war, US economy, Fed policy, and market impact assessment.
---

# Poly Tradebot

## Overview

Poly-tradebot automates the news-to-trading-analysis workflow: fetches CNBC world news, filters by relevant tags (us, iran, war, market, the fed), classifies each article as geopolitics or macroeconomics, and invokes the appropriate specialized skill (geopolitics-expert or the_fed_agent) to produce structured 5-section output following each skill's native format.

## Workflow

### 1. Fetch CNBC World News

```
poly-tradebot fetch
```

Fetches articles from `https://www.cnbc.com/world/?region=world` using `web_fetch` tool. Extracts at least 3 articles matching tags: `us`, `iran`, `war`, `market`, `the fed`.

**Article Selection Criteria:**
- Headline or content contains at least one tag keyword
- Published within last 24-48 hours (freshness)
- Substantive content (not brief mentions)

### 2. Classify Article Topic

For each fetched article, classify as:

| Topic | Classification Triggers | Skill to Invoke |
|-------|------------------------|-----------------|
| **Geopolitics** | Iran, war, military, conflict, sanctions, regime, IRGC, drone, missile, Strait of Hormuz, UAE, Middle East tensions | `geopolitics-expert` |
| **Macroeconomics** | Fed, Treasury yields, interest rates, inflation, central bank, CPI, employment, GDP, monetary policy, oil price (economic impact) | `the_fed_agent` |

**Note:** `the_fed_agent` skill may not be available in all skill lists. If unavailable, adapt the 5-section format using direct macro analysis (see Section 4).

### 3. Invoke Specialized Skill

**For Geopolitics Articles:**
```
geopolitics-expert <article_url>
```

Produces 5-section output:
1. Conclusion
2. Economic/Commodity Impact
3. Commodity Trading Odds
4. War Duration Categorization
5. Termination Scenarios

**For Macroeconomics Articles:**
```
the_fed_agent <article_url>
```

Produces 5-section output (same structure, adapted for monetary policy):
1. Conclusion
2. Economic/Commodity Impact
3. Commodity Trading Odds
4. War Duration Categorization (inflation persistence / policy uncertainty)
5. Termination Scenarios (policy path scenarios)

### 4. Fallback: Direct Macro Analysis (if the_fed_agent unavailable)

If `the_fed_agent` skill is not in the available skills list, use this adapted 5-section format:

```markdown
## 1. Conclusion
[Central bank decision summary + policy stance]

## 2. Economic/Commodity Impact
| Factor | Current Status | Policy Implication |
|--------|---------------|-------------------|
| [rate decision] | [value] | [implication] |
| [inflation] | [value] | [implication] |
| [growth] | [value] | [implication] |

## 3. Commodity Trading Odds
| Position | Recommendation | Rationale |
|----------|---------------|-----------|
| [asset] | [Buy/Sell/Hold] | [reason] |

## 4. War Duration Categorization
- **Short-term probability**: X%
- **Long-term probability**: X%
- **Key indicators**: [inflation persistence, policy uncertainty, etc.]

## 5. Termination Scenarios
[Ranked policy path scenarios with probabilities]
```

### 5. Output Per News Article

Each article produces a standalone analysis file saved to `memory/`:
- Geopolitics: `memory/geopolitics-YYYY-MM-DD-cnbc-<topic>.md`
- Macroeconomics: `memory/macro-YYYY-MM-DD-cnbc-<topic>.md`

**Output Format:** Follows exact skill output format (5 sections as shown above).

## Usage Examples

### Example 1: Full Pipeline Run

```
poly-tradebot
```

Fetches 3+ CNBC articles, classifies each, invokes appropriate skills, saves analyses to memory.

### Example 2: Re-run Workflow

```
poly-tradebot fetch
```

Re-fetches fresh articles from CNBC world page, re-runs classification and analysis pipeline.

### Example 3: Analyze Specific URL

```
poly-tradebot analyze <url>
```

Classifies and analyzes a single article URL using the appropriate skill.

## Output Summary

After pipeline completion, produces:

1. **Per-Article Analysis Files** (saved to `memory/`)
   - Full 5-section structured output per article
   - References to skill frameworks used

2. **Cross-Article Synthesis** (optional)
   - Unified trading recommendations
   - Risk monitors across all analyzed articles

## Skill Dependencies

- `geopolitics-expert` — Required for geopolitics articles
- `the_fed_agent` — Optional (falls back to direct macro analysis if unavailable)
- `web_fetch` — Built-in tool for article retrieval
- `web_search` — Built-in tool for Polymarket market discovery (optional)

## Resources

### references/
- `classification_rules.md` — Topic classification heuristics
- `output_templates.md` — 5-section format templates per skill type

### scripts/
- `fetch_cnbc.py` — Article fetching and parsing utility
- `classify_topic.py` — Geopolitics vs macroeconomics classifier

---

**Skill Version:** 1.0  
**Created:** 2026-03-17  
**Author:** poly-tradebot skill creator
