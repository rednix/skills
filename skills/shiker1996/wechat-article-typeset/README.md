# OpenClaw 中使用本技能

## 加载方式

本技能放在**工作区**目录 `.openclaw/skills/wechat-article-typeset/` 下，在 OpenClaw 中打开本仓库（`wework`）时，会按工作区技能优先加载。

- 若未自动加载：确认 OpenClaw 的「工作区」或「当前目录」为本项目根目录。
- 全局使用：可把整个 `wechat-article-typeset` 目录复制到 `~/.openclaw/skills/`，则任意工作区都会加载。

## 触发方式

`SKILL.md` 中已配置 `trigger`，当用户输入包含以下关键词时会激活本技能：

- 公众号排版  
- 复制到公众号  
- edit.shiker.tech  
- 公众号文章  

也可在对话中直接说「帮我排成公众号格式并生成复制链接」等。

## 可选配置（Gate / 专属 Agent）

若希望仅在某些场景或某个 Agent 下启用，可在 OpenClaw 配置中为该技能设置 gate 或 agents，例如：

```yaml
skills:
  wechat-article-typeset:
    enabled: true
    # gate:
    #   keywords: ["公众号", "排版"]
    # agents: ["your-agent-name"]
```

## 主题混搭

- **预设**：`node wechat-html.js --list-presets` 或 `node wechat-copy.js --list-presets` 查看全部。使用：`--preset 墨色下划线`、`--preset 青绿左边线` 等（环境变量 `WEWORK_PRESET`）。
- **自定义混搭**：任意主题 + 任意版式，例如 `--theme teal-fresh --layout leftline`（或 `-t` / `-l`）。`--list-themes`、`--list-layouts` 列出可用 id。
- **图片 / 代码主题**：`--image-style rounded`、`--code-theme monokai`（或环境变量）。

## 技能目录内的 JS（自包含，不依赖仓库 src/）

- **lib/**：为 Web 端 `src/themes`、`src/utils` 的副本，仅在本技能目录使用。
- **presets.js**：主题+版式预设（如 暖色色块、墨色下划线、紫调渐变）；**opts.js**：解析 `--preset`、`--theme`、`--layout` 等。
- **wechat-html.js**：读入 Markdown（文件或 stdin），输出公众号排版用 HTML；支持上述选项。
- **wechat-copy.js**：读入 Markdown 文件，生成 HTML 并 POST 到 edit.shiker.tech，输出复制页 URL；支持上述选项。

复制到 `~/.openclaw/skills/` 后，**无需配置 WEWORK_REPO**，直接在技能目录下执行即可。

## 依赖

- Node.js（支持 ES Module）。
- 网络：需能请求 `https://edit.shiker.tech/api/copy` 以获取复制页链接。
