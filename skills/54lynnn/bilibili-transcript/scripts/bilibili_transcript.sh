#!/bin/bash
# B站视频字幕智能获取脚本 v2.0
# 使用 Whisper large 模型 + GPU 加速
# 输出格式化的 TXT 文件（含元数据、摘要、原文）

VIDEO_URL="$1"
OUTPUT_DIR="${2:-/tmp}"

if [ -z "$VIDEO_URL" ]; then
    echo "用法: $0 <B站视频链接> [输出目录]"
    exit 1
fi

echo "🔍 正在获取视频信息..."

# 获取视频元数据
VIDEO_INFO=$(yt-dlp --dump-json "$VIDEO_URL" 2>/dev/null | head -1)

if [ -z "$VIDEO_INFO" ]; then
    echo "❌ 无法获取视频信息"
    exit 1
fi

# 提取元数据
TITLE=$(echo "$VIDEO_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('title', '未知标题'))")
AUTHOR=$(echo "$VIDEO_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('uploader', '未知作者'))")
UPLOAD_DATE=$(echo "$VIDEO_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('upload_date', '未知时间'))")
DURATION=$(echo "$VIDEO_INFO" | python3 -c "import sys, json; d=json.load(sys.stdin).get('duration', 0); print(f'{d//60}分{d%60}秒')")
VIDEO_ID=$(echo "$VIDEO_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

# 格式化日期
if [ "$UPLOAD_DATE" != "未知时间" ]; then
    UPLOAD_DATE_FORMATTED=$(echo "$UPLOAD_DATE" | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')
else
    UPLOAD_DATE_FORMATTED="$UPLOAD_DATE"
fi

echo "📹 视频: $TITLE"
echo "👤 作者: $AUTHOR"
echo "📅 发布: $UPLOAD_DATE_FORMATTED"
echo "⏱️  时长: $DURATION"

# 检查字幕
echo ""
echo "🔍 正在检查字幕..."
SUB_CHECK=$(yt-dlp --list-subs "$VIDEO_URL" 2>&1)
HAS_REAL_SUBS=false

if echo "$SUB_CHECK" | grep -E "^[[:space:]]*(zh|en|ja|ko)-" | grep -v "danmaku" | grep -q "[[:space:]]"; then
    HAS_REAL_SUBS=true
fi

TRANSCRIPT_SOURCE=""
TRANSCRIPT_TEXT=""

if [ "$HAS_REAL_SUBS" = true ]; then
    echo "✅ 发现人工字幕，优先下载..."
    
    yt-dlp --skip-download --write-subs --sub-langs zh-CN,zh-TW,zh-Hans,zh --convert-subs srt \
        -o "${OUTPUT_DIR}/bilibili_subtitle.%(ext)s" "$VIDEO_URL" 2>&1
    
    SUB_FILE=$(find "$OUTPUT_DIR" -maxdepth 1 -name "bilibili_subtitle*.srt" -type f 2>/dev/null | head -1)
    
    if [ -n "$SUB_FILE" ] && [ -s "$SUB_FILE" ]; then
        echo "✅ 字幕下载成功"
        TRANSCRIPT_SOURCE="B站CC字幕"
        # 提取纯文本
        TRANSCRIPT_TEXT=$(sed '/^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/d' "$SUB_FILE" | sed '/^[0-9]*$/d' | sed '/^$/d')
    else
        echo "⚠️  字幕下载失败，切换到语音转录..."
        HAS_REAL_SUBS=false
    fi
fi

if [ "$HAS_REAL_SUBS" = false ]; then
    echo "🎤 正在使用 Whisper medium 模型转录（GPU加速）..."
    echo "⏳ 这可能需要一些时间，请耐心等待..."
    
    # 下载音频
    yt-dlp -x --audio-format mp3 -o "${OUTPUT_DIR}/bilibili_audio.%(ext)s" "$VIDEO_URL" 2>&1
    
    AUDIO_FILE=$(find "$OUTPUT_DIR" -maxdepth 1 \( -name "bilibili_audio*.mp3" -o -name "bilibili_audio*.m4a" \) 2>/dev/null | head -1)
    
    if [ -z "$AUDIO_FILE" ]; then
        echo "❌ 音频下载失败"
        exit 1
    fi
    
    # 使用 medium 模型 + GPU
    whisper "$AUDIO_FILE" --model medium --language Chinese --output_format txt --output_dir "$OUTPUT_DIR" 2>&1
    
    TXT_FILE=$(find "$OUTPUT_DIR" -maxdepth 1 -name "*.txt" -type f 2>/dev/null | head -1)
    
    if [ -n "$TXT_FILE" ] && [ -s "$TXT_FILE" ]; then
        echo "✅ 转录完成"
        TRANSCRIPT_SOURCE="Whisper large 模型"
        TRANSCRIPT_TEXT=$(cat "$TXT_FILE")
        # 清理临时文件
        rm -f "$TXT_FILE"
    else
        echo "❌ 转录失败"
        exit 1
    fi
fi

# 繁体转简体（使用 opencc 如果可用，否则保留原文）
if command -v opencc >/dev/null 2>&1; then
    echo "🔄 正在转换为简体字..."
    TRANSCRIPT_TEXT_SIMPLIFIED=$(echo "$TRANSCRIPT_TEXT" | opencc -c tw2s)
else
    TRANSCRIPT_TEXT_SIMPLIFIED="$TRANSCRIPT_TEXT"
fi

# 生成输出文件名（安全文件名）
SAFE_TITLE=$(echo "$TITLE" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5]/_/g' | cut -c1-50)
OUTPUT_FILE="${OUTPUT_DIR}/${SAFE_TITLE}_${VIDEO_ID}_transcript.txt"

# 生成格式化的 TXT 文件
echo "📝 正在生成转录文件..."

cat > "$OUTPUT_FILE" << EOF
================================================================================
B站视频转录文档
================================================================================

📹 视频标题：$TITLE
🔗 B站链接：$VIDEO_URL
👤 作者：$AUTHOR
📅 发布时间：$UPLOAD_DATE_FORMATTED
⏱️  视频时长：$DURATION
📝 转录来源：$TRANSCRIPT_SOURCE
⏰ 转录时间：$(date '+%Y-%m-%d %H:%M:%S')

================================================================================
第一部分：视频摘要（AI生成）
================================================================================

【请在此处添加视频摘要】

================================================================================
第二部分：完整原文
================================================================================

$TRANSCRIPT_TEXT_SIMPLIFIED

================================================================================
文档结束
================================================================================
EOF

echo ""
echo "✅ 转录完成！"
echo "📄 文件已保存: $OUTPUT_FILE"
echo ""
echo "💡 提示：请阅读文件中的摘要部分，并根据完整原文补充详细摘要。"

# 输出文件路径（供调用者使用）
echo "$OUTPUT_FILE"
