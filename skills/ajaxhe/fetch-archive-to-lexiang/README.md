# fetch-archive-to-lexiang

通用 AI Agent Skill：抓取文章 / 视频 / 播客，并归档到[乐享](https://lexiangla.com)知识库。

适用于 [CodeBuddy](https://www.codebuddy.ai/)、[OpenClaw](https://github.com/anthropics/openclaw)、[Claude Code](https://docs.anthropic.com/en/docs/claude-code)、[Gemini CLI](https://github.com/google-gemini/gemini-cli) 等所有支持 Skill / Custom Instructions 机制的 AI Agent。

## 功能概述

将任意 URL 的内容抓取为结构化 Markdown，自动转存到乐享知识库，实现素材归档和可追溯。

### 支持的内容类型

| 类型 | 来源 | 处理方式 |
|------|------|---------|
| 📝 **图文文章** | 微信公众号、Substack、Medium、知识星球等 | Playwright 抓取 → Markdown + 图片 → PDF → 上传乐享 |
| 🔒 **付费/登录墙文章** | Substack 付费订阅、Medium 会员等 | Chrome Cookie 注入 / CDP 模式 → 全文抓取 |
| 🎬 **YouTube 视频** | YouTube | yt-dlp 下载 → Whisper 转录 → AI 翻译（中英对照）→ 上传乐享 |
| 🎙️ **播客音频** | 小宇宙FM、Apple Podcasts 等 | yt-dlp 下载音频 → Whisper 转录 → 繁简转换 → 上传乐享 |
| 📄 **免费文章** | 任意公开网页 | web_fetch / Playwright → Markdown → 上传乐享 |

### 乐享知识库归档

- 按**天维度**自动创建日期目录（如 `2026-03-18/`）
- 图文文章转为 **PDF**（嵌入图片）上传
- 纯文本/文字稿以**在线文档（page）**格式创建，支持在线编辑
- 自动**去重检查**，避免重复上传
- 通过 **lexiang MCP** 工具操作知识库，安全且通用

## 文件结构

```
fetch-archive/
├── SKILL.md                      # Skill 定义文件（Agent 指令）
├── config.json.example           # 配置模板（首次使用时复制为 config.json）
├── README.md                     # 本文件
└── scripts/
    ├── fetch_article.py          # 文章抓取脚本（Cookie 注入 / CDP 模式）
    ├── md_to_pdf.py              # Markdown → PDF 转换（嵌入图片、中文渲染）
    └── yt_download_transcribe.py # YouTube/播客 下载 + Whisper 转录 + AI 翻译
```

## 安装

只需在 Agent 对话中发送：

```
帮我安装这个 skill：https://github.com/ajaxhe/fetch-archive-to-lexiang
```

Agent 会自动完成仓库克隆、依赖安装和初始配置。

### 前置条件

1. **乐享 MCP**：本 Skill 通过 [lexiang MCP](https://github.com/nicognaW/lexiang-mcp) 操作乐享知识库，需提前在 Agent 的 MCP 配置中添加 lexiang server（[获取 Token](https://lexiangla.com/mcp)）
2. **Python 3.8+**：脚本运行环境

> 其他依赖（Playwright、yt-dlp、Whisper 等）均由 Agent 在首次使用时自动检测并安装，无需手动操作。

## 使用方式

在 Agent 对话中直接使用自然语言：

```
# 抓取微信公众号文章并归档
把这篇文章转存到知识库：https://mp.weixin.qq.com/s/xxxxx

# 抓取 Substack 付费文章
抓取这篇文章：https://www.lennysnewsletter.com/p/xxxxx

# YouTube 视频转录
转录这个视频：https://www.youtube.com/watch?v=xxxxx

# 播客转录
转录这期播客：https://www.xiaoyuzhoufm.com/episode/xxxxx
```

## 脚本独立使用

脚本也可以脱离 Skill 框架独立运行：

```bash
# 抓取文章（Cookie 注入模式）
python3 scripts/fetch_article.py fetch <URL> --output-dir <输出目录>

# 抓取文章（CDP 模式，适用于 LinkedIn 等需要 Google 登录的站点）
python3 scripts/fetch_article.py fetch <URL> --output-dir <输出目录> --cdp

# Substack 登录（首次使用前执行一次）
python3 scripts/fetch_article.py login

# Markdown 转 PDF
python3 scripts/md_to_pdf.py <article.md路径>

# YouTube 视频下载 + 转录 + 翻译
python3 scripts/yt_download_transcribe.py <YouTube URL> --output-dir <输出目录>
```

## 配置说明

首次使用时将 `config.json.example` 复制为 `config.json`，Skill 会在对话中引导完成配置，也可手动编辑：

```bash
cp config.json.example config.json
```

```json
{
  "_initialized": true,
  "lexiang": {
    "target_space": {
      "space_id": "<知识库ID>",
      "space_name": "<知识库名称>",
      "company_from": "<企业标识>"
    },
    "access_domain": {
      "domain": "lexiangla.com",
      "page_url_template": "https://lexiangla.com/pages/{entry_id}",
      "space_url_template": "https://lexiangla.com/spaces/{space_id}?company_from={company_from}"
    }
  }
}
```

> ⚠️ `config.json` 包含你的私有知识库信息，已被 `.gitignore` 忽略，不会被提交到仓库。

## 兼容性

| Agent | 支持方式 | 说明 |
|-------|---------|------|
| **CodeBuddy** | `.codebuddy/skills/` | 原生 Skill 目录，自动加载 |
| **OpenClaw** | `.claude/skills/` | 通过 Custom Instructions 加载 SKILL.md |
| **Claude Code** | `.claude/skills/` | 同 OpenClaw |
| **Gemini CLI** | `.gemini/skills/` | 通过 Custom Instructions 加载 SKILL.md |
| **其他 Agent** | 手动加载 | 将 SKILL.md 内容作为 System Prompt 传入即可 |

## License

MIT
