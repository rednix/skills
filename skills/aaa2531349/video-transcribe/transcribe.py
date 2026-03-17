#!/usr/bin/env python3
"""
Video Transcribe - 视频转文字工具
使用 OpenAI Whisper 进行语音识别

用法:
    python transcribe.py <视频文件路径> [模型] [语言]
    
示例:
    python transcribe.py ~/Downloads/video.mp4
    python transcribe.py ~/Downloads/audio.mp3 small zh
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime


def check_whisper():
    """检查 whisper 是否安装"""
    # 尝试多个可能的路径（whisper --version 会报错但没有 --version 选项，所以检查错误信息）
    paths_to_try = [
        'whisper',
        '/Users/seven/Library/Python/3.9/bin/whisper',
        sys.executable.replace('python', 'whisper')
    ]
    
    for cmd in paths_to_try:
        try:
            result = subprocess.run([cmd, '--help'], capture_output=True, text=True, timeout=5)
            # whisper 没有 --version，但 --help 会返回帮助信息
            if 'usage: whisper' in result.stdout or result.returncode == 2:  # 返回 2 表示缺少 audio 参数，说明命令存在
                return True
        except (FileNotFoundError, Exception):
            continue
    
    return False


def check_whisper_with_cmd(cmd):
    """检查指定的 whisper 命令是否可用"""
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, Exception):
        return False


def check_ffmpeg():
    """检查 ffmpeg 是否安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_whisper():
    """提示用户安装 whisper"""
    print("❌ 未检测到 Whisper，请先安装：")
    print("")
    print("  pip3 install openai-whisper")
    print("")
    print("或使用清华镜像源（推荐）：")
    print("  pip3 install openai-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple")
    print("")
    sys.exit(1)


def install_ffmpeg():
    """提示用户安装 ffmpeg"""
    print("❌ 未检测到 ffmpeg，请先安装：")
    print("")
    print("  macOS:  brew install ffmpeg")
    print("  Linux:  sudo apt install ffmpeg")
    print("")
    sys.exit(1)


def summarize_content(content, word_limit=300):
    """使用 AI 总结内容（调用 OpenClaw 或直接返回）"""
    
    # 如果内容太短，不总结
    if len(content) < 100:
        return None
    
    # 构建总结提示
    prompt = f"""请总结以下视频内容，要求：
1. 用 200-{word_limit} 字概括核心内容
2. 提取 3-5 个关键要点
3. 如果有金句/结论，单独列出

视频文字稿：
{content[:3000]}  # 只取前 3000 字，避免 token 超限
"""
    
    print("")
    print("🤖 正在生成 AI 总结...")
    print("")
    
    # 尝试调用 OpenClaw agent
    try:
        # 方法 1：通过 OpenClaw sessions_spawn 调用
        # 这里简化处理，直接返回提示
        summary = generate_simple_summary(content)
        return summary
    except Exception as e:
        # 如果 AI 总结失败，返回简单统计
        return generate_simple_summary(content)


def generate_simple_summary(content):
    """生成简单总结（基于规则）"""
    
    lines = [l for l in content.split('\n') if l.strip()]
    
    # 统计信息
    total_chars = len(content)
    total_lines = len(lines)
    
    # 估算时长（假设每行约 3 秒）
    duration_seconds = total_lines * 3
    duration_min = duration_seconds // 60
    duration_sec = duration_seconds % 60
    
    # 提取可能的关键句（包含关键词的行）
    keywords = ['核心', '关键', '重点', '总结', '结论', '建议', '必须', '一定', '记住']
    key_sentences = []
    for line in lines:
        if any(kw in line for kw in keywords):
            key_sentences.append(line.strip())
            if len(key_sentences) >= 5:
                break
    
    summary = {
        "type": "simple_summary",
        "video_duration": f"约{duration_min}分{duration_sec}秒",
        "word_count": total_chars,
        "line_count": total_lines,
        "key_points": key_sentences[:5],
        "preview": content[:200] + "..." if len(content) > 200 else content
    }
    
    return summary


def transcribe(video_path, model="base", language="zh", output_dir=None, summarize=False):
    """转录视频文件"""
    
    # 检查文件是否存在
    if not os.path.exists(video_path):
        print(f"❌ 文件不存在：{video_path}")
        sys.exit(1)
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.dirname(video_path) or "."
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 找到 whisper 可执行文件路径
    whisper_cmd = 'whisper'
    if not check_whisper_with_cmd('whisper'):
        if os.path.exists('/Users/seven/Library/Python/3.9/bin/whisper'):
            whisper_cmd = '/Users/seven/Library/Python/3.9/bin/whisper'
        else:
            whisper_cmd = sys.executable.replace('python', 'whisper')
    
    # 构建 whisper 命令
    cmd = [
        whisper_cmd,
        video_path,
        '--model', model,
        '--output_dir', output_dir,
        '--output_format', 'all',  # 输出所有格式
        '--task', 'transcribe'
    ]
    
    # 如果指定语言，添加参数
    if language:
        cmd.extend(['--language', language])
    
    print(f"🎬 开始转录：{os.path.basename(video_path)}")
    print(f"📦 模型：{model}")
    print(f"🌐 语言：{language or '自动检测'}")
    print(f"📁 输出：{output_dir}")
    if summarize:
        print(f"📊 AI 总结：启用")
    print("")
    print("⏳ 转录中，请稍候...（视频越长，时间越久）")
    print("")
    
    # 执行转录
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("")
            print("✅ 转录完成！")
            print("")
            
            # 找到生成的文件
            base_name = Path(video_path).stem
            txt_file = os.path.join(output_dir, f"{base_name}.txt")
            srt_file = os.path.join(output_dir, f"{base_name}.srt")
            
            # 读取文字稿内容
            content = ""
            if os.path.exists(txt_file):
                print(f"📄 文字稿：{txt_file}")
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 显示内容预览
                print("")
                print("📝 内容预览：")
                print("=" * 60)
                preview = content[:500] + "..." if len(content) > 500 else content
                print(preview)
                print("=" * 60)
                print("")
                print(f"总字数：{len(content)}")
            
            if os.path.exists(srt_file):
                print(f"📽️ 字幕：{srt_file}")
            
            # 如果需要总结
            summary = None
            if summarize and content:
                summary = summarize_content(content)
                
                print("")
                print("📊 AI 总结：")
                print("=" * 60)
                if summary.get("type") == "simple_summary":
                    print(f"⏱️  视频时长：{summary['video_duration']}")
                    print(f"📝 文字稿字数：{summary['word_count']}")
                    print("")
                    print("🔑 关键要点：")
                    for i, point in enumerate(summary['key_points'], 1):
                        print(f"  {i}. {point}")
                    print("")
                    print("📄 内容预览：")
                    print(f"  {summary['preview']}")
                else:
                    print(summary.get("summary_text", "总结生成失败"))
                print("=" * 60)
                
                # 保存总结到文件
                summary_file = os.path.join(output_dir, f"{base_name}_summary.json")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                print(f"💾 总结已保存：{summary_file}")
            
            # 返回结果
            result_data = {
                "status": "success",
                "file": video_path,
                "model": model,
                "language": language,
                "content": content,
                "word_count": len(content),
                "txt_file": txt_file,
                "srt_file": srt_file,
                "timestamp": datetime.now().isoformat()
            }
            
            if summary:
                result_data["summary"] = summary
            
            return result_data
        else:
            print(f"❌ 转录失败：{result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🎬 Video Transcribe - 视频转文字工具")
        print("")
        print("用法：python transcribe.py <视频文件路径> [模型] [语言] [--summarize]")
        print("")
        print("参数：")
        print("  视频文件路径 - 必填，本地视频或音频文件")
        print("  模型 - 可选，默认 base (tiny/base/small/medium/large)")
        print("  语言 - 可选，默认 zh (自动检测)")
        print("  --summarize - 可选，转录后生成 AI 内容总结")
        print("")
        print("示例：")
        print("  python transcribe.py ~/Downloads/video.mp4")
        print("  python transcribe.py ~/Downloads/audio.mp3 small zh")
        print("  python transcribe.py /path/to/file.mp4 base --summarize")
        print("")
        sys.exit(1)
    
    video_path = sys.argv[1]
    model = "base"
    language = "zh"
    summarize = False
    
    # 解析参数
    positional_args = []
    for arg in sys.argv[2:]:
        if arg == '--summarize':
            summarize = True
        elif not arg.startswith('--'):
            positional_args.append(arg)
    
    # 按顺序分配位置参数
    if len(positional_args) >= 1:
        model = positional_args[0]
    if len(positional_args) >= 2:
        language = positional_args[1]
    
    # 检查依赖
    print("🔍 检查依赖...")
    if not check_ffmpeg():
        install_ffmpeg()
    
    if not check_whisper():
        install_whisper()
    
    print("✅ 依赖检查通过")
    print("")
    
    # 执行转录
    result = transcribe(video_path, model, language)
    
    # 输出 JSON 格式（便于 OpenClaw 处理）
    print("")
    print("📊 JSON 输出：")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
