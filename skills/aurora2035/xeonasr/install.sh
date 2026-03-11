#!/bin/bash

# Xeon ASR Skill 安装脚本
# 自动创建环境、安装依赖、配置服务

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SKILL_DIR"

echo "========================================"
echo "  Xeon ASR Skill 安装脚本"
echo "========================================"
echo ""

# 步骤 1：检查 Python 3.10
echo "📦 步骤 1/6: 检查 Python 3.10..."
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "✓ Python 3.10 已安装"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    if [[ "$PYTHON_VERSION" == "3.10"* ]]; then
        PYTHON_CMD="python3"
        echo "✓ Python 3.10 已安装"
    else
        echo "⚠ 未找到 Python 3.10，当前 Python 版本：$PYTHON_VERSION"
        echo "  建议安装 Python 3.10: sudo apt install python3.10 python3.10-venv"
        exit 1
    fi
else
    echo "✗ 未找到 Python 3.10"
    echo "  请安装：sudo apt install python3.10 python3.10-venv"
    exit 1
fi

# 步骤 2：创建虚拟环境
echo ""
echo "📦 步骤 2/6: 创建 Python 虚拟环境..."
if [ -d "venv" ]; then
    echo "✓ 虚拟环境已存在，跳过创建"
else
    $PYTHON_CMD -m venv venv
    echo "✓ 虚拟环境创建完成"
fi
source venv/bin/activate

# 步骤 3：安装 xdp-audio-service
echo ""
echo "📦 步骤 3/6: 安装 xdp-audio-service..."
pip install --upgrade pip
pip install xdp-audio-service==0.1.1
echo "✓ xdp-audio-service 安装完成"

# 步骤 4：生成配置文件
echo ""
echo "📦 步骤 4/6: 生成 ASR 配置文件..."
if [ -f "audio_config.json" ]; then
    echo "⚠ audio_config.json 已存在"
    read -p "是否覆盖？(y/N): " overwrite
    if [[ "$overwrite" == "y" || "$overwrite" == "Y" ]]; then
        xdp-asr-init-config --output ./audio_config.json
        echo "✓ 配置文件已重新生成"
    else
        echo "✓ 保留现有配置文件"
    fi
else
    xdp-asr-init-config --output ./audio_config.json
    echo "✓ 配置文件生成完成"
fi

# 步骤 5：配置模型路径
echo ""
echo "📦 步骤 5/6: 配置模型路径..."
echo ""
echo "请输入 Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO 模型的路径"
echo "示例：/root/models/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO"
read -p "模型路径：" MODEL_PATH

if [ -d "$MODEL_PATH" ]; then
    echo "✓ 模型目录存在"
    
    # 使用 Node.js 或 Python 修改 JSON
    if command -v node &> /dev/null; then
        node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('./audio_config.json', 'utf8'));
config.qwen3_asr_ov.model = '$MODEL_PATH';
fs.writeFileSync('./audio_config.json', JSON.stringify(config, null, 2));
console.log('✓ 配置文件已更新');
"
    else
        python3 -c "
import json
with open('./audio_config.json', 'r') as f:
    config = json.load(f)
config['qwen3_asr_ov']['model'] = '$MODEL_PATH'
with open('./audio_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('✓ 配置文件已更新')
"
    fi
else
    echo "⚠ 模型目录不存在：$MODEL_PATH"
    echo "  请确认路径正确，或稍后手动修改 audio_config.json"
fi

# 步骤 6：检查并配置 QQ Bot
echo ""
echo "📦 步骤 6/6: 检查 QQ Bot 配置..."
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "✓ 发现 OpenClaw 配置文件"
    
    # 检查是否已配置 qqbot
    HAS_QQBOT=$(grep -c '"qqbot"' "$OPENCLAW_CONFIG" || true)
    if [ "$HAS_QQBOT" -gt 0 ]; then
        echo "✓ QQ Bot 已配置"
        
        # 询问是否配置 STT
        echo ""
        read -p "是否配置语音转文字 (STT)？(Y/n): " config_stt
        if [[ "$config_stt" != "n" && "$config_stt" != "N" ]]; then
            # 备份配置文件
            cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.bak.$(date +%Y%m%d%H%M%S)"
            
            # 使用 Node.js 修改配置
            if command -v node &> /dev/null; then
                node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$OPENCLAW_CONFIG', 'utf8'));

if (!config.channels) config.channels = {};
if (!config.channels.qqbot) config.channels.qqbot = {};

config.channels.qqbot.stt = {
  enabled: true,
  provider: 'custom',
  baseUrl: 'http://127.0.0.1:9001',
  model: 'Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO',
  apiKey: 'not-needed'
};

fs.writeFileSync('$OPENCLAW_CONFIG', JSON.stringify(config, null, 2));
console.log('✓ STT 配置已添加到 openclaw.json');
console.log('⚠ 请重启 OpenClaw Gateway: openclaw gateway restart');
"
            fi
        fi
    else
        echo "⚠ QQ Bot 未配置"
        echo "  请先在 OpenClaw 中配置 QQ Bot"
        echo "  运行：openclaw configure channels add qqbot"
    fi
else
    echo "⚠ 未找到 OpenClaw 配置文件：$OPENCLAW_CONFIG"
    echo "  请先安装并配置 OpenClaw"
fi

# 完成
echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 启动 ASR Skill 服务："
echo "   cd $SKILL_DIR"
echo "   npm install"
echo "   npm start"
echo ""
echo "2. 重启 OpenClaw Gateway（如果已配置 STT）："
echo "   openclaw gateway restart"
echo ""
echo "3. 发送语音消息测试"
echo ""
