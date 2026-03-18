---
name: fetch-archive
description: 通用文章抓取与归档工具。抓取任意 URL（免费/付费/登录墙）的文章全文，转换为结构化 Markdown，并可选转存到乐享知识库。支持 Substack、Medium、知识星球等付费平台的登录态管理。支持 YouTube 视频下载（yt-dlp）、播客音频下载（小宇宙FM等）、音频转录（Whisper）、翻译（中英对照格式），并将音视频和文字稿上传乐享知识库（文字稿使用在线文档格式，支持按块编辑）。关键词触发：抓取文章、获取全文、付费文章、转存知识库、乐享、保存原文、fetch article、归档、YouTube、视频转录、字幕提取、视频下载、播客、podcast、小宇宙、xiaoyuzhou。
---

# 抓取链接内容 & 转存知识库

## 概述

将文章 URL（免费/付费/登录墙）抓取为结构化 Markdown，并自动转存到乐享知识库，实现素材归档和可追溯。

### 最终产出物
1. `<项目子目录>/<原文标题>.md` — 完整文章 Markdown（含图片引用）
2. `<项目子目录>/<原文标题>_meta.json` — 结构化元信息（原文链接、作者、发布时间、抓取时间等）
3. `<项目子目录>/images/` — 所有文章配图
4. 乐享知识库中的文档副本（按天维度归档）

### 文件命名规则（重要）

- **必须使用原文标题命名**，不要用 `article.md` 等通用名称
- 文件名格式：`<原文标题>.md`、`<原文标题>_meta.json`
- 示例：`How Notion uses Custom Agents.md`、`How Notion uses Custom Agents_meta.json`
- 如果标题中包含文件名不合法字符（`/`、`\`、`:`等），替换为 `-`
- 乐享知识库转存时也使用原文标题作为文档标题

## 工作流程

### Step 1：素材收集

#### 抓取方式决策树

根据 URL 类型选择抓取方式（按优先级排列）：

1. **微信公众号文章**（`mp.weixin.qq.com`）→ **必须**用 `fetch_article.py`（`web_fetch` 无法获取图片）
2. **YouTube 视频** → 使用 `yt_download_transcribe.py`（yt-dlp 下载 + Whisper 转录 + AI 翻译），详见下方「YouTube 视频处理」章节
3. **播客音频**（小宇宙 `xiaoyuzhoufm.com`、Apple Podcasts 等）→ yt-dlp 下载音频 + Whisper 转录，详见下方「播客音频处理」章节
4. **付费/登录墙文章** → 用 `fetch_article.py`（Cookie 注入或 CDP 模式）
5. **免费图文文章**（正文含图片/截图/图表）→ **必须**用 `fetch_article.py`（`web_fetch` 只能返回文本，无法提取和下载页面中的图片）
6. **免费纯文字文章**（正文无配图）→ 可用 `web_fetch`，内容不完整时切换 `fetch_article.py`
7. **文字观点** → 直接整理
8. **图片素材** → 分析图片内容

> **⚠️ 关键原则**：`web_fetch` 工具**只能返回文本内容，无法提取和下载页面中的图片**。任何包含图片、截图、图表的文章，都**必须**使用 `fetch_article.py` 抓取，否则图片信息会完全丢失。当不确定文章是否含图时，**默认用 `fetch_article.py`**。

#### 付费/登录墙文章获取

适用于**所有需要登录态才能查看全文的网站**（Substack 付费订阅、Medium 会员、知识星球、财新网、The Information 等），使用 `fetch_article.py` 脚本：

```bash
# Cookie 注入模式（默认，适用于大部分站点）
python scripts/fetch_article.py fetch <URL> --output-dir <项目子目录>

# CDP 模式（适用于需要 Google 账号登录的站点，如 LinkedIn）
python scripts/fetch_article.py fetch <URL> --output-dir <项目子目录> --cdp
```

**两种浏览器模式**：

| 模式 | 参数 | 原理 | 适用场景 |
|------|------|------|----------|
| Cookie 注入 | （默认） | 从 Chrome Cookie DB 提取 cookies → 注入 Playwright 浏览器 | Substack、Medium 等大部分站点 |
| **CDP** | `--cdp` | 通过 Chrome DevTools Protocol 连接用户真实 Chrome（port 9222），复用完整登录态 | **LinkedIn、Google 系网站**等会检测自动化浏览器的站点 |

> **何时必须用 CDP 模式**：当目标网站需要通过 Google 账号登录时（如 LinkedIn "通过 Google 登录"），Google 登录页面会检测 Playwright 自动化浏览器并拒绝登录（报错"此浏览器或应用可能不安全"）。CDP 模式连接的是用户真实的 Chrome 浏览器，完全绕过此检测。

**CDP 模式前置条件**：确保 Chrome 浏览器已开启 CDP 远程调试端口：
```bash
# 启动 Chrome（开启 CDP 远程调试端口 9222）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &

# 验证 CDP 端口可连接
curl -s http://localhost:9222/json/version
```
> 如果 Chrome 已在运行但未开启 CDP，脚本会尝试优雅关闭 Chrome 后以 CDP 模式重启。

**工作原理**：
1. 自动从 Chrome 浏览器的 Cookie 数据库提取目标域名的登录 cookies
2. 将 cookies 注入 Playwright 浏览器上下文
3. 加载页面、滚动加载懒加载内容、下载所有图片
4. 将正文转换为 Markdown（`article.md`），图片保存到 `images/` 子目录
5. 内容提取时自动选择**最长的内容容器**（避免只抓到免费预览区域）

**标题提取增强**（多策略回退）：
1. CSS 选择器优先级：`h1.post-title` > `article h1` > `[class*="title"] h1` > `h1`
2. 回退到 `<meta property="og:title">` → `<meta name="title">` → `document.title`
3. 自动清理标题中的网站后缀（如 `" - Cursor"`、`" | Substack"`）
4. 正文中与已提取标题相同的第一个 `<h1>` 会被自动去重，避免 MD 中标题重复

**作者提取增强**：
- CSS 选择器 + `meta[name="author"]` + `[rel="author"]` + `meta[property="article:author"]` 多策略回退

**微信公众号文章（mp.weixin.qq.com）专项优化**：
脚本对微信公众号文章有专门的检测和处理策略：

1. **自动检测**：识别 `mp.weixin.qq.com` 域名，自动启用微信模式
2. **无需登录**：微信公众号文章是公开可读的，跳过登录检测和 Cookie 注入流程
3. **专用内容选择器**：使用 `#js_content` / `.rich_media_content` 精准定位正文区域（而非通用选择器可能匹配到页面其他内容）
4. **标题提取**：`#activity-name` > `h1.rich_media_title` > 通用 h1 > meta 标签回退
5. **作者提取**：`#js_name`（公众号名称）> `.rich_media_meta_nickname` > 通用选择器回退
6. **日期提取**：`#publish_time` > 通用 time/date 选择器回退
7. **图片懒加载增强**：
   - 微信图片使用 `data-src` + IntersectionObserver 懒加载
   - 滚动速度放慢（300px 步长、200ms 间隔）以确保触发所有 IntersectionObserver
   - 强制将未触发的 `data-src` 复制到 `src`（兜底策略）
   - 图片下载时优先使用 `data-src` 的高清原图 URL
8. **图片格式识别**：微信图片 URL 格式特殊（`mmbiz.qpic.cn/...?wx_fmt=png`），从 `wx_fmt` 查询参数推断文件扩展名
9. **Referer 防盗链**：通过 Playwright 页面上下文的 `page.request.get()` 下载图片，自动携带正确的 Referer 头

**Substack 站点（如 www.lennysnewsletter.com）专项优化**：
脚本对 Substack 托管的站点（`*.substack.com`、`lennysnewsletter.com` 等）有专门的登录检测和**登录态缓存**机制：

1. **登录态缓存**：登录成功后自动保存 Playwright `storage_state` 到 `~/.substack/storage_state.json`，后续抓取直接复用，**无需重复登录和邮箱验证**
2. **优先级**：缓存 `storage_state` > Chrome cookies > 引导登录
3. **自动检测登录状态**：加载页面后检查右上角是否有用户头像（已登录）还是 "Sign in" 按钮（未登录）
4. **已登录** → 直接抓取全文，并刷新缓存延长有效期
5. **缓存过期** → 自动清理旧缓存，进入引导登录流程
6. **未登录** → 打开可见浏览器窗口引导登录，用户在终端输入 `y` 确认后二次验证，通过后自动缓存

**独立登录命令**（推荐首次使用时先执行）：
```bash
python scripts/fetch_article.py login
```
此命令单独完成 Substack 登录并缓存，不需要指定文章 URL。后续所有 Substack 文章抓取都会自动复用此登录态。

**非 Substack 站点的登录确认机制**：
- 无 Chrome cookies 时自动切换到非无头模式，打开可见浏览器窗口
- 终端提示用户完成登录操作后**按回车键**继续
- 收到确认信号后重新加载页面并检测付费墙状态

**付费墙检测**：脚本同时检测以下信号：
- DOM 元素：`[data-testid="paywall"]`、`.paywall`
- 文本关键词：`This post is for paid subscribers`、`Subscribe to read`、`Upgrade to paid` 等
- 注意：不同网站的付费墙 DOM 结构和关键词不同，如遇新网站抓取不完整，需检查页面实际的付费墙标识并更新检测逻辑

**判断内容是否完整的方法**：
- 先用 `web_fetch` 尝试获取，如果明显被截断（内容不完整、出现付费提示），则切换到 `fetch_article.py`
- 抓取完成后**必须**告知用户查看 `article.md` 确认内容完整性
- 关注文章末尾是否有作者署名/总结段落作为完整性标志
- 如果用户反馈内容不完整，检查：(1) 登录账号是否有付费权限 (2) 页面是否有懒加载内容未触发 (3) 内容选择器是否匹配到了免费预览区而非全文区

**产出物**：
- `<项目子目录>/<原文标题>.md` — 完整文章 Markdown（含图片引用）
- `<项目子目录>/<原文标题>_meta.json` — 结构化元信息（原文链接、作者、发布时间、抓取时间等）
- `<项目子目录>/images/` — 所有文章配图

`<原文标题>_meta.json` 格式：
```json
{
  "url": "原文链接",
  "title": "文章标题",
  "subtitle": "副标题",
  "author": "作者",
  "date": "发布时间",
  "content_length": 12345,
  "image_count": 5,
  "images": ["images/img_01_xxx.png", ...],
  "fetched_at": "2026-02-25T10:30:00"
}
```

#### 使用 `web_fetch` 获取的免费文章

对于通过 `web_fetch` 获取到完整内容的免费文章，**同样需要保存原文**：
1. **保存原文全文**：将 `web_fetch` 返回的内容直接保存为 Markdown，**不做总结、不做摘要、不做改写**，保持原文的完整结构和措辞
2. 文件名使用原文标题：`<项目子目录>/<原文标题>.md`
3. 手动构建 `<原文标题>_meta.json`，包含 URL、标题、作者、日期等元信息
4. 如果文章包含图片，尽量下载保存到 `<项目子目录>/images/`

> **关键区分**：`web_fetch` 工具可能会返回总结/摘要版本而非原文全文。如果返回的内容明显是总结（缺少原始段落、引用、细节），需要在 `web_fetch` 调用时明确要求"返回完整原始全文内容，不要总结或缩写"。保存到本地的**必须是原文全文**，而不是经过 AI 总结的摘要。

#### YouTube 视频处理（yt-dlp + Whisper + 翻译 + 乐享）

**当用户提供 YouTube 视频链接时**，使用 `yt_download_transcribe.py` 脚本完成完整的下载-转录-翻译-归档工作流。

**⚠️ 重要**：**不要**使用 `web_fetch`（无法获取视频内容），**不要**使用 NotebookLM（已替换为本地 Whisper 方案，速度更快、无外部依赖）。

**工作流概述**：
1. **yt-dlp 下载视频** → 本地 `.mp4` 文件
2. **ffmpeg 提取音频** → WAV 格式（16kHz 单声道）
3. **Whisper 转录** → 带时间戳的文字稿
4. **AI 翻译**（如果是英文）→ 中英对照格式的 Markdown
5. **上传乐享知识库**：
   - 文字稿：**以在线文档（page）格式上传**，支持后续按块维度编辑更新
   - 视频文件：以文件（file）格式上传
6. **清理**：上传成功后删除本地视频文件

**Step 1：下载 + 转录 + 翻译**

```bash
cd <项目子目录>

# 完整流程（下载 + 转录 + 翻译）
python3 scripts/yt_download_transcribe.py "<YouTube URL>" \
  --output-dir . \
  --whisper-model base

# 常用参数：
#   --whisper-model tiny|base|small|medium|large  转录模型（越大越准但越慢）
#   --skip-download    跳过下载（用于重新转录已下载的视频）
#   --skip-translate   跳过翻译步骤
#   --keep-audio       保留提取的音频文件
```

**产出物**：
- `<视频标题>.mp4` — 下载的视频文件
- `<视频标题>.md` — 文字稿 Markdown（英文视频为中英对照格式）
- `<视频标题>_meta.json` — 视频元信息

**文字稿格式**（英文视频，中英对照）：

```markdown
# 视频标题

**频道**: xxx
**发布日期**: 2026-03-10
**时长**: 15:30
**原始链接**: https://www.youtube.com/watch?v=xxx
**转录语言**: en

---

## 文字稿（中英对照）

> 以下内容采用「英文原文 + 中文翻译」对照排列。

**[00:00]**

This is the original English text from the video...

🇨🇳 这是视频中的中文翻译文本...

---

**[01:23]**

Next paragraph of English text...

🇨🇳 下一段中文翻译...

---
```

**Whisper 模型选择建议**：

| 模型 | 速度 | 精度 | 适用场景 |
|------|------|------|---------|
| `tiny` | 最快 | 较低 | 快速预览、非关键内容 |
| `base` | 快 | 中等 | **默认推荐**，适合大部分场景 |
| `small` | 中等 | 较高 | 口音较重、背景噪音较多 |
| `medium` | 慢 | 高 | 重要内容、需要高精度 |
| `large` | 最慢 | 最高 | 专业内容、学术演讲 |

**Step 2：上传到乐享知识库**

> 通过 lexiang MCP 工具完成上传，流程与 Step 2（普通文章转存乐享）一致。**前提是 lexiang MCP 已连接**（参见 Step 2 的「乐享 MCP 工具的调用方式」章节）。

**文字稿上传**（在线文档 page 类型）：
1. 获取知识库根节点 → 检查/创建日期目录（同上述步骤 1-3）
2. 调用 `entry_import_content`（参数：`space_id`, `parent_id=<日期目录ID>`, `name="<视频标题>"`, `content=<文字稿Markdown内容>`, `content_type="markdown"`）
3. 在线文档支持后续在乐享中按块维度编辑更新（如修正翻译）

**视频文件上传**（file 类型，三步上传）：
1. `file_apply_upload`（参数：`parent_entry_id=<日期目录ID>`, `name="<视频标题>.mp4"`, `size=<文件字节数>`, `mime_type="video/mp4"`, `upload_type="PRE_SIGNED_URL"`）
2. `curl -X PUT "<upload_url>" -H "Content-Type: video/mp4" --data-binary "@<视频文件路径>"`
3. `file_commit_upload`（参数：`session_id=<上一步返回的session_id>`）

**上传成功后**：自动删除本地视频文件（`rm -f <视频文件路径>`），节省磁盘空间。

**依赖**：
- `yt-dlp`（**推荐 `brew install yt-dlp`**，不要用 `pip3 install`）— YouTube 视频下载。必须用 brew 安装以获取最新版本，pip 版本受限于系统 Python 版本（如 Python 3.9 无法安装 nightly 版），而 brew 版自带独立 Python 环境
- `openai-whisper`（`pip3 install openai-whisper`）— 音频转录
- `ffmpeg`（`brew install ffmpeg`）— 音频提取
- `openai`（`pip3 install openai`）— 翻译（需要 `OPENAI_API_KEY` 环境变量）。**如果没有 API Key，可以跳过翻译步骤，由 AI 助手直接在对话中翻译后更新文档**

#### 播客音频处理（yt-dlp + Whisper + 乐享）

**当用户提供播客链接时**（小宇宙FM `xiaoyuzhoufm.com`、Apple Podcasts 等），使用 yt-dlp 下载音频 + Whisper 转录的方式处理。

**⚠️ 重要**：yt-dlp 的 generic extractor 可以从播客页面中自动提取音频 URL（m4a/mp3），**不需要** cookies，也**不需要**专门的播客 extractor。

**工作流概述**：
1. **yt-dlp 下载音频** → 本地 `.m4a` 或 `.mp3` 文件（播客没有视频，直接是音频）
2. **ffmpeg 提取/转换音频** → WAV 格式（16kHz 单声道，Whisper 推荐）
3. **Whisper 转录** → 带时间戳的文字稿
4. **繁简转换**（如需要）→ Whisper base 模型对中文会输出繁体，需用 `opencc` 转为简体
5. **上传乐享知识库**（通过 lexiang MCP 工具）：
   - 文字稿：`entry_import_content` 创建为在线文档（page）格式
   - 音频文件：`file_apply_upload` → `curl PUT` → `file_commit_upload` 三步上传

**Step 1：下载音频**

```bash
cd <项目子目录>

# yt-dlp 直接下载播客音频（不需要 cookies）
yt-dlp --no-playlist -o "%(title)s.%(ext)s" "<播客链接>"
```

> **小宇宙链接格式**：`https://www.xiaoyuzhoufm.com/episode/<episode_id>`
> yt-dlp 会通过 generic extractor 自动从页面中提取 `media.xyzcdn.net` 的音频直链。

**Step 2：提取 WAV + Whisper 转录**

```bash
# 提取 WAV（16kHz 单声道）
ffmpeg -i "<音频文件>.m4a" -vn -acodec pcm_s16le -ar 16000 -ac 1 -y "<音频文件>.wav"

# Whisper 转录（中文播客指定 language=zh）
python3 -c "
import whisper, json, time
model = whisper.load_model('base')
result = model.transcribe('<音频文件>.wav', language='zh', verbose=False)
with open('whisper_segments.json', 'w', encoding='utf-8') as f:
    json.dump(result['segments'], f, ensure_ascii=False, indent=2)
print(f'Done: {len(result[\"segments\"])} segments')
"
```

**Step 3：合并段落 + 繁简转换 + 生成 Markdown**

使用与 YouTube 视频相同的段落合并逻辑（max_gap=2s, max_duration=60s）。

**关键**：Whisper base 模型对中文普通话倾向输出繁体字，必须用 `opencc` 进行繁简转换：
```bash
pip3 install opencc-python-reimplemented
```

```python
import opencc
converter = opencc.OpenCC("t2s")
simplified_text = converter.convert(traditional_text)
```

**文字稿 Markdown 格式**（中文播客）：
```markdown
# 播客标题

**播客**: 节目名称
**平台**: 小宇宙FM
**时长**: 01:03:47
**原始链接**: https://www.xiaoyuzhoufm.com/episode/xxx
**转录语言**: zh

---

## 文字稿

**[00:00]** 第一段转录文本...

**[01:23]** 第二段转录文本...
```

**Step 4：上传到乐享知识库**

与 YouTube 视频处理相同的流程（通过 lexiang MCP 工具完成，**前提是 MCP 已连接**）：
1. 获取知识库根节点 → 检查/创建日期目录
2. 文字稿使用 `entry_import_content` 创建为**在线文档（page 类型）**
3. 音频文件使用三步上传流程（`file_apply_upload` → `curl PUT` → `file_commit_upload`），注意 MIME 类型为 `audio/mp4`（m4a）或 `audio/mpeg`（mp3）

**播客 vs YouTube 的关键区别**：

| 维度 | YouTube 视频 | 播客音频 |
|------|-------------|---------|
| 文件格式 | `.mp4`（视频） | `.m4a`/`.mp3`（纯音频） |
| 文件大小 | 较大（HLS 720p ~500MB） | 较小（~60MB/小时） |
| 下载方式 | 需要 HLS 格式避免 403 | 直接下载，无反爬 |
| cookies | 通常需要 | 不需要 |
| Whisper 语言 | 通常是英文（需翻译） | 通常是中文（需繁简转换） |
| 上传 MIME | `video/mp4` | `audio/mp4` 或 `audio/mpeg` |

**依赖**（额外）：
- `opencc-python-reimplemented`（`pip3 install opencc-python-reimplemented`）— 繁体转简体（Whisper base 模型中文输出为繁体时需要）

#### 结构化分析

输出结构化分析：
```
【文章主题】一句话概括
【核心论点】3-5 个关键观点
【关键数据】文章中的重要数据/图表
【利益相关】作者/机构的立场与潜在倾向（如有）
【原文出处】完整标题 + URL
```

规划图表：第 1 张为总览图，第 2-N 张各聚焦 1 个核心论点。向用户确认图表数量和主题划分。

### Step 2：原文保存到乐享知识库

**在进入信息图生成流程之前，先将原文完整保存到乐享知识库**，确保素材归档和可追溯。

#### 配置文件与初始化

本 skill 的目标知识库等信息通过配置文件管理，**不在 SKILL.md 中硬编码**。

配置文件路径：**`config.json`**（位于 skill 根目录，即与本 SKILL.md 同级）

##### 对话式配置初始化（首次使用时自动触发）

当 `config.json` 中 `_initialized` 为 `false` 或 `space_id` 为空时，**在执行任何乐享操作前**，必须先通过对话引导用户完成配置。

**核心设计**：用户只需要粘贴一个乐享知识库链接，Agent 自动完成所有配置。

**链接格式**：`https://<domain>/spaces/<space_id>?company_from=<company_from>`
- 示例：`https://lexiangla.com/spaces/b6013f6492894a29abbd89d5f2e636c6?company_from=e6c565d6d16811efac17768586f8a025`
- 从链接中可解析出三个关键信息：**域名**（`lexiangla.com`）、**space_id**、**company_from**

---

**流程如下**：

**第一步：检测 MCP 连接**
1. 尝试调用任意一个 lexiang MCP 工具（如 `whoami`）检测 MCP 是否已连接
2. 如果调用成功 → MCP 已连接，进入第二步
3. 如果调用失败（MCP 未连接）→ 引导用户完成 MCP 鉴权：
   ```
   ⚠️ 乐享 MCP 尚未连接。请先完成鉴权配置：

   1. 访问 https://lexiangla.com/mcp 登录后获取 COMPANY_FROM 和 LEXIANG_TOKEN
   2. 按照你使用的 Agent 配置 MCP 连接：
      - CodeBuddy：在 MCP 管理面板中添加 lexiang server
      - OpenClaw：运行 claw install https://github.com/tencent-lexiang/lexiang-mcp-skill
      - 其他 Agent：在 MCP 配置文件中添加 lexiang server
   3. 完成后告诉我，我会继续配置流程。
   ```
   **不要继续后续步骤**，等待用户完成 MCP 连接后重试。

**第二步：请求用户提供知识库链接**
1. 向用户发送引导消息：
   ```
   🔧 首次使用，需要配置目标知识库。

   请粘贴你想用来归档文章的乐享知识库链接，格式如：
   https://lexiangla.com/spaces/xxxxx?company_from=yyyyy

   💡 获取方式：在乐享中打开目标知识库，复制浏览器地址栏中的链接即可。
   ```
2. **等待用户输入**，不要自行猜测或列举知识库

**第三步：解析链接并验证**
1. 从用户提供的链接中用正则解析出三个字段：
   - **domain**：链接的域名部分（如 `lexiangla.com`），用于生成后续访问链接
   - **space_id**：`/spaces/` 后面的路径段（如 `b6013f6492894a29abbd89d5f2e636c6`）
   - **company_from**：`company_from=` 参数值（如 `e6c565d6d16811efac17768586f8a025`）
2. 如果链接格式不正确（缺少 `space_id` 或 `company_from`）→ 提示用户重新粘贴正确的链接
3. 调用 `space_describe_space`（参数：`space_id=<解析出的 space_id>`）验证知识库是否存在
4. 如果验证失败 → 提示用户检查链接是否正确或是否有该知识库的访问权限

**第四步：写入配置并确认**
1. 将解析和验证得到的信息写入 `config.json`：
   - `lexiang.target_space.space_id` = 解析出的 space_id
   - `lexiang.target_space.space_name` = 从 `space_describe_space` 返回值获取的知识库名称
   - `lexiang.target_space.company_from` = 解析出的 company_from
   - `lexiang.access_domain.domain` = 解析出的域名
   - `lexiang.access_domain.page_url_template` = `https://<domain>/pages/{entry_id}`
   - `lexiang.access_domain.space_url_template` = `https://<domain>/spaces/{space_id}?company_from={company_from}`
   - `_initialized` = `true`
2. 向用户确认配置结果：
   ```
   ✅ 配置完成！

   📚 目标知识库：<知识库名称>
   🔗 访问链接：https://<domain>/spaces/<space_id>?company_from=<company_from>

   后续抓取的文章将自动归档到此知识库。如需更换，告诉我「重新配置知识库」即可。
   ```

##### 重新配置

当用户说「重新配置知识库」、「切换知识库」、「更换目标知识库」等类似意图时：
1. 将 `config.json` 中 `_initialized` 设为 `false`
2. 重新执行上述对话式初始化流程（从第一步开始）

##### 用户输入容错

用户可能不会粘贴完美的链接，需要处理以下情况：

| 用户输入 | 处理方式 |
|---------|---------|
| 完整链接 `https://lexiangla.com/spaces/xxx?company_from=yyy` | 直接解析 ✅ |
| 不带 company_from 的链接 `https://lexiangla.com/spaces/xxx` | 提示：「链接中缺少 company_from 参数。请在乐享中重新复制完整链接（地址栏中通常会包含 ?company_from=xxx），或者访问 https://lexiangla.com/mcp 获取你的 COMPANY_FROM 值告诉我。」|
| 纯 space_id `b6013f6492894a29abbd89d5f2e636c6` | 提示：「请提供完整的知识库链接（包含 company_from 参数），我需要从链接中同时获取知识库 ID 和企业标识。」|
| 页面链接 `https://lexiangla.com/pages/xxx` | 提示：「这是一个页面链接，请提供知识库链接（格式：https://lexiangla.com/spaces/xxx?company_from=yyy）。你可以在乐享中进入目标知识库首页，复制地址栏链接。」|

##### 配置结构

```json
{
  "_initialized": false,
  "lexiang": {
    "target_space": {
      "space_id": "",
      "space_name": "",
      "company_from": ""
    },
    "access_domain": {
      "domain": "lexiangla.com",
      "page_url_template": "https://lexiangla.com/pages/{entry_id}",
      "space_url_template": "https://lexiangla.com/spaces/{space_id}?company_from={company_from}"
    }
  }
}
```

> **`access_domain` 会从用户粘贴的链接中自动提取域名**，无需手动配置。适配自定义域名的乐享部署。

后续文档中所有 `<SPACE_ID>`、`<COMPANY_FROM>`、`<ACCESS_DOMAIN>` 等占位符，均指从 `config.json` 中读取的实际值。

#### 乐享 MCP 工具的调用方式（重要 — 多 Agent 适配）

本 skill 需要服务多个 Agent 产品（OpenClaw、CodeBuddy、Claude Desktop 等）。不同 Agent 连接乐享 MCP 的方式不同，但**暴露的工具名称和参数完全一致**（都是 lexiang MCP server 提供的标准工具）。

> **核心原则**：本 skill 只描述「调用哪个工具 + 传什么参数」，**不规定具体的 MCP 调用语法**。每个 Agent 按自己的方式调用即可。

**各 Agent 产品的 MCP 连接方式**：

| Agent 产品 | lexiang MCP 连接方式 | 工具调用方式 |
|-----------|---------------------|-------------|
| **CodeBuddy** | 在 `~/.codebuddy/mcp.json` 中配置 lexiang server，通过 IDE 的 MCP 管理面板启用连接 | 直接调用 `space_describe_space`、`file_apply_upload` 等 lexiang MCP 工具 |
| **OpenClaw** | `claw install https://github.com/tencent-lexiang/lexiang-mcp-skill`，加载 skill 时自动连接 MCP | 同上，通过 skill 暴露的 MCP 工具调用 |
| **Claude Desktop / 其他 MCP 兼容 Agent** | 在 Agent 的 MCP 配置文件中添加 lexiang server URL | 同上 |

**MCP 连接检测与降级**：

在执行乐享操作前，**必须先检测 lexiang MCP 是否已连接**：
1. 读取 `config.json`，检查 `_initialized` 和 `lexiang.target_space.space_id`
2. 如果未初始化 → 先触发对话式配置初始化（参见上方「对话式配置初始化」），初始化流程中会自动完成 MCP 连接检测
3. 如果已初始化，尝试调用 `space_describe_space`（参数：`space_id=<config 中的 space_id>`）验证 MCP 连接
4. 如果调用成功 → MCP 已连接，继续后续流程
5. 如果调用失败（MCP 未连接）→ **提示用户检查 MCP 连接**，给出对应 Agent 的操作指引：
   - CodeBuddy：「请在 MCP 管理面板中确认 lexiang server 已启用并显示为已连接状态」
   - OpenClaw：「请确认已安装 lexiang skill（`claw install https://github.com/tencent-lexiang/lexiang-mcp-skill`）」
   - 其他 Agent：「请确认 MCP 配置中已添加 lexiang server」

> **⚠️ 禁止降级为 curl 调用 REST API**：即使 MCP 未连接，也**不要**自行编写 curl 调用乐享 REST API，因为：(1) 认证信息硬编码在 curl 中不安全；(2) 不同 Agent 的执行环境差异大，curl 方式不通用；(3) REST API 的 URL 格式和鉴权方式可能变化。应该引导用户修复 MCP 连接。

**认证配置**（首次使用时需要）：

1. 访问 [https://lexiangla.com/mcp](https://lexiangla.com/mcp) 登录后获取 **`LEXIANG_TOKEN`**（访问令牌，格式：`lxmcp_xxx`）
   > `COMPANY_FROM` 无需手动获取 — 会从用户粘贴的知识库链接中自动解析

2. 配置方式（二选一）：
   - **环境变量**（推荐）：`export LEXIANG_TOKEN="lxmcp_xxx"`
   - **直接修改 MCP 配置**：将 MCP server URL 中的 `${LEXIANG_TOKEN}` 占位符替换为实际值

3. 详细配置步骤参见：[lexiang-mcp-skill setup.md](https://github.com/tencent-lexiang/lexiang-mcp-skill/blob/main/setup.md)

#### 目标知识库

从 `config.json` 的 `lexiang.target_space` 中读取：

- **知识库名称**：`config.lexiang.target_space.space_name`
- **知识库访问链接**：按 `config.lexiang.access_domain.space_url_template` 格式拼接
- **Space ID**：`config.lexiang.target_space.space_id`

> **⚠️ 访问链接域名**：用户可访问的乐享前端域名从 `config.lexiang.access_domain.domain` 读取（默认为 `lexiangla.com`），**不是** `mcp.lexiang-app.com`（后者是 MCP API 服务端域名，浏览器无法直接访问）。所有展示给用户的链接必须按 `config.lexiang.access_domain.page_url_template` 格式生成。

#### 目录组织方式

按**天维度**组织目录：
```
知识库根目录/
  2026-02-25/
    文章标题A.pdf  (图文文章，文件上传)
    文章标题B      (纯文本文章，在线文档 page 类型)
  2026-02-26/
    文章标题C.pdf
```

#### 操作流程

通过 lexiang MCP 工具，按以下步骤完成转存：

**步骤 0：读取配置（含初始化检测）**
- 读取 skill 目录下的 `config.json` 文件
- 检查 `_initialized` 是否为 `true` 且 `lexiang.target_space.space_id` 非空
- 如果**未初始化**（`_initialized` 为 `false` 或 `space_id` 为空）→ **触发对话式配置初始化流程**（参见上方「对话式配置初始化」），完成后再继续
- 提取 `lexiang.target_space.space_id`、`lexiang.access_domain.page_url_template` 等配置项

**步骤 1：获取知识库根节点**
- 调用 `space_describe_space`（参数：`space_id=<config 中的 SPACE_ID>`）
- 从返回结果中提取 `root_entry_id`

**步骤 2：检查/创建当天日期目录**
- 调用 `entry_list_children`（参数：`parent_id=<root_entry_id>`）查询根目录下的子条目
- 查找是否已存在以当天日期命名（如 `2026-03-18`）的 `folder` 类型条目
- 如不存在，调用 `entry_create_entry`（参数：`parent_entry_id=<root_entry_id>`, `name="2026-03-18"`, `entry_type="folder"`）创建

**步骤 3：去重检查**
- 调用 `entry_list_children`（参数：`parent_id=<日期目录ID>`）查询该日期目录下已有的条目
- 按「名称 + 类型」检查是否已存在同名文档，如果已存在则跳过上传并告知用户

**步骤 4：图文检测与上传**

检查 `<原文标题>.md` 文件同目录下是否存在 `images/` 目录且包含图片文件：

- **有图片（图文文章）** → 先调用 `scripts/md_to_pdf.py` 将 Markdown 转换为 PDF（嵌入图片），然后通过三步上传流程上传 PDF：
  1. `file_apply_upload`（参数：`parent_entry_id=<日期目录ID>`, `name="<原文标题>.pdf"`, `size=<文件字节数>`, `mime_type="application/pdf"`, `upload_type="PRE_SIGNED_URL"`）
  2. 使用 `curl -X PUT` 将 PDF 文件上传到返回的 `upload_url`（这是预签名 URL 直传 COS，不涉及认证信息）
  3. `file_commit_upload`（参数：`session_id=<上一步返回的session_id>`）

- **无图片（纯文本文章）** → 使用 `entry_import_content` 创建为**在线文档（page 类型）**：
  - 参数：`space_id=<config 中的 SPACE_ID>`, `parent_id=<日期目录ID>`, `name="<原文标题>"`, `content=<Markdown文件内容>`, `content_type="markdown"`
  - 在线文档支持在乐享中直接编辑

**步骤 5：输出结果**
- 按 `config.json` 中的 `lexiang.access_domain.page_url_template` 格式拼接文档链接，告知用户
- 示例：`https://lexiangla.com/pages/<entry_id>`（域名从配置读取，**不要**硬编码）

#### 注意事项

- **配置初始化是前置条件**：首次使用时会自动通过对话引导完成知识库配置，无需手动编辑文件
- **MCP 连接是前置条件**：必须先确认 lexiang MCP 已连接才能执行操作。不同 Agent 的连接方式不同，参见上方「乐享 MCP 工具的调用方式」
- **访问链接域名**：展示给用户的链接一律按 `config.json` 中 `page_url_template` 格式生成，**不要**使用 `mcp.lexiang-app.com`
- **上传前自动去重**：按「文档名称 + 文档类型」在目标日期目录下查重，避免重复上传
- 图文文章自动转为 PDF 上传（嵌入图片），确保知识库中保留完整图文信息
- 纯文本文章以**在线文档（page）**格式创建，可在乐享中直接编辑
- PDF 转换依赖 `pymupdf` 库（`pip3 install pymupdf`），如未安装则回退为在线文档方式上传 Markdown
- 如果同一天多次处理不同文章，它们会归入同一个日期目录下
- 使用 `_mcp_fields` 参数可以减少返回数据量，如 `_mcp_fields=["id", "root_entry_id", "name"]`

## 脚本文件

| 文件 | 用途 |
|------|------|
| `scripts/fetch_article.py` | 付费/登录墙文章全文抓取脚本（Chrome cookies + Playwright，Substack 登录态缓存，输出 Markdown + 图片 + 元信息 JSON） |
| `scripts/md_to_pdf.py` | Markdown 转 PDF 脚本（使用 pymupdf，嵌入本地图片，正确渲染中文，支持标题回退和拆行标题修复） |
| `scripts/yt_download_transcribe.py` | YouTube 视频下载 + Whisper 转录 + AI 翻译脚本（yt-dlp 下载、ffmpeg 提取音频、Whisper 转录、OpenAI 翻译为中英对照 Markdown）。也可用于播客音频转录（跳过视频下载步骤） |

> **注意**：乐享知识库操作不再通过独立脚本（`save_to_lexiang.sh`/`upload_yt_to_lexiang.sh`）完成，而是由大模型通过 **lexiang MCP 工具**直接执行。不同 Agent 产品（OpenClaw、CodeBuddy、Claude Desktop 等）各自管理 MCP 连接，但调用的工具名称和参数完全一致。

## 经验总结

### YouTube 视频下载与转录

**核心方案**：yt-dlp 下载 → ffmpeg 提取音频 → Whisper 本地转录 → OpenAI API 翻译

**为什么不用 NotebookLM / summarize.sh**：
1. NotebookLM 需要 Google 账号且有额度限制，部分视频可能因版权限制无法提取
2. summarize.sh 依赖外部 API（Apify/YouTube 字幕 API），部分视频无字幕时无法工作
3. Whisper 本地转录**不依赖字幕**，直接从音频波形识别语音，覆盖率 100%

**yt-dlp 版本与安装（关键！）**：
- **必须使用 `brew install yt-dlp`** 安装，不要用 `pip3 install yt-dlp`
- 原因：pip 版本受限于系统 Python 版本（macOS 自带 Python 3.9），无法安装 yt-dlp 的 nightly 版本（需要 Python 3.10+）。而 YouTube 频繁更新反爬策略，旧版 yt-dlp 会遇到 HTTP 403 Forbidden 错误
- brew 安装的 yt-dlp 自带独立 Python 环境，始终能获取最新版本
- 脚本中调用方式：直接用 `yt-dlp` 命令，**不要**用 `python3 -m yt_dlp`

**YouTube DASH 格式 403 错误（重要！）**：
- YouTube 正在强制使用 SABR（Streaming ABR）流媒体协议，传统 DASH 分片下载（`bestvideo+bestaudio`）会触发 HTTP 403 Forbidden
- **解决方案**：优先使用 HLS（m3u8）格式下载，不会被 SABR 拦截
- 脚本中的格式选择顺序：`95-1/94-1/93-1/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best`
  - `95-1`: 720p HLS（推荐，画质和文件大小的最佳平衡）
  - `94-1`: 480p HLS
  - `93-1`: 360p HLS
  - 后面是传统 DASH 格式作为回退
- HLS 格式下载的视频文件会比 DASH 大一些（720p HLS 约 500-600MB vs DASH 约 200-300MB）
- **注意**：`--extractor-args "youtube:player_client=android"` 不支持 cookies，不是可靠的 403 解决方案

**Whisper 转录最佳实践**：
- 音频预处理：16kHz 采样率、单声道 WAV（`ffmpeg -ar 16000 -ac 1`），减少文件大小且是 Whisper 推荐格式
- 段落合并策略：相邻 segment 间隔 <2s 且总时长 <60s 则合并，句号/问号结尾时倾向断开
- 模型选择：默认用 `base`（速度和精度的最佳平衡），重要内容用 `small` 或 `medium`

**翻译策略**：
- 使用 OpenAI `gpt-4o-mini`，分批翻译（每批 10 段），避免 token 超限
- 翻译 prompt 要求"自然流畅的中文表达，专业术语保留英文并附中文注释"
- 中英对照格式：每段先展示英文原文，紧跟中文翻译（以 🇨🇳 前缀标识），段间用分隔线
- **如果没有 OPENAI_API_KEY**：脚本会跳过翻译步骤，输出纯英文文字稿。此时可以由 AI 助手在对话中直接翻译全文，然后用 `md_to_page.py --entry-id` 更新乐享文档

**上传乐享的关键决策**：
- 文字稿使用 **在线文档（page）格式**而非文件上传，原因：支持在乐享中按块维度编辑更新，可以逐段修正翻译或补充注释
- 视频使用 **文件（file）格式**上传，因为视频不需要在线编辑
- 上传成功后自动删除本地视频文件，避免占用磁盘空间

**视频上传到乐享的正确方式（重要！）**：
- 通过 lexiang MCP 工具完成，使用三步上传流程：
  1. `file_apply_upload`：申请上传凭证（传入 `parent_entry_id`=日期目录 ID、`upload_type`=PRE_SIGNED_URL、`mime_type`=video/mp4、`size`=文件字节数）
  2. `curl -X PUT` 上传文件到返回的 `upload_url`（预签名 URL，直传 COS）
  3. `file_commit_upload`：确认上传完成（传入 `session_id`）
- 518MB 视频的 PUT 上传约需 30-60 秒

### 播客音频转录

**核心方案**：yt-dlp（generic extractor）下载音频 → ffmpeg 转 WAV → Whisper 转录 → opencc 繁简转换

**yt-dlp 对小宇宙的支持**：
- yt-dlp 没有小宇宙专用 extractor，但 **generic extractor 完全够用**
- 小宇宙页面中嵌入了 `<audio>` 标签，音频直链在 `media.xyzcdn.net`
- 下载不需要 cookies，直接用 `yt-dlp --no-playlist -o "%(title)s.%(ext)s" <URL>` 即可
- 下载速度约 7MB/s，63 分钟播客（59MB）仅需 8 秒

**Whisper 中文转录的繁体问题（重要！）**：
- Whisper base 模型对中文普通话**倾向输出繁体字**（如「歡迎」→ 应为「欢迎」）
- 这是 Whisper 的已知行为，因为训练数据中繁体中文比重较大
- **解决方案**：转录后用 `opencc-python-reimplemented` 的 `t2s`（Traditional to Simplified）模式批量转换
- 安装：`pip3 install opencc-python-reimplemented`
- 用法：`opencc.OpenCC("t2s").convert(text)`

**中文播客 vs 英文 YouTube 的流程差异**：
- 中文播客**不需要翻译**，但**需要繁简转换**
- 播客音频是直接的 m4a/mp3 文件，**不需要从视频中提取音频**（但仍需 ffmpeg 转为 WAV 格式给 Whisper）
- Whisper 转录时**指定 `language='zh'`** 可以提高中文识别准确率
- 上传乐享时 MIME 类型用 `audio/mp4`（m4a）或 `audio/mpeg`（mp3），不是 `video/mp4`

**转录性能参考**：
- 63 分钟中文播客 → Whisper base 模型在 CPU 上转录耗时约 115 秒
- 产出 2496 个 segments，合并后 65 个段落

### 微信公众号图文抓取

**核心问题**：`web_fetch` 工具无法获取微信公众号文章的图片（懒加载 + 防盗链），**必须**使用 `fetch_article.py`。

**技术原理**：
1. **懒加载机制**：微信图片的真实 URL 存放在 `data-src` 而非 `src`，依赖 `IntersectionObserver` 在元素进入视口时才加载。Playwright 无头浏览器通过 `window.scrollBy(0, 300)` 配合 `asyncio.sleep(0.2)` 模拟慢速滚动，逐步触发所有图片的懒加载观察器
2. **兜底策略**：滚动完成后，通过 `page.evaluate()` 遍历所有 `img[data-src]`，将未被触发的 `data-src` 强制复制到 `src`
3. **高清图优先**：提取图片 URL 时优先使用 `data-src`（高清原图），而非 `src`（可能是低分辨率占位图）
4. **格式识别**：微信图片 URL 无常规扩展名（如 `mmbiz.qpic.cn/...?wx_fmt=png`），需解析 `wx_fmt` 查询参数推断文件格式
5. **防盗链绕过**：通过 Playwright 页面上下文的 `page.request.get()` 下载图片，自动携带正确的 Referer 头
6. **专用选择器**：微信文章有固定 DOM 结构（`#js_content`、`#activity-name`、`#js_name`、`#publish_time`），使用专用选择器比通用选择器更精准可靠

**关键决策**：
- 微信文章是公开可读的，跳过登录检测和 Cookie 注入流程
- 滚动参数（300px 步长、200ms 间隔）经实测可平衡速度与懒加载触发成功率
- Markdown 转换时 `imageMap` 同时匹配 `src` 和 `data-src`，确保无论 HTML 中引用哪个属性都能正确替换

**验证标准**：抓取完成后检查 `article_meta.json` 中的 `image_count` 字段，与原文图片数量比对，确认无遗漏。

### 新平台适配思路

适配新平台时，需依次识别和处理以下 4 个维度：
1. **懒加载机制** — 图片是否用 `data-src`、`data-lazy` 等延迟加载？需要怎样的滚动策略触发？
2. **专用 DOM 结构** — 正文、标题、作者、日期的选择器是什么？
3. **图片 URL 格式** — 扩展名是否在路径中？是否需要从查询参数推断？
4. **防盗链策略** — 是否需要正确的 Referer？是否有其他鉴权机制？

### Python 兼容性

脚本使用 `from __future__ import annotations` 以兼容 Python 3.9（`str | None` 联合类型语法在 3.9 中不可用）。

## 常见问题

| 问题 | 原因 | 修复方法 |
|------|------|----------|
| YouTube 视频下载 HTTP 403 Forbidden | yt-dlp 版本过旧 + YouTube 强制 SABR 流媒体协议，传统 DASH 分片下载被拦截 | ① `brew install yt-dlp` 升级到最新版（不要用 pip）；② 脚本已配置优先使用 HLS(m3u8) 格式（`95-1/94-1/93-1`），自动回退 |
| `pip3 install --upgrade yt-dlp` 无法安装最新版 | macOS 自带 Python 3.9，yt-dlp nightly 版需要 Python 3.10+ | 改用 `brew install yt-dlp`，brew 版自带独立 Python 环境 |
| 脚本中 `python3 -m yt_dlp` 调用失败 | pip 安装的旧版 yt-dlp 与 brew 安装的新版不一致 | 脚本已修改为直接调用 `yt-dlp` 命令（brew 安装的版本） |
| 视频上传乐享报"不支持的文件格式" | 旧版 COS API（`/kb/files/upload-params`）不识别视频格式 | 通过 lexiang MCP 工具使用三步上传流程：`file_apply_upload` → `curl PUT` → `file_commit_upload` |
| Whisper 转录速度极慢 | 模型太大或音频太长 | 换用 `tiny` 或 `base` 模型；对于长视频（>1h），考虑用 `--whisper-model tiny` 先快速预览 |
| 翻译结果为空 | 未设置 `OPENAI_API_KEY` 环境变量 | `export OPENAI_API_KEY=sk-xxx`；或使用 `--skip-translate` 跳过翻译，由 AI 助手在对话中直接翻译全文后用 `md_to_page.py --entry-id` 更新乐享文档 |
| 中英对照格式段落错位 | AI 翻译返回的段落数与原文不匹配 | 脚本已有容错处理（缺少翻译的段落会跳过），可手动补充翻译 |
| 视频上传乐享超时 | 视频文件过大（>500MB）| 使用 MCP 的 `file_apply_upload` 预签名 URL 方式上传，518MB 文件约 30-60 秒即可完成 |
| Whisper 中文转录输出繁体字 | Whisper base 模型对中文普通话倾向输出繁体 | 用 `opencc-python-reimplemented` 的 `t2s` 模式进行繁简转换：`opencc.OpenCC("t2s").convert(text)` |
| 小宇宙播客下载提示 generic extractor | yt-dlp 没有小宇宙专用 extractor | 正常现象，generic extractor 能自动从页面提取音频直链（`media.xyzcdn.net`），下载完全正常 |
| 微信文章图片丢失 | `web_fetch` 无法触发懒加载和绕过防盗链 | **必须**使用 `fetch_article.py`，脚本自动检测微信域名并启用专用处理策略 |
| 乐享知识库操作失败 | MCP 连接异常或 Token 过期 | ① 确认当前 Agent 的 lexiang MCP 已连接（CodeBuddy 检查 MCP 面板、OpenClaw 检查 skill 安装状态）；② Token 过期时访问 https://lexiangla.com/mcp 获取新 Token 并更新 MCP 配置 |
| 文件上传到了知识库根目录而非日期目录 | 跳过了步骤 2（创建日期目录）和步骤 3（去重检查），直接以 `root_entry_id` 作为 `parent_entry_id` 上传 | 严格按照步骤 1→2→3→4 顺序执行，步骤 2 中先 `entry_list_children` 检查日期目录是否存在，不存在则创建 |
| 展示给用户的乐享链接无法访问 | 使用了 MCP API 域名 `mcp.lexiang-app.com` 而非用户可访问的前端域名 | 所有展示给用户的链接必须按 `config.json` 中 `page_url_template` 格式生成（默认为 `https://lexiangla.com/pages/<entry_id>`） |
| PDF 中缺少标题 | `fetch_article.py` 的 `processNode` 将正文 `<h1>` 转为 `# 标题`，与手动拼接的元信息头标题重复；某些网站（如 Lenny's Newsletter）标题在 `articleEl` 外部导致 MD 文件第一行 `# ` 为空 | 已修复：(1) `processNode` 中自动去重正文中与已提取 title 相同的第一个 h1 (2) 标题提取增加 `og:title`、`meta[name="title"]`、`document.title` 多策略回退 (3) `md_to_pdf.py` 增加标题回退——当 MD 中无有效 h1 时从 `article_meta.json` 补充 |
| PDF 中缺少子标题 | 某些网站的 HTML 结构导致 `### # 从 Tab 到 Agents` 被拆为两行：`### #` 和 `从 Tab 到 Agents`，`parse_markdown` 将 `#` 视为无效标题丢弃 | 已修复：`parse_markdown` 增加拆行标题检测——当标题文字为 `#` 或空时，检查下一行是否为实际标题文字并合并 |
