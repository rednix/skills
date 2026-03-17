#!/usr/bin/env python3
"""
任务拆解器

核心理念：
1. 把复杂任务拆解为可执行的子任务
2. 识别依赖关系
3. 估算工时
4. 排序优先级
5. 跟踪执行进度
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class Priority(Enum):
    """优先级"""
    CRITICAL = "critical"  # 关键
    HIGH = "high"          # 高
    MEDIUM = "medium"      # 中
    LOW = "low"            # 低


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    DONE = "done"              # 已完成
    BLOCKED = "blocked"        # 已阻塞


@dataclass
class SubTask:
    """子任务"""
    id: int
    name: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[int] = field(default_factory=list)
    estimated_hours: float = 1.0
    actual_hours: float = 0.0
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class TaskDecomposer:
    """任务拆解器"""
    
    def __init__(self):
        self.tasks: Dict[int, SubTask] = {}
        self.next_id = 1
    
    def decompose(self, task_description: str, code_analysis: Dict = None) -> List[SubTask]:
        """
        将复杂任务拆解为子任务
        
        Args:
            task_description: 任务描述
            code_analysis: 代码分析结果（可选）
        
        Returns:
            子任务列表
        """
        print(f"\n📋 拆解任务：{task_description[:50]}...", flush=True)
        
        # 清空现有任务
        self.tasks.clear()
        self.next_id = 1
        
        # 基于任务描述和代码分析生成子任务
        if code_analysis:
            self._decompose_from_analysis(task_description, code_analysis)
        else:
            self._decompose_from_description(task_description)
        
        # 识别依赖关系
        self._identify_dependencies()
        
        # 排序优先级
        self._prioritize()
        
        print(f"  ✅ 拆解为 {len(self.tasks)} 个子任务", flush=True)
        return list(self.tasks.values())
    
    def _decompose_from_analysis(self, task_description: str, analysis: Dict):
        """基于代码分析拆解任务"""
        issues = analysis.get('issues', [])
        suggestions = analysis.get('suggestions', [])
        
        # 为每个问题创建修复任务
        for issue in issues:
            self._add_task(
                name=f"修复：{issue}",
                description=f"解决代码分析问题：{issue}",
                priority=Priority.HIGH,
                estimated_hours=1.0
            )
        
        # 为每个建议创建改进任务
        for sug in suggestions:
            self._add_task(
                name=f"改进：{sug}",
                description=f"实施改进建议：{sug}",
                priority=Priority.MEDIUM,
                estimated_hours=2.0
            )
        
        # 添加测试任务
        if issues or suggestions:
            self._add_task(
                name="测试验证",
                description="运行测试验证所有修复和改进",
                priority=Priority.HIGH,
                estimated_hours=1.0,
                dependencies=list(range(1, len(self.tasks) + 1))
            )
    
    def _decompose_from_description(self, task_description: str):
        """基于任务描述拆解任务（简单版本）"""
        # 通用任务拆解
        self._add_task(
            name="分析需求",
            description="理解任务目标和约束",
            priority=Priority.HIGH,
            estimated_hours=0.5
        )
        
        self._add_task(
            name="设计方案",
            description="设计实现方案",
            priority=Priority.HIGH,
            estimated_hours=1.0,
            dependencies=[1]
        )
        
        self._add_task(
            name="实施",
            description="编写代码实现功能",
            priority=Priority.MEDIUM,
            estimated_hours=2.0,
            dependencies=[2]
        )
        
        self._add_task(
            name="测试",
            description="测试验证功能",
            priority=Priority.HIGH,
            estimated_hours=1.0,
            dependencies=[3]
        )
    
    def _add_task(self, name: str, description: str, priority: Priority = Priority.MEDIUM,
                  estimated_hours: float = 1.0, dependencies: List[int] = None):
        """添加子任务"""
        task = SubTask(
            id=self.next_id,
            name=name,
            description=description,
            priority=priority,
            estimated_hours=estimated_hours,
            dependencies=dependencies or []
        )
        self.tasks[self.next_id] = task
        self.next_id += 1
    
    def _identify_dependencies(self):
        """识别依赖关系（简单版本）"""
        # 当前版本依赖关系在创建时已经指定
        # 未来可以添加智能依赖分析
        pass
    
    def _prioritize(self):
        """排序优先级"""
        # 按优先级排序任务
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: (priority_order[t.priority], t.id)
        )
        
        # 重新编号
        self.tasks = {}
        for i, task in enumerate(sorted_tasks, 1):
            task.id = i
            self.tasks[i] = task
        
        self.next_id = len(self.tasks) + 1
    
    def mark_done(self, task_id: int, actual_hours: float = None):
        """标记任务完成"""
        if task_id not in self.tasks:
            print(f"  ⚠️  任务 {task_id} 不存在", flush=True)
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now().isoformat()
        if actual_hours:
            task.actual_hours = actual_hours
        
        print(f"  ✅ 任务 {task_id} 完成：{task.name}", flush=True)
    
    def get_progress(self) -> Dict:
        """获取进度"""
        total = len(self.tasks)
        done = sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE)
        in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        
        total_estimated = sum(t.estimated_hours for t in self.tasks.values())
        total_actual = sum(t.actual_hours for t in self.tasks.values())
        
        return {
            'total': total,
            'done': done,
            'in_progress': in_progress,
            'pending': pending,
            'progress_percent': (done / total * 100) if total > 0 else 0,
            'estimated_hours': total_estimated,
            'actual_hours': total_actual
        }
    
    def print_status(self):
        """打印任务状态"""
        print("\n" + "="*60, flush=True)
        print("📊 任务状态", flush=True)
        print("="*60, flush=True)
        
        progress = self.get_progress()
        print(f"总任务：{progress['total']}")
        print(f"✅ 完成：{progress['done']}")
        print(f"🔄 进行中：{progress['in_progress']}")
        print(f"⏳ 待处理：{progress['pending']}")
        print(f"📈 进度：{progress['progress_percent']:.1f}%")
        print(f"⏱️  预估工时：{progress['estimated_hours']:.1f}小时")
        print(f"⏱️  实际工时：{progress['actual_hours']:.1f}小时")
        print("="*60, flush=True)
        
        print("\n📋 任务列表:", flush=True)
        for task in self.tasks.values():
            status_icon = {
                TaskStatus.DONE: "✅",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.PENDING: "⏳",
                TaskStatus.BLOCKED: "🚫"
            }[task.status]
            
            priority_icon = {
                Priority.CRITICAL: "🔴",
                Priority.HIGH: "🟠",
                Priority.MEDIUM: "🟡",
                Priority.LOW: "🟢"
            }[task.priority]
            
            deps = f" (依赖：{task.dependencies})" if task.dependencies else ""
            print(f"{status_icon} {priority_icon} #{task.id} {task.name} - {task.estimated_hours}h{deps}", flush=True)


def create_decomposer() -> TaskDecomposer:
    """创建任务拆解器"""
    return TaskDecomposer()
