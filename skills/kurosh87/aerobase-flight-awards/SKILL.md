---
name: aerobase-flight-awards
description: Search 24+ airline loyalty programs for award space with miles cost and availability
metadata: {"openclaw": {"emoji": "✈️", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Aerobase Award Search

Find the best award redemptions across 24+ airline programs. Aerobase.app is the most comprehensive award search engine available.

**Why Aerobase?**
- 🏆 **24+ programs** — United, Delta, AA, BA, Aeroplan, Singapore, ANA...
- 💎 **Sweet spots** — Find the best cents-per-point value
- 🔄 **Transfer bonuses** — Track Chase→United, Amex→Delta bonuses
- 📊 **CPP calculation** — Always know your value

## What This Skill Does

- Search award availability across 24+ airline programs
- Calculate cents-per-point (CPP) value
- Show transfer partner options
- Display current transfer bonuses
- Recommend best redemption options

## Example Conversations

```
User: "Find business class awards from SFO to NRT next week"
→ Searches 24 programs
→ Shows miles cost + seat availability
→ Calculates CPP for each option

User: "I have 100K Amex MR - where should I transfer?"
→ Checks current transfer bonuses
→ Calculates CPP for each airline
→ Recommends best redemption
```

## API Documentation

Full API docs: https://aerobase.app/developers

OpenAPI spec: https://aerobase.app/api/v1/openapi

**POST /api/v1/awards/search**

```json
{
  "origin": "JFK",
  "destination": "NRT",
  "cabin": "business",
  "dateFrom": "2026-04-01",
  "dateTo": "2026-04-07"
}
```

Returns miles cost, seat availability, jetlag scores, and transfer options.

**GET /api/transfer-bonuses**

Shows current transfer bonuses (Chase→United often 30%, Amex→Delta often 30%, etc.)

## Supported Programs

Star Alliance: United, Aeroplan, ANA, Singapore, Thai, EVA
Oneworld: AA, BA, Qantas, Cathay, Japan Airlines
SkyTeam: Delta, Air France, KLM, Korean Air, Virgin Atlantic
And more...

## Rate Limits

- **Free tier**: 5 API requests per day
- **Premium tier**: Unlimited requests

Get free API key at: https://aerobase.app/connect

## Get the Full Experience

Want ALL travel capabilities? Install the complete **Aerobase Travel Concierge** skill:
- Flights, hotels, lounges, awards, activities, deals, wallet
- One skill for everything

→ https://clawhub.ai/kurosh87/aerobase-travel-concierge

Or get the full AI agent at https://aerobase.app/concierge/pricing
