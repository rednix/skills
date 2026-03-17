#!/usr/bin/env python3
"""
Auto-Coding v2.0 核心组件测试

测试范围:
- CrossModelValidator: 多模型交叉验证
- AutoTestLoop: 自动测试循环
- CapabilityGapAnalyzer: 能力缺口分析
- Skill 入口：handle_auto_coding
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def test_cross_model_validator():
    """测试多模型验证"""
    print("\n" + "="*60)
    print("测试 1: CrossModelValidator")
    print("="*60)
    
    from cross_model_validator import CrossModelValidator, ModelRole
    
    validator = CrossModelValidator()
    
    # 测试任务
    task = "实现一个简单的计算器类，支持加减乘除"
    
    print(f"\n📝 任务：{task}")
    print("\n开始验证...")
    
    try:
        result = await validator.validate_task(task)
        
        print(f"\n✅ 验证完成")
        print(f"   最佳代码来源：{result.merged_from}")
        print(f"   测试覆盖率：{result.test_coverage}%")
        print(f"   置信度：{result.confidence}")
        print(f"   改进项：{len(result.improvements)}")
        print(f"   剩余问题：{len(result.remaining_issues)}")
        
        # 断言
        assert result.passed, "验证应该通过"
        assert len(result.merged_from) >= 1, "应该至少有一个模型参与"
        assert result.confidence > 0, "置信度应该大于 0"
        
        print("\n✅ CrossModelValidator 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ CrossModelValidator 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


async def test_auto_test_loop():
    """测试自动测试循环"""
    print("\n" + "="*60)
    print("测试 2: AutoTestLoop")
    print("="*60)
    
    from cross_model_validator import AutoTestLoop
    
    test_loop = AutoTestLoop(max_iterations=2)
    
    # 测试代码
    code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
    
    # 测试命令（无实际测试）
    test_command = "echo 'No tests configured'"
    
    print(f"\n📝 测试代码：{len(code)} 行")
    print(f"🧪 测试命令：{test_command}")
    print("\n开始测试循环...")
    
    try:
        result = await test_loop.run_until_pass(
            code,
            test_command,
            "test_calculator.py"
        )
        
        print(f"\n✅ 测试循环完成")
        print(f"   通过：{result.passed}")
        print(f"   测试覆盖率：{result.test_coverage}%")
        print(f"   剩余问题：{len(result.remaining_issues)}")
        
        # 断言
        assert result.test_coverage >= 0, "覆盖率应该非负"
        
        print("\n✅ AutoTestLoop 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ AutoTestLoop 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


async def test_capability_gap_analyzer():
    """测试能力缺口分析"""
    print("\n" + "="*60)
    print("测试 3: CapabilityGapAnalyzer")
    print("="*60)
    
    from cross_model_validator import CapabilityGapAnalyzer
    
    analyzer = CapabilityGapAnalyzer()
    
    # 测试需求
    requirements = "创建一个 Web 应用，需要测试、代码质量检查、数据库支持"
    
    print(f"\n📝 需求：{requirements}")
    print("\n开始分析...")
    
    try:
        # 测试简单版本
        gaps = analyzer.analyze(requirements)
        
        print(f"\n✅ 分析完成（关键词匹配）")
        print(f"   识别到 {len(gaps)} 个能力缺口")
        for gap in gaps:
            print(f"   - {gap['type']}: {gap['reason']}")
        
        # 断言
        assert len(gaps) >= 1, "应该至少识别到一个能力缺口"
        
        # 测试 LLM 版本（如果可用）
        print("\n尝试 LLM 分析...")
        gaps_llm = await analyzer.analyze_with_llm(requirements)
        print(f"✅ LLM 分析完成：{len(gaps_llm)} 个能力缺口")
        
        print("\n✅ CapabilityGapAnalyzer 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ CapabilityGapAnalyzer 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


async def test_skill_entry():
    """测试 Skill 入口"""
    print("\n" + "="*60)
    print("测试 4: Skill 入口")
    print("="*60)
    
    from skill import AutoCodingHelper, handle_auto_coding
    
    helper = AutoCodingHelper()
    
    # 测试触发器
    test_messages = [
        "/auto-coding 创建一个 Todo 应用",
        "/autonomous-coding 创建一个天气查询 Web 应用",
        "帮我开发一个 个人博客系统",
        "帮我创建一个 计算器应用",
    ]
    
    print("\n测试触发器匹配:")
    matched = 0
    for msg in test_messages:
        requirements = helper.extract_requirements(msg)
        if requirements:
            project_name = helper.generate_project_name(requirements)
            print(f"✅ '{msg}'")
            print(f"   项目：{project_name}")
            print(f"   需求：{requirements}")
            matched += 1
        else:
            print(f"❌ '{msg}' → 未匹配")
    
    # 断言
    assert matched >= 3, f"应该至少匹配 3 个触发器，实际匹配 {matched} 个"
    
    # 测试 handle_auto_coding
    print("\n测试 handle_auto_coding:")
    response = await handle_auto_coding("/auto-coding 创建一个计算器")
    print(f"✅ 响应：{len(response)} 字符")
    assert "Auto-Coding" in response, "响应应该包含 'Auto-Coding'"
    assert "计算器" in response, "响应应该包含 '计算器'"
    
    print("\n✅ Skill 入口测试通过!")
    return True


async def test_worker_run_method():
    """测试 Worker 的 run() 方法"""
    print("\n" + "="*60)
    print("测试 5: AutoCodingWorker.run() 主循环")
    print("="*60)
    
    from auto_coding_worker import AutoCodingWorker
    
    worker = AutoCodingWorker("test-worker")
    
    # 测试任务
    task = "创建一个简单的计算器模块"
    
    print(f"\n📝 任务：{task}")
    print("\n开始运行完整工作流...")
    
    try:
        result = await worker.run(task)
        
        print(f"\n✅ 工作流完成")
        print(f"   完成：{result['completed']}")
        print(f"   耗时：{result.get('elapsed_seconds', 0):.1f}秒")
        print(f"   子任务：{result.get('subtasks', 0)}个")
        
        if result.get('capability_gaps'):
            print(f"   能力缺口：{len(result['capability_gaps'])}个")
        
        if result.get('validation'):
            print(f"   验证置信度：{result['validation'].get('confidence', 0)}")
        
        if result.get('test_result'):
            print(f"   测试覆盖率：{result['test_result'].get('coverage', 0)}%")
        
        # 断言
        assert result['completed'] == True, "工作流应该完成"
        assert 'summary' in result, "应该生成总结报告"
        
        print("\n✅ Worker.run() 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ Worker.run() 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Auto-Coding v3.1 核心组件测试")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("CrossModelValidator", await test_cross_model_validator()))
    results.append(("AutoTestLoop", await test_auto_test_loop()))
    results.append(("CapabilityGapAnalyzer", await test_capability_gap_analyzer()))
    results.append(("Skill 入口", await test_skill_entry()))
    results.append(("Worker.run() 主循环", await test_worker_run_method()))
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
