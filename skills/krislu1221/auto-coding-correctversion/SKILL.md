---
name: auto-coding
description: 自主完善的编程系统 - 多模型交叉验证、自动测试、能力补充，达到交付标准后进入 RoundTable 讨论
user-invocable: true
version: 3.2.0
author: Claw Soft Team
license: MIT
---

# Auto-Coding Skill v3.2

## 🎯 简介

Auto-Coding 是一个基于 OpenClaw 平台的自主编程系统，通过多模型交叉验证和自动测试循环，实现高质量的代码生成和优化。

### 核心特性

- ✅ **多模型交叉验证** - 不同模型扮演不同角色，取长补短
- ✅ **自动测试循环** - 测试→失败→修复→再测试
- ✅ **能力缺口分析** - 自动识别所需工具和能力
- ✅ **任务智能拆解** - 复杂任务拆分为可执行子任务
- ✅ **安全防护** - 路径遍历、命令注入、敏感信息检测

---

## 🚀 快速开始

### 触发方式

```
/auto-coding 创建一个 Todo 应用
帮我开发一个 个人博客系统
```

### 编程方式

```python
from auto_coding_worker import AutoCodingWorker

worker = AutoCodingWorker()
result = await worker.run("创建一个计算器应用")
print(result['summary'])
```

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────┐
│              Auto-Coding v3.2                       │
├─────────────────────────────────────────────────────┤
│  核心模块：                                         │
│  - auto_coding_worker.py (自主工作者)              │
│  - cross_model_validator.py (多模型验证)           │
│  - task_decomposer.py (任务拆解)                   │
│  - security.py (安全防护)                          │
├─────────────────────────────────────────────────────┤
│  工作流程：                                         │
│  用户→分析→实现→测试→反思→修复→交付             │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 配置

### 环境变量

```bash
# 允许的基础路径（逗号分隔）
export AUTO_CODING_ALLOWED_PATHS="~/.my-workspace,/tmp/projects"

# 最大输入长度
export AUTO_CODING_MAX_INPUT_LENGTH=10000

# 项目目录
export AUTO_CODING_PROJECTS_DIR="/path/to/projects"

# 最大迭代次数
export MAX_ITERATIONS=50

# 模型配置（根据你的模型提供商设置）
export AUTO_CODING_MODEL_IMPLEMENTER="your-implementer-model"
export AUTO_CODING_MODEL_REVIEWER="your-reviewer-model"
export AUTO_CODING_MODEL_TESTER="your-tester-model"
export AUTO_CODING_MODEL_FIXER="your-fixer-model"

# 或指定模型配置文件路径
export AUTO_CODING_MODELS_CONFIG="/path/to/models_config.json"
```

### 模型角色说明

| 角色 | 职责 | 建议特点 |
|------|------|---------|
| IMPLEMENTER | 代码实现 | 代码生成能力强 |
| REVIEWER | 代码审查 | 分析能力强，能发现问题 |
| TESTER | 测试设计 | 长文本理解好，细节关注 |
| FIXER | 问题修复 | 调试能力强，错误理解好 |

---

## 🛡️ 安全特性

- 🔒 **路径遍历防护** - 验证所有文件路径
- 🛡️ **命令注入防护** - 检测危险模式
- ✅ **输入验证** - 长度和内容双重验证
- 🔐 **敏感信息检测** - 自动检测 API Key、密码等

---

## 📁 文件结构

```
auto-coding/
├── SKILL.md                    # Skill 定义
├── README.md                   # 使用说明
├── clawhub.json               # ClawHub 配置
├── LICENSE                    # MIT 许可证
├── requirements.txt           # 依赖
├── __init__.py               # 包入口
├── skill.py                  # Skill 入口
├── auto_coding_worker.py     # 核心工作者
├── cross_model_validator.py  # 多模型验证
├── task_decomposer.py        # 任务拆解
├── security.py               # 安全模块
├── task_manager.py           # 任务管理
├── agent_controller.py       # Agent 控制
├── self_reflection.py        # 自我反思
├── prompts/                  # 提示词
│   ├── initializer.md
│   └── coder.md
└── tests/                    # 测试
    └── test_core_components.py
```

---

## ⚠️ 注意事项

### 适用场景
- ✅ 需要高质量代码的项目
- ✅ 需要多模型交叉验证
- ✅ 从零创建或优化现有代码

### 不适用场景
- ❌ 快速原型验证
- ❌ 一次性脚本
- ❌ 时间紧迫的项目

---

## 📝 更新日志

### v3.2.0
- ✅ 安全加固优化
- ✅ 配置弹性化
- ✅ 敏感信息检测
- ✅ 错误信息脱敏

---

## 📄 许可证

MIT License