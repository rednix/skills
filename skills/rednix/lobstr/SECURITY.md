# Security Notes

This skill makes outbound HTTPS requests to the following domains only:

| Domain | Purpose |
|--------|---------|
| `api.anthropic.com` | Claude Haiku (idea parsing) and Claude Sonnet (scoring) |
| `api.exa.ai` | Neural web search for competitor discovery |
| `grid.nma.vc` | Public investor match count API (no auth, read-only) |
| `runlobstr.com` | Optional: publish shareable score card URL |
| `www.moltbook.com` | Optional: post scan result to m/lobstrscore community |

## Credentials

All credentials are read from environment variables only — nothing is hardcoded:

- `ANTHROPIC_API_KEY` — required
- `EXA_API_KEY` — required
- `RUNLOBSTR_PUBLISH_SECRET` — optional
- `MOLTBOOK_API_KEY` — optional

The skill will not start if required keys are missing. Optional keys are silently skipped if absent.

## No data persistence

The skill does not write any files, cache any data, or persist state between runs.
