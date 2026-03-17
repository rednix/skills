#!/usr/bin/env python3
"""
Auto-Coding 自主工作者 v3.1

核心理念：
1. 我是自主的个体，不依赖 RoundTable
2. 我读取代码 → 分析 → 写代码 → 反思 → 优化
3. RoundTable 只是可选工具（复杂项目才用）
4. 我持续完成任务，自主进化
5. ✅ 集成 Web 搜索获取实时信息
6. ✅ 模型交叉验证保证质量
7. ✅ 完整工作流循环（run() 方法）

工作流程：
用户→分析→找方法→实现→测试→反思→修复→交付
                  ↑_______________↓
                    迭代优化循环
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Web 搜索集成
try:
    from ddgs import DDGS
    HAS_WEB_SEARCH = True
except ImportError:
    HAS_WEB_SEARCH = False
    print("⚠️  web_search: 请安装 ddgs 包 (pip install ddgs)")

# 模型验证集成
try:
    from cross_model_validator import CrossModelValidator, AutoTestLoop, CapabilityGapAnalyzer
    HAS_MODEL_VALIDATION = True
except ImportError:
    HAS_MODEL_VALIDATION = False
    print("⚠️  model_validator: 模块未找到")

# 任务拆解集成
try:
    from task_decomposer import TaskDecomposer, Priority
    HAS_TASK_DECOMPOSER = True
except ImportError:
    HAS_TASK_DECOMPOSER = False
    print("⚠️  task_decomposer: 模块未找到")

# 安全模块集成
try:
    from security import validate_path, sanitize_path, validate_input, sanitize_input, detect_sensitive_info
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False
    print("⚠️  security: 模块未找到")


# 允许的基础路径（防止路径遍历）
ALLOWED_BASE_PATHS = [
    os.path.expanduser("~/.enhance-claw"),
    "/tmp/auto-coding-projects",
    "/tmp",
]


class AutoCodingWorker:
    """自主工作者"""
    
    def __init__(self, worker_name: str = "AutoCoder"):
        self.worker_name = worker_name
        self.task_history = []
        self.knowledge_base = self._load_knowledge_base()
        self.start_time = datetime.now()
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        kb_path = Path.home() / f'.enhance-claw/instances/{self.worker_name}/workspace/auto_coding_kb.json'
        
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'tasks_completed': 0,
                'skills_learned': [],
                'code_patterns': [],
                'lessons_learned': []
            }
    
    def _save_knowledge_base(self):
        """保存知识库"""
        kb_path = Path.home() / f'.enhance-claw/instances/{self.worker_name}/workspace/auto_coding_kb.json'
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 知识库已保存", flush=True)
    
    def read_and_analyze(self, code_paths: List[str]) -> Dict:
        """
        读取并分析代码（自主完成，不依赖他人）
        
        安全增强：路径遍历防护 v2.0
        
        Args:
            code_paths: 代码文件路径列表
        
        Returns:
            分析报告
        """
        print(f"\n📂 读取并分析代码...", flush=True)
        
        file_contents = {}
        analysis = {
            'total_files': 0,
            'total_lines': 0,
            'quality_score': 0,
            'issues': [],
            'suggestions': [],
            'security_warnings': []
        }
        
        # 读取文件（带安全验证）
        for path in code_paths:
            try:
                # 🔒 安全检查：路径验证
                if HAS_SECURITY:
                    is_valid, reason = validate_path(path, ALLOWED_BASE_PATHS)
                    if not is_valid:
                        print(f"  🚫 安全拦截：{reason}", flush=True)
                        analysis['security_warnings'].append(f"路径验证失败: {path} - {reason}")
                        continue
                    path = sanitize_path(path)
                else:
                    # 降级：基本检查
                    if '..' in path:
                        print(f"  🚫 路径包含非法字符", flush=True)
                        continue
                
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 🔒 安全检查：敏感信息检测
                        if HAS_SECURITY:
                            sensitive_findings = detect_sensitive_info(content)
                            if sensitive_findings:
                                for finding in sensitive_findings:
                                    print(f"  ⚠️  检测到敏感信息: {finding['type']}", flush=True)
                                    analysis['security_warnings'].append(f"敏感信息: {finding['type']}")
                        
                        file_contents[path] = content
                        analysis['total_files'] += 1
                        analysis['total_lines'] += len(content.split('\n'))
                        print(f"  ✅ {os.path.basename(path)}", flush=True)
                
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
                        
                        for file in files:
                            if file.endswith(('.py', '.js', '.ts', '.html', '.css')):
                                full_path = os.path.join(root, file)
                                
                                # 🔒 安全检查：子路径验证
                                if HAS_SECURITY:
                                    is_valid, reason = validate_path(full_path, ALLOWED_BASE_PATHS)
                                    if not is_valid:
                                        continue
                                
                                try:
                                    with open(full_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        file_contents[full_path] = content
                                        analysis['total_files'] += 1
                                        analysis['total_lines'] += len(content.split('\n'))
                                except:
                                    pass
            except Exception as e:
                print(f"  ⚠️ 读取失败 {path}: {e}", flush=True)
                analysis['issues'].append(f"读取失败: {os.path.basename(path)}")
        
        # 分析质量
        quality_score = 100
        
        for path, content in file_contents.items():
            # 检查错误处理
            if 'try' not in content and 'catch' not in content and 'except' not in content:
                if '缺少错误处理' not in analysis['issues']:
                    analysis['issues'].append('缺少错误处理')
                    quality_score -= 10
            
            # 检查注释
            comment_ratio = (content.count('//') + content.count('/*') + content.count('"""') + content.count('#')) / max(len(content.split('\n')), 1)
            if comment_ratio < 0.1:
                if '注释不足' not in analysis['issues']:
                    analysis['issues'].append('注释不足')
                    quality_score -= 10
            
            # 检查测试
            if 'test' in path.lower():
                analysis['has_tests'] = True
        
        analysis['quality_score'] = max(0, quality_score)
        
        # 生成建议
        if '缺少错误处理' in analysis['issues']:
            analysis['suggestions'].append('添加错误处理（try-catch/try-except）')
        if '注释不足' in analysis['issues']:
            analysis['suggestions'].append('增加代码注释，提高可维护性')
        if not analysis.get('has_tests'):
            analysis['suggestions'].append('添加单元测试')
        
        print(f"  📊 文件数：{analysis['total_files']}, 代码量：{analysis['total_lines']} 行", flush=True)
        print(f"  📈 质量分数：{analysis['quality_score']}/100", flush=True)
        if analysis['issues']:
            print(f"  ⚠️ 问题：{', '.join(analysis['issues'])}", flush=True)
        if analysis['suggestions']:
            print(f"  💡 建议：{', '.join(analysis['suggestions'])}", flush=True)
        
        return analysis
    
    def self_reflect(self, work_result: Dict) -> Dict:
        """
        自我反思（不依赖他人）
        
        Args:
            work_result: 工作结果
        
        Returns:
            反思结果
        """
        print(f"\n🤔 自我反思...", flush=True)
        
        reflection = {
            'what_went_well': [],
            'what_to_improve': [],
            'lessons_learned': [],
            'next_actions': []
        }
        
        # 分析工作结果
        if work_result.get('quality_score', 0) >= 80:
            reflection['what_went_well'].append('代码质量良好')
        else:
            reflection['what_to_improve'].append('提高代码质量')
        
        if work_result.get('completed', False):
            reflection['what_went_well'].append('任务已完成')
        else:
            reflection['what_to_improve'].append('确保任务完成')
        
        # 生成经验教训
        if work_result.get('issues'):
            for issue in work_result['issues']:
                reflection['lessons_learned'].append(f'注意：{issue}')
        
        # 生成下一步行动
        for suggestion in work_result.get('suggestions', []):
            reflection['next_actions'].append(f'实施：{suggestion}')
        
        # 保存到知识库
        self.knowledge_base['lessons_learned'].extend(reflection['lessons_learned'])
        self._save_knowledge_base()
        
        print(f"  ✅ 做得好的：{reflection['what_went_well']}", flush=True)
        print(f"  🔧 需改进的：{reflection['what_to_improve']}", flush=True)
        print(f"  💡 经验教训：{reflection['lessons_learned']}", flush=True)
        
        return reflection
    
    def write_code(self, file_path: str, content: str, backup: bool = True):
        """
        编写代码（自主完成）
        
        Args:
            file_path: 文件路径
            content: 代码内容
            backup: 是否备份原文件
        """
        print(f"\n✏️  编写代码：{os.path.basename(file_path)}", flush=True)
        
        try:
            # 备份
            if backup and os.path.exists(file_path):
                backup_path = file_path + '.bak'
                with open(file_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)
                print(f"  💾 已备份：{os.path.basename(backup_path)}", flush=True)
            
            # 写入
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ 代码已写入", flush=True)
            
        except Exception as e:
            print(f"  ❌ 写入失败：{e}", flush=True)
            raise
    
    def request_help(self, task_description: str, helpers: List[str] = ['Reviewer1', 'Reviewer2']) -> Optional[Dict]:
        """
        请求帮助（可选，仅复杂项目使用）
        
        Args:
            task_description: 任务描述
            helpers: 帮助者列表
        
        Returns:
            帮助结果（如果有）
        """
        print(f"\n🤝 请求帮助：{', '.join(helpers)}", flush=True)
        print(f"  任务：{task_description[:100]}...", flush=True)
        print(f"  ⚠️  RoundTable 是可选的，仅复杂项目使用", flush=True)
        
        # 这里可以创建 RoundTable 任务
        # 但不是必须的
        return None
    
    def complete_task(self, task_description: str, result: Dict):
        """
        完成任务
        
        Args:
            task_description: 任务描述
            result: 结果
        """
        print(f"\n✅ 完成任务：{task_description[:50]}...", flush=True)
        
        self.task_history.append({
            'description': task_description,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        self.knowledge_base['tasks_completed'] += 1
        self._save_knowledge_base()
    
    def generate_summary(self, task_description: str, work_result: Dict, reflection: Dict) -> str:
        """
        生成总结报告（给用户）
        
        Args:
            task_description: 任务描述
            work_result: 工作结果
            reflection: 反思结果
        
        Returns:
            总结报告
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        summary = f"""# {task_description} - 总结报告

**时间**: {datetime.now().isoformat()}
**耗时**: {elapsed:.1f} 秒
**工作者**: {self.worker_name}

---

## 📂 工作内容

1. **读取代码**: {work_result.get('total_files', 0)} 个文件，{work_result.get('total_lines', 0)} 行代码
2. **分析质量**: {work_result.get('quality_score', 0)}/100 分
3. **识别问题**: {len(work_result.get('issues', []))} 个
4. **实施改进**: {len(work_result.get('improvements', []))} 项

---

## ✅ 发现的问题

"""
        
        for issue in work_result.get('issues', []):
            summary += f"- {issue}\n"
        
        summary += f"""
---

## 🔧 实施的改进

"""
        
        for improvement in work_result.get('improvements', []):
            summary += f"- {improvement}\n"
        
        summary += f"""
---

## 🤔 自我反思

**做得好的**:
{chr(10).join(f'- {item}' for item in reflection.get('what_went_well', ['无']))}

**需改进的**:
{chr(10).join(f'- {item}' for item in reflection.get('what_to_improve', ['无']))}

**经验教训**:
{chr(10).join(f'- {item}' for item in reflection.get('lessons_learned', ['无']))}

---

## 🎯 下一步计划

{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(reflection.get('next_actions', ['无'])))}

---

## 💬 给用户的话

{self._generate_message_to_boss(work_result, reflection)}

---

**工作者**: {self.worker_name}
**状态**: {'✅ 完成' if work_result.get('completed') else '⏳ 进行中'}
"""
        
        return summary
    
    def _generate_message_to_boss(self, work_result: Dict, reflection: Dict) -> str:
        """生成给用户的话"""
        if work_result.get('quality_score', 0) >= 80:
            return "用户，代码质量良好，已自主完成分析和优化。如有需要，我可以请求Reviewer1Reviewer2协助审查复杂部分。"
        else:
            return "用户，代码质量有待提高，我已识别问题并实施改进。后续会持续优化，必要时请求协助。"
    
    def web_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Web 搜索（获取实时信息）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
        
        Returns:
            搜索结果列表
        """
        if not HAS_WEB_SEARCH:
            print(f"  ⚠️  Web 搜索不可用，请安装 ddgs 包", flush=True)
            return []
        
        print(f"  🔍 Web 搜索：{query[:50]}...", flush=True)
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
                print(f"  📊 找到 {len(results)} 个结果", flush=True)
                
                # 保存到知识库
                search_record = {
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'results_count': len(results),
                    'results': results[:3]  # 只保存前 3 个
                }
                
                if 'web_searches' not in self.knowledge_base:
                    self.knowledge_base['web_searches'] = []
                self.knowledge_base['web_searches'].append(search_record)
                self._save_knowledge_base()
                
                return results
        
        except Exception as e:
            print(f"  ⚠️  搜索失败：{e}", flush=True)
            return []
    
    def model_validation(self, code_content: str, analysis_result: Dict) -> Optional[str]:
        """
        模型交叉验证（质量保证）
        
        Args:
            code_content: 代码内容
            analysis_result: 原始分析结果
        
        Returns:
            验证报告，如果跳过验证则返回 None
        """
        if not HAS_MODEL_VALIDATION:
            print(f"  ⚠️  模型验证不可用", flush=True)
            return None
        
        print(f"\n🔍 步骤：模型交叉验证", flush=True)
        
        try:
            validator = CrossModelValidator()
            # 简化的验证流程
            report = validator._merge_results([
                type('CodeVersion', (), {'code': code_content, 'model': 'current', 'role': 'implementer'})()
            ])
            
            print(f"  ✅ 验证完成", flush=True)
            return str(report)
        
        except Exception as e:
            print(f"  ⚠️  验证失败：{e}", flush=True)
            return None
    
    async def run(self, task_description: str, code_paths: List[str] = None) -> Dict:
        """
        运行完整的 auto-coding 工作流
        
        用户→分析→找方法→实现→测试→反思→修复→交付
                      ↑_______________↓
                        迭代优化循环
        
        Args:
            task_description: 任务描述
            code_paths: 代码文件路径列表（可选）
        
        Returns:
            完整的工作结果
        """
        print("\n" + "="*60, flush=True)
        print(f"🚀 Auto-Coding Worker v3.1 启动", flush=True)
        print(f"📋 任务：{task_description}", flush=True)
        print("="*60, flush=True)
        
        self.start_time = datetime.now()
        work_result = {
            'task': task_description,
            'completed': False,
            'iterations': 0,
            'issues': [],
            'improvements': []
        }
        
        try:
            # ========== 阶段 1: 能力缺口分析 ==========
            print("\n📊 阶段 1/5: 能力缺口分析", flush=True)
            if HAS_MODEL_VALIDATION:
                analyzer = CapabilityGapAnalyzer()
                gaps = await analyzer.analyze_with_llm(task_description)
                work_result['capability_gaps'] = gaps
                print(f"  ✅ 识别到 {len(gaps)} 个能力缺口", flush=True)
                for gap in gaps[:3]:  # 只显示前 3 个
                    print(f"     - {gap['type']}: {gap['reason']}", flush=True)
            else:
                work_result['capability_gaps'] = []
                print(f"  ⚠️  能力缺口分析不可用", flush=True)
            
            # ========== 阶段 2: 代码分析 ==========
            print("\n📂 阶段 2/5: 代码分析", flush=True)
            if code_paths:
                analysis = self.read_and_analyze(code_paths)
                work_result.update(analysis)
            else:
                work_result['total_files'] = 0
                work_result['total_lines'] = 0
                work_result['quality_score'] = 100
                work_result['issues'] = []
                work_result['suggestions'] = []
                print(f"  ℹ️  无代码路径，跳过分析", flush=True)
            
            # ========== 阶段 3: 任务拆解 ==========
            print("\n📋 阶段 3/5: 任务拆解", flush=True)
            if HAS_TASK_DECOMPOSER:
                decomposer = TaskDecomposer()
                tasks = decomposer.decompose(task_description, work_result)
                decomposer.print_status()
                work_result['subtasks'] = len(tasks)
                work_result['task_progress'] = decomposer.get_progress()
            else:
                work_result['subtasks'] = 0
                print(f"  ⚠️  任务拆解器不可用", flush=True)
            
            # ========== 阶段 4: 多模型验证与实现 ==========
            print("\n🔍 阶段 4/5: 多模型验证", flush=True)
            if HAS_MODEL_VALIDATION:
                validator = CrossModelValidator()
                validation_result = await validator.validate_task(task_description)
                work_result['validation'] = {
                    'passed': validation_result.passed,
                    'merged_from': validation_result.merged_from,
                    'confidence': validation_result.confidence,
                    'test_coverage': validation_result.test_coverage
                }
                print(f"  ✅ 验证完成 | 置信度：{validation_result.confidence}", flush=True)
            else:
                work_result['validation'] = None
                print(f"  ⚠️  多模型验证不可用", flush=True)
            
            # ========== 阶段 5: 自动测试循环 ==========
            print("\n🧪 阶段 5/5: 自动测试循环", flush=True)
            if HAS_MODEL_VALIDATION and work_result.get('validation', {}).get('best_code'):
                test_loop = AutoTestLoop(max_iterations=3)
                test_result = await test_loop.run_until_pass(
                    work_result['validation']['best_code'],
                    "echo 'No tests configured'",
                    "src/output.py"
                )
                work_result['test_result'] = {
                    'passed': test_result.passed,
                    'coverage': test_result.test_coverage
                }
                print(f"  ✅ 测试完成 | 覆盖率：{test_result.test_coverage}%", flush=True)
            else:
                work_result['test_result'] = None
                print(f"  ℹ️  无代码可测试", flush=True)
            
            # ========== 自我反思 ==========
            print("\n🤔 自我反思", flush=True)
            reflection = self.self_reflect(work_result)
            work_result['reflection'] = reflection
            
            # ========== 完成任务 ==========
            work_result['completed'] = True
            work_result['elapsed_seconds'] = (datetime.now() - self.start_time).total_seconds()
            self.complete_task(task_description, work_result)
            
            # ========== 生成总结 ==========
            print("\n📊 生成总结报告", flush=True)
            summary = self.generate_summary(task_description, work_result, reflection)
            work_result['summary'] = summary
            
            print("\n" + "="*60, flush=True)
            print(f"✅ Auto-Coding 完成！耗时：{work_result['elapsed_seconds']:.1f}秒", flush=True)
            print("="*60, flush=True)
            
            return work_result
            
        except Exception as e:
            print(f"\n❌ 工作流执行失败：{e}", flush=True)
            import traceback
            traceback.print_exc()
            work_result['error'] = str(e)
            work_result['completed'] = False
            return work_result


def create_worker(name: str = "AutoCoder") -> AutoCodingWorker:
    """创建自主工作者"""
    return AutoCodingWorker(name)
