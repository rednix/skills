# Video Transcribe v1.0.0 - 发布说明

## 📦 发布信息

- **技能名称：** video-transcribe
- **版本：** 1.0.0
- **发布日期：** 2026-03-13
- **作者：** Seven
- **分类：** 媒体工具

---

## ✨ 功能简介

一键转录本地视频/音频为文字稿，使用 OpenAI Whisper 引擎：

- ✅ 完全免费，无需 API 密钥
- ✅ 本地运行，保护隐私
- ✅ 支持 90+ 种语言
- ✅ 输出带时间戳的 SRT 字幕
- ✅ 支持多种视频/音频格式

---

## 📁 文件结构

```
video-transcribe-v1/
├── SKILL.md          # 使用说明文档
├── transcribe.py     # 主程序脚本
└── skill.json        # 技能配置文件
```

---

## 🚀 安装方法

### 方式 1：通过 ClawHub 安装（推荐）

```bash
openclaw skills install video-transcribe
```

### 方式 2：手动安装

1. 下载 `video-transcribe-v1.0.0.zip`
2. 解压到 `~/.openclaw/workspace/skills/`
3. 安装依赖：

```bash
pip3 install openai-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple
brew install ffmpeg  # macOS
```

---

## 📖 使用示例

### 基础用法

```bash
# 转录视频（默认 base 模型，中文）
python transcribe.py ~/Downloads/video.mp4

# 指定模型和语言
python transcribe.py ~/Downloads/audio.mp3 small zh

# 输出到指定目录
python transcribe.py ~/Videos/lecture.mp4 --output_dir ~/Documents/
```

### 在 OpenClaw 中使用

```
/whisper /path/to/video.mp4
```

---

## 📊 模型选择指南

| 模型 | 大小 | 速度 | 准确率 | 适用场景 |
|------|------|------|--------|----------|
| tiny | 39M | ⚡⚡⚡ | ⭐⭐ | 快速测试 |
| base | 74M | ⚡⚡ | ⭐⭐⭐ | **日常使用（推荐）** |
| small | 244M | ⚡ | ⭐⭐⭐⭐ | 正式场景 |
| medium | 769M | 🐌 | ⭐⭐⭐⭐⭐ | 高精度需求 |
| large | 1550M | 🐌🐌 | ⭐⭐⭐⭐⭐ | 专业场景 |

---

## 📝 输出文件

转录完成后生成：

- `视频名.txt` - 纯文字稿
- `视频名.srt` - 带时间戳字幕（可导入剪映/PR）
- `视频名.vtt` - WebVTT 格式

---

## ⚠️ 注意事项

1. **首次运行会下载模型**（一次性，约 100-800 MB）
2. **需要安装 ffmpeg**（视频处理依赖）
3. **长视频需要耐心等待**（约 1:1 到 1:2 的转录时间）
4. **文件路径有空格时用引号括起来**

---

## 🔧 常见问题

### Q: 提示 `command not found: whisper`

**A:** 使用完整路径或重新安装：

```bash
/Users/你的用户名/Library/Python/3.9/bin/whisper /path/to/video.mp4
```

### Q: 转录速度慢

**A:** 换用更小的模型（tiny 或 base），M 系列 Mac 比 Intel 快很多。

### Q: 识别准确率不高

**A:** 换用更大的模型（small 或 medium），确保音频清晰。

---

## 📮 反馈与支持

- **问题反馈：** 提交到 GitHub Issues
- **技能主页：** https://clawhub.com/skills/video-transcribe
- **文档：** 查看 SKILL.md

---

## 🙏 致谢

- 核心引擎：[OpenAI Whisper](https://github.com/openai/whisper)
- 开源协议：MIT

---

## 📄 许可证

MIT License
