# 豆包 AI 视频水印去除 - 完美版

智能识别并自动去除豆包 AI/QQ 视频水印，支持用户自定义水印区域和批量高质量处理，保留原始音频。

## ✨ 功能特点

- 🧠 **智能识别**: 多算法投票机制自动检测水印位置
- 🎯 **精确定位**: 支持用户自定义水印位置和时间段
- 🔊 **音频保留**: 使用 FFmpeg 保留原始音频轨道
- 🚀 **批量处理**: 支持批量处理多个视频文件
- 💎 **多种模式**: 
  - 标准模式 (CRF 18) - 平衡画质和文件大小
  - 超高质量模式 (CRF 14) - 接近无损画质
  - **完美无损模式** - 完全匹配原始编码参数，无插帧

## 📦 安装

### 方法 1: 通过 ClawHub 安装（推荐）

```bash
clawhub install yun520-1/doubao-watermark-remover
```

### 方法 2: 手动安装

```bash
# 克隆或下载项目
cd doubao-watermark-remover

# 安装依赖
pip install -r requirements.txt
```

### 系统要求

- Python 3.8+
- FFmpeg (用于视频编码)
- OpenCV, NumPy, tqdm

## 🚀 使用方法

### 单个视频处理

#### 标准模式
```bash
python final_perfect.py input.mp4 output.mp4
```

#### 超高质量模式
```bash
python final_ultra_quality.py input.mp4 output.mp4
```

#### 完美无损模式（推荐）
```bash
python final_perfect_lossless.py input.mp4 output.mp4
```

### 批量处理

#### 完美无损批量处理（推荐）
```bash
bash batch_qq_lossless.sh
```

## 📊 处理模式对比

| 模式 | CRF | Preset | 码率策略 | 文件大小 | 画质 |
|------|-----|--------|----------|----------|------|
| 标准 | 18 | slow | 固定 CRF | 中等 | 好 |
| 超高质量 | 14 | veryslow | 固定 CRF | +60% | 极佳 |
| **完美无损** | - | slow | **匹配原始** | **±0%** | **原始** |

## 📄 许可证

MIT-0 - Free to use, modify, and redistribute.

## 👨‍💻 作者

mac 小虫子 · 严谨专业版
