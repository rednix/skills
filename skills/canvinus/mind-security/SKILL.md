---
name: mind-security
description: >
  AI security toolkit — deepfake and AI-generated media detection.
  Use when verifying if an image, video, or audio is a deepfake or AI-generated.
metadata: {"openclaw": {"emoji": "🛡️", "requires": {"bins": ["python3"], "anyBins": ["curl", "wget"]}, "homepage": "https://github.com/mind-sec/mind-security"}}
---

# mind-security

Deepfake detection powered by [Bittensor Subnet 34](https://bitmind.ai). The detection model evolves continuously through adversarial competition — generation miners push realism while detection miners improve accuracy.

## Quick Reference

| Task | Command | Docs |
|------|---------|------|
| Detect image | `python3 scripts/check_deepfake.py <path_or_url>` | [deepfake-detection.md](references/deepfake-detection.md) |
| Detect via curl | `curl -X POST https://api.bitmind.ai/detect-image -H "Authorization: Bearer $BITMIND_API_KEY" -d '{"image":"<url>"}'` | [deepfake-detection.md](references/deepfake-detection.md) |
| Detect video | `curl -X POST https://api.bitmind.ai/detect-video -d '{"video":"<url>","debug":true}'` | [deepfake-detection.md](references/deepfake-detection.md) |

## How It Works

The API accepts **any URL** — direct image links, social media posts, YouTube videos. Media is downloaded and analyzed server-side.

**Image pipeline:** Auth → Cache → Download → Preprocess → C2PA → Parallel (Subnet 34 detection + similarity matching) → isAI + confidence

**Video pipeline:** Same, plus absurdity analysis (3-way parallel). Absurdity returns a natural language description of what the video shows and flags physically impossible content.

**isAI logic:** C2PA evidence > similarity ≥0.7 > absurdity ≥0.8 (video) > model prediction ≥0.5. Each signal can only increase confidence.

**Response:** `{isAI: bool, confidence: float, similarity: float}`. With `debug: true`, adds raw score, processing time, C2PA details, and absurdity analysis (video).

## Setup

Requires `BITMIND_API_KEY` — register or log in at [app.bitmind.ai](https://app.bitmind.ai), then generate a key at [app.bitmind.ai/api/keys](https://app.bitmind.ai/api/keys).

## Script Conventions

- `python3 scripts/<script>.py --help`
- Zero pip dependencies (stdlib only)
- JSON to stdout, errors to stderr
- Exit 0 success, exit 1 failure
