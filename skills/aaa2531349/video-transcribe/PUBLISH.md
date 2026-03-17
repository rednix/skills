# 🎬 Video Transcribe - 视频转文字

> **一键转录本地视频/音频为文字稿，AI 自动生成内容总结**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://clawhub.com/skills/video-transcribe)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-macos%20%7C%20linux-lightgrey.svg)](https://clawhub.com/skills/video-transcribe)

---

## ✨ 核心功能

### 🎯 一键转录
- 支持 **90+ 种语言**自动识别
- 本地运行，**完全离线**，保护隐私
- 输出 **5 种格式**：TXT、SRT、VTT、TSV、JSON

### 🤖 AI 内容总结
- 转录后自动生成 **200-300 字摘要**
- 提取 **3-5 个关键要点**
- 识别 **金句/结论** 单独列出

### 📊 多模型选择
| 模型 | 大小 | 速度 | 准确率 | 适用场景 |
|------|------|------|--------|----------|
| tiny | 39M | ⚡⚡⚡ | ⭐⭐ | 快速测试 |
| **base** | 74M | ⚡⚡ | ⭐⭐⭐ | **日常使用（推荐）** |
| small | 244M | ⚡ | ⭐⭐⭐⭐ | 正式场景 |
| medium | 769M | 🐌 | ⭐⭐⭐⭐⭐ | 高精度需求 |
| large | 1550M | 🐌🐌 | ⭐⭐⭐⭐⭐ | 专业场景 |

---

## 🚀 快速开始

### 1️⃣ 安装技能

```bash
openclaw skills install video-transcribe
```

### 2️⃣ 安装依赖

```bash
# 安装 Whisper（首次使用）
pip3 install openai-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 ffmpeg（视频处理依赖）
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux
```

### 3️⃣ 开始使用

```bash
# 基础用法
python transcribe.py ~/Downloads/video.mp4

# 转录 + AI 总结
python transcribe.py ~/Downloads/video.mp4 --summarize

# 指定模型和语言
python transcribe.py ~/Videos/lecture.mp4 small zh --summarize
```

---

## 📝 使用示例

### 示例 1：转录抖音视频

```bash
$ python transcribe.py ~/Downloads/抖音 - 记录美好生活.mp4 --summarize

🎬 开始转录：抖音 - 记录美好生活.mp4
📦 模型：base
🌐 语言：zh
📊 AI 总结：启用

⏳ 转录中，请稍候...

✅ 转录完成！

📄 文字稿：~/Downloads/抖音 - 记录美好生活.txt
📽️ 字幕：~/Downloads/抖音 - 记录美好生活.srt

📊 AI 总结：
============================================================
⏱️  视频时长：约 5 分 09 秒
📝 文字稿字数：2149

🔑 关键要点：
  1. 品牌年轻化不是万能药，消费者不在乎视觉
  2. 审美无法形成壁垒，明天别人就能抄
  3. 品牌升级 = 定价权保卫战
  4. 信任摩擦成本是核心概念
  5. 要做拿着账本的刺客，不是美学翻译官

📄 内容预览：
  这是一个在无数公司会议势力反复上演过的处行现场...
============================================================
💾 总结已保存：~/Downloads/抖音 - 记录美好生活_summary.json
```

### 示例 2：批量转录会议录音

```bash
for audio in ~/Recordings/*.m4a; do
    python transcribe.py "$audio" small zh --summarize
done
```

### 示例 3：在 OpenClaw 中使用

```
/transcribe /path/to/video.mp4 --summarize
```

---

## 📁 输出文件

转录完成后生成以下文件（同一目录）：

| 文件 | 格式 | 说明 |
|------|------|------|
| `视频名.txt` | 纯文本 | 无时间戳文字稿 |
| `视频名.srt` | SRT 字幕 | 带时间戳，可导入剪映/PR |
| `视频名.vtt` | WebVTT | 网页字幕格式 |
| `视频名.tsv` | 表格 | Excel 可打开 |
| `视频名.json` | JSON | 完整日志（含元数据） |
| `视频名_summary.json` | JSON | AI 内容总结 |

---

## 💡 应用场景

### 📺 自媒体创作者
- 抖音视频 → 文案稿
- 播客音频 → 文章摘要
- 课程录像 → 学习笔记

### 💼 职场人士
- 会议录音 → 会议纪要
- 培训视频 → 培训资料
- 访谈录音 → 访谈稿

### 🎓 学生/研究者
- 讲座录像 → 讲义
- 采访视频 → 研究素材
- 外语视频 → 翻译底稿

---

## ⚙️ 高级选项

```bash
# 输出所有格式
python transcribe.py video.mp4 --output_format all

# 只输出文字稿
python transcribe.py video.mp4 --output_format txt

# 翻译为英文
python transcribe.py video.mp4 --task translate

# 调整温度（0 最确定，1 最随机）
python transcribe.py video.mp4 --temperature 0.5

# 显示详细日志
python transcribe.py video.mp4 --verbose True
```

完整选项：`python transcribe.py --help`

---

## ❓ 常见问题

### Q1: 安装时提示 `command not found: pip3`

**解决：** 使用 `python3 -m pip` 替代

```bash
python3 -m pip install openai-whisper
```

### Q2: 转录速度慢

**解决：**
- 换用更小的模型（`tiny` 或 `base`）
- M 系列 Mac 比 Intel Mac 快很多
- 视频越长，时间越久（约 1:1 到 1:2 的转录时间）

### Q3: 识别准确率不高

**解决：**
- 换用更大的模型（`small` 或 `medium`）
- 确保音频清晰，减少背景噪音
- 指定正确的语言（`--language zh`）

### Q4: 提示 `ffmpeg not found`

**解决：** 安装 ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### Q5: 文件路径有空格怎么办？

**解决：** 用引号括起来

```bash
python transcribe.py "~/Downloads/我的视频.mp4"
```

---

## 🔧 技术栈

- **核心引擎：** [OpenAI Whisper](https://github.com/openai/whisper)
- **编程语言：** Python 3.9+
- **支持平台：** macOS, Linux, Windows (WSL)
- **开源协议：** MIT

---

## 📮 反馈与支持

- **技能主页：** https://clawhub.com/skills/video-transcribe
- **问题反馈：** 提交到 GitHub Issues
- **使用文档：** 查看 SKILL.md

---

## 🙏 致谢

感谢 OpenAI 团队开发 Whisper，让语音识别变得如此简单！

---

## 📄 许可证

MIT License © 2026 Seven

---

**最后更新：** 2026-03-13  
**版本：** 1.0.0  
**作者：** Seven
