#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
活动名称中文化映射 + 区域限制检测
"""

# 区域限制关键词（华语地区）
REGION_RESTRICTED_KEYWORDS = [
    "not available in your region",
    "香港居民不可参与",
    "香港用户不可参与",
    "中国大陆用户不可参与",
    "中国用户不可参与",
    "台湾用户不可参与",
    "澳门用户不可参与",
    "restricted regions",
    "excluded jurisdictions",
    "unavailable in certain regions",
    # 非华语地区
    "pakistan", "africa", "balkans", "nigeria", "uganda", "ghana", "kenya",
    "morocco", "cameroon", "turkmenistan", "ramadan", "jalsat", "suhoor",
    "巴基斯坦", "非洲", "巴尔干", "尼日利亚", "乌干达", "加纳", "肯尼亚",
    "摩洛哥", "喀麦隆", "土库曼", "斋月"
]

# 英文标题 -> 中文标题映射
ACTIVITY_NAMES = {
    # 理财产品
    "Enjoy Up to 8% APR with RLUSD Flexible Products": "RLUSD 灵活理财 8% 年化",
    "Binance Earn Yield Arena: Earn Up to 11.5% APR": "Yield Arena 理财 最高 11.5% 年化",
    "Binance Will Add Midnight (NIGHT) on Earn": "NIGHT 代币理财上线",
    "Binance Will Add Opinion (OPN) on Earn": "OPN 代币理财上线",
    "Enjoy Up to 10.5% APR with U Flexible Products": "U 灵活理财 10.5% 年化",
    "Subscribe to Binance Earn Products & Share 2,000 USDC": "理财申购瓜分 2000 USDC",
    "Introducing Midnight (NIGHT) on Binance Super Earn": "Midnight (NIGHT) 超级赚币",
    "Binance Earn: Share 10 Million SHELL Rewards": "SHELL 代币奖励（1000 万）",
    "Africa Exclusive: Create and Share Videos": "非洲专属：视频创作赢奖励",
    "Binance Earn: Enjoy Up to 8% APR with RLUSD": "RLUSD 灵活理财 8% 年化",
    
    # 活动奖励
    "Share 10 Million SHELL Rewards": "SHELL 代币奖励（1000 万）",
    "Tria Trading Competition": "Tria 交易竞赛",
    "KITE Trading Tournament": "KITE 交易锦标赛",
    "Grab a Share of 2,000,000 NIGHT Rewards": "NIGHT 代币奖励（200 万）",
    "Trade Tokenized Securities on Binance Alpha": "币安 Alpha 代币化证券交易",
    "ETHGas Trading Competition": "ETHGas 交易竞赛",
    "Humanity Protocol Trading Competition": "Humanity Protocol 交易竞赛",
    "Introducing Midnight (NIGHT): Grab a Share of the 90,000,000 NIGHT Token Voucher Prize Pool": "Midnight 空投（9000 万代币）",
    "Balkans Futures Frenzy: Grab a Share of the 17,100 USDC Reward Pool": "巴尔干期货交易（1.7 万 USDC）",
    "Join the Binance Wallet On-Chain Perpetuals Milestone Challenge": "币安钱包链上永续合约挑战",
    "Word of the Day: Test Your Knowledge on": "每日一词：知识测试",
    "Word of the Day: Test Your Knowledge": "每日一词：知识测试",
    "Velvet Trading Competition: Trade Velvet (VELVET) and Share $200K Worth of Rewards": "Velvet 交易竞赛（20 万美金）",
    "Pakistan Exclusive: Join the Binance x Islamabad United Referral Challenge": "巴基斯坦专属：推荐挑战赛",
    
    # 其他活动
    "Introducing Fabric Protocol (ROBO)": "Fabric Protocol (ROBO) 介绍",
    "Introducing Opinion (OPN)": "Opinion (OPN) 代币介绍",
}

# 代币提取规则
TOKEN_PATTERNS = {
    "RLUSD": "RLUSD",
    "NIGHT": "NIGHT",
    "OPN": "OPN",
    "SHELL": "SHELL",
    "TRIA": "TRIA",
    "Tria": "TRIA",
    "KITE": "KITE",
    "ETHGas": "ETHGas",
    "GWEI": "GWEI",
    "ROBO": "ROBO",
    "USDC": "USDC",
    "U": "U",
    "ETH": "ETH",
    "BNB": "BNB",
    "FDUSD": "FDUSD",
    "VELVET": "VELVET",
    "H": "H",
    "CFG": "CFG",
    "Midnight": "NIGHT",
}

def get_chinese_name(english_title):
    """获取中文名称"""
    # 先精确匹配
    if english_title in ACTIVITY_NAMES:
        return ACTIVITY_NAMES[english_title]
    
    # 再模糊匹配（提取主要关键词匹配）
    title_lower = english_title.lower()
    for en, zh in ACTIVITY_NAMES.items():
        en_lower = en.lower()
        # 提取代币名称作为关键词（如 SHELL, NIGHT, OPN 等）
        for token in ["shell", "night", "opn", "robo", "tria", "kite", "velvet", "ethgas", "humanity", "kat"]:
            if token in en_lower and token in title_lower:
                # 进一步确认活动类型匹配
                if "earn" in en_lower and "earn" in title_lower:
                    return zh
                elif "reward" in en_lower and "reward" in title_lower:
                    return zh
                elif "competition" in en_lower and "competition" in title_lower:
                    return zh
    
    # 没有匹配就返回原标题
    return english_title

def extract_token(title):
    """从标题提取代币名称"""
    title_upper = title.upper()
    
    # 特殊处理 1：ETHGas 的代币是 GWEI
    if "ETHGAS" in title_upper:
        return "GWEI"
    
    # 特殊处理 2：Yield Arena 是理财竞技场，代币不固定
    if "YIELD ARENA" in title_upper:
        return "多币种"
    
    # 特殊处理 3：Velvet 交易竞赛
    if "VELVET" in title_upper:
        return "VELVET"
    
    # 特殊处理 4：Midnight 的代币是 NIGHT
    if "MIDNIGHT" in title_upper:
        return "NIGHT"
    
    # 特殊处理 5：Humanity Protocol 的代币是 H
    if "HUMANITY PROTOCOL" in title_upper:
        return "H"
    
    # 特殊处理 6：Opinion 的代币是 OPN
    if "OPINION" in title_upper or "(OPN)" in title_upper:
        return "OPN"
    
    # 特殊处理 7：单独字母 U 需要前后是空格或标点（避免匹配到 OpenClaw 等）
    import re
    # 检查是否有 " U " 或 " U," 或 " U." 等模式（U 币理财）
    if re.search(r'\bU\s+(Flexible|理财|Products)', title, re.IGNORECASE):
        return "U"
    
    # 先检查完整代币名（按长度倒序，优先匹配长的）
    for token in sorted(TOKEN_PATTERNS.keys(), key=len, reverse=True):
        # 使用单词边界匹配，避免部分匹配
        if re.search(r'\b' + re.escape(token) + r'\b', title, re.IGNORECASE):
            return TOKEN_PATTERNS[token]
    
    # 如果没有匹配，检查是否是交易竞赛（通常标题里有代币名）
    if "TRADING COMPETITION" in title_upper or "交易竞赛" in title:
        # 尝试从标题提取第一个大写字母组合（至少 2 个字母）
        match = re.search(r'\b([A-Z]{2,10})\b', title)
        if match:
            return match.group(1)
    
    return "多币种"

def is_region_restricted(content_text):
    """检测内容是否有区域限制（华语地区）"""
    if not content_text:
        return False
    
    content_lower = content_text.lower()
    for keyword in REGION_RESTRICTED_KEYWORDS:
        if keyword.lower() in content_lower:
            return True
    return False

def is_square_task(code, title="", body=""):
    """识别是否是广场任务（通过 code 匹配 + 关键词判断）"""
    # 手动维护的广场任务列表（需要进入详情页确认）
    square_codes = [
        "d6fd86054b00445a97897606033970d8",  # NIGHT CreatorPad - 广场任务 ✅
        "820d2bb637d04f17983048ab7f4bf1f1",  # ROBO CreatorPad - 广场任务 ✅
    ]
    
    # 如果 code 匹配，直接返回 True
    if code in square_codes:
        return True
    
    # 通过关键词判断（备用方案）
    content = (title + " " + body).lower()
    square_keywords = ["creatorpad", "binance square", "广场", "square task"]
    
    for keyword in square_keywords:
        if keyword in content:
            return True
    
    return False

def get_reward_apr(title):
    """从标题提取奖池或 APR 信息"""
    import re
    
    # 提取 APR（如 8%、11.5%）
    apr_match = re.search(r'(\d+\.?\d*)\s*%\s*APR', title, re.IGNORECASE)
    if apr_match:
        return f"{apr_match.group(1)}% APR"
    
    # 提取奖池（如 2000 USDC、1000 万 SHELL）
    reward_patterns = [
        r'(\d+[,\d]*\s*(?: 万)?\s*(?:USDC|USDT|BUSD|RLUSD|SHIB|NIGHT|OPN|ROBO|TRIA|KITE|VELVET|H))',
        r'\$\s*(\d+[,\d]*(?:K|M|B)?)',  # $200K, $500K
        r'(\d+\s*USDT)',  # 100 USDT
    ]
    
    for pattern in reward_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 特定活动（只针对明确的活动名称）
    if "Yield Arena" in title:
        return "11.5% APR"
    elif "Share Up to 120M NIGHT" in title:
        return "1.2 亿 NIGHT"
    elif "Grab a Share of the 90,000,000 NIGHT" in title:
        return "9000 万 NIGHT"
    elif "2,500,000 OPN Token Voucher" in title:
        return "250 万 OPN"
    elif "Share 10 Million SHELL Rewards" in title:
        return "1000 万 SHELL"
    elif "Grab a Share of 8,600,000 ROBO" in title:
        return "860 万 ROBO"
    elif "Trading Competition" in title and "$200K" in title:
        return "20 万美金"
    
    return "详见页面"
