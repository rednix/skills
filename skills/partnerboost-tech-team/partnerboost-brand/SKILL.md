---
name: partnerboost-api
description: Call PartnerBoost merchant APIs to manage transactions, performance, billing, partners and more
version: 0.1.0
tags: [partnerboost, api, merchant]
requires:
  env:
    - PARTNERBOOST_API_KEY
---

# PartnerBoost Merchant API

You can call PartnerBoost merchant APIs using curl. All requests require the `X-Api-Key` header for authentication.

Please contact CSM to get the API key.

## Setup

The operator must configure `PARTNERBOOST_API_KEY` in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "partnerboost-api": {
        env: {
          PARTNERBOOST_API_KEY: "your-api-key-here"
        }
      }
    }
  }
}
```

## Authentication

Every request must include:

```
-H "X-Api-Key: $PARTNERBOOST_API_KEY"
```

## Base URL

```
https://app.partnerboost.com
```

## API Pattern

All WebUI APIs follow this pattern:

- **GET**: `curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" "https://app.partnerboost.com/a/{controller}/{action}?param1=value1&param2=value2"`
- **POST**: `curl -s -X POST -H "X-Api-Key: $PARTNERBOOST_API_KEY" -H "Content-Type: application/json" -d '{"key":"value"}' "https://app.partnerboost.com/a/{controller}/{action}"`

## Response Format

All APIs return JSON: `{ "code": 0, "message": "ok", "data": ... }`. Code 0 means success.

Paged responses include: `total_size`, `total_page`, `page_size`, `page_num`, `current_size` in the data.

---

## 1. Transaction (订单)

### 1.1 List Transactions

Query orders with filters. Supports pagination and sorting.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/transaction/list3?page_num=1&page_size=20&start_date=1735689600&end_date=1741737600"
```

Parameters (all optional):
- `page_num` (int): page number, default 1
- `page_size` (int): items per page, default 20
- `start_date` (int): start time, Unix timestamp (10-digit)
- `end_date` (int): end time, Unix timestamp (10-digit)
- `medium_id` (string): filter by media ID
- `status` (string): order status
- `search_word` (string): search keyword
- `sort_type` (string): sort field
- `sort_order` (string): asc or desc

### 1.2 Transaction Statistics

Get order statistics summary.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/transaction/list_stats?start_date=2026-01-01&end_date=2026-03-12"
```

Parameters (all optional):
- `start_date`, `end_date`, `medium_id`, `status` — same as above

### 1.3 Recent Transactions

Get the latest 10 orders. No parameters needed.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/transaction/nearly_list"
```

---

## 2. Performance (业绩)

### 2.1 Performance Charts

Get performance chart data (clicks, orders, commission trends).

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/performance/charts_v2?start_date=1735689600&end_date=1741737600&group_by=day"
```

Parameters:
- `start_date` (int, required): Unix timestamp (10-digit)
- `end_date` (int, required): Unix timestamp (10-digit)
- `group_by` (string): day, week, or month. Default: day
- `medium_id` (string): filter by media ID
- `channel` (string): filter by channel
- `partner_group_id` (int): filter by partner group

### 2.2 Performance List

Get performance detail list with pagination.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/performance/list_v2?start_date=1735689600&end_date=1741737600&page_num=1&page_size=20"
```

Parameters:
- `start_date` (int, required): Unix timestamp (10-digit)
- `end_date` (int, required): Unix timestamp (10-digit)
- `page_num`, `page_size`
- `group_by` (string): day, week, month, medium, or channel
- `medium_id`, `channel`, `partner_group_id` — same as charts
- `sort_type` (string): sort field
- `sort_order` (string): asc or desc

### 2.3 Performance Totals

Get performance summary totals.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/performance/charts_total?start_date=1735689600&end_date=1741737600"
```

Parameters:
- `start_date` (int, required): Unix timestamp (10-digit)
- `end_date` (int, required): Unix timestamp (10-digit)
- `medium_id`, `channel`, `partner_group_id`

### 2.4 Search Partner Performance

Search partners by keyword in performance reports.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/performance/search_partner?word=keyword"
```

Parameters:
- `word` (string, required): search keyword

---

## 3. Account / Billing (结算)

### 3.1 Billing List

Get billing records with filters.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/account/billing_list?page_num=1&page_size=20"
```

Parameters (all optional):
- `page_num`, `page_size`
- `mid` (string): media ID
- `ids` (string): billing IDs, comma-separated
- `time_start` (int): start time, Unix timestamp
- `time_end` (int): end time, Unix timestamp
- `payment_method`, `payment_type`, `status`, `search_word`

### 3.2 Account Info

Get account information including balance.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/account/account_info"
```

### 3.3 Current Plan

Get current subscription plan details.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/account/current_plan"
```

### 3.4 Prepayment List

Get prepayment records.

```bash
curl -s -H "X-Api-Key: $PARTNERBOOST_API_KEY" \
  "https://app.partnerboost.com/a/account/pre_payment?page_num=1&page_size=20"
```

Parameters (all optional): `page_num`, `page_size`, `mid`, `time_start`, `time_end`