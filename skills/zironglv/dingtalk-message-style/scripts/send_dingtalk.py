#!/usr/bin/env python3
"""
钉钉消息发送工具 - 支持多种消息格式
用法:
    python3 send_dingtalk.py markdown "标题" "内容"
    python3 send_dingtalk.py link "标题" "描述" "图片URL" "跳转URL"
    python3 send_dingtalk.py image "图片URL"
    python3 send_dingtalk.py action "标题" "描述" "图片URL" '[{"title":"按钮","actionURL":"url"}]'
    python3 send_dingtalk.py feed '[{"title":"","picURL":"","messageURL":""}]'
    python3 send_dingtalk.py text "内容"
"""
import sys
import json
import urllib.request
import os

WEBHOOKS_FILE = "/Users/qf/.copaw/dingtalk_session_webhooks.json"

def get_webhook(session_id=None):
    """获取 webhook，默认使用当前会话"""
    if not os.path.exists(WEBHOOKS_FILE):
        raise Exception("webhook 文件不存在")
    
    with open(WEBHOOKS_FILE, 'r') as f:
        data = json.load(f)
    
    # 优先使用指定 session，否则使用第一个（当前会话）
    if session_id:
        key = f"dingtalk:sw:{session_id}"
        if key in data:
            return data[key]
    
    # 返回第一个 webhook
    for key, webhook in data.items():
        return webhook
    
    raise Exception("未找到 webhook")

def fix_taobao_image_url(url):
    """修复淘宝图片链接，去掉 _.webp 后缀"""
    if not url:
        return url
    return url.replace('.jpg_.webp', '.jpg').replace('.png_.webp', '.png')

def send_message(payload, webhook=None):
    """发送消息到钉钉"""
    if webhook is None:
        webhook = get_webhook()
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(webhook)
    req.add_header('Content-Type', 'application/json')
    
    response = urllib.request.urlopen(req, data, timeout=10)
    result = json.loads(response.read().decode('utf-8'))
    return result

def send_markdown(title, text):
    """发送 Markdown 消息"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        }
    }
    return send_message(payload)

def send_text(content):
    """发送纯文本消息"""
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    return send_message(payload)

def send_link(title, text, pic_url, message_url):
    """发送 Link 卡片消息"""
    pic_url = fix_taobao_image_url(pic_url)
    payload = {
        "msgtype": "link",
        "link": {
            "title": title,
            "text": text,
            "picUrl": pic_url,
            "messageUrl": message_url
        }
    }
    return send_message(payload)

def send_image(pic_url):
    """发送纯图片消息"""
    pic_url = fix_taobao_image_url(pic_url)
    payload = {
        "msgtype": "image",
        "image": {
            "picURL": pic_url
        }
    }
    return send_message(payload)

def send_action_card(title, text, pic_url=None, buttons=None, single_title=None, single_url=None):
    """发送 ActionCard 消息"""
    payload = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": title,
            "text": text
        }
    }
    
    if pic_url:
        payload["actionCard"]["picURL"] = fix_taobao_image_url(pic_url)
    
    if single_title and single_url:
        # 单按钮模式
        payload["actionCard"]["singleTitle"] = single_title
        payload["actionCard"]["singleURL"] = single_url
    elif buttons:
        # 多按钮模式
        payload["actionCard"]["btnOrientation"] = "0"
        payload["actionCard"]["btns"] = buttons
    
    return send_message(payload)

def send_feed_card(links):
    """发送 FeedCard 消息（多图文）"""
    # 修复所有图片链接
    for link in links:
        if "picURL" in link:
            link["picURL"] = fix_taobao_image_url(link["picURL"])
    
    payload = {
        "msgtype": "feedCard",
        "feedCard": {
            "links": links
        }
    }
    return send_message(payload)

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    msg_type = sys.argv[1].lower()
    
    try:
        if msg_type == "markdown":
            if len(sys.argv) < 4:
                print("用法: send_dingtalk.py markdown '标题' '内容'")
                sys.exit(1)
            title = sys.argv[2]
            text = sys.argv[3]
            result = send_markdown(title, text)
        
        elif msg_type == "text":
            content = sys.argv[2]
            result = send_text(content)
        
        elif msg_type == "link":
            if len(sys.argv) < 6:
                print("用法: send_dingtalk.py link '标题' '描述' '图片URL' '跳转URL'")
                sys.exit(1)
            title = sys.argv[2]
            text = sys.argv[3]
            pic_url = sys.argv[4]
            message_url = sys.argv[5]
            result = send_link(title, text, pic_url, message_url)
        
        elif msg_type == "image":
            pic_url = sys.argv[2]
            result = send_image(pic_url)
        
        elif msg_type == "action":
            if len(sys.argv) < 4:
                print("用法: send_dingtalk.py action '标题' '描述' '图片URL' '[按钮JSON]'")
                sys.exit(1)
            title = sys.argv[2]
            text = sys.argv[3]
            pic_url = sys.argv[4] if len(sys.argv) > 4 else None
            buttons = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
            result = send_action_card(title, text, pic_url, buttons)
        
        elif msg_type == "feed":
            links = json.loads(sys.argv[2])
            result = send_feed_card(links)
        
        else:
            print(f"不支持的消息类型: {msg_type}")
            print("支持的类型: markdown, text, link, image, action, feed")
            sys.exit(1)
        
        if result.get('errcode', 0) == 0:
            print(f"✅ 消息发送成功")
        else:
            print(f"❌ 发送失败: {result}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()