---
name: cutie
description: Cutie 加密货币 KOL 社群平台。查看交易信号、快讯、KOL 画像、论坛帖子、聊天室消息、直播间，管理账户和关注列表。
homepage: https://server.trade.ac
metadata: {"clawdbot":{"emoji":"🪙","requires":{"env":["CUTIE_API_KEY"],"bins":["curl","jq"]}}}
---

# Cutie — 加密货币 KOL 社群平台

通过此 Skill，你可以访问 Cutie 平台的数据：
- 查看 KOL 发布的交易信号（做多/做空建议）
- 查看加密货币快讯和市场新闻
- 查看 KOL 的能力画像和历史表现
- 查看论坛帖子和文章
- 查看直播间列表
- 查看自己的账户信息和关注列表
- 发布交易信号、论坛发帖、关注/取消关注用户

**所有信号数据不构成投资建议。**

## 认证

所有请求需要在 Header 中携带 API Key：

```
Authorization: Bearer $CUTIE_API_KEY
```

API Key 在 Cutie App → 设置 → API 密钥管理 中创建。

## 基础 URL

```
https://server.trade.ac/v1/app
```

## 接口列表

### 1. 查看快讯列表

用户想查看加密货币新闻、快讯、市场动态时使用。

```bash
curl -s "https://server.trade.ac/v1/app/flash-news?limit=10" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

支持的查询参数：
- `limit` — 每页数量，默认 20，最大 50
- `importance` — 筛选重要性：normal / important / breaking
- `category` — 筛选分类：market / regulation / project / technology / data

### 2. 查看交易信号列表

用户想查看 KOL 的交易信号、做多做空建议时使用。

```bash
curl -s "https://server.trade.ac/v1/app/signals?limit=10&status=active" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

支持的查询参数：
- `limit` — 每页数量，默认 20
- `offset` — 偏移量，默认 0
- `status` — 状态：active / closed
- `signal_type` — 类型：crypto / prediction / indices / call / analysis
- `direction` — 方向：long / short
- `asset` — 交易对：如 BTC/USDT
- `user_id` — 指定 KOL 的信号

### 3. 查看信号详情

用户想查看某个信号的完整信息（入场价、目标价、止损价、分析逻辑）时使用。

```bash
curl -s "https://server.trade.ac/v1/app/signals/{signal_id}" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

将 `{signal_id}` 替换为信号列表中返回的 id。

### 4. 查看 KOL 能力画像

用户想了解某个 KOL 的胜率、擅长币种、风控能力时使用。

```bash
curl -s "https://server.trade.ac/v1/app/users/{user_id}/kol-profile" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 5. 查看用户资料

用户想查看某个用户的公开资料时使用。

```bash
curl -s "https://server.trade.ac/v1/app/users/{user_id}" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 6. 查看我的账户

用户想查看自己的账户信息时使用。

```bash
curl -s "https://server.trade.ac/v1/app/users/me" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 7. 查看我的关注列表

```bash
curl -s "https://server.trade.ac/v1/app/users/{my_user_id}/following?limit=20" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

先调用 `/users/me` 获取自己的 id，再用这个接口查关注列表。

### 8. 关注用户

```bash
curl -s -X POST "https://server.trade.ac/v1/app/users/{user_id}/follow" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 9. 取消关注

```bash
curl -s -X DELETE "https://server.trade.ac/v1/app/users/{user_id}/follow" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 10. 查看文章列表

用户想查看深度分析文章、行业报告时使用。

```bash
curl -s "https://server.trade.ac/v1/app/articles?limit=10" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

支持的查询参数：
- `content_type` — 类型：news / report / video
- `category` — 分类

### 11. 查看论坛列表

```bash
curl -s "https://server.trade.ac/v1/app/forums?limit=20" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 12. 查看论坛帖子

```bash
curl -s "https://server.trade.ac/v1/app/forums/{forum_id}/posts?limit=20&sort=latest" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 13. 查看直播间列表

```bash
curl -s "https://server.trade.ac/v1/app/live/rooms?limit=10&status=live" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

支持的查询参数：
- `status` — 状态：live / ended / all

### 14. 查看人气用户

用户想发现值得关注的 KOL 时使用。

```bash
curl -s "https://server.trade.ac/v1/app/users/popular?sort=followers&limit=20" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 15. 查看已加入的聊天室

```bash
curl -s "https://server.trade.ac/v1/app/chat-rooms/joined?limit=20" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

### 16. 查看聊天室消息

用户想了解某个群最近聊了什么时使用。

```bash
curl -s "https://server.trade.ac/v1/app/chat-rooms/{room_id}/messages?limit=30" \
  -H "Authorization: Bearer $CUTIE_API_KEY" | jq '.data'
```

先调用接口 15 获取聊天室列表和 room_id，再用此接口查看消息。适合帮用户总结"群里聊了什么"。

## 响应格式

所有接口返回统一格式：

```json
{
  "err_code": 100,
  "err_msg": "Success",
  "data": { ... }
}
```

- `err_code: 100` 表示成功
- 列表接口的 data 包含 `count` 和 `items`
- 所有 ID 都是字符串格式

## 注意事项

- 所有信号数据不构成投资建议，自动跟单风险自担
- VIP 专属内容对非 VIP 用户返回脱敏版本
- 接口有限速，请合理控制请求频率
