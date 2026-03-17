# SKILL.md - 豆包 AI 视频水印去除

## 技能描述

智能豆包 AI 视频水印去除工具，支持多种处理模式：
- 标准模式：平衡画质和文件大小
- 超高质量模式：CRF 14 接近无损
- **完美无损模式**：完全匹配原始编码参数，无插帧

## 功能特点

- 🧠 **智能识别**: 多算法投票机制自动检测水印位置
- 🎯 **精确定位**: 支持用户自定义水印位置和时间段
- 🔊 **音频保留**: 使用 FFmpeg 保留原始音频轨道
- 🚀 **批量处理**: 支持批量处理多个视频文件
- 💎 **完美无损**: 完全匹配原始编码参数，帧数 100% 一致

## 安装依赖

```bash
pip install -r requirements.txt
```

**系统要求:**
- Python 3.8+
- FFmpeg (用于视频编码)
- OpenCV, NumPy, tqdm

## 使用方法

### 单个视频处理（完美无损模式 - 推荐）

```bash
python final_perfect_lossless.py <输入视频路径> [输出视频路径]
```

**示例:**
```bash
python final_perfect_lossless.py /path/to/video.mp4 /path/to/output.mp4
```

### 其他模式

```bash
# 标准模式
python final_perfect.py input.mp4 output.mp4

# 超高质量模式
python final_ultra_quality.py input.mp4 output.mp4
```

### 批量处理

```bash
bash batch_qq_lossless.sh
```

### 自定义水印位置

编辑 `final_perfect_lossless.py` 中的 `watermark_regions` 配置：

```python
self.watermark_regions = [
    {"start_sec": 0, "end_sec": 4, "x": 510, "y": 1170, "w": 180, "h": 70, "name": "右下"},
    {"start_sec": 3, "end_sec": 7, "x": 20, "y": 600, "w": 170, "h": 60, "name": "左中"},
    {"start_sec": 6, "end_sec": 10, "x": 510, "y": 20, "w": 180, "h": 70, "name": "右上"},
]
```

## 配置参数

每个水印区域包含：
- `start_sec`: 开始时间（秒）
- `end_sec`: 结束时间（秒）
- `x`, `y`: 水印区域左上角坐标
- `w`, `h`: 水印区域宽度和高度
- `name`: 区域名称

## 典型配置

### 豆包 AI 生成水印（10 秒视频）
```python
[
    {"start_sec": 0, "end_sec": 4, "x": 510, "y": 1170, "w": 180, "h": 70},
    {"start_sec": 3, "end_sec": 7, "x": 20, "y": 600, "w": 170, "h": 60},
    {"start_sec": 6, "end_sec": 10, "x": 510, "y": 20, "w": 180, "h": 70},
]
```

### 抖音水印
```python
[
    {"start_sec": 0, "end_sec": 999, "x": 50, "y": 50, "w": 150, "h": 50},
]
```

## 技术原理

### 水印去除算法
使用 FFmpeg 的 `delogo` 滤镜，支持时间动态控制：
```
delogo=x=X:y=Y:w=W:h=H:enable=between(t,START,END)
```

### 完美无损模式
- 完全匹配原始视频编码参数
- 帧数 100% 一致（无插帧）
- 智能码率匹配（原始的 120%）
- 固定 GOP 结构，无场景切换

## 文件说明

- `final_perfect_lossless.py` - 完美无损版主程序（推荐）
- `final_perfect.py` - 标准版主程序
- `final_ultra_quality.py` - 超高质量版主程序
- `batch_qq_lossless.sh` - 批量处理脚本
- `requirements.txt` - Python 依赖

## 性能参考

| 视频规格 | 处理速度 | 说明 |
|----------|----------|------|
| 720x1280, 10 秒 | ~2 秒 | 完美无损模式 |
| 1080x1920, 30 秒 | ~8 秒 | 完美无损模式 |

## 常见问题

**Q: 水印去除不干净？**
A: 调整 `watermark_regions` 中的坐标和大小

**Q: 视频模糊？**
A: 使用完美无损模式或超高质量模式

**Q: 音频丢失？**
A: 确保安装了 FFmpeg

## 许可证

MIT-0 - Free to use, modify, and redistribute.

## 作者

mac 小虫子 · 严谨专业版
