# Auto-Coding Skill

**自主完善的编程系统 - 多模型交叉验证、自动测试、能力补充**

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://clawhub.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 简介

Auto-Coding 是一个基于 OpenClaw 平台的自主编程系统，通过多模型交叉验证和自动测试循环，实现高质量的代码生成和优化。

### 核心特性

| 特性 | 说明 |
|------|------|
| **多模型交叉验证** | 不同模型扮演不同角色，取长补短 |
| **自动测试循环** | 测试→失败→修复→再测试 |
| **能力缺口分析** | 自动识别所需工具和能力 |
| **任务智能拆解** | 复杂任务拆分为可执行子任务 |
| **安全防护** | 路径遍历、命令注入、敏感信息检测 |

---

## 🚀 快速开始

### 安装

```bash
# 通过 ClawHub 安装
clawhub install auto-coding
```

### 使用

```
/auto-coding 创建一个 Todo 应用
```

或编程方式：

```python
from auto_coding_worker import AutoCodingWorker

worker = AutoCodingWorker()
result = await worker.run("创建一个计算器应用")
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
```

### 模型角色

| 角色 | 职责 | 建议特点 |
|------|------|---------|
| IMPLEMENTER | 代码实现 | 代码生成能力强 |
| REVIEWER | 代码审查 | 分析能力强 |
| TESTER | 测试设计 | 长文本理解好 |
| FIXER | 问题修复 | 调试能力强 |

---

## 🛡️ 安全特性

- 🔒 路径遍历防护
- 🛡️ 命令注入防护
- ✅ 输入验证
- 🔐 敏感信息检测
- 📝 错误信息脱敏

---

## 📊 测试

```bash
# 运行核心组件测试
python tests/test_core_components.py

# 运行安全测试
python security.py
```

---

## 📝 更新日志

### v3.2.0
- ✅ 安全加固优化
- ✅ 配置弹性化
- ✅ 敏感信息检测

---

## 📄 许可证

MIT License

---

**Made with ❤️ by Claw Soft Team**