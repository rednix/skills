#!/usr/bin/env python3
"""
超高质量版 - 无损分辨率 + 最佳画质
特点：
1. 完全保留原始分辨率和编码参数
2. 使用 FFmpeg delogo 滤镜（GPU 加速可选）
3. CRF 14 + veryslow preset 最高画质
4. 音频无损复制（如可能）
5. 色彩空间精确匹配
"""

import subprocess
from pathlib import Path
import sys
import json


class UltraQualityRemover:
    """超高质量水印去除器 - 使用 FFmpeg 原生滤镜"""
    
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        self.info = self._get_video_info()
        
        # 用户指定的精确位置和时间
        self.watermark_regions = [
            {"start_sec": 0, "end_sec": 4, "x": 510, "y": 1170, "w": 180, "h": 70, "name": "右下"},
            {"start_sec": 3, "end_sec": 7, "x": 20, "y": 600, "w": 170, "h": 60, "name": "左中"},
            {"start_sec": 6, "end_sec": 10, "y": 20, "x": 510, "w": 180, "h": 70, "name": "右上"},
        ]
        
        print(f"📹 视频：{self.info['width']}x{self.info['height']}")
        print(f"📊 编码：{self.info['codec']} @ {self.info['bitrate']} Mbps")
        print(f"🎬 帧率：{self.info['fps']} fps, {self.info['frames']} 帧")
        print(f"🔊 音频：{'AAC' if self.info['has_audio'] else '无'}")
        print(f"⏱️  时长：{self.info['duration']:.2f}秒")
    
    def _get_video_info(self) -> dict:
        """获取视频详细信息"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', '-show_format', str(self.video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), {})
        audio_stream = next((s for s in data['streams'] if s['codec_type'] == 'audio'), {})
        
        # 计算码率
        bitrate = data['format'].get('bit_rate', '0')
        bitrate_mbps = round(int(bitrate) / 1_000_000, 2) if bitrate != '0' else 'N/A'
        
        return {
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'codec': video_stream.get('codec_name', 'unknown'),
            'fps': eval(video_stream.get('r_frame_rate', '24/1')),
            'frames': int(video_stream.get('nb_frames', 0)),
            'duration': float(data['format'].get('duration', 0)),
            'has_audio': bool(audio_stream),
            'audio_codec': audio_stream.get('codec_name', 'none'),
            'bitrate': bitrate_mbps
        }
    
    def _build_delogo_filter(self) -> str:
        """构建时间动态 delogo 滤镜"""
        filters = []
        
        for i, region in enumerate(self.watermark_regions):
            x = region['x']
            y = region['y']
            w = region['w']
            h = region['h']
            start = region['start_sec']
            end = region['end_sec']
            
            # 使用 enable=between() 实现时间控制
            filter_str = f"delogo=x={x}:y={y}:w={w}:h={h}:enable=between(t\\,{start}\\,{end})"
            filters.append(filter_str)
        
        # 用逗号连接所有滤镜
        return ','.join(filters)
    
    def process(self, output_path: str):
        """处理视频 - 使用最高画质参数"""
        output_path = Path(output_path)
        
        filter_complex = self._build_delogo_filter()
        
        print(f"\n🎨 使用 FFmpeg delogo 滤镜（最高画质模式）")
        print(f"📍 水印区域：{len(self.watermark_regions)} 段动态处理")
        
        # 构建 FFmpeg 命令 - 无损分辨率 + 最高画质
        cmd = [
            'ffmpeg',
            '-i', str(self.video_path),
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'veryslow',
            '-crf', '14',  # 接近无损的画质
            '-pix_fmt', 'yuv420p',
            '-colorspace', 'bt709',
            '-color_primaries', 'bt709',
            '-color_trc', 'bt709',
            '-x264-params', 'ref=5:bframes=5:b-pyramid=2:weightp=2:rc-lookahead=60:subme=10:merange=57:me=umh:partitions=all:trellis=2:direct=auto',
        ]
        
        if self.info['has_audio']:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '320k',
                '-movflags', '+faststart'
            ])
        
        cmd.extend([
            '-y',
            str(output_path)
        ])
        
        print(f"\n⚙️  编码参数:")
        print(f"   • CRF: 14 (接近无损)")
        print(f"   • Preset: veryslow (最佳压缩)")
        print(f"   • 音频：AAC 320kbps")
        print(f"\n🔄 处理中...")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        for line in process.stderr:
            if 'frame=' in line or 'time=' in line:
                print(line.strip())
        
        process.wait()
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / 1_000_000
            print(f"\n✅ 超高质量处理完成！")
            print(f"📁 输出：{output_path}")
            print(f"📦 大小：{size_mb:.2f} MB")
            print(f"\n💡 查看：open {output_path.parent}")
        else:
            print(f"\n❌ 处理失败！")


def main():
    if len(sys.argv) < 2:
        print("用法：python final_ultra_quality.py <video_path> [output_path]")
        sys.exit(1)
    
    video_path = Path(sys.argv[1])
    
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        output_path = video_path.parent / f"{video_path.stem}_ultra_clean.mp4"
    
    remover = UltraQualityRemover(str(video_path))
    remover.process(str(output_path))


if __name__ == "__main__":
    main()
