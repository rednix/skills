# 🦞 lobstr

> Validate your startup idea in 60 seconds — right from Telegram.

An [OpenClaw](https://openclaw.ai) skill that runs a full startup idea scan: competitor landscape, LOBSTR pitch score across 6 dimensions, and EU investor signal from GRID. Every scan auto-publishes a shareable score card at [runlobstr.com](https://runlobstr.com).

```
/lobstr "B2B GDPR compliance tool for DACH SMEs"
```

```
🦞 LOBSTR SCAN
"B2B GDPR compliance tool for DACH SMEs"

LOBSTR SCORE  38/100  [===-------]

L  Landscape    🔴  35/100  Saturated — OneTrust, TrustArc, dozens of local tools
O  Opportunity  🟡  65/100  Real market but SMEs want cheap checkboxes
B  Biz model    🔴  40/100  High churn, grudge purchase, CAC will kill you
S  Sharpness    🔴  25/100  Zero differentiation — "for SMEs" is what all claim
T  Timing       🟡  50/100  GDPR is old news — you're late, not early
R  Reach        🔴  45/100  DACH caps scale, heavy localized sales required

VERDICT
Tired compliance play in a picked-over market with no stated differentiation.
Pass unless you have a radically better distribution model.

🚫 NOT YET.

GRID: 3 investors match this space
→ https://grid.nma.vc/vc-list?search=SaaS&countries=Germany,Austria,Switzerland

Share your scan: https://runlobstr.com/scan/x7k2p9
```

---

## Install

**Via ClawHub (recommended):**

Find it at [clawhub.ai/rednix/lobstr](https://clawhub.ai/rednix/lobstr) and install directly from OpenClaw.

**Or clone manually** into your OpenClaw skills directory:

```bash
cd ~/.openclaw/workspace
git clone https://github.com/NMA-vc/lobstr
cd lobstr
```

---

## Usage

```
/lobstr "your startup idea"
/validate "your startup idea"
/scan "your startup idea"
```

Results arrive in ~60 seconds. Score card published to runlobstr.com automatically — no account required.

**Tips for better results:**
- Be specific about market and geography: *"AI invoicing for German freelancers"* beats *"AI invoicing tool"*
- Include the problem: *"SMEs spend 4h/week on GDPR paperwork"* gets a sharper score
- The LOBSTR score is intentionally harsh. If it hurts, that's the point.

---

## The LOBSTR Score

Six dimensions, each scored 0–100. The overall score is a **weighted judgment, not an average**. A 90 on Timing with a 20 on Sharpness is still a weak idea.

| Dimension | What it measures |
|-----------|-----------------|
| **L — Landscape** | How crowded is this space? Fewer strong competitors = higher score |
| **O — Opportunity** | Is there a real, large, funded market here? |
| **B — Business model** | Is monetization obvious and defensible? |
| **S — Sharpness** | How differentiated is this vs existing solutions? |
| **T — Timing** | Why is now the right moment for this idea? |
| **R — Reach** | How large and accessible is the addressable market? |

---

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude Haiku (parsing) + Claude Sonnet (scoring) |
| `EXA_API_KEY` | Yes | Competitor search — free tier at [exa.ai](https://exa.ai) |
| `MOLTBOOK_API_KEY` | Optional | Auto-posts scans to m/lobstrscore on Moltbook |

No `.env` file is loaded — keys must be exported in your shell or set in OpenClaw's environment config.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export EXA_API_KEY=...
```

---

## How it works

1. **Parse** — Claude Haiku extracts problem, market, geography, category, and 3 competitor search queries
2. **Scrape** — Exa neural search finds who's already in your space
3. **Score** — Claude Sonnet scores across 6 LOBSTR dimensions
4. **Signal** — Queries GRID's public EU investor database for matching firms
5. **Publish** — Posts the score card to runlobstr.com and returns a shareable URL
6. **Moltbook** — If MOLTBOOK_API_KEY is set, posts to m/lobstrscore for agent-to-agent debate

**Cost per scan:** ~$0.05 in API calls, charged directly to your own keys.

---

## GRID investor signal

Every scan queries [GRID](https://grid.nma.vc) — a database of 6,000+ EU VC firms — and shows how many investors are actively hunting your idea's space. The score card includes a deep link to a filtered investor list.

- **No account:** investor count + filtered list link
- **GRID account:** full investor names and profiles
- **GRID Pro:** warm intro paths

[Get a GRID account](https://grid.nma.vc)

---

## Score cards

Every scan auto-publishes a permanent public score card at runlobstr.com/scan/[slug].

Browse all scans: [runlobstr.com/scans](https://runlobstr.com/scans)

---

## Security

See [SECURITY.md](SECURITY.md) for a full list of outbound domains and what data is sent where.

- **api.anthropic.com** — idea text + competitor snippets for parsing and scoring
- **api.exa.ai** — search queries derived from your idea
- **grid.nma.vc** — category, geography, keywords (no idea text)
- **runlobstr.com** — full score card data for publishing
- **moltbook.com** — score summary + public URL (only if MOLTBOOK_API_KEY is set)

No data is stored locally. No .env file is read.

---

## Links

- Score cards: [runlobstr.com](https://runlobstr.com)
- EU investor database: [grid.nma.vc](https://grid.nma.vc)
- Moltbook submolt: [moltbook.com/m/lobstrscore](https://moltbook.com/m/lobstrscore)
- ClawHub: [clawhub.ai/rednix/lobstr](https://clawhub.ai/rednix/lobstr)
- Built by NMA: [nma.vc](https://nma.vc)

---

## License

MIT — use it, fork it, build on it.
