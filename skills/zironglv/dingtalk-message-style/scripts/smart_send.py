#!/usr/bin/env python3
"""
钉钉消息智能发送 - 自动选择最佳格式
用法:
    python3 smart_send.py                   # 交互模式，自动分析内容
    python3 smart_send.py --template goods  # 使用模板
"""
import sys
import json
import urllib.request
import os
import re

WEBHOOKS_FILE = "/Users/qf/.copaw/dingtalk_session_webhooks.json"
TEMPLATES_FILE = "/Users/qf/.copaw/skills/dingtalk-message-style/templates/templates.json"

def get_webhook(session_id=None):
    """获取 webhook"""
    if not os.path.exists(WEBHOOKS_FILE):
        raise Exception("webhook 文件不存在")
    
    with open(WEBHOOKS_FILE, 'r') as f:
        data = json.load(f)
    
    if session_id:
        key = f"dingtalk:sw:{session_id}"
        if key in data:
            return data[key]
    
    for key, webhook in data.items():
        return webhook
    raise Exception("未找到 webhook")

def fix_taobao_image_url(url):
    """修复淘宝图片链接"""
    if not url:
        return url
    return re.sub(r'\.(jpg|png)_\.webp', r'.\1', url)

def send_message(payload, webhook=None):
    """发送消息"""
    if webhook is None:
        webhook = get_webhook()
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(webhook)
    req.add_header('Content-Type', 'application/json')
    
    response = urllib.request.urlopen(req, data, timeout=10)
    return json.loads(response.read().decode('utf-8'))

# ============ 消息格式发送函数 ============

def send_markdown(title, text):
    return send_message({
        "msgtype": "markdown",
        "markdown": {"title": title, "text": text}
    })

def send_text(content):
    return send_message({
        "msgtype": "text",
        "text": {"content": content}
    })

def send_link(title, text, pic_url, message_url):
    return send_message({
        "msgtype": "link",
        "link": {
            "title": title,
            "text": text,
            "picUrl": fix_taobao_image_url(pic_url),
            "messageUrl": message_url
        }
    })

def send_image(pic_url):
    return send_message({
        "msgtype": "image",
        "image": {"picURL": fix_taobao_image_url(pic_url)}
    })

def send_feed_card(links):
    for link in links:
        if "picURL" in link:
            link["picURL"] = fix_taobao_image_url(link["picURL"])
    return send_message({
        "msgtype": "feedCard",
        "feedCard": {"links": links}
    })

def send_action_card(title, text, single_title, single_url, pic_url=None):
    payload = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": title,
            "text": text,
            "singleTitle": single_title,
            "singleURL": single_url
        }
    }
    if pic_url:
        payload["actionCard"]["picURL"] = fix_taobao_image_url(pic_url)
    return send_message(payload)

# ============ 智能格式选择 ============

class SmartSender:
    """智能消息发送器 - 自动选择最佳格式"""
    
    def __init__(self):
        self.items = []      # 商品/链接列表
        self.title = ""      # 标题
        self.content = ""    # 文本内容
        self.images = []     # 图片列表
        self.has_table = False
        self.has_list = False
    
    def add_product(self, title, image_url=None, link_url=None, price=None, desc=None):
        """添加商品/链接项"""
        item = {
            "title": title,
            "picURL": fix_taobao_image_url(image_url) if image_url else None,
            "messageURL": link_url,
            "price": price,
            "desc": desc
        }
        self.items.append(item)
        if image_url:
            self.images.append(image_url)
        return self
    
    def set_title(self, title):
        """设置标题"""
        self.title = title
        return self
    
    def set_content(self, content):
        """设置文本内容"""
        self.content = content
        # 检测表格
        self.has_table = "|" in content and "---" in content
        # 检测列表
        self.has_list = "\n-" in content or "\n*" in content or "\n1." in content
        return self
    
    def add_image(self, image_url):
        """添加图片"""
        self.images.append(fix_taobao_image_url(image_url))
        return self
    
    def analyze_and_send(self):
        """分析内容并选择最佳格式发送"""
        
        # 1. 多个商品项 → FeedCard
        if len(self.items) > 1:
            links = []
            for item in self.items:
                if item.get("picURL"):
                    links.append({
                        "title": item["title"],
                        "picURL": item["picURL"],
                        "messageURL": item.get("messageURL") or "https://clawhub.ai"
                    })
            if links:
                return send_feed_card(links)
        
        # 2. 单个商品 + 图片 + 链接 → Link
        if len(self.items) == 1 and self.items[0].get("picURL") and self.items[0].get("messageURL"):
            item = self.items[0]
            text = item.get("desc") or ""
            if item.get("price"):
                text = f"💰 价格: {item['price']}\n{text}"
            return send_link(item["title"], text, item["picURL"], item["messageURL"])
        
        # 3. 只有图片 → Image
        if self.images and not self.items and not self.content:
            return send_image(self.images[0])
        
        # 4. 有表格或列表 → Markdown
        if self.has_table or self.has_list or self.content:
            text = self.content
            if self.title:
                text = f"### {self.title}\n\n{text}"
            if self.images and not self.has_table:
                # Markdown 不支持图片，提示用户
                text += f"\n\n📷 附图: {len(self.images)} 张（Markdown 不支持图片，请使用 Link 类型）"
            return send_markdown(self.title or "消息", text)
        
        # 5. 默认纯文本
        if self.title:
            return send_text(self.title)
        
        raise Exception("没有可发送的内容")

# ============ 模板库 ============

def load_templates():
    """加载模板"""
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_templates()

def get_default_templates():
    """默认模板库"""
    return {
        "goods_recommend": {
            "name": "商品推荐",
            "emoji": "🔥",
            "description": "推荐单个商品，带图片和链接",
            "format": "link",
            "template": {
                "title": "🔥 {商品名}",
                "text": "💰 价格: {价格}\n⭐ 亮点: {亮点}\n\n{描述}",
                "picUrl": "{图片URL}",
                "messageUrl": "{商品链接}"
            }
        },
        "goods_list": {
            "name": "商品列表",
            "emoji": "📋",
            "description": "多个商品推荐列表",
            "format": "feedCard",
            "template": {
                "links": [
                    {"title": "🔥 {商品名1} - {价格1}", "picURL": "{图片1}", "messageURL": "{链接1}"},
                    {"title": "🔥 {商品名2} - {价格2}", "picURL": "{图片2}", "messageURL": "{链接2}"}
                ]
            }
        },
        "task_report": {
            "name": "任务报告",
            "emoji": "📋",
            "description": "任务完成情况报告",
            "format": "markdown",
            "template": {
                "title": "📋 任务完成报告",
                "text": """### 📋 任务完成报告

**时间**: {时间}

---

| 任务 | 状态 | 备注 |
|------|------|------|
{任务表格}

---

**总计**: 完成 {完成数}/{总数} 个任务

> 💡 {总结}"""
            }
        },
        "price_alert": {
            "name": "降价提醒",
            "emoji": "📉",
            "description": "商品降价通知",
            "format": "link",
            "template": {
                "title": "📉 降价提醒: {商品名}",
                "text": "📉 原价: ~~{原价}~~\n💰 现价: **{现价}**\n📉 降幅: {降幅}\n\n⏰ 限时优惠，速抢！",
                "picUrl": "{图片URL}",
                "messageUrl": "{商品链接}"
            }
        },
        "order_status": {
            "name": "订单状态",
            "emoji": "📦",
            "description": "订单状态更新通知",
            "format": "markdown",
            "template": {
                "title": "📦 订单状态更新",
                "text": """### 📦 订单状态更新

**订单号**: {订单号}
**商品**: {商品名}
**状态**: {状态}

---

📦 物流信息:
{物流信息}

---

> ⏰ 更新时间: {时间}"""
            }
        },
        "daily_summary": {
            "name": "每日总结",
            "emoji": "📊",
            "description": "每日工作/任务总结",
            "format": "markdown",
            "template": {
                "title": "📊 每日总结 - {日期}",
                "text": """### 📊 每日总结

**日期**: {日期}

---

#### ✅ 已完成

{已完成列表}

#### ⏳ 进行中

{进行中列表}

#### 📌 待办

{待办列表}

---

**统计**: 完成 {完成数} 项，进行中 {进行中数} 项"""
            }
        },
        "meeting_reminder": {
            "name": "会议提醒",
            "emoji": "📅",
            "description": "会议开始前提醒",
            "format": "actionCard",
            "template": {
                "title": "📅 会议提醒",
                "text": "### 📅 会议提醒\n\n**主题**: {主题}\n**时间**: {时间}\n**地点**: {地点}\n\n**参会人**: {参会人}",
                "singleTitle": "查看详情",
                "singleURL": "{链接}"
            }
        },
        "shopping_cart": {
            "name": "购物车提醒",
            "emoji": "🛒",
            "description": "购物车商品汇总",
            "format": "markdown",
            "template": {
                "title": "🛒 购物车提醒",
                "text": """### 🛒 购物车提醒

您购物车中有 **{商品数}** 件商品，总计 **¥{总金额}**

---

| 商品 | 价格 | 数量 |
|------|------|------|
{商品表格}

---

> 💡 部分商品有优惠，点击查看详情"""
            }
        }
    }

def apply_template(template_name, **kwargs):
    """应用模板并发送"""
    templates = load_templates()
    
    if template_name not in templates:
        raise Exception(f"模板不存在: {template_name}\n可用模板: {list(templates.keys())}")
    
    tmpl = templates[template_name]
    fmt = tmpl["format"]
    data = tmpl["template"]
    
    # 替换占位符
    def replace_placeholders(text, values):
        if isinstance(text, str):
            for k, v in values.items():
                text = text.replace(f"{{{k}}}", str(v))
            return text
        return text
    
    if fmt == "link":
        return send_link(
            replace_placeholders(data["title"], kwargs),
            replace_placeholders(data["text"], kwargs),
            fix_taobao_image_url(kwargs.get("图片URL", kwargs.get("picUrl", ""))),
            kwargs.get("商品链接", kwargs.get("messageUrl", "https://clawhub.ai"))
        )
    
    elif fmt == "markdown":
        return send_markdown(
            replace_placeholders(data["title"], kwargs),
            replace_placeholders(data["text"], kwargs)
        )
    
    elif fmt == "actionCard":
        return send_action_card(
            replace_placeholders(data["title"], kwargs),
            replace_placeholders(data["text"], kwargs),
            replace_placeholders(data.get("singleTitle", "查看详情"), kwargs),
            kwargs.get("链接", kwargs.get("singleURL", "https://clawhub.ai"))
        )
    
    elif fmt == "feedCard":
        links = data.get("links", [])
        formatted_links = []
        for link in links:
            formatted_links.append({
                "title": replace_placeholders(link["title"], kwargs),
                "picURL": fix_taobao_image_url(kwargs.get(link.get("picURL", "").strip("{}"), "")),
                "messageURL": kwargs.get(link.get("messageURL", "").strip("{}"), "https://clawhub.ai")
            })
        return send_feed_card(formatted_links)
    
    else:
        raise Exception(f"不支持的格式: {fmt}")

def list_templates():
    """列出所有模板"""
    templates = load_templates()
    print("\n📋 可用模板:\n")
    for key, tmpl in templates.items():
        print(f"  {tmpl['emoji']} {key:20} - {tmpl['name']}")
        print(f"     {tmpl['description']}\n")

# ============ 主函数 ============

def main():
    args = sys.argv[1:]
    
    if not args or args[0] == "--help":
        print(__doc__)
        list_templates()
        print("示例:")
        print('  # 使用商品推荐模板')
        print('  python3 smart_send.py --template goods_recommend --vars \'{"商品名":"iPhone","价格":"5999","图片URL":"...","商品链接":"..."}\'')
        print()
        return
    
    if args[0] == "--list":
        list_templates()
        return
    
    if args[0] == "--template":
        if len(args) < 2:
            print("请指定模板名: --template <模板名>")
            list_templates()
            return
        
        template_name = args[1]
        vars_data = {}
        
        if "--vars" in args:
            vars_idx = args.index("--vars")
            if len(args) > vars_idx + 1:
                vars_data = json.loads(args[vars_idx + 1])
        
        result = apply_template(template_name, **vars_data)
        
        if result.get('errcode', 0) == 0:
            print(f"✅ 消息发送成功 (模板: {template_name})")
        else:
            print(f"❌ 发送失败: {result}")
            sys.exit(1)

if __name__ == "__main__":
    main()