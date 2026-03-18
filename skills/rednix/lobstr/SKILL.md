---
name: lobstr
description: >
  LOBSTR is a startup idea scorer. Use when a user types /lobstr followed by a startup idea (e.g. /lobstr "AI-powered legal contracts for SMEs"). The skill parses the idea, searches for competitors via Exa, scores the idea across 6 LOBSTR dimensions using Claude, fetches investor match data from the NMA Grid API, and returns a formatted score card. Requires ANTHROPIC_API_KEY and EXA_API_KEY in environment.
metadata:
  version: "0.1.4"
  credentials:
    - name: ANTHROPIC_API_KEY
      required: true
      description: Anthropic API key for Claude Haiku (parsing) and Claude Sonnet (scoring)
    - name: EXA_API_KEY
      required: true
      description: Exa neural search API key for competitor scraping
    - name: RUNLOBSTR_PUBLISH_SECRET
      required: false
      description: Optional — enables shareable score card URLs at runlobstr.com
    - name: MOLTBOOK_API_KEY
      required: false
      description: Optional — posts every scan to m/lobstrscore on Moltbook
---

# LOBSTR — Startup Idea Scorer

## Trigger

User types: `/lobstr "their startup idea"`

## Workflow

Run `scripts/lobstr.py` with the idea as a single argument:

```bash
python3 scripts/lobstr.py "their startup idea"
```

The script handles the full pipeline and prints the formatted score card. Capture its stdout and reply to the user with it verbatim.

If the script errors (missing API keys, network issues), surface the error message to the user clearly.

## Moltbook Integration

Every scan is automatically posted to **m/lobstrscore** on Moltbook (https://www.moltbook.com/m/lobstrscore) by the `clawdnma` agent account.

- Requires `MOLTBOOK_API_KEY` env var — silently skipped if not set
- Posts include the full score card + runlobstr.com share link
- Verification challenges are solved automatically
- Non-fatal: if Moltbook post fails, the scan still completes

## Requirements

- `ANTHROPIC_API_KEY` — for Claude haiku (parsing) and Claude sonnet (scoring)
- `EXA_API_KEY` — for competitor search
- No `.env` file is loaded — keys must be exported in the shell before running:
  ```bash
  export ANTHROPIC_API_KEY=<your-key>
  export EXA_API_KEY=<your-key>
  ```

## Score Card Format (for reference)

```
🦞 LOBSTR SCAN
"idea here"

LOBSTR SCORE 74/100 ███████░░░

L  Landscape   🟢  82/100  one line verdict
O  Opportunity 🟡  71/100  one line verdict
B  Biz model   🟡  65/100  one line verdict
S  Sharpness   🔴  61/100  one line verdict
T  Timing      🟢  88/100  one line verdict
R  Reach       🟢  79/100  one line verdict

VERDICT
Two sentence VC verdict here.

✅ BUILD IT.

GRID: 4 EU investors match this space → https://grid.nma.vc
```

Color rules: 🟢 ≥ 70, 🟡 50–69, 🔴 < 50
Progress bar: 10 blocks, filled = round(score/10)

## Competitor Search Reference

See `references/exa-search.md` for Exa API usage patterns.
