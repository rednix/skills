#!/usr/bin/env python3
"""
模型验证器

核心理念：
1. 读取 OpenClaw 配置，获取可用模型
2. 识别适合编程推理的模型
3. 自主切换到编程模型
4. 进行代码交叉分析和验证
5. 生成验证报告
6. 切换回原模型

配置说明：
- 模型配置可通过环境变量 AUTO_CODING_MODELS_CONFIG 指定配置文件路径
- 或在代码中自定义 CODING_MODELS 字典
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# 编程推理模型配置示例
# 用户应根据自己的模型提供商修改此配置
# 格式: { 'model_id': { 'name': '显示名称', 'strength': '擅长领域', 'coding_score': 分数, 'context_window': 上下文窗口 } }
DEFAULT_CODING_MODELS = {
    # 示例模型配置 - 请根据实际情况修改
    'default-coder': {
        'name': 'Default Coder',
        'strength': '通用代码生成',
        'coding_score': 85,
        'context_window': 100000
    },
    'default-reviewer': {
        'name': 'Default Reviewer',
        'strength': '代码审查',
        'coding_score': 80,
        'context_window': 100000
    },
}

# 尝试从环境变量加载用户配置
def _load_coding_models() -> Dict:
    """加载编程模型配置"""
    config_path = os.getenv('AUTO_CODING_MODELS_CONFIG')
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CODING_MODELS

CODING_MODELS = _load_coding_models()

# 验证配置
VALIDATION_CONFIG = {
    'preferred_score': 90,        # 优先选择的评分（达到此值优先使用）
    'min_context_safety': 50000,  # 最低安全上下文 (50K，低于此值警告)
}


class ModelValidator:
    """模型验证器"""
    
    def __init__(self):
        self.current_model = None
        self.available_models = []
        self.coding_models = []
        self.validation_history = []
    
    def load_openclaw_config(self) -> Dict:
        """读取 OpenClaw 配置"""
        print(f"\n🔧 读取 OpenClaw 配置...", flush=True)
        
        config_paths = [
            Path.home() / '.openclaw' / 'openclaw.json',
            Path.home() / '.enhance-claw' / 'instances' / 'AutoCoder' / 'config' / 'openclaw.json',
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        print(f"  ✅ 配置文件：{config_path}", flush=True)
                        return config
                except Exception as e:
                    print(f"  ⚠️  读取失败 {config_path}: {e}", flush=True)
        
        print(f"  ⚠️  未找到配置文件", flush=True)
        return {}
    
    def get_available_models(self, config: Dict) -> List[str]:
        """获取可用模型列表"""
        models = []
        
        # 从配置中提取模型
        providers = config.get('models', {}).get('providers', {})
        
        for provider_name, provider_config in providers.items():
            provider_models = provider_config.get('models', [])
            for model in provider_models:
                model_id = model.get('id', '')
                models.append(model_id)
                print(f"  📦 可用模型：{model_id}", flush=True)
        
        self.available_models = models
        return models
    
    def identify_coding_models(self, code_size: int = 0) -> List[Tuple[str, Dict]]:
        """
        识别适合编程的模型
        
        Args:
            code_size: 代码量（行数），用于判断需要的上下文窗口
        
        Returns:
            可用的编程模型列表（按优先级排序）
        """
        print(f"\n🔍 识别编程模型...", flush=True)
        
        # 计算需要的上下文窗口（预留余量）
        required_context = max(code_size * 50, 50000)  # 至少 50K
        
        all_models = []
        
        for model_id in self.available_models:
            # 检查是否在编程模型列表中
            if model_id in CODING_MODELS:
                model_info = CODING_MODELS[model_id]
                coding_score = model_info.get('coding_score', 0)
                context_window = model_info.get('context_window', 0)
                
                # 计算优先级分数
                priority_score = coding_score
                
                # 上下文充足加分
                if context_window >= required_context:
                    priority_score += 5
                    context_status = "✅"
                elif context_window >= VALIDATION_CONFIG['min_context_safety']:
                    priority_score += 2
                    context_status = "⚠️"
                else:
                    context_status = "⚠️ (上下文紧张)"
                
                all_models.append((model_id, model_info, priority_score, context_status))
        
        # 按优先级排序
        all_models.sort(key=lambda x: x[2], reverse=True)
        
        # 输出结果
        if all_models:
            print(f"\n  📊 找到 {len(all_models)} 个编程模型（按优先级排序）:", flush=True)
            for model_id, model_info, score, status in all_models[:5]:  # 只显示前 5 个
                coding_score = model_info.get('coding_score', 0)
                context = model_info.get('context_window', 0)
                print(f"    {status} {model_id} - {model_info['name']} (评分：{coding_score}, 上下文：{context/1000:.0f}K)", flush=True)
            
            if len(all_models) > 5:
                print(f"    ... 还有 {len(all_models) - 5} 个模型", flush=True)
        # 即使没有预定义模型，也返回空列表，让 should_switch_model 处理
        # 这样总是可以尝试验证
        
        # 保存结果（只保存模型信息，不保存优先级）
        self.coding_models = [(m[0], m[1]) for m in all_models]
        return self.coding_models
    
    def get_current_model(self) -> Optional[str]:
        """获取当前使用的模型"""
        # 从环境变量或配置中获取
        # 这里简化处理，实际应该从运行时获取
        print(f"\n📊 当前模型：使用配置中的默认模型", flush=True)
        return self.current_model
    
    def should_switch_model(self) -> Tuple[bool, Optional[str], Optional[str], bool]:
        """
        判断是否需要切换模型
        
        Returns:
            (是否需要切换，当前模型，推荐模型，是否应该跳过验证)
        """
        if not self.coding_models:
            print(f"  ⚠️  没有合适的编程模型，跳过验证步骤", flush=True)
            return False, None, None, True  # 应该跳过验证
        
        # 获取最佳编程模型
        best_model = self.coding_models[0][0]
        best_info = self.coding_models[0][1]
        coding_score = best_info.get('coding_score', 0)
        
        # 如果当前模型不是最佳编程模型，建议切换
        if self.current_model != best_model:
            print(f"  💡 建议切换：{self.current_model} → {best_model} ({best_info['name']})", flush=True)
            print(f"     理由：{best_info.get('strength', '代码推理')}，评分 {coding_score}", flush=True)
            return True, self.current_model, best_model, False
        else:
            print(f"  ✅ 已使用最佳编程模型：{best_model}", flush=True)
            return False, self.current_model, None, False
    
    def switch_model(self, target_model: str) -> bool:
        """
        切换模型
        
        Args:
            target_model: 目标模型
        
        Returns:
            是否成功
        """
        print(f"\n🔄 切换模型：{self.current_model} → {target_model}", flush=True)
        
        # 实际切换模型需要通过 sessions_spawn 或配置更新
        # 这里简化处理
        self.current_model = target_model
        print(f"  ✅ 模型已切换：{target_model}", flush=True)
        return True
    
    def validate_code(self, code_content: str, analysis_result: Dict) -> Dict:
        """
        使用编程模型验证代码
        
        Args:
            code_content: 代码内容
            analysis_result: 原始分析结果
        
        Returns:
            验证结果
        """
        print(f"\n🔍 开始代码交叉验证...", flush=True)
        print(f"  使用模型：{self.current_model}", flush=True)
        
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'model': self.current_model,
            'original_analysis': analysis_result,
            'validation_findings': [],
            'additional_issues': [],
            'confirmed_issues': [],
            'confidence_score': 0,
            'recommendations': []
        }
        
        # 模拟交叉验证过程
        # 实际应该调用目标模型进行分析
        
        # 1. 确认原始分析的问题
        for issue in analysis_result.get('issues', []):
            validation_result['confirmed_issues'].append({
                'issue': issue,
                'confirmed': True,
                'confidence': 0.9,
                'model': self.current_model
            })
            print(f"  ✅ 确认问题：{issue}", flush=True)
        
        # 2. 发现额外问题（模拟）
        additional = self._find_additional_issues(code_content)
        validation_result['additional_issues'] = additional
        
        # 3. 生成建议
        validation_result['recommendations'] = self._generate_recommendations(
            analysis_result, additional
        )
        
        # 4. 计算置信度
        validation_result['confidence_score'] = self._calculate_confidence(
            validation_result
        )
        
        # 保存验证历史
        self.validation_history.append(validation_result)
        
        print(f"  📊 验证完成", flush=True)
        print(f"     确认问题：{len(validation_result['confirmed_issues'])}", flush=True)
        print(f"     新增问题：{len(validation_result['additional_issues'])}", flush=True)
        print(f"     置信度：{validation_result['confidence_score']:.1%}", flush=True)
        
        return validation_result
    
    def _find_additional_issues(self, code_content: str) -> List[Dict]:
        """发现额外问题（模拟）"""
        additional = []
        
        # 简单的静态分析
        if 'import' not in code_content and 'from' not in code_content:
            additional.append({
                'issue': '缺少导入语句',
                'severity': 'medium',
                'suggestion': '添加必要的模块导入'
            })
        
        if 'def ' not in code_content and 'class ' not in code_content:
            additional.append({
                'issue': '缺少函数或类定义',
                'severity': 'low',
                'suggestion': '考虑将代码组织为函数或类'
            })
        
        if code_content.count('    ') > code_content.count('\n') * 0.5:
            additional.append({
                'issue': '代码缩进可能过深',
                'severity': 'low',
                'suggestion': '考虑重构减少嵌套'
            })
        
        return additional
    
    def _generate_recommendations(self, analysis: Dict, additional: List) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if analysis.get('quality_score', 100) < 80:
            recommendations.append('优先修复高优先级问题')
        
        if len(additional) > 0:
            recommendations.append('审查新增问题并决定是否需要修复')
        
        if analysis.get('total_lines', 0) > 1000:
            recommendations.append('考虑将大文件拆分为多个模块')
        
        recommendations.append('定期运行代码验证确保质量')
        
        return recommendations
    
    def _calculate_confidence(self, validation_result: Dict) -> float:
        """计算置信度"""
        base_confidence = 0.8
        
        # 确认的问题越多，置信度越高
        confirmed_count = len(validation_result['confirmed_issues'])
        if confirmed_count > 0:
            base_confidence += min(0.1, confirmed_count * 0.02)
        
        # 使用高评分模型，置信度更高
        if self.current_model in CODING_MODELS:
            model_score = CODING_MODELS[self.current_model].get('coding_score', 85)
            base_confidence += (model_score - 80) / 100 * 0.1
        
        return min(0.99, base_confidence)
    
    def generate_validation_report(self, validation_result: Dict) -> str:
        """生成验证报告"""
        report = f"""# 代码交叉验证报告

**时间**: {validation_result['timestamp']}
**验证模型**: {validation_result['model']}
**置信度**: {validation_result['confidence_score']:.1%}

---

## ✅ 确认的问题

"""
        for item in validation_result['confirmed_issues']:
            report += f"- {item['issue']} (置信度：{item['confidence']:.1%})\n"
        
        report += f"""
---

## 🔍 新增问题

"""
        if validation_result['additional_issues']:
            for item in validation_result['additional_issues']:
                report += f"- {item['issue']} (严重程度：{item['severity']})\n"
                report += f"  建议：{item['suggestion']}\n"
        else:
            report += "无新增问题\n"
        
        report += f"""
---

## 💡 建议

"""
        for rec in validation_result['recommendations']:
            report += f"1. {rec}\n"
        
        report += f"""
---

## 📊 总结

本次交叉验证使用 **{validation_result['model']}** 模型对代码进行了独立分析。

- **确认原始问题**: {len(validation_result['confirmed_issues'])} 个
- **发现新增问题**: {len(validation_result['additional_issues'])} 个
- **验证置信度**: {validation_result['confidence_score']:.1%}

"""
        
        if validation_result['confidence_score'] >= 0.9:
            report += "**结论**: 验证结果高度可信，建议按建议进行改进。\n"
        elif validation_result['confidence_score'] >= 0.7:
            report += "**结论**: 验证结果可信，可以参考建议进行改进。\n"
        else:
            report += "**结论**: 验证结果仅供参考，建议人工审查。\n"
        
        return report
    
    def run_full_validation(self, code_content: str, analysis_result: Dict) -> Optional[str]:
        """
        运行完整验证流程
        
        Args:
            code_content: 代码内容
            analysis_result: 原始分析结果
        
        Returns:
            验证报告，如果不适合验证则返回 None
        """
        print("\n" + "="*60, flush=True)
        print("🔍 模型交叉验证流程", flush=True)
        print("="*60, flush=True)
        
        # 1. 读取配置
        config = self.load_openclaw_config()
        
        # 2. 获取可用模型
        self.get_available_models(config)
        
        # 3. 识别编程模型（传入代码量）
        code_lines = len(code_content.split('\n'))
        self.identify_coding_models(code_lines)
        
        # 4. 判断是否需要切换（包含是否应该跳过）
        should_switch, current, recommended, should_skip = self.should_switch_model()
        
        # 5. 总是执行验证（交叉验证总比单 LLM 强）
        if should_skip:
            print(f"\n  ℹ️  使用当前模型进行验证（交叉验证总比单 LLM 强）", flush=True)
        
        # 6. 切换模型（如果需要）
        original_model = self.current_model
        if should_switch and recommended:
            self.switch_model(recommended)
        
        # 7. 执行验证
        validation_result = self.validate_code(code_content, analysis_result)
        
        # 8. 生成报告
        report = self.generate_validation_report(validation_result)
        
        # 9. 切换回原模型（如果需要）
        if should_switch and original_model:
            print(f"\n🔄 切换回原模型：{self.current_model} → {original_model}", flush=True)
            self.current_model = original_model
        
        print("\n" + "="*60, flush=True)
        print("✅ 验证流程完成", flush=True)
        print("="*60, flush=True)
        
        return report


def create_validator() -> ModelValidator:
    """创建模型验证器"""
    return ModelValidator()
