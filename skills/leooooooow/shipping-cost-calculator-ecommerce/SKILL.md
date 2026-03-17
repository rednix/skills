---
name: shipping-cost-calculator-ecommerce
description: Estimate ecommerce shipping cost per order across weight, zones, carrier rules, and free-shipping policies. Use when teams need to understand how shipping affects margin and offer design.
---

# Shipping Cost Calculator Ecommerce

运费不是一个固定值，而是一整套会吞利润的变量。

## 解决的问题

很多团队在设“包邮”“满额包邮”或选物流商时，只看了表面报价，没算清：
- 不同地区 / 重量段的差异；
- 包材和履约费；
- 满额包邮对单均利润的影响；
- 退货或补寄带来的额外成本。

这个 skill 的目标是：
**把 shipping 成本从模糊印象，变成可用于定价和包邮策略的决策输入。**

## 何时使用

- 调整包邮门槛；
- 更换物流商或仓配方案；
- 想知道某些地区是否持续亏损；
- 做 bundle / 提升客单价策略前。

## 输入要求

- 发货区域或国家 / 州
- 包裹重量、尺寸、材积重规则
- 物流商报价 / 仓配费用
- 包材与处理费
- 包邮政策 / 促销规则
- 可选：退货、补寄、丢件损耗假设

## 工作流

1. 计算单笔基础 shipping 成本。
2. 区分区域、重量段和政策差异。
3. 评估包邮 / 满额包邮的利润影响。
4. 给出阈值和策略建议。

## 输出格式

1. Shipping 成本假设表
2. 单笔 / 分区成本结果
3. 包邮政策影响
4. 建议动作

## 质量标准

- 区分 carrier 报价与真实总履约成本。
- 明确哪些地区或重量段风险更高。
- 输出能直接支持定价或门槛设置。
- 不用虚假精度掩盖估算。

## 资源

参考 `references/output-template.md`。
