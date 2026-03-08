---
name: asr-sentence-recognition
description: >
  Skill for Tencent Cloud ASR (Automatic Speech Recognition). Provides three recognition modes:
  (1) SentenceRecognition for short audio ≤60s, (2) Flash ASR for fast synchronous recognition
  of audio ≤2h/100MB, (3) CreateRecTask for async recognition of long audio ≤5h.
  Use when: recognizing/transcribing speech from audio files, converting voice to text, speech
  recognition, generating subtitles, meeting transcription, or any audio-to-text tasks.
  Supports Chinese, English, Cantonese, Japanese, and 20+ other languages.
---

# 腾讯云语音识别 Skill

## 功能描述

本 Skill 提供**三种语音识别**能力，覆盖从短音频到超长录音的全场景需求：

| 场景 | API | 脚本 | 音频限制 | 返回方式 |
|------|-----|------|----------|----------|
| 短音频 | SentenceRecognition | `main.py` | ≤60s, ≤3MB | 同步 |
| 长音频极速 | Flash ASR | `flash_recognize.py` | ≤2h, ≤100MB | 同步 |
| 超长音频 | CreateRecTask | `file_recognize.py` | ≤5h (URL) / ≤5MB (上传) | 异步轮询 |

### 支持特性

- **多语种**：中文普通话、英语、粤语、日语、韩语、法语、德语等 20+ 语种
- **多方言**：上海话、四川话、武汉话、南京话等 23 种方言
- **多格式**：wav、pcm、ogg-opus、speex、silk、mp3、m4a、aac、amr、flv、mp4、wma、3gp、flac
- **自动安装依赖**：首次运行时自动安装所需 SDK
- **智能凭证检测**：优先从环境变量获取密钥，仅在未配置时提示用户开通
- **自动格式检测**：根据文件扩展名自动推断音频格式

### 🎯 选择规则

```
先用 inspect_audio.py 探测元数据（时长 / 采样率 / 声道数）
如果输入是公网 URL 且已经是 16kHz 单声道：
  短音频（满足一句话识别限制） →  main.py（URL）
  60s < 音频 ≤ 5h  →  file_recognize.py（URL）
  音频 > 5h  →  转本地处理链
如果输入是本地文件，或 URL 需要转码：
  先用 FFmpeg 转为 16kHz 单声道 WAV
  短音频（满足一句话识别限制） →  main.py
  单文件满足 Flash 限制  →  flash_recognize.py
  超限  →  切片后逐片 flash_recognize.py
```

### 🔌 可作为 CLI transcription backend（如 OpenClaw）

当用户要把腾讯云 ASR 接入某个支持自定义 CLI transcription 的宿主系统时：

- 直接优先复用 `scripts/cli_transcribe.py`
- 宿主只应拿到**纯文本转写结果**
- 不要把这件事理解成“依赖渠道自带转文字”或“让多模态模型直接听音频”

命中 **OpenClaw**、**CLI transcription**、**audio backend**、**voice note transcription backend** 等场景时，继续阅读 [references/cli_transcription_backend.md](references/cli_transcription_backend.md)。

> **🕵️ 音频时长与脚本选择策略（Agent 必读）**
> 1. **首选 `ffprobe`**：必须优先执行 `python3 <SKILL_DIR>/scripts/inspect_audio.py "<AUDIO_INPUT>"`。该脚本会优先调用 `ffprobe`，因为它能稳定获取时长、采样率、声道数、编码格式，这是本 Skill 做脚本选择和预检的首选依据。
> 2. **有限降级**：如果机器上没有 `ffprobe`，探测脚本会自动尝试 macOS 自带的 `afinfo`；对于 `.wav` 文件，还会自动尝试 Python `wave` 库。降级模式只能覆盖部分格式，不能替代 `ffprobe`。
> 3. **不要再用文件大小“盲猜”时长**：严禁使用 `<1.5MB≈60s`、`<100MB 直接走 Flash` 这类经验规则。它会导致脚本选择错误，也会在本可用 `main.py` 的场景里不必要地向用户多要一个 `AppId`。
> 4. **公网 URL 且已合规时，优先 URL 路径**：如果输入本来就是公网可下载 URL，且探测结果表明它已经是 `16kHz` 单声道，那么默认不要先下载切片；优先考虑 `main.py`（短音频）或 `file_recognize.py`（其余 URL 场景）。
> 5. **安装 FFmpeg 也应优先后台自治完成**：当 `inspect_audio.py` 明确返回 `requires_ffprobe_or_ffmpeg`，或确实需要做格式转换而系统中没有 `ffmpeg` / `ffprobe` 时，Agent 必须先执行 `python3 <SKILL_DIR>/scripts/ensure_ffmpeg.py --execute`，优先使用本机已有包管理器自动安装。只有当自动安装被权限、包管理器缺失或网络环境阻塞时，才参考 [references/ffmpeg_guide.md](references/ffmpeg_guide.md) 用最小化的话术向用户请求协助。
> 6. **本地大文件默认不要先要求 COS**：只有在最终确定必须走异步 URL 接口、且用户手里又没有公网可下载 URL 时，才可以告诉用户需要提供可下载链接。不要一上来就要求用户配置 COS。
> 7. **命中特殊分流时再读详细规则**：如果输入是公网 URL、音频超过 60 秒、文件可能超过 3MB/100MB、需要决定 body vs URL，或需要判断是否切片，必须继续阅读 [references/routing_strategy.md](references/routing_strategy.md)。

## 环境配置指引（Agent 必读）

本 Skill 需要腾讯云 API 密钥 `SECRET_ID`、`SECRET_KEY` 才能正常工作。
> ⚠️ **注意**：使用极速版（`flash_recognize.py`）**额外需要** `TENCENTCLOUD_APPID` 环境变量。

### 🔑 智能凭证检测与自动配置（零代码干扰原则）

当检测到缺少 `TENCENTCLOUD_SECRET_ID`、`TENCENTCLOUD_SECRET_KEY`（或极速版缺失 `TENCENTCLOUD_APPID`）时，Agent **必须**遵循以下原则：

1. **白话沟通**：直接用自然语言告诉用户需要哪些密钥，例如：“为了进行语音识别，我需要您的腾讯云 SecretId 和 SecretKey（如果是极速版还需要 AppId）。请提供给我，我会帮您配置好。”
2. **隐藏技术细节**：**严禁**向用户解释如何使用 `export`、修改 `~/.zshrc`、`环境变量` 等技术词汇。不要把任何 Bash 命令或底层配置逻辑透露给用户，以免造成困惑。
3. **单次执行优先“当前命令注入”**：当用户刚提供密钥、且你只是要继续当前一次识别任务时，**不要**先去写 `~/.bashrc`、`~/.zshrc` 再 `source`。优先把密钥直接注入到当前执行命令或当前子进程环境里，让下一条识别命令立即可用。
4. **自主后台配置**：只有当你明确需要“后续会反复调用，且希望跨 shell 持久生效”时，才考虑写入配置文件。请参考以下针对不同系统的配置代码（**仅限 Agent 后台查阅使用，绝对不要把这些代码展示给用户，也不要转述成“请你执行以下命令”**）：

   **Linux / macOS：**
   ```bash
   export TENCENTCLOUD_SECRET_ID="用户的SecretId"
   export TENCENTCLOUD_SECRET_KEY="用户的SecretKey"
   export TENCENTCLOUD_APPID="用户的AppId"    # 仅极速版需要
   ```
   如需持久化（Agent 可根据情况后台执行）：
   ```bash
   echo 'export TENCENTCLOUD_SECRET_ID="用户的SecretId"' >> ~/.zshrc
   echo 'export TENCENTCLOUD_SECRET_KEY="用户的SecretKey"' >> ~/.zshrc
   echo 'export TENCENTCLOUD_APPID="用户的AppId"' >> ~/.zshrc
   source ~/.zshrc
   ```

   **Windows (PowerShell)：**
   ```powershell
   $env:TENCENTCLOUD_SECRET_ID = "用户的SecretId"
   $env:TENCENTCLOUD_SECRET_KEY = "用户的SecretKey"
   $env:TENCENTCLOUD_APPID = "用户的AppId"
   ```

5. **简洁反馈**：配置完成后，只需轻描淡写地反馈：“配置成功，现在为您开始识别”，然后直接进入语音识别流程环节。

> ⚠️ **安全提示**：Agent 在后台配置时，切勿将密钥硬编码在工作区代码中。

## Agent 执行指令（必读）

> ⚠️ **本节是 Agent（AI 模型）的核心执行规范。当用户提供音频并请求语音识别时，Agent 必须严格按照以下步骤自主执行，无需询问用户确认。**

### 🔑 通用执行规则

1. **触发条件**：用户提供了音频文件或音频 URL，且用户意图为语音转文本。
2. **零交互原则**：Agent 应直接执行脚本，不要向用户询问任何确认。
3. **先探测再识别**：先运行 `inspect_audio.py` 获取时长、采样率、声道数，再根据上方「选择规则」自动选择脚本。
4. **⛔ 禁止使用大模型自身能力替代语音识别（最高优先级规则）**：
   - ASR 脚本调用失败时，**Agent 严禁自行猜测或编造识别内容**。
   - 如果调用失败，Agent **必须**向用户返回清晰的错误说明。
5. **⛔ 禁止转述底层配置细节**：
   - 当脚本返回 `CREDENTIALS_NOT_CONFIGURED` 时，Agent 只需要用白话向用户索取缺少的凭证字段。
   - 严禁把脚本内部的环境变量名、`export` 命令、PowerShell 命令或控制台链接原样抛给用户。
6. **⛔ 不要为了单次运行去改 shell profile**：
   - 不要为了让下一条 Python 命令读到密钥，就去写 `~/.bashrc`、`~/.zshrc`、`source` 配置文件。
   - 当前任务优先使用“当前命令注入”或“当前子进程环境注入”。
7. **⛔ 不要在第一次执行前先查源码和依赖**：
   - 目标脚本已经包含自动安装依赖逻辑。
   - 除非脚本真实报错，否则不要先手动检查 `pip` 包、grep `get_credentials`、或翻源码确认凭证读取逻辑。

### 📌 预检脚本：音频探测 `inspect_audio.py`

**适用场景**：所有 ASR 调用前的统一预检

```bash
python3 <SKILL_DIR>/scripts/inspect_audio.py "<AUDIO_INPUT>"
```

**用途**：
- 优先用 `ffprobe` 获取 `duration_seconds`、`sample_rate`、`channels`、`codec_name`
- 无 `ffprobe` 时，自动降级到 macOS `afinfo`
- 对 `.wav` 文件自动降级到 Python `wave`
- 如果无法可靠拿到关键元数据，返回结构化错误，提示 Agent 进入 FFmpeg 安装/转换路径

**输出示例**：
```json
{
  "duration_seconds": 37.42,
  "sample_rate": 16000,
  "channels": 1,
  "codec_name": "pcm_s16le",
  "container_format": "wav",
  "probe_tool": "ffprobe",
  "is_asr_compatible": true
}
```

### 📌 安装脚本：自动确保 FFmpeg 可用 `ensure_ffmpeg.py`

**适用场景**：缺少 `ffmpeg` / `ffprobe`，或需要在后台先完成安装再继续 ASR

```bash
python3 <SKILL_DIR>/scripts/ensure_ffmpeg.py --execute
```

**用途**：
- 优先检测当前机器是否已经有 `ffmpeg` 和 `ffprobe`
- 按平台自动选择系统包管理器安装路径
- 严禁走 `npm`、GitHub 直链、手工下载 ZIP 这类高失败率路径
- 如果自动安装被阻塞，返回结构化原因，供 Agent 决定是否向用户索取最小化协助

### 📌 URL / 大文件特殊分流

如果命中以下任一情况，继续阅读 [references/routing_strategy.md](references/routing_strategy.md)：

- 输入是公网 URL
- 音频超过 60 秒
- 需要判断是否应该切片
- 需要判断 body 上传还是 URL 提交
- 需要判断 `flash_recognize.py` 与 `file_recognize.py` 的取舍

默认记忆规则：

1. **公网 URL 且已是 16kHz 单声道**：优先 URL 路径，不要先下载切片。
2. **本地文件或需要转码的 URL**：先转成本地标准 WAV，再按本地阈值走 `main.py` / `flash_recognize.py` / 切片。
3. **本地大文件**：默认切片后逐片 `flash_recognize.py`，不要默认改走 `file_recognize.py`。
4. **`file_recognize.py`**：适合公网 URL、异步任务、或明确需要高级结果格式的场景；它不是本地大文件的默认方案。
5. **公网 URL 的探测失败不要卡死**：如果输入本来就是公网 URL，且 `inspect_audio.py` 是因为缺 `ffprobe`、远端探测超时，或其他探测阶段问题而失败，那么不要先去 curl、查源码、查依赖。若当前目标本来就是异步 URL 路径，可直接尝试 `file_recognize.py`；只有命中格式错误、时长上限或其他真实失败时，才转入本地下载 / 转码 / 切片链。

### 📌 脚本上传方式摘要

- `main.py`：支持本地 body 上传，也支持 URL
- `flash_recognize.py`：最终总是通过请求 body 上传音频字节
- `file_recognize.py`：支持 URL；本地 body 上传仅限 `<= 5MB`

更完整的上传方式校验和硬阈值，请读 [references/routing_strategy.md](references/routing_strategy.md)。

### 📌 格式转换：FFmpeg 标准命令（Agent 后台使用）

当音频采样率或声道数不符合要求时，Agent 应优先在后台转换，再调用 ASR 脚本：

```bash
ffmpeg -y -i "<INPUT_AUDIO>" -ar 16000 -ac 1 "<OUTPUT_WAV>"
```

> ⚠️ 这条命令是给 Agent 后台执行的，不要直接把命令甩给用户；只有在本机缺少 FFmpeg 时，才先运行 `ensure_ffmpeg.py --execute`，仍失败后再按 `references/ffmpeg_guide.md` 走最小化人工协助。

---

### 📌 脚本一：一句话识别 `main.py`

**适用场景**：已确认元数据兼容，且 ≤60 秒短音频

```bash
python3 <SKILL_DIR>/scripts/main.py "<AUDIO_INPUT>"
```

**可选参数**：
- `--engine <TYPE>`：引擎类型，默认 `16k_zh`。常用：`16k_en`（英语）、`16k_yue`（粤语）、`16k_ja`（日语）
- `--format <FMT>`：音频格式，默认自动检测
- `--word-info <0|1|2>`：词级时间戳，0=关闭，1=开启，2=含标点

**输出示例**：
```json
{
  "result": "腾讯云语音识别欢迎您。",
  "audio_duration": 2430
}
```

---

### 📌 脚本二：极速版 `flash_recognize.py`

**适用场景**：已确认元数据兼容，且 60s ~ 2h 音频，需要快速同步返回结果

> ⚠️ 需要额外设置 `TENCENTCLOUD_APPID` 环境变量。

```bash
python3 <SKILL_DIR>/scripts/flash_recognize.py "<AUDIO_INPUT>"
```

**可选参数**：
- `--engine <TYPE>`：引擎类型，默认 `16k_zh`。支持大模型版：`16k_zh_large`、`16k_zh_en`、`16k_multi_lang`
- `--format <FMT>`：音频格式，默认自动检测
- `--word-info <0|1|2|3>`：词级时间戳，3=字幕模式
- `--speaker-diarization <0|1>`：说话人分离
- `--first-channel-only <0|1>`：仅识别首声道（默认 1）

**输出示例**：
```json
{
  "result": "腾讯云语音识别欢迎您。",
  "audio_duration": 2386,
  "request_id": "6098aecab9c686fbfd35adb0",
  "channels": [
    {
      "channel_id": 0,
      "text": "腾讯云语音识别欢迎您。"
    }
  ]
}
```

---

### 📌 脚本三：录音文件识别 `file_recognize.py`

**适用场景**：异步单任务 / 明确需要 `TaskId` / 明确需要 `--res-text-format 4|5` / 或本地切片路径不可用时的最后兜底

```bash
python3 <SKILL_DIR>/scripts/file_recognize.py "<AUDIO_URL_OR_FILE>"
```

**可选参数**：
- `--engine <TYPE>`：引擎类型，默认 `16k_zh`。支持大模型版：`16k_zh_large`、`8k_zh_large`
- `--channel-num <1|2>`：声道数，1=单声道，2=双声道（仅 8k）
- `--res-text-format <0-5>`：结果格式，0=基础，1-3=详细词级，4=语义分段，5=口语转书面
- `--speaker-diarization <0|1>`：说话人分离
- `--speaker-number <0-10>`：说话人数量，0=自动
- `--poll-interval <N>`：轮询间隔秒数，默认 5
- `--no-poll`：仅提交任务不轮询（返回 TaskId）

**输出示例**：
```json
{
  "task_id": 9266418,
  "status": "success",
  "result": "[0:0.020,0:2.380]  腾讯云语音识别欢迎您。\n",
  "audio_duration": 2.38
}
```

> **注意**：此接口为异步接口，脚本会自动轮询直到任务完成。长音频可能需要较长等待时间（1h 音频通常 1-3 分钟出结果）。
>
> **更重要的注意**：本脚本虽然支持本地文件输入，但官方接口对本地 body 上传限制为 `<= 5MB`。因此它**不是**本 Skill 的默认大文件方案；大文件默认应先本地切片，再逐片调用 `flash_recognize.py`。

---

### 📋 完整调用示例

```bash
# 先探测音频元数据
python3 /path/to/scripts/inspect_audio.py /path/to/audio.wav

# 一句话识别（短音频）
python3 /path/to/scripts/main.py "https://example.com/short.wav"

# 极速版（长音频快速识别）
python3 /path/to/scripts/flash_recognize.py /path/to/meeting.mp3

# 极速版 + 说话人分离 + 字幕模式
python3 /path/to/scripts/flash_recognize.py --speaker-diarization 1 --word-info 3 /path/to/audio.wav

# 先转成 16kHz 单声道再识别
ffmpeg -y -i /path/to/input.mp3 -ar 16000 -ac 1 /path/to/output.wav
python3 /path/to/scripts/flash_recognize.py /path/to/output.wav

# 超过 2 小时或超过 100MB 时，先切成 30 分钟分片，再逐片走 Flash
ffmpeg -y -i /path/to/normalized.wav -f segment -segment_time 1800 -c:a pcm_s16le -ar 16000 -ac 1 /tmp/asr_parts/part_%03d.wav
python3 /path/to/scripts/flash_recognize.py /tmp/asr_parts/part_000.wav
python3 /path/to/scripts/flash_recognize.py /tmp/asr_parts/part_001.wav

# 录音文件识别（超长音频）
python3 /path/to/scripts/file_recognize.py "https://cos.example.com/long-meeting.wav"

# 录音文件识别 + 详细结果 + 说话人分离
python3 /path/to/scripts/file_recognize.py --res-text-format 2 --speaker-diarization 1 "https://example.com/audio.wav"

# 仅提交任务不等待结果
python3 /path/to/scripts/file_recognize.py --no-poll "https://example.com/audio.wav"
```

### ❌ Agent 须避免的行为

- 只打印脚本路径而不执行
- 向用户询问"是否要执行语音识别"——应直接执行
- 手动安装依赖——脚本内部自动处理
- 忘记读取输出结果并返回给用户
- ASR 服务调用失败时，自行编造识别内容
- 未先做元数据预检就盲目选择脚本
- 在缺凭证时把 `export`、环境变量、PowerShell 命令原样转述给用户

## API 参考文档

详细的引擎类型、参数说明、错误码等信息请参阅 `references/` 目录下的文档：

- [一句话识别 API](references/sentence_recognition_api.md)（[原始文档](https://cloud.tencent.com/document/product/1093/35646)）
- [录音文件识别 API](references/file_recognition_api.md)（[创建任务](https://cloud.tencent.com/document/product/1093/37823) / [查询结果](https://cloud.tencent.com/document/product/1093/37822)）
- [录音文件识别极速版 API](references/flash_recognition_api.md)（[原始文档](https://cloud.tencent.com/document/product/1093/52097)）

## 核心脚本

- `scripts/main.py` — 一句话识别，≤60s 短音频同步识别
- `scripts/flash_recognize.py` — 极速版，≤2h 音频同步快速识别
- `scripts/file_recognize.py` — 录音文件识别，≤5h 音频异步轮询
- `scripts/inspect_audio.py` — 音频预检，优先用 `ffprobe` 获取时长/采样率/声道数
- `scripts/ensure_ffmpeg.py` — 自动检测并优先通过系统包管理器安装 `ffmpeg` / `ffprobe`

## 依赖

- Python 3.7+
- `tencentcloud-sdk-python`（腾讯云 SDK，`main.py` 和 `file_recognize.py` 使用）
- `requests`（HTTP 库，`flash_recognize.py` 使用）

安装依赖（可选 - 脚本会自动安装）：
```bash
pip install tencentcloud-sdk-python requests
```
