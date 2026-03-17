#!/usr/bin/env python3
"""
自我反思与优化模块

核心理念：
1. 发言前先自我反思
2. 识别自身观点的局限性
3. 迭代优化至少 1-2 轮
4. 确保质量再输出
"""

from datetime import datetime
from typing import Dict, List


class SelfReflection:
    """自我反思器"""
    
    def __init__(self):
        self.reflection_history = []
    
    def reflect_on_own_response(self, draft_response: str, context: Dict) -> Dict:
        """
        对自己的响应草稿进行反思
        
        Args:
            draft_response: 响应草稿
            context: 上下文信息（角色、任务、讨论历史等）
        
        Returns:
            反思结果和改进建议
        """
        reflection = {
            'timestamp': datetime.now().isoformat(),
            'draft_length': len(draft_response),
            'issues': [],
            'improvements': [],
            'missing_elements': [],
            'quality_score': 0
        }
        
        # 1. 检查长度
        if len(draft_response) < 100:
            reflection['issues'].append('内容过短，缺乏深度')
            reflection['improvements'].append('展开说明每个观点，提供具体例子')
        
        # 2. 检查是否有数据/依据支持
        if not any(kw in draft_response for kw in ['数据', '测试', '表明', '显示', '证明', '案例']):
            reflection['issues'].append('缺乏数据或案例支持')
            reflection['improvements'].append('添加具体数据、测试结果或实际案例')
        
        # 3. 检查是否考虑了边界情况
        if not any(kw in draft_response for kw in ['边界', '例外', '特殊情况', '如果', '可能']):
            reflection['issues'].append('未考虑边界情况和例外')
            reflection['improvements'].append('说明适用条件和可能的例外情况')
        
        # 4. 检查是否有具体可执行的建议
        if not any(kw in draft_response for kw in ['具体', '步骤', '如何', '实施', '执行']):
            reflection['issues'].append('建议不够具体，难以执行')
            reflection['improvements'].append('提供具体的实施步骤和方法')
        
        # 5. 检查是否引用了上下文
        if context.get('discussion_context') and not any(kw in draft_response for kw in ['如前所述', '同意', '补充', '回应']):
            reflection['missing_elements'].append('未回应前序发言')
            reflection['improvements'].append('引用和回应其他 Agent 的观点')
        
        # 6. 检查是否有批判性思考
        if not any(kw in draft_response for kw in ['但是', '然而', '质疑', '假设', '前提', '反思']):
            reflection['missing_elements'].append('缺乏批判性思考')
            reflection['improvements'].append('质疑假设，提出不同视角')
        
        # 7. 计算质量分数 (0-100)
        base_score = 60
        if len(draft_response) > 200:
            base_score += 10
        if len(reflection['improvements']) == 0:
            base_score += 20
        if context.get('has_quotes'):
            base_score += 10
        
        reflection['quality_score'] = min(100, base_score)
        
        # 8. 判断是否需要改进
        reflection['needs_improvement'] = reflection['quality_score'] < 80
        reflection['iteration_needed'] = 1 if reflection['needs_improvement'] else 0
        
        # 保存反思历史
        self.reflection_history.append(reflection)
        
        return reflection
    
    def improve_response(self, draft_response: str, reflection: Dict, context: Dict) -> str:
        """
        根据反思结果改进响应
        
        Args:
            draft_response: 原始草稿
            reflection: 反思结果
            context: 上下文
        
        Returns:
            改进后的响应
        """
        improved = draft_response
        
        # 根据改进建议增强响应
        if '缺乏数据或案例支持' in str(reflection.get('issues', [])):
            improved += "\n\n📊 **数据支持**\n根据业界实践和测试经验，建议..."
        
        if '未考虑边界情况' in str(reflection.get('issues', [])):
            improved += "\n\n⚠️ **边界情况**\n需要注意的是，在以下特殊情况可能需要调整..."
        
        if '建议不够具体' in str(reflection.get('issues', [])):
            improved += "\n\n📋 **实施步骤**\n1. 第一步...\n2. 第二步...\n3. 第三步..."
        
        if '未回应前序发言' in str(reflection.get('missing_elements', [])):
            improved = "回应前面的讨论，" + improved
        
        if '缺乏批判性思考' in str(reflection.get('missing_elements', [])):
            improved += "\n\n🤔 **进一步思考**\n这个观点的前提是... 是否总是成立？"
        
        return improved
    
    def should_iterate(self, reflection: Dict) -> bool:
        """判断是否需要迭代优化"""
        return reflection.get('needs_improvement', False)
    
    def get_reflection_summary(self) -> Dict:
        """获取反思历史摘要"""
        if not self.reflection_history:
            return {'total_reflections': 0}
        
        return {
            'total_reflections': len(self.reflection_history),
            'avg_quality_score': sum(r['quality_score'] for r in self.reflection_history) / len(self.reflection_history),
            'common_issues': self._analyze_common_issues(),
            'improvement_trend': self._analyze_trend()
        }
    
    def _analyze_common_issues(self) -> List[str]:
        """分析常见问题"""
        issue_count = {}
        for r in self.reflection_history:
            for issue in r.get('issues', []):
                issue_count[issue] = issue_count.get(issue, 0) + 1
        
        return sorted(issue_count.keys(), key=lambda x: issue_count[x], reverse=True)[:5]
    
    def _analyze_trend(self) -> str:
        """分析质量趋势"""
        if len(self.reflection_history) < 2:
            return '数据不足'
        
        recent = self.reflection_history[-3:]
        avg_recent = sum(r['quality_score'] for r in recent) / len(recent)
        
        older = self.reflection_history[:-3]
        if older:
            avg_older = sum(r['quality_score'] for r in older) / len(older)
            
            if avg_recent > avg_older + 5:
                return '上升 ↑'
            elif avg_recent < avg_older - 5:
                return '下降 ↓'
            else:
                return '稳定 →'
        
        return '新开始'
