#!/usr/bin/env python3
"""
Auto-Coding 项目管理人

核心理念：
1. 我是项目负责人，不是讨论主持人
2. 我读取代码，分析现状
3. 我邀请Reviewer1Reviewer2审查，收集建议
4. 我决定是否接受建议
5. 我编写代码
6. 我给老板总结理由
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path


class ProjectManager:
    """项目管理人"""
    
    def __init__(self, project_name: str, code_paths: list):
        self.project_name = project_name
        self.code_paths = code_paths
        self.file_contents = {}
        self.suggestions = []
        self.decisions = []
        self.start_time = datetime.now()
    
    def read_code(self):
        """读取项目代码"""
        print(f"\n📂 读取项目代码：{self.project_name}", flush=True)
        
        for path in self.code_paths:
            try:
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.file_contents[path] = content
                        print(f"  ✅ {os.path.basename(path)} ({len(content)} 字节)", flush=True)
                
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        # 跳过无关目录
                        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
                        
                        for file in files:
                            if file.endswith(('.py', '.js', '.ts', '.html', '.css')):
                                full_path = os.path.join(root, file)
                                try:
                                    with open(full_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        self.file_contents[full_path] = content
                                        print(f"  ✅ {full_path} ({len(content)} 字节)", flush=True)
                                except:
                                    pass
            except Exception as e:
                print(f"  ⚠️ 读取失败 {path}: {e}", flush=True)
        
        print(f"  📚 共读取 {len(self.file_contents)} 个文件", flush=True)
        return self.file_contents
    
    def analyze_code(self):
        """分析代码质量"""
        print(f"\n🔍 分析代码质量...", flush=True)
        
        analysis = {
            'total_files': len(self.file_contents),
            'total_lines': 0,
            'has_error_handling': False,
            'has_comments': False,
            'has_tests': False,
            'has_type_hints': False,
            'issues': []
        }
        
        for path, content in self.file_contents.items():
            lines = content.split('\n')
            analysis['total_lines'] += len(lines)
            
            # 检查错误处理
            if 'try' in content or 'except' in content or 'catch' in content:
                analysis['has_error_handling'] = True
            
            # 检查注释
            if '//' in content or '/*' in content or '"""' in content or '#' in content:
                analysis['has_comments'] = True
            
            # 检查测试
            if 'test' in path.lower() or 'describe' in content or 'def test_' in content:
                analysis['has_tests'] = True
            
            # 检查类型提示
            if '->' in content or ': str' in content or ': int' in content or 'interface' in content:
                analysis['has_type_hints'] = True
        
        # 识别问题
        if not analysis['has_error_handling']:
            analysis['issues'].append('缺少错误处理')
        if not analysis['has_comments']:
            analysis['issues'].append('注释不足')
        if not analysis['has_tests']:
            analysis['issues'].append('缺少测试')
        
        print(f"  📊 总代码量：{analysis['total_lines']} 行", flush=True)
        print(f"  ✅ 错误处理：{'有' if analysis['has_error_handling'] else '无'}", flush=True)
        print(f"  ✅ 注释：{'充分' if analysis['has_comments'] else '不足'}", flush=True)
        print(f"  ✅ 测试：{'有' if analysis['has_tests'] else '无'}", flush=True)
        
        if analysis['issues']:
            print(f"  ⚠️ 发现问题：{', '.join(analysis['issues'])}", flush=True)
        
        return analysis
    
    def collect_suggestions(self, discussion_messages: list):
        """收集Reviewer1Reviewer2的建议"""
        print(f"\n📋 收集建议...", flush=True)
        
        for msg in discussion_messages:
            from_agent = msg.get('from', '')
            content = msg.get('content', '')
            
            if from_agent in ['Reviewer1', 'Reviewer2']:
                # 提取建议
                suggestion = {
                    'from': from_agent,
                    'content': content,
                    'timestamp': msg.get('time', ''),
                    'accepted': None,  # True/False/None (未决定)
                    'reason': ''
                }
                self.suggestions.append(suggestion)
                print(f"  📝 收到 {from_agent} 的建议", flush=True)
        
        print(f"  共收集 {len(self.suggestions)} 条建议", flush=True)
        return self.suggestions
    
    def make_decision(self, suggestion_idx: int, accept: bool, reason: str):
        """
        对建议做出决策
        
        Args:
            suggestion_idx: 建议索引
            accept: 是否接受
            reason: 理由
        """
        if suggestion_idx >= len(self.suggestions):
            print(f"  ⚠️ 建议索引超出范围", flush=True)
            return
        
        suggestion = self.suggestions[suggestion_idx]
        suggestion['accepted'] = accept
        suggestion['reason'] = reason
        
        decision = {
            'suggestion_idx': suggestion_idx,
            'from': suggestion['from'],
            'accept': accept,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        self.decisions.append(decision)
        
        status = "✅ 接受" if accept else "❌ 拒绝"
        print(f"  {status} {suggestion['from']} 的建议：{reason}", flush=True)
    
    def write_code(self, file_path: str, new_content: str):
        """
        编写/修改代码
        
        Args:
            file_path: 文件路径
            new_content: 新内容
        """
        print(f"\n✏️  编写代码：{file_path}", flush=True)
        
        try:
            # 备份原文件
            if os.path.exists(file_path):
                backup_path = file_path + '.bak'
                with open(file_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)
                print(f"  💾 已备份原文件：{backup_path}", flush=True)
            
            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ 代码已写入", flush=True)
            self.file_contents[file_path] = new_content
            
        except Exception as e:
            print(f"  ❌ 写入失败：{e}", flush=True)
            raise
    
    def generate_summary(self) -> str:
        """生成总结报告"""
        print(f"\n📊 生成总结报告...", flush=True)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        summary = f"""# {self.project_name} - 项目总结报告

**时间**: {datetime.now().isoformat()}
**耗时**: {elapsed:.1f} 秒

---

## 📂 代码分析

- **文件数**: {len(self.file_contents)}
- **总代码量**: {sum(len(c.split('\\n')) for c in self.file_contents.values())} 行
- **错误处理**: {'✅ 有' if any('try' in c for c in self.file_contents.values()) else '⚠️ 无'}
- **注释**: {'✅ 充分' if any('//' in c or '"""' in c for c in self.file_contents.values()) else '⚠️ 不足'}
- **测试**: {'✅ 有' if any('test' in p for p in self.file_contents.keys()) else '⚠️ 无'}

---

## 📋 收集的建议

"""
        
        for i, sug in enumerate(self.suggestions, 1):
            status = "✅ 接受" if sug['accepted'] else ("❌ 拒绝" if sug['accepted'] == False else "⏳ 待定")
            summary += f"""### 建议 {i} ({sug['from']}) {status}
{sug['content'][:300]}

"""
            if sug['reason']:
                summary += f"**理由**: {sug['reason']}\n\n"
        
        summary += f"""---

## ✅ 已实施的修改

"""
        
        for decision in self.decisions:
            if decision['accept']:
                summary += f"- {decision['from']}: {decision['reason']}\n"
        
        summary += f"""
---

## 🎯 下一步计划

1. ...
2. ...
3. ...

---

**项目管理人**: AutoCoder
**状态**: {'完成' if all(s['accepted'] is not None for s in self.suggestions) else '进行中'}
"""
        
        return summary
    
    def save_report(self, summary: str, output_path: str = None):
        """保存总结报告"""
        if not output_path:
            output_path = f'/tmp/{self.project_name.replace(" ", "_")}_summary.md'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"  💾 报告已保存：{output_path}", flush=True)
        return output_path


def create_project_manager(project_name: str, code_paths: list) -> ProjectManager:
    """创建项目管理人"""
    return ProjectManager(project_name, code_paths)
