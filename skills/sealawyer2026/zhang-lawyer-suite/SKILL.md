---
name: zhang-lawyer-suite
description: 张律师法律AI中台 - 中国首个开源法律AI技能库，涵盖刑事辩护、民商事诉讼、合同审查全流程
author: 张律师
license: MIT
repository: https://github.com/zhang-lawyer/zhang-lawyer-suite
homepage: https://zhang-lawyer.ai
version: 1.0.0
category: legal
tags: [law, legal, lawyer, criminal, civil, contract, litigation, china]
language: zh
official: true
featured: true
---

# 张律师法律AI中台 ⚖️🤖

> 中国首个开源法律AI技能库 | 专业律师团队打造 | 全领域法律实践支持

## 🎯 核心价值

为律师、法务、法律从业者提供**开箱即用的AI法律助手**，覆盖执业全流程。

## 📦 包含内容

### 1. 刑事辩护全流程 (`zhang-criminal-defense`)
- 6大阶段：接案洽谈 → 侦查阶段 → 审查起诉 → 审判阶段 → 上诉申诉 → 执行阶段
- 21个专业提示词模板
- 会见笔录、阅卷摘要、质证意见、辩护词生成

### 2. 民商事诉讼全流程 (`zhang-civil-litigation`)
- 7大阶段：案件评估 → 立案准备 → 证据整理 → 庭前准备 → 庭审应对 → 判决分析 → 执行阶段
- 15个专业提示词模板
- 起诉状、答辩状、代理词、证据清单生成

### 3. 合同审查清单 (`zhang-contract-review`)
- 5类合同：买卖合同、劳动合同、借款合同、租赁合同、股权转让
- 3大特殊条款：保密条款、竞业限制、争议解决
- 风险识别 + 修改建议 + 条款起草

### 4. 法律文书润色 (`zhang-legal-polish`)
- 12种润色维度：观点深度、语言简洁、逻辑梳理、风格统一等
- 专业法律语言优化
- 符合司法实践的表达规范

## 🚀 快速开始

```bash
# 安装全套技能
clawhub install zhang-lawyer-suite

# 或单独安装专项
clawhub install zhang-criminal-defense
clawhub install zhang-civil-litigation
clawhub install zhang-contract-review
clawhub install zhang-legal-polish
```

## 📖 使用示例

### 刑事辩护场景
```
@zhang-criminal-defense 会见笔录整理
- 案件：涉嫌诈骗罪
- 会见时间：2026年3月14日
- 会见地点：XX看守所
- 笔录内容：[粘贴笔录]
```

### 合同审查场景
```
@zhang-contract-review 劳动合同审查
- 合同文本：[粘贴合同]
- 审查重点：竞业限制、保密条款、违约责任
```

## 🏆 为什么选择张律师法律AI中台？

| 特性 | 张律师中台 | 通用AI |
|------|-----------|--------|
| **专业深度** | ✅ 基于真实案件和司法实践 | ❌ 通用法律知识 |
| **流程完整** | ✅ 覆盖执业全流程 | ❌ 碎片化回答 |
| **中文优化** | ✅ 针对中国法律体系 | ❌ 英美法为主 |
| **持续更新** | ✅ 跟随立法和判例更新 | ❌ 知识滞后 |
| **社区支持** | ✅ 律师社群互助 | ❌ 无专业社区 |

## 👨‍⚖️ 关于作者

**张律师** - 执业律师，全领域法律实践者
- 专注：刑事辩护、民商事诉讼、企业合规
- 理念：用AI赋能法律实践，让专业服务更高效

## 🤝 参与贡献

欢迎律师同行、法务、开发者共同参与建设！

- 提交Issue：反馈问题或需求
- 提交PR：贡献新的提示词模板
- 加入社群：飞书群「张律师法律AI交流群」

## 📜 许可证

MIT License - 自由使用，欢迎Fork，请保留署名

## 🔗 相关链接

- 官方文档：https://docs.zhang-lawyer.ai
- GitHub：https://github.com/zhang-lawyer/zhang-lawyer-suite
- ClawHub：https://clawhub.com/skills/zhang-lawyer-suite
- 微信公众号：张律师法律AI

---

**⚠️ 免责声明**：本技能库仅供法律专业人士参考使用，不构成正式法律意见。具体案件请咨询执业律师。

**🌟 Star 我们**：如果对你有帮助，请在GitHub给个Star！
