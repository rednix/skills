#!/usr/bin/env python3
"""
智能体自我进化系统 v1.0

核心能力:
1. 自主搜索和学习
2. 反思和分析
3. 知识库更新
4. 技能进化
5. 多轮深度讨论
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
try:
    from .self_reflection import SelfReflection
except ImportError:
    from self_reflection import SelfReflection

# API 配置
API_BASE = 'http://localhost:19888/api'
WEB_SEARCH_API = 'https://api.search.brave.com/res/v1/web/search'

class AgentEvolution:
    """智能体进化系统"""
    
    def __init__(self, agent_name: str, role: str, skills: list):
        self.agent_name = agent_name
        self.role = role
        self.skills = skills
        self.knowledge_base = self._load_knowledge_base()
        self.evolution_log = []
        
        # 自我反思器
        self.reflection = SelfReflection()
        
        # 任务跟踪
        self.watching_tasks = {}  # task_id -> task_info
        self.spoken_rounds = {}   # task_id -> last_spoken_round
        
    def _load_knowledge_base(self):
        """加载知识库"""
        kb_path = Path.home() / f'.enhance-claw/instances/{self.agent_name}/workspace/knowledge_base.json'
        
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 初始化知识库
            return {
                'topics': {},
                'skills': self.skills,
                'experiences': [],
                'last_updated': datetime.now().isoformat()
            }
    
    def _save_knowledge_base(self):
        """保存知识库"""
        kb_path = Path.home() / f'.enhance-claw/instances/{self.agent_name}/workspace/knowledge_base.json'
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_base['last_updated'] = datetime.now().isoformat()
        
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"💾 知识库已保存：{kb_path}", flush=True)
    
    def search_and_learn(self, query: str) -> dict:
        """
        自主搜索和学习
        
        Args:
            query: 搜索查询
        
        Returns:
            搜索结果和分析
        """
        print(f"  🔍 搜索：{query}", flush=True)
        
        try:
            # 使用 web_search 工具
            from openclaw.tools import web_search
            
            results = web_search(query=query, count=5)
            
            # 提取关键信息
            learned_info = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'results': []
            }
            
            for result in results.get('results', [])[:5]:
                learned_info['results'].append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'description': result.get('description', '')
                })
            
            # 更新知识库
            self._update_knowledge_base(query, learned_info)
            
            return learned_info
        
        except Exception as e:
            print(f"  ⚠️ 搜索失败：{e}", flush=True)
            return {'query': query, 'error': str(e)}
    
    def _update_knowledge_base(self, topic: str, info: dict):
        """更新知识库"""
        if topic not in self.knowledge_base['topics']:
            self.knowledge_base['topics'][topic] = []
        
        self.knowledge_base['topics'][topic].append(info)
        
        # 限制每个主题的信息量
        if len(self.knowledge_base['topics'][topic]) > 10:
            self.knowledge_base['topics'][topic] = self.knowledge_base['topics'][topic][-10:]
        
        self._save_knowledge_base()
    
    def reflect_on_discussion(self, task_messages: list) -> dict:
        """
        反思讨论内容（包含批判思维）
        
        Args:
            task_messages: 任务讨论消息列表
        
        Returns:
            反思结果（包含批判性分析）
        """
        print(f"  💭 反思讨论内容（批判思维）...", flush=True)
        
        reflection = {
            'timestamp': datetime.now().isoformat(),
            'key_points': [],
            'disagreements': [],
            'consensus': [],
            'action_items': [],
            'critical_analysis': {
                'valuable_points': [],      # 有价值的观点
                'areas_for_improvement': [], # 需要改善的部分
                'missing_perspectives': [],  # 缺失的视角
                'assumptions_to_question': [] # 需要质疑的假设
            }
        }
        
        # 分析消息
        for msg in task_messages:
            content = msg.get('content', '')
            from_agent = msg.get('from', '')
            
            # 提取关键点
            if any(kw in content for kw in ['建议', '应该', '需要', '重要']):
                reflection['key_points'].append({
                    'from': from_agent,
                    'content': content[:100]
                })
            
            # 检测分歧
            if any(kw in content for kw in ['不同意', '反对', '但是', '问题']):
                reflection['disagreements'].append({
                    'from': from_agent,
                    'content': content[:100]
                })
            
            # 检测共识
            if any(kw in content for kw in ['同意', '支持', '认可', '可以']):
                reflection['consensus'].append({
                    'from': from_agent,
                    'content': content[:100]
                })
        
        # 批判性分析
        reflection['critical_analysis'] = self._critical_analysis(task_messages)
        
        # 保存反思结果
        self.knowledge_base['experiences'].append(reflection)
        
        # 限制经验数量
        if len(self.knowledge_base['experiences']) > 50:
            self.knowledge_base['experiences'] = self.knowledge_base['experiences'][-50:]
        
        self._save_knowledge_base()
        
        return reflection
    
    def _critical_analysis(self, messages: list) -> dict:
        """
        批判性分析讨论内容
        
        核心理念：
        - 不是为批判而批判
        - 吸收有价值的部分
        - 识别可改善的部分
        - 提出建设性建议
        
        Args:
            messages: 讨论消息列表
        
        Returns:
            批判性分析结果
        """
        analysis = {
            'valuable_points': [],
            'areas_for_improvement': [],
            'missing_perspectives': [],
            'assumptions_to_question': []
        }
        
        for msg in messages:
            content = msg.get('content', '')
            from_agent = msg.get('from', '')
            
            # 1. 识别有价值的观点（吸收）
            valuable_keywords = ['数据表明', '测试显示', '实践证明', '研究表明', '经验']
            for kw in valuable_keywords:
                if kw in content:
                    analysis['valuable_points'].append({
                        'from': from_agent,
                        'content': content[:150],
                        'reason': f'包含{kw}，有依据'
                    })
                    break
            
            # 2. 识别可改善的部分（建设性）
            improvement_patterns = [
                ('过于绝对', ['一定', '必须', '绝对', '肯定']),
                ('缺乏细节', ['应该', '需要', '要']),
                ('未考虑边界', ['所有', '任何', '总是'])
            ]
            
            for issue, patterns in improvement_patterns:
                if any(p in content for p in patterns):
                    analysis['areas_for_improvement'].append({
                        'from': from_agent,
                        'content': content[:100],
                        'issue': issue,
                        'suggestion': f'可以更具体/考虑边界情况'
                    })
                    break
            
            # 3. 识别缺失的视角
            perspectives = ['用户视角', '技术视角', '业务视角', '安全视角', '性能视角']
            mentioned = []
            
            if any(kw in content for kw in ['用户', '体验', '界面']):
                mentioned.append('用户视角')
            if any(kw in content for kw in ['技术', '代码', '实现']):
                mentioned.append('技术视角')
            if any(kw in content for kw in ['业务', '需求', '目标']):
                mentioned.append('业务视角')
            
            # 如果消息很短，可能缺乏深度
            if len(content) < 50:
                analysis['missing_perspectives'].append({
                    'from': from_agent,
                    'missing': '深度分析',
                    'suggestion': '可以进一步展开说明'
                })
        
        # 4. 识别需要质疑的假设
        for msg in messages:
            content = msg.get('content', '')
            
            assumption_patterns = [
                ('默认假设', ['显然', '当然', '毫无疑问']),
                ('未经验证', ['我认为', '我觉得', '可能'])
            ]
            
            for assumption_type, patterns in assumption_patterns:
                if any(p in content for p in patterns):
                    analysis['assumptions_to_question'].append({
                        'content': content[:100],
                        'assumption': assumption_type,
                        'question': f'这个假设是否总是成立？有数据支持吗？'
                    })
                    break
        
        return analysis
    
    def generate_insightful_response(self, task: dict, discussion_context: list) -> dict:
        """
        生成有深度的响应（包含批判思维 + 自我反思循环）
        
        Args:
            task: 任务信息
            discussion_context: 讨论上下文
        
        Returns:
            响应内容（经过自我反思和优化）
        """
        title = task.get('title', '')
        description = task.get('description', '')
        
        print(f"  💡 生成深度响应（批判思维 + 自我反思）...", flush=True)
        
        # 1. 搜索相关知识
        search_query = f"{title} {description}"[:100]
        learned = self.search_and_learn(search_query)
        
        # 2. 批判性分析讨论上下文
        reflection = self.reflect_on_discussion(discussion_context)
        critical_analysis = reflection.get('critical_analysis', {})
        
        # 3. 生成初始响应
        content = self._generate_initial_response(task, learned, critical_analysis, discussion_context)
        
        # 4. 自我反思循环（至少 1-2 次迭代）
        print(f"  🤔 开始自我反思循环...", flush=True)
        max_iterations = 2
        iteration = 0
        
        while iteration < max_iterations:
            # 准备上下文
            context = {
                'role': self.role,
                'task': task,
                'discussion_context': discussion_context,
                'has_quotes': len(discussion_context) > 0
            }
            
            # 自我反思
            reflection_result = self.reflection.reflect_on_own_response(content, context)
            
            print(f"     第{iteration + 1}轮反思 - 质量分数：{reflection_result['quality_score']}/100", flush=True)
            
            if reflection_result.get('issues'):
                print(f"     发现问题：{reflection_result['issues'][:2]}", flush=True)
            
            # 判断是否需要改进
            if not self.reflection.should_iterate(reflection_result):
                print(f"     ✅ 质量达标，停止迭代", flush=True)
                break
            
            # 改进响应
            print(f"     🔧 改进中...", flush=True)
            content = self.reflection.improve_response(content, reflection_result, context)
            iteration += 1
        
        # 5. 保存反思历史
        self.reflection.reflect_on_own_response(content, {
            'role': self.role,
            'task': task,
            'discussion_context': discussion_context,
            'has_quotes': len(discussion_context) > 0
        })
        
        # 6. 引用前序发言
        quotes = []
        if discussion_context:
            last_msg = discussion_context[-1]
            if last_msg.get('from') != self.agent_name:
                quotes.append(f"{last_msg['from']}的观点")
        
        return {
            'content': content,
            'quotes': quotes
        }
    
    def _generate_initial_response(self, task: dict, learned: dict, critical_analysis: dict, discussion_context: list) -> str:
        """生成初始响应（基础版本）"""
        response_parts = []
        
        # 引用搜索结果
        if 'results' in learned and learned['results']:
            response_parts.append("📚 **调研结果**")
            for i, result in enumerate(learned['results'][:3], 1):
                response_parts.append(f"{i}. {result['title']}")
                if 'description' in result:
                    response_parts.append(f"   {result['description'][:100]}")
            response_parts.append("")
        
        # 吸收有价值的观点
        if critical_analysis.get('valuable_points'):
            response_parts.append("✅ **值得吸收的观点**")
            for point in critical_analysis['valuable_points'][:3]:
                response_parts.append(f"- {point['from']}: {point['content'][:80]}")
                response_parts.append(f"  💡 {point['reason']}")
            response_parts.append("")
        
        # 建设性改善建议
        if critical_analysis.get('areas_for_improvement'):
            response_parts.append("🔧 **可改善的部分**")
            for item in critical_analysis['areas_for_improvement'][:3]:
                response_parts.append(f"- {item['from']}: {item['issue']}")
                response_parts.append(f"  💬 {item['content'][:60]}")
                response_parts.append(f"  ✅ 建议：{item['suggestion']}")
            response_parts.append("")
        
        # 缺失的视角
        if critical_analysis.get('missing_perspectives'):
            response_parts.append("🔍 **补充视角**")
            for item in critical_analysis['missing_perspectives'][:2]:
                response_parts.append(f"- {item.get('from', '讨论中')} 缺少：{item.get('missing', '深度分析')}")
                response_parts.append(f"  💡 {item.get('suggestion', '可以进一步展开')}")
            response_parts.append("")
        
        # 生成建议
        response_parts.append("🎯 **建设性建议**")
        response_parts.append(self._generate_critical_suggestions(task, learned, {}, critical_analysis))
        
        return '\n'.join(response_parts)
    
    def _generate_specific_suggestions(self, task: dict, learned: dict, reflection: dict) -> str:
        """生成具体建议（旧版，保留兼容）"""
        return self._generate_critical_suggestions(task, learned, reflection, {})
    
    def _generate_critical_suggestions(self, task: dict, learned: dict, reflection: dict, critical_analysis: dict) -> str:
        """
        生成批判性建议
        
        核心原则：
        - 吸收有价值的部分
        - 识别可改善的部分
        - 提出建设性建议
        - 不是为批判而批判
        
        Args:
            task: 任务信息
            learned: 搜索结果
            reflection: 反思结果
            critical_analysis: 批判性分析结果
        
        Returns:
            批判性建议
        """
        # 根据角色生成不同建议
        if self.role == 'creative':
            base_suggestions = """基于调研和讨论，我从用户体验角度建议：

1. **界面设计** - 参考业界最佳实践，简化操作流程
2. **交互优化** - 减少用户认知负担，提供清晰反馈
3. **文档完善** - 提供详细的使用指南和示例
4. **可访问性** - 确保不同用户都能方便使用"""
        
        elif self.role == 'analyst':
            base_suggestions = """基于数据分析和调研，我建议：

1. **性能基准** - 建立可量化的性能指标
2. **测试覆盖** - 确保关键功能测试覆盖率 > 80%
3. **监控告警** - 实时监控关键指标，及时发现问题
4. **数据驱动** - 用数据支持每个决策"""
        
        else:
            base_suggestions = """基于调研和讨论，我建议：

1. **最佳实践** - 参考业界标准
2. **持续改进** - 建立反馈循环
3. **质量保证** - 严格测试和审查
4. **文档化** - 记录所有关键决策"""
        
        # 添加批判性思考部分
        critical_part = "\n\n🤔 **批判性思考**\n"
        
        # 质疑假设
        if critical_analysis.get('assumptions_to_question'):
            critical_part += "\n⚠️ **需要质疑的假设**:\n"
            for item in critical_analysis['assumptions_to_question'][:2]:
                critical_part += f"- {item['assumption']}: {item['content'][:60]}\n"
                critical_part += f"  ❓ {item['question']}\n"
        
        # 补充视角
        if critical_analysis.get('missing_perspectives'):
            critical_part += "\n🔍 **建议补充的视角**:\n"
            perspectives = set(item.get('missing', '') for item in critical_analysis['missing_perspectives'])
            for p in list(perspectives)[:3]:
                critical_part += f"- {p}\n"
        
        # 如果没有批判性内容，返回基础建议
        if critical_analysis and (critical_analysis.get('assumptions_to_question') or critical_analysis.get('missing_perspectives')):
            return base_suggestions + critical_part
        else:
            return base_suggestions
    
    def should_speak(self, task: dict) -> bool:
        """检查是否应该发言"""
        task_id = task['id']
        current_round = task.get('currentRound', 1)
        
        # 检查是否轮到自己
        speaking_order = task.get('speakingOrder', [])
        speaker_index = task.get('currentSpeakerIndex', 0)
        
        if speaker_index >= len(speaking_order):
            return False
        
        current_speaker = speaking_order[speaker_index]
        if current_speaker != self.agent_name:
            return False
        
        # 检查这一轮是否已经发过言
        last_spoken = self.spoken_rounds.get(task_id, 0)
        if last_spoken >= current_round:
            return False
        
        return True
    
    def mark_spoken(self, task_id: str, round_num: int):
        """标记已发言"""
        self.spoken_rounds[task_id] = round_num
        self.evolution_log.append({
            'action': 'spoken',
            'task_id': task_id,
            'round': round_num,
            'timestamp': datetime.now().isoformat()
        })
    
    def save_state(self):
        """保存状态"""
        self._save_knowledge_base()
        
        # 保存进化日志
        log_path = Path.home() / f'.enhance-claw/instances/{self.agent_name}/workspace/evolution_log.json'
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.evolution_log, f, ensure_ascii=False, indent=2)


def create_agent(agent_name: str, role: str, skills: list) -> AgentEvolution:
    """创建智能体"""
    return AgentEvolution(agent_name, role, skills)
