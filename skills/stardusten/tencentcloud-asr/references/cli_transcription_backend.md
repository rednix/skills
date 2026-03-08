# CLI transcription backend 接入

当用户要把腾讯云 ASR 接到某个支持自定义 CLI transcription 的宿主系统时，优先使用：

```bash
python3 <SKILL_DIR>/scripts/cli_transcribe.py "<MEDIA_PATH_OR_URL>"
```

适用宿主：

- OpenClaw
- 任何要求“命令 exit 0 且 stdout 输出纯文本转写”的音频处理宿主

## 宿主约定

这个 wrapper 的职责很窄：

- 输入：本地音频路径，或公网 URL
- 成功：`stdout` 只输出纯文本转写
- 失败：`stderr` 输出错误信息，并以非 0 退出

不要把 JSON 直接暴露给宿主。宿主通常只接受纯文本 transcript。

## wrapper 内部行为

`cli_transcribe.py` 会复用本 Skill 的现有脚本，而不是重写腾讯云调用逻辑：

1. 先调用 `inspect_audio.py`
2. 缺少 `ffmpeg` / `ffprobe` 时，尝试 `ensure_ffmpeg.py --execute`
3. 本地文件不合规时，转为 `16kHz` 单声道 WAV
4. 路由规则：
   - `<=60s` 且 `<=3MB`：`main.py`
   - `<=2h` 且 `<=100MB`：优先 `flash_recognize.py`
   - 更大的本地文件：切片后逐片 `flash_recognize.py`
   - URL 且已合规：短音频走 `main.py`，其余优先 `file_recognize.py`
5. 从脚本 JSON 输出里提取 `result`

## 凭证要求

- 基础识别：需要 `TENCENTCLOUD_SECRET_ID`、`TENCENTCLOUD_SECRET_KEY`
- 本地长音频走 Flash：额外需要 `TENCENTCLOUD_APPID`

如果本地长音频缺少 `AppId`：

- 仅当文件仍满足 `file_recognize.py` 的本地 body 上传限制时，才可走 `file_recognize.py` 兜底
- 否则应明确报错，不要假装可用

## OpenClaw 示例

OpenClaw 的音频节点支持 `type: "cli"` 模型项，要求命令输出纯文本。一个最小配置形态可以写成：

```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [
          {
            "type": "cli",
            "command": "python3",
            "args": [
              "/absolute/path/to/.agents/skills/asr-sentence-recognition/scripts/cli_transcribe.py",
              "{{MediaPath}}"
            ],
            "timeoutSeconds": 1800
          }
        ]
      }
    }
  }
}
```

对 OpenClaw 这类宿主，优先传本地媒体路径，不要强依赖 URL 路径，因为宿主通常已经先把音频下载到了本地。

## Agent 行为要求

如果用户明确提到以下任一关键词，应把本 Skill 当作 CLI backend 来接，而不是当作“让模型直接听音频”：

- OpenClaw
- CLI transcription
- audio backend
- voice note transcription backend

命中这些场景时：

- 先读本文件
- 优先复用 `scripts/cli_transcribe.py`
- 只有在宿主接口不兼容时，才修改或派生 wrapper
