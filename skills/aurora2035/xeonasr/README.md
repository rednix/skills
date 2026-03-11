# Xeon ASR Skill

🎤 基于 OpenVINO Qwen3-ASR 模型的语音转文字技能，为 OpenClaw/QQBot 提供本地语音识别能力。

## 功能特性

- ✅ 本地运行，无需外部 API
- ✅ 基于 OpenVINO 优化的 Qwen3-ASR-0.6B 模型
- ✅ 支持多种音频格式（.silk, .slk, .amr, .wav, .mp3, .ogg, .pcm）
- ✅ 自动集成 QQ Bot
- ✅ 一键安装脚本
- ✅ 支持模型名称传递
- ✅ OpenAI 兼容接口 (`/audio/transcriptions`)
- ✅ 启动时自动检测配置，缺失时提示用户确认安装

---

## 快速开始

### 方式 1：一键安装（推荐）

```bash
# 克隆 skill
git clone <repository-url> xeon_asr
cd xeon_asr

# 运行安装脚本
bash install.sh
```

安装脚本会自动：
1. 检查 Python 3.10
2. 创建虚拟环境
3. 安装 xdp-audio-service
4. 生成配置文件
5. 配置模型路径
6. 配置 QQ Bot STT

### 方式 2：从 ClawHub 安装

```bash
clawhub install xeon-asr
cd ~/.openclaw/skills/xeon-asr
bash install.sh
```

### 方式 3：直接启动（自动检测配置）

```bash
npm start
```

**智能配置检测：**
- 首次启动时会自动检查配置是否完整
- 如果缺少配置文件或依赖，会提示你运行 `install.sh`
- **需要用户确认后才执行安装**，不会自动修改系统
- 配置完整则直接启动服务

---

## 手动安装步骤

### 步骤 1：创建 Python 3.10 环境

```bash
# 安装 Python 3.10（如果没有）
sudo apt install python3.10 python3.10-venv

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate
```

### 步骤 2：安装 xdp-audio-service

```bash
pip install --upgrade pip
pip install xdp-audio-service==0.1.0
```

### 步骤 3：生成配置文件

```bash
xdp-asr-init-config --output ./audio_config.json
```

### 步骤 4：配置模型路径

编辑 `audio_config.json`，修改 `qwen3_asr_ov` 部分：

```json
{
  "qwen3_asr_ov": {
    "model": "/path/to/your/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
    "language": "zh",
    "task": "transcribe",
    "backend": "openvino",
    "device": "CPU",
    "inference_precision": "int8",
    "max_new_tokens": 256
  }
}
```

**模型获取：**
- HuggingFace: https://huggingface.co/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
- ModelScope: https://modelscope.cn/models/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO

### 步骤 5：安装 Node.js 依赖

```bash
npm install
```

### 步骤 6：配置 OpenClaw QQ Bot STT

编辑 `~/.openclaw/openclaw.json`，添加：

```json
{
  "channels": {
    "qqbot": {
      "stt": {
        "enabled": true,
        "provider": "custom",
        "baseUrl": "http://127.0.0.1:9001",
        "model": "Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
        "apiKey": "not-needed"
      }
    }
  }
}
```

---

## 启动服务

### 启动 ASR Skill（9001 端口）

```bash
npm start
```

**启动时的自动检测：**
- 首次运行或配置缺失时，会提示：`⚠️ 检测到配置不完整`
- 询问是否运行安装脚本：`是否现在运行安装脚本？(y/N):`
- 输入 `y` 确认后立即执行 `install.sh`
- 输入 `n` 或跳过则仅以健康检查模式运行

### 启动 Flask ASR 服务（5001 端口）

```bash
# 在另一个终端
source venv/bin/activate
npm run start:asr
# 或
xdp-asr-service --host 127.0.0.1 --port 5001 --config ./audio_config.json
```

### 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

---

## 测试

发送一条语音消息到 QQ，应该能自动转写成文字！

```bash
# 手动测试 API
curl -X POST -F "file=@test.wav" http://localhost:9001/audio/transcriptions
```

---

## 目录结构

```
xeon_asr/
├── SKILL.md              # ClawHub 技能说明
├── README.md             # 本文件
├── install.sh            # 一键安装脚本
├── server.js             # ASR Skill 主服务
├── config.json           # Skill 配置
├── audio_config.json     # xdp-audio-service 配置（自动生成）
├── package.json          # npm 配置
├── venv/                 # Python 虚拟环境（自动生成）
├── LICENSE               # MIT 许可证
└── .clawhub.json         # ClawHub 发布配置
```

---

## API 接口

### POST /audio/transcriptions（OpenAI 兼容）

```bash
curl -X POST \
  -F "file=@voice.wav" \
  -F "model=Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO" \
  http://localhost:9001/audio/transcriptions
```

**响应：**
```json
{
  "text": "转写结果文字"
}
```

### POST /transcribe（原始接口）

```bash
curl -X POST \
  -F "file=@voice.wav" \
  http://localhost:9001/transcribe
```

**响应：**
```json
{
  "success": true,
  "text": "转写结果文字"
}
```

### GET /health

```bash
curl http://localhost:9001/health
```

**响应：**
```json
{
  "status": "ok",
  "port": 9001
}
```

---

## 配置说明

### config.json（Skill 配置）

```json
{
  "port": 9001,
  "flaskAsrUrl": "http://127.0.0.1:5001/transcribe",
  "modelName": "Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
  "openclawSession": "default"
}
```

### audio_config.json（xdp-audio-service 配置）

```json
{
  "qwen3_asr_ov": {
    "model": "/root/models/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
    "language": "zh",
    "task": "transcribe",
    "backend": "openvino",
    "device": "CPU",
    "inference_precision": "int8",
    "max_new_tokens": 256
  }
}
```

---

## 常见问题

### Q1: 找不到 Python 3.10

**解决：**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv
```

### Q2: xdp-audio-service 安装失败

**解决：**
```bash
pip install --upgrade pip
pip install xdp-audio-service==0.1.0
```

### Q3: 模型加载失败

**原因：** 模型路径配置错误

**解决：**
1. 检查 `audio_config.json` 中的 `qwen3_asr_ov.model` 路径
2. 确认模型文件存在：`ls /path/to/model`
3. 确认有读取权限

### Q4: 语音消息显示"语音识别未配置"

**解决：**
1. 检查 `~/.openclaw/openclaw.json` 中是否有 `channels.qqbot.stt` 配置
2. 确保 `apiKey` 字段存在（可以是 `not-needed`）
3. 重启 Gateway：`openclaw gateway restart`

### Q5: ASR Skill 无法连接 Flask 服务

**解决：**
1. 确认 Flask 服务正在运行：`curl http://127.0.0.1:5001/health`
2. 检查 `config.json` 中的 `flaskAsrUrl`
3. 查看日志：`tail -f ~/.openclaw/logs/*.log | grep ASR`

---

## 依赖要求

- **Node.js:** >= 18.0.0
- **Python:** 3.10
- **xdp-audio-service:** 0.1.0
- **OpenVINO:** （xdp-audio-service 会自动安装）
- **Qwen3-ASR 模型:** 需自行下载

---

## 发布到 ClawHub

```bash
cd xeon_asr
clawhub publish . --version 1.0.0 --slug "xeon-asr"
```

---

## 许可证

MIT License

## 作者

aurora2035

## 支持

如有问题，请提交 Issue 或联系作者。

---

## 完整架构图

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   QQ 用户    │ ──→ │  QQ Bot API  │ ──→ │   qqbot     │ ──→ │  ASR Skill   │
│  发送语音    │     │              │     │  (OpenClaw) │     │  (9001 端口)  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                    │
                                                                    │ POST /transcribe
                                                                    │ + model 参数
                                                                    ↓
                                                             ┌──────────────┐
                                                             │ xdp-audio-   │
                                                             │ service      │
                                                             │ (5001 端口)   │
                                                             │ + Qwen3-ASR  │
                                                             │ + OpenVINO   │
                                                             └──────────────┘
                                                                    │
                                                                    │ 返回文字
                                                                    ↓
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  QQ 用户收到  │ ←── │  QQ Bot API  │ ←── │   qqbot     │ ←── │  ASR Skill   │
│  转写文字    │     │              │     │  (OpenClaw) │     │  (返回结果)  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```
