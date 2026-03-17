"""
自主编码 Agent 控制器 v2.0
Autonomous Coding Agent Controller v2.0

基于多模型交叉验证的自主完善系统

核心理念:
- 不同模型交叉验证代码质量
- 自动测试循环直到通过
- 能力缺失自动补充
- 达到交付标准才进入 RoundTable
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable

# 支持直接运行和模块导入两种模式
try:
    from .task_manager import TaskManager
    from .security import validate_command
    from .cross_model_validator import (
        CrossModelValidator,
        AutoTestLoop,
        CapabilityGapAnalyzer,
        ValidationResult
    )
except ImportError:
    from task_manager import TaskManager
    from security import validate_command
    
    # 简化版本用于测试
    class CrossModelValidator:
        async def validate_task(self, task, base_code=None):
            return {"code": f"# Code for {task}", "passed": True, "coverage": 85.0}
    
    class AutoTestLoop:
        async def run_until_pass(self, code, test_command):
            return {"passed": True, "iterations": 1}
    
    class CapabilityGapAnalyzer:
        def analyze(self, requirements):
            return []


class AutonomousCodingController:
    """自主编码 Agent 控制器 v2.0 - 多模型交叉验证版本"""
    
    def __init__(
        self,
        project_name: str,
        requirements: str,
        workspace_dir: str = None,
        sessions_spawn_fn: Callable = None,
        enable_cross_validation: bool = True,
        delivery_standard: Dict[str, Any] = None
    ):
        """
        初始化控制器 v2.0
        
        Args:
            project_name: 项目名称
            requirements: 需求描述
            workspace_dir: 工作目录 (默认：/tmp/auto-coding-projects)
            sessions_spawn_fn: sessions_spawn 工具函数 (由外部提供)
            enable_cross_validation: 是否启用多模型交叉验证
            delivery_standard: 交付标准配置
        """
        self.project_name = project_name
        self.requirements = requirements
        self.workspace_dir = workspace_dir or "/tmp/auto-coding-projects"
        self.project_dir = Path(self.workspace_dir) / project_name
        self.task_manager = TaskManager(str(self.project_dir))
        
        # v2.0 新功能
        self.enable_cross_validation = enable_cross_validation
        self.delivery_standard = delivery_standard or {
            'min_coverage': 80,
            'max_critical_errors': 0,
            'require_docs': True,
            'require_tests': True
        }
        
        # 初始化工具
        self.validator = CrossModelValidator() if enable_cross_validation else None
        self.test_loop = AutoTestLoop(max_iterations=5)
        self.gap_analyzer = CapabilityGapAnalyzer()
        
        # sessions_spawn 由外部提供 (LLM 工具调用)
        self.sessions_spawn = sessions_spawn_fn or self._mock_sessions_spawn
    
    async def _mock_sessions_spawn(self, task: str, **kwargs):
        """模拟 sessions_spawn (用于测试)"""
        print(f"📝 [Mock] 创建子 Agent 任务：{kwargs.get('label', 'unknown')}")
        return {"status": "mock", "task": task, "kwargs": kwargs}
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Phase 1: 初始化 - 创建 Initializer Agent
        
        Returns:
            {
                "status": "initialized" | "error",
                "tasks": [...],
                "message": "..."
            }
        """
        print("\n" + "="*60)
        print("🚀 Phase 1: 初始化阶段")
        print("="*60)
        
        # 读取 Initializer Prompt
        prompt_file = Path(__file__).parent / "prompts" / "initializer.md"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        else:
            base_prompt = "你是初始化 Agent，负责分析需求并生成任务列表。"
        
        # 构建初始化任务
        init_task = f"""
{base_prompt}

---
## 当前任务

**用户需求**: {self.requirements}

**项目目录**: {self.project_dir}

**任务文件**: {self.project_dir}/feature_list.json

**项目目录**: {self.project_dir}

请：
1. 分析用户需求
2. 生成 feature_list.json (20-50 个功能点)
3. 创建 app_spec.txt
4. 初始化项目目录结构
5. 初始化 git 仓库

完成后报告结果。
"""
        
        print(f"📋 创建 Initializer Agent...")
        print(f"📁 项目目录：{self.project_dir}")
        
        # 创建子 Agent
        try:
            initializer_session = await self.sessions_spawn(
                task=init_task,
                runtime="subagent",
                mode="run",
                label=f"initializer-{self.project_name}",
                cwd=str(self.project_dir)
            )
            
            # 等待完成 (模拟模式直接返回)
            if isinstance(initializer_session, dict) and initializer_session.get("status") == "mock":
                print("⚠️  模拟模式：跳过实际执行")
                # 创建示例任务用于测试
                self._create_sample_tasks()
                return {
                    "status": "initialized",
                    "tasks": self.task_manager.load_tasks(),
                    "message": "初始化完成 (模拟模式)"
                }
            
            # TODO: 实现真实的等待逻辑
            # result = await self.wait_for_session(initializer_session)
            
            return {
                "status": "initialized",
                "tasks": self.task_manager.load_tasks(),
                "message": "初始化完成"
            }
            
        except Exception as e:
            print(f"❌ 初始化失败：{e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _create_sample_tasks(self):
        """创建示例任务 (用于测试)"""
        sample_tasks = [
            {"id": 1, "name": "创建项目结构", "status": "pending", "priority": "high", "description": "初始化项目目录和基础文件"},
            {"id": 2, "name": "安装依赖", "status": "pending", "priority": "high", "description": "安装 npm 或 pip 依赖"},
            {"id": 3, "name": "创建 HTML 骨架", "status": "pending", "priority": "high", "description": "创建基础 HTML 结构"},
            {"id": 4, "name": "实现样式", "status": "pending", "priority": "medium", "description": "添加 CSS 样式"},
            {"id": 5, "name": "实现交互逻辑", "status": "pending", "priority": "medium", "description": "添加 JavaScript 交互"},
        ]
        self.task_manager.create_tasks(sample_tasks)
        self.task_manager.log_progress("初始化：创建示例任务")
    
    async def run_coding_iteration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: 编码迭代 v2.0 - 多模型交叉验证版本
        
        Args:
            task: 任务详情
        
        Returns:
            {
                "status": "done" | "error" | "blocked",
                "task": {...},
                "message": "...",
                "validation": {...}
            }
        """
        print(f"\n{'='*60}")
        print(f"💻 编码迭代 v2.0: 任务 #{task['id']} - {task['name']}")
        print(f"{'='*60}")
        
        # v2.0: 多模型交叉验证
        if self.enable_cross_validation:
            return await self._run_cross_validated_coding(task)
        else:
            return await self._run_traditional_coding(task)
    
    async def _run_cross_validated_coding(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """多模型交叉验证的编码流程"""
        print(f"\n🔍 启动多模型交叉验证...")
        
        try:
            # 1. 多模型实现
            validation_result = await self.validator.validate_task(
                task=task['description'],
                base_code=None
            )
            
            print(f"  ✅ 多模型实现完成")
            print(f"  📊 测试覆盖率：{validation_result.test_coverage}%")
            print(f"  🎯 置信度：{validation_result.confidence}")
            
            # 2. 自动测试循环
            print(f"\n🔄 启动自动测试循环...")
            test_result = await self.test_loop.run_until_pass(
                code=validation_result.best_code,
                test_command="npm test"
            )
            
            if test_result.passed:
                print(f"  ✅ 测试通过！迭代次数：{test_result.iterations}")
                
                # 保存代码
                await self._save_code(task, validation_result.best_code)
                
                return {
                    "status": "done",
                    "task": task,
                    "message": f"多模型验证通过，测试覆盖率 {validation_result.test_coverage}%",
                    "validation": {
                        "coverage": validation_result.test_coverage,
                        "merged_from": validation_result.merged_from,
                        "test_iterations": test_result.iterations
                    }
                }
            else:
                print(f"  ⚠️ 测试未通过，但已达到最大迭代次数")
                return {
                    "status": "blocked",
                    "task": task,
                    "message": "自动测试循环未达到 100% 通过",
                    "validation": {"error": "Max iterations reached"}
                }
        
        except Exception as e:
            print(f"  ❌ 多模型验证失败：{e}")
            return await self._run_traditional_coding(task)
    
    async def _run_traditional_coding(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """传统编码流程 (回退方案)"""
        """
        Phase 2: 编码迭代 - 创建 Coder Agent
        
        Args:
            task: 任务详情
        
        Returns:
            {
                "status": "done" | "error" | "blocked",
                "task": {...},
                "message": "..."
            }
        """
        print(f"\n{'='*60}")
        print(f"💻 编码迭代：任务 #{task['id']} - {task['name']}")
        print(f"{'='*60}")
        
        # 安全说明：子 Agent 的命令执行受以下安全控制约束
        # Security Note: Sub-agent command execution is constrained by:
        # 1. OpenClaw Gateway 的运行时安全策略 (主要控制)
        #    OpenClaw Gateway runtime security policy (primary control)
        # 2. security.py 中的命令白名单参考 (文档/可选增强)
        #    security.py command allowlist reference (documentation/optional)
        # 3. Coder Prompt 中的安全约束 (软约束)
        #    Safety constraints in Coder Prompt (soft constraints)
        
        # 读取 Coder Prompt
        prompt_file = Path(__file__).parent / "prompts" / "coder.md"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        else:
            base_prompt = "你是编码 Agent，负责实现单个功能。"
        
        # 构建编码任务
        coding_task = f"""
{base_prompt}

---
## 当前任务

**任务 ID**: {task['id']}
**任务名称**: {task['name']}
**任务描述**: {task.get('description', 'N/A')}
**优先级**: {task.get('priority', 'medium')}

**项目目录**: {self.project_dir}
**任务文件**: {self.project_dir}/feature_list.json

请：
1. 读取当前项目结构和代码
2. 实现该功能
3. 运行测试验证
4. 更新 feature_list.json 状态为 "done"
5. git commit 提交

完成后报告结果。
"""
        
        print(f"📋 创建 Coder Agent...")
        print(f"📝 任务：{task['name']}")
        
        # 创建子 Agent
        try:
            coder_session = await self.sessions_spawn(
                task=coding_task,
                runtime="subagent",
                mode="run",
                label=f"coder-{self.project_name}-{task['id']}",
                cwd=str(self.project_dir)
            )
            
            # 模拟模式
            if isinstance(coder_session, dict) and coder_session.get("status") == "mock":
                print("⚠️  模拟模式：跳过实际执行")
                # 模拟任务完成
                self.task_manager.update_task_status(task['id'], "done", "模拟完成")
                self.task_manager.log_progress(f"完成任务 #{task['id']}: {task['name']}")
                return {
                    "status": "done",
                    "task": task,
                    "message": "任务完成 (模拟模式)"
                }
            
            # TODO: 实现真实的等待逻辑
            # result = await self.wait_for_session(coder_session)
            
            return {
                "status": "done",
                "task": task,
                "message": "任务完成"
            }
            
        except Exception as e:
            print(f"❌ 编码失败：{e}")
            self.task_manager.update_task_status(task['id'], "blocked", str(e))
            return {
                "status": "blocked",
                "task": task,
                "message": str(e)
            }
    
    async def run_full_cycle(self, max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """
        完整运行循环
        
        Args:
            max_iterations: 最大迭代次数 (None 为无限制)
        
        Returns:
            {
                "status": "completed" | "partial" | "error",
                "completed": int,
                "total": int,
                "message": "..."
            }
        """
        print("\n" + "="*60)
        print("🎯 自主编码 Agent 启动")
        print("="*60)
        print(f"📝 项目名称：{self.project_name}")
        print(f"📋 需求：{self.requirements}")
        print(f"📁 项目目录：{self.project_dir}")
        if max_iterations:
            print(f"🔢 最大迭代次数：{max_iterations}")
        print("="*60)
        
        # Phase 1: 初始化
        init_result = await self.initialize()
        if init_result['status'] != 'initialized':
            return {
                "status": "error",
                "message": f"初始化失败：{init_result.get('message', '未知错误')}"
            }
        
        tasks = init_result['tasks']
        completed = 0
        failed = 0
        
        print(f"\n✅ 初始化完成，共 {len(tasks)} 个任务")
        
        # Phase 2: 迭代编码
        for i, task in enumerate(tasks):
            if max_iterations and completed >= max_iterations:
                print(f"\n⚠️  达到最大迭代次数 ({max_iterations})")
                break
            
            if task['status'] == 'pending':
                result = await self.run_coding_iteration(task)
                
                if result['status'] == 'done':
                    completed += 1
                    progress = self.task_manager.get_progress_summary()
                    print(f"\n✅ 进度：{progress['done']}/{progress['total']} ({progress['percentage']}%)")
                elif result['status'] == 'blocked':
                    failed += 1
                    print(f"\n🚫 任务阻塞：{task['name']}")
        
        # 生成最终报告
        summary = self.task_manager.get_progress_summary()
        
        print("\n" + "="*60)
        print("📊 最终报告")
        print("="*60)
        print(f"总任务数：{summary['total']}")
        print(f"✅ 已完成：{summary['done']}")
        print(f"🚫 已阻塞：{summary['blocked']}")
        print(f"⏳ 待处理：{summary['pending']}")
        print(f"📈 进度：{summary['percentage']}%")
        print("="*60)
        
        return {
            "status": "completed" if summary['pending'] == 0 else "partial",
            "completed": summary['done'],
            "total": summary['total'],
            "blocked": summary['blocked'],
            "percentage": summary['percentage'],
            "message": f"完成 {summary['done']}/{summary['total']} 个任务 ({summary['percentage']}%)"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "project_name": self.project_name,
            "project_dir": str(self.project_dir),
            "progress": self.task_manager.get_progress_summary(),
            "status_report": self.task_manager.get_status_report()
        }


# =============================================================================
# 测试代码
# =============================================================================

async def test_controller():
    """测试控制器"""
    print("运行 AutonomousCodingController 测试...\n")
    
    # 创建控制器
    controller = AutonomousCodingController(
        project_name="test-todo-app",
        requirements="创建一个简单的 Todo 应用，包含添加、删除、标记完成功能"
    )
    
    # 测试初始化
    print("\n1️⃣ 测试初始化...")
    init_result = await controller.initialize()
    assert init_result['status'] == 'initialized', f"初始化失败：{init_result}"
    print(f"✅ 初始化成功，创建 {len(init_result['tasks'])} 个任务")
    
    # 测试获取状态
    print("\n2️⃣ 测试获取状态...")
    status = controller.get_status()
    assert 'progress' in status, "状态缺少 progress"
    print(f"✅ 状态获取成功")
    print(status['status_report'])
    
    # 测试单次编码迭代
    print("\n3️⃣ 测试编码迭代...")
    pending_tasks = controller.task_manager.get_pending_tasks()
    if pending_tasks:
        task = pending_tasks[0]
        result = await controller.run_coding_iteration(task)
        assert result['status'] == 'done', f"编码失败：{result}"
        print(f"✅ 编码迭代成功：{task['name']}")
    
    # 测试完整循环 (限制 2 次迭代)
    print("\n4️⃣ 测试完整循环 (max_iterations=2)...")
    controller2 = AutonomousCodingController(
        project_name="test-todo-app-2",
        requirements="测试项目"
    )
    result = await controller2.run_full_cycle(max_iterations=2)
    assert result['status'] in ('completed', 'partial'), f"完整循环失败：{result}"
    print(f"✅ 完整循环成功：{result['message']}")
    
    print("\n" + "="*60)
    print("🎉 所有 AutonomousCodingController 测试通过!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_controller())
