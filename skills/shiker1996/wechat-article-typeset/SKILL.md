---
name: wechat-article-typeset
version: 1.0.0
description: 公众号文章排版——用本技能目录内 lib 生成 HTML，并调用 edit.shiker.tech 生成可复制到公众号的复制页链接
trigger: "公众号排版|复制到公众号|edit.shiker.tech|公众号文章"
tools: [filesystem, http, shell]
author: wework
---

# 公众号文章排版

当用户需要进行**公众号文章排版**、**生成可复制到公众号的页面**或**调用 edit.shiker.tech 复制页**时，使用**本技能目录内的 JS**（不依赖仓库 `src/`）生成 HTML，再请求复制页链接。

## When to Use

- 用户提到「公众号排版」「复制到公众号」「生成公众号页面」「edit.shiker.tech」。
- 需要把 Markdown 或正文内容排成公众号可用的富文本并得到复制页链接时。

## 1. 生成逻辑所在位置（技能目录自包含）

- **HTML 生成**：使用本技能目录下的 **`lib/utils/markdown.js`**（与 Web 端逻辑一致，为副本，便于在任意目录或复制到 `~/.openclaw/skills/` 后独立运行）。
- **入口脚本**：`wechat-html.js`（仅生成 HTML）、`wechat-copy.js`（生成 HTML 并请求复制页 URL）。

**执行方式**：在**本技能目录**下执行（复制到 `~/.openclaw/skills/wechat-article-typeset/` 后同样在该目录下执行）：

- 生成 HTML：`node wechat-html.js [选项] [input.md]` 或从 stdin 传入内容。选项见下「主题混搭」。
- 生成并获取复制页链接：`node wechat-copy.js [选项] <input.md>`，输出即为 `https://edit.shiker.tech/copy.html?id=xxx`。
- 列出预设：`node wechat-html.js --list-presets`；列出主题：`--list-themes`；列出版式：`--list-layouts`。

**getFullHtml 签名**（与 Web 端一致）：

```js
getFullHtml(content, themeId, imageStyleId, layoutId = 'default', imageResolver, codeThemeId = 'vscode-dark')
```

## 2. 主题混搭（推荐）

**任意主题 + 任意版式** 均可自由组合（底层为 `getResolvedTheme(themeId, layoutId)`）。推荐两种用法：

### 2.1 预设（主题+版式一键）

- 使用 **`presets.js`** 中的预设名，如：`暖色色块`、`墨色下划线`、`青绿左边线`、`紫调渐变`、`极简黑白`、`雁栖湖`、`深色护眼` 等。
- 命令行：`node wechat-html.js --preset 墨色下划线 [input.md]`，或 `node wechat-copy.js --preset 青绿左边线 article.md`。
- 环境变量：`WEWORK_PRESET=墨色下划线`。
- 查看全部预设：`node wechat-html.js --list-presets`（或 `wechat-copy.js --list-presets`）。

### 2.2 自定义混搭（主题 + 版式分别指定）

- **themeId**：如 coral-warm、ink-seri、teal-fresh、purple-elegant、minimal-bw、amber-paper、starry-blue 等（`--list-themes` 列出全部）。
- **layoutId**：如 default、block、underline、leftline、minimal、gradient、card、yanqi 等（`--list-layouts` 列出全部）。
- 命令行：`node wechat-html.js --theme teal-fresh --layout leftline [input.md]`，或 `node wechat-copy.js -t ink-seri -l underline article.md`。
- 环境变量：`WEWORK_THEME_ID`、`WEWORK_LAYOUT_ID`。可与 `--preset` 同时使用，命令行会覆盖预设。

### 2.3 图片样式与代码主题

- **imageStyleId**：`default`、`rounded`、`shadow`、`border`。命令行 `--image-style` 或 `-i`，环境变量 `WEWORK_IMAGE_STYLE_ID`。
- **codeThemeId**：代码块高亮，如 `vscode-dark`、`monokai`。命令行 `--code-theme` 或 `-c`，环境变量 `WEWORK_CODE_THEME_ID`。

## 3. Steps（执行步骤）

1. 确定样式：用 **预设**（`--preset` 或 `WEWORK_PRESET`）或 **自定义混搭**（`--theme` + `--layout` 等），无指定则用默认（coral-warm + default）。
2. 在本技能目录下运行 **`node wechat-html.js [input.md]`** 得到 HTML，或运行 **`node wechat-copy.js <input.md>`** 直接得到复制页 URL。
3. 若仅生成 HTML：将 HTML 请求 **`POST https://edit.shiker.tech/api/copy`**，Body：`{ "html": "..." }`，取得 `data.url`。
4. 将 `data.url` 交给用户：在浏览器打开该链接 → 页面点击「复制到剪贴板」→ 粘贴到公众号后台。

## 4. API 说明（edit.shiker.tech）

- **接口**：`POST https://edit.shiker.tech/api/copy`
- **请求体**：`Content-Type: application/json`，`{ "html": "完整 HTML 字符串" }`
- **响应**：`{ success: true, data: { id, url } }`；`url` 即为复制页地址。

## 5. 注意点

- 图片：内容中的图片需为可公网访问的 URL，否则公众号内无法显示。
- 本技能目录内 `lib/` 为 Web 端 `src/themes`、`src/utils` 的副本；若 Web 端主题/版式有更新，可酌情同步到本技能 `lib/`。

## 简要流程小结

1. 在本技能目录下执行 **`node wechat-copy.js <input.md>`** 得到复制页 URL（或先 `node wechat-html.js` 再自行 POST）。
2. 把复制页链接交给用户，在浏览器打开后复制再粘贴到公众号。
