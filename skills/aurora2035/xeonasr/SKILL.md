# Xeon ASR

🎤 基于 OpenVINO Qwen3-ASR 模型的本地语音转文字技能。集成 xdp-audio-service，一键安装自动配置。

## 快速安装

```bash
# 从 ClawHub 安装
clawhub install xeon-asr
cd xeon-asr

# 运行一键安装脚本
bash install.sh
```

安装脚本会自动：
1. ✅ 检查 Python 3.10
2. ✅ 创建虚拟环境
3. ✅ 安装 xdp-audio-service
4. ✅ 生成配置文件
5. ✅ 配置模型路径
6. ✅ 配置 QQ Bot STT

## 智能启动

直接运行 `npm start` 时会自动检测配置：
- 配置完整 → 直接启动服务
- 配置缺失 → 提示用户确认是否运行安装脚本
- **不会自动执行安装**，需要用户输入 `y` 确认

## 配置

### 1. 下载 Qwen3-ASR 模型

```bash
# 从 HuggingFace 下载
git lfs install
git clone https://huggingface.co/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO /root/models/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
```

### 2. 启动服务

```bash
# 启动 ASR Skill (9001 端口)
npm start

# 启动 Flask ASR (5001 端口，另一个终端)
source venv/bin/activate
npm run start:asr
```

### 3. 重启 OpenClaw

```bash
openclaw gateway restart
```

## 使用

- QQ 收到语音消息时自动转写
- 本地运行，无需外部 API
- 基于 OpenVINO 优化的 Qwen3-ASR-0.6B 模型

## 依赖

- Node.js 18+
- Python 3.10
- xdp-audio-service 0.1.0
- Qwen3-ASR 模型（需下载）

## 文档

详细文档请查看 README.md

## 许可证

MIT
