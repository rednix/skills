#!/bin/bash

echo "================================================================"
echo "📦 豆包 AI 视频水印去除 - 发布到 ClawHub"
echo "================================================================"
echo ""

# 检查登录状态
echo "🔍 检查登录状态..."
clawhub whoami > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  未登录，请先登录 ClawHub"
    echo ""
    echo "运行：clawhub login"
    echo ""
    exit 1
fi

echo "✅ 已登录"
echo ""

# 发布
echo "🚀 开始发布..."
echo ""

clawhub publish ./ \
  --slug doubao-watermark-remover \
  --name "豆包 AI 视频水印去除" \
  --version 1.0.0 \
  --changelog "初始版本 - 智能豆包 AI 视频水印去除工具" \
  --tags "latest,doubao,watermark,video,ai"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo "🎉 发布成功！"
    echo "================================================================"
    echo ""
    echo "📦 项目名称：doubao-watermark-remover"
    echo "🏷️  版本：1.0.0"
    echo "🔖 标签：doubao, watermark, video, ai"
    echo ""
    echo "📥 安装命令:"
    echo "   clawhub install doubao-watermark-remover"
    echo ""
    echo "🔗 ClawHub 页面:"
    echo "   https://clawhub.ai/skills/doubao-watermark-remover"
    echo ""
else
    echo ""
    echo "================================================================"
    echo "❌ 发布失败"
    echo "================================================================"
    exit 1
fi
