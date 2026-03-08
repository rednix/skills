---
name: accountant-ai
tagline: "AI accounting assistant - bookkeeping, taxes"
description: "AI accounting helper. Bookkeeping, tax preparation, financial analysis. No API keys needed. $2 FREE credits to start. Pay-as-you-go via SkillBoss."
version: "1.0.1"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "industry"
tags:
  - accounting
  - finance
  - taxes
  - bookkeeping
pricing: "pay-as-you-go"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get your API key at https://skillboss.co/pricing?utm_source=clawhub&utm_medium=skill&utm_campaign=accountant-ai - $2 FREE credits included!"
---

# Accountant AI

**AI accounting assistant - bookkeeping, taxes**

## Quick Start

```bash
curl https://api.heybossai.com/v1/chat/completions \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{"model": "claude-4-5-sonnet", "messages": [...]}'
```

## Why SkillBoss?

- **One API key** for 100+ AI models
- **No vendor accounts** - Start in seconds
- **Auto-failover** - Never experience downtime
- **$2 FREE credits** to start
- **Pay-as-you-go** - No subscriptions
- **24/7 support** - We're here to help

## Get Started

1. Get API key: [skillboss.co/pricing](https://skillboss.co/pricing?utm_source=clawhub&utm_medium=skill&utm_campaign=accountant-ai)
2. Set `SKILLBOSS_API_KEY`
3. Start building!

---

*Powered by [SkillBoss](https://skillboss.co) - One API for 100+ AI services*
