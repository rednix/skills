---
name: dingtalk-message-style
description: "提升钉钉消息展示样式，支持 Markdown、Link 卡片、ActionCard 按钮、FeedCard 图文列表、纯图片等多种格式。使用场景：(1) 发送商品信息带图片 (2) 发送任务报告表格 (3) 发送可点击的操作卡片 (4) 发送多图文列表。"
metadata:
  copaw:
    emoji: "🎨"
---

# 钉钉消息样式 Skill

提升钉钉消息的视觉效果和交互体验，支持智能格式选择和模板库。

## 快速开始

### 1. 使用模板（推荐）

```bash
# 查看所有模板
python3 ~/.copaw/skills/dingtalk-message-style/scripts/smart_send.py --list

# 商品推荐
python3 ~/.copaw/skills/dingtalk-message-style/scripts/smart_send.py --template goods_recommend --vars '{"商品名":"iPhone","价格":"5999","亮点":"最新款","描述":"性能强劲","图片URL":"...","商品链接":"..."}'

# 任务报告
python3 ~/.copaw/skills/dingtalk-message-style/scripts/smart_send.py --template task_report --vars '{"时间":"2026-03-18","任务表格":"|任务|状态|\n|A|✅|","完成数":"1","总数":"1","总结":"完成"}'

# 降价提醒
python3 ~/.copaw/skills/dingtalk-message-style/scripts/smart_send.py --template price_alert --vars '{"商品名":"iPhone","原价":"6999","现价":"5999","降幅":"1000","图片URL":"...","商品链接":"..."}'
```

### 2. 智能发送（自动选择格式）

```python
from smart_send import SmartSender

# 多商品 → 自动选择 FeedCard
sender = SmartSender()
sender.add_product("商品1", "图片1", "链接1", "¥99")
sender.add_product("商品2", "图片2", "链接2", "¥199")
sender.analyze_and_send()  # 自动选择 FeedCard

# 单商品+图片+链接 → 自动选择 Link
sender = SmartSender()
sender.add_product("商品名", "图片", "链接", "¥99", "描述")
sender.analyze_and_send()  # 自动选择 Link

# 表格/列表 → 自动选择 Markdown
sender = SmartSender()
sender.set_title("报告")
sender.set_content("| 任务 | 状态 |\n|------|------|\n| A | ✅ |")
sender.analyze_and_send()  # 自动选择 Markdown
```

---

## 支持的消息格式

| 格式 | 图片 | 按钮 | 最佳场景 |
|------|------|------|----------|
| **markdown** | ❌ | ❌ | 报告、表格、列表 |
| **text** | ❌ | ❌ | 简单通知 |
| **link** | ✅ | ❌ | 商品推荐、文章分享 |
| **image** | ✅ | ❌ | 纯图片展示 |
| **actionCard** | ✅ | ✅ | 操作确认、选择菜单 |
| **feedCard** | ✅ | ❌ | 多图文列表 |

---

## 模板库

| 模板 | 说明 | 格式 |
|------|------|------|
| `goods_recommend` | 商品推荐 | Link |
| `goods_list` | 商品列表 | FeedCard |
| `task_report` | 任务报告 | Markdown |
| `price_alert` | 降价提醒 | Link |
| `order_status` | 订单状态 | Markdown |
| `daily_summary` | 每日总结 | Markdown |
| `meeting_reminder` | 会议提醒 | ActionCard |
| `shopping_cart` | 购物车提醒 | Markdown |

---

## 智能格式选择规则

| 内容特征 | 自动选择 | 说明 |
|----------|----------|------|
| 多个商品+图片 | **FeedCard** | 多图文列表 |
| 单商品+图片+链接 | **Link** | 卡片形式 |
| 只有图片 | **Image** | 纯图片 |
| 有表格/列表 | **Markdown** | 富文本展示 |
| 纯文本 | **Text** | 简单通知 |

---

## 命令行工具

### 基础发送

```bash
# Markdown
python3 ~/.copaw/skills/dingtalk-message-style/scripts/send_dingtalk.py markdown "标题" "内容"

# Link 卡片
python3 ~/.copaw/skills/dingtalk-message-style/scripts/send_dingtalk.py link "标题" "描述" "图片URL" "跳转URL"

# 纯图片
python3 ~/.copaw/skills/dingtalk-message-style/scripts/send_dingtalk.py image "图片URL"

# 多图文
python3 ~/.copaw/skills/dingtalk-message-style/scripts/send_dingtalk.py feed '[{"title":"标题","picURL":"图片","messageURL":"链接"}]'
```

### 模板发送

```bash
python3 ~/.copaw/skills/dingtalk-message-style/scripts/smart_send.py --template <模板名> --vars '<JSON变量>'
```

---

## 图片链接处理

⚠️ **重要**：淘宝图片 URL 需去掉 `_.webp` 后缀

```python
# 自动处理
fix_taobao_image_url(url)  # xxx.jpg_.webp → xxx.jpg
```

---

## 样式美化技巧

### Markdown 表格

```markdown
| 任务 | 状态 | 备注 |
|------|------|------|
| 任务A | ✅ 完成 | 正常 |
| 任务B | ⏳ 进行中 | 等待中 |
```

### 表情符号推荐

| 场景 | 推荐表情 |
|------|----------|
| 完成/成功 | ✅ 🎉 ✔️ |
| 进行中 | ⏳ 🔄 |
| 警告 | ⚠️ ❗ |
| 提示 | 💡 📌 |
| 购物 | 🛒 🔥 💰 |
| 降价 | 📉 💸 |
| 任务 | 📋 📝 |

---

## 文件结构

```
~/.copaw/skills/dingtalk-message-style/
├── SKILL.md                    # 本文档
├── scripts/
│   ├── send_dingtalk.py       # 基础发送工具
│   └── smart_send.py          # 智能发送+模板库
└── templates/
    └── templates.json         # 模板定义
```

---

## 使用建议

1. **有图片优先用 Link/FeedCard** - 视觉效果好
2. **报告用模板** - 格式统一美观
3. **多商品用 FeedCard** - 一次展示多个
4. **复杂内容先智能分析** - 自动选择最佳格式