#!/bin/bash
cd "$(dirname "$0")"

echo "🎬 视频转文字 v1.0.0"
echo "===================="
echo ""

# 检查依赖
if ! command -v whisper &> /dev/null; then
    echo "❌ Whisper 未安装"
    echo ""
    echo "📦 请先安装依赖："
    echo "   pip3 install openai-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple"
    echo ""
    exit 1
fi

if [ -z "$1" ]; then
    echo "❌ 请提供视频/音频文件路径"
    echo ""
    echo "📝 用法："
    echo "   ./run.sh <文件路径> [模型] [语言] [--summarize]"
    echo ""
    echo "🌰 示例："
    echo "   ./run.sh ~/Downloads/video.mp4"
    echo "   ./run.sh ~/Downloads/video.mp4 base zh --summarize"
    echo ""
    exit 1
fi

# 执行转录
echo "🎬 开始转录：$1"
python3 transcribe.py "$@"
