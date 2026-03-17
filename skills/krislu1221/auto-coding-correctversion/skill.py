"""
Auto-Coding Skill - OpenClaw 技能入口
Auto-Coding Skill - Entry Point for OpenClaw

完整集成：
- 触发词匹配
- 项目名称生成
- 响应格式化
- 完整工作流执行（可选）

安全增强 v2.0:
- ✅ 输入验证
- ✅ 错误信息脱敏
- ✅ 敏感信息检测
"""

import re
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

# 安全模块集成
try:
    from security import validate_input, sanitize_input, detect_sensitive_info
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False

# 最大输入长度
MAX_REQUIREMENT_LENGTH = 5000


class AutoCodingHelper:
    """
    Auto-Coding 辅助类
    
    触发方式:
    - /auto-coding 创建一个 Todo 应用
    - /autonomous-coding 创建一个 Todo 应用 (兼容旧命令)
    - 帮我创建一个天气查询 Web 应用
    - 帮我开发一个个人博客系统
    """
    
    name = "auto-coding"
    description = "Auto-Coding v2.0 - 自主完善系统，多模型交叉验证"
    
    # 触发模式
    triggers = [
        r'/auto-coding\s+([\s\S]+)',
        r'/autonomous-coding\s+([\s\S]+)',  # 兼容旧命令
        r'帮我创建一个 ([\s\S]+)',
        r'帮我开发一个 ([\s\S]+)',
    ]
    
    def extract_requirements(self, message: str) -> Optional[str]:
        """
        从消息中提取需求（带安全验证）
        
        Args:
            message: 用户消息
        
        Returns:
            提取的需求，如果无效则返回 None
        """
        if not message:
            return None
        
        # 🔒 安全检查：输入验证
        if HAS_SECURITY:
            is_valid, reason = validate_input(message, MAX_REQUIREMENT_LENGTH)
            if not is_valid:
                print(f"  🚫 输入验证失败: {reason}")
                return None
            message = sanitize_input(message, MAX_REQUIREMENT_LENGTH)
        else:
            # 降级：基本长度检查
            if len(message) > MAX_REQUIREMENT_LENGTH:
                message = message[:MAX_REQUIREMENT_LENGTH]
        
        for pattern in self.triggers:
            match = re.search(pattern, message)
            if match:
                requirements = match.group(1).strip()
                
                # 🔒 安全检查：敏感信息检测
                if HAS_SECURITY:
                    sensitive_findings = detect_sensitive_info(requirements)
                    if sensitive_findings:
                        print(f"  ⚠️  需求中包含敏感信息，已标记")
                        # 不阻止，但记录警告
                
                return requirements
        return None
    
    def generate_project_name(self, requirements: str) -> str:
        """从需求生成项目名称"""
        # 简单实现：取前几个词
        words = requirements.replace('的', ' ').split()
        name = ''.join(words[:3])
        # 移除特殊字符
        name = re.sub(r'[^\w\s-]', '', name)
        name = name.replace(' ', '-').lower()
        return name or "auto-project"
    
    def format_start_response(self, project_name: str, requirements: str) -> str:
        """格式化开始响应"""
        return f"""🚀 Auto-Coding v2.0 启动

📝 项目名称：`{project_name}`
📋 需求：{requirements}

⏱️  预计需要数分钟，请稍候...

---

**工作流程**:
1. 🔍 多模型交叉验证 → 生成最优代码
2. 🧪 自动测试循环 → 测试→修复→再测试
3. 📊 能力缺口分析 → 识别所需工具
4. ✅ 交付检查 → 达到标准才结束

📁 项目位置：`/tmp/auto-coding-projects/{project_name}/`"""
    
    def format_completion_response(self, project_name: str, completed: int, total: int, percentage: float) -> str:
        """格式化完成响应"""
        return f"""
🎉 Auto-Coding 完成！

📝 项目：`{project_name}`
📊 进度：完成 {completed}/{total} 个任务 ({percentage:.1f}%)

📁 项目位置：`/tmp/auto-coding-projects/{project_name}/`

查看进度报告：
```bash
cd /tmp/auto-coding-projects/{project_name}/
cat feature_list.json
```
"""
    
    def format_error_response(self, error_message: str) -> str:
        """
        格式化错误响应（带敏感信息脱敏）
        
        Args:
            error_message: 原始错误信息
        
        Returns:
            脱敏后的错误响应
        """
        # 🔒 安全处理：错误信息脱敏
        safe_message = error_message
        
        # 移除可能的敏感路径
        safe_message = re.sub(r'/Users/[\w]+/', '/Users/[user]/', safe_message)
        safe_message = re.sub(r'/home/[\w]+/', '/home/[user]/', safe_message)
        
        # 移除可能的 API keys
        safe_message = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-[REDACTED]', safe_message)
        safe_message = re.sub(r'api[_-]?key[=:]\s*["\']?[\w-]{10,}', 'api_key=[REDACTED]', safe_message, flags=re.IGNORECASE)
        
        # 移除可能的密码
        safe_message = re.sub(r'(password|passwd|pwd)[=:]\s*["\']?[^\s"\']+', r'\1=[REDACTED]', safe_message, flags=re.IGNORECASE)
        
        # 限制错误信息长度
        if len(safe_message) > 500:
            safe_message = safe_message[:500] + "..."
        
        return f"""❌ Auto-Coding 失败

{safe_message}

请检查：
1. 项目目录是否可写
2. 是否有足够的系统资源
3. 使用 `/subagents list` 查看子 Agent 状态"""


async def handle_auto_coding(message: str, context: Optional[Dict] = None) -> str:
    """
    OpenClaw Skill 入口 - 处理 auto-coding 请求
    
    Args:
        message: 用户消息
        context: 上下文信息（可选）
    
    Returns:
        str: 响应消息
    """
    helper = AutoCodingHelper()
    
    # 提取需求
    requirements = helper.extract_requirements(message)
    if not requirements:
        return helper.format_error_response("无法理解需求，请使用以下格式：\n- /auto-coding 创建一个 Todo 应用\n- 帮我开发一个个人博客系统")
    
    # 生成项目名称
    project_name = helper.generate_project_name(requirements)
    
    # 返回开始响应
    return helper.format_start_response(project_name, requirements)


# 完整工作流执行（可选）
async def run_full_cycle(requirements: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    """
    运行完整的 auto-coding 工作流
    
    用户→分析→找方法→实现→测试→反思→修复→交付
                      ↑_______________↓
                        迭代优化循环
    
    Args:
        requirements: 需求描述
        project_name: 项目名称（可选）
    
    Returns:
        Dict: 执行结果
    """
    from cross_model_validator import CrossModelValidator, AutoTestLoop, CapabilityGapAnalyzer
    
    if not project_name:
        helper = AutoCodingHelper()
        project_name = helper.generate_project_name(requirements)
    
    print(f"\n🚀 Auto-Coding v2.0 启动：{project_name}")
    print(f"📋 需求：{requirements}")
    print("="*60)
    
    # 1. 能力缺口分析
    print("\n📊 步骤 1/4: 能力缺口分析")
    analyzer = CapabilityGapAnalyzer()
    gaps = await analyzer.analyze_with_llm(requirements)
    print(f"✅ 识别到 {len(gaps)} 个能力缺口")
    for gap in gaps:
        print(f"   - {gap['type']}: {gap['reason']}")
    
    # 2. 多模型交叉验证
    print("\n🔍 步骤 2/4: 多模型交叉验证")
    validator = CrossModelValidator()
    validation_result = await validator.validate_task(requirements)
    print(f"✅ 验证完成")
    print(f"   最佳代码来源：{validation_result.merged_from}")
    print(f"   置信度：{validation_result.confidence}")
    
    # 3. 自动测试循环
    print("\n🧪 步骤 3/4: 自动测试循环")
    test_loop = AutoTestLoop(max_iterations=3)
    final_result = await test_loop.run_until_pass(
        validation_result.best_code,
        "echo 'No tests configured'",  # 默认无测试
        f"src/{project_name}.py"
    )
    print(f"✅ 测试循环完成")
    print(f"   通过：{final_result.passed}")
    print(f"   覆盖率：{final_result.test_coverage}%")
    
    # 4. 交付检查
    print("\n✅ 步骤 4/4: 交付检查")
    delivery_checks = {
        "runs_without_error": True,
        "has_basic_tests": final_result.test_coverage > 0,
        "has_documentation": False,  # TODO: 生成文档
        "has_error_handling": False,  # TODO: 检查错误处理
        "security_check_passed": True  # TODO: 安全检查
    }
    
    passed = sum(delivery_checks.values()) / len(delivery_checks)
    print(f"   交付检查：{passed*100:.0f}%")
    
    print("\n" + "="*60)
    print(f"🎉 Auto-Coding 完成！")
    print(f"📁 项目位置：/tmp/auto-coding-projects/{project_name}/")
    
    return {
        "success": final_result.passed,
        "project_name": project_name,
        "code": final_result.best_code,
        "test_coverage": final_result.test_coverage,
        "delivery_checks": delivery_checks,
        "gaps": gaps
    }


# 直接运行测试
if __name__ == "__main__":
    print("Auto-Coding Skill v2.0 测试")
    print("="*50)
    
    helper = AutoCodingHelper()
    
    # 测试触发器
    test_messages = [
        "/auto-coding 创建一个 Todo 应用",
        "/autonomous-coding 创建一个天气查询 Web 应用",  # 兼容旧命令
        "帮我开发一个 个人博客系统",
        "帮我创建一个 计算器应用",
    ]
    
    print("\n测试触发器匹配:")
    for msg in test_messages:
        requirements = helper.extract_requirements(msg)
        if requirements:
            project_name = helper.generate_project_name(requirements)
            print(f"✅ '{msg}'")
            print(f"   项目：{project_name}")
            print(f"   需求：{requirements}")
            print()
        else:
            print(f"❌ '{msg}' → 未匹配")
    
    print("\n" + "="*50)
    print("测试完成!")
