# SKILL.md - 股票预测系统

## 技能描述

基于多因子分析的股票走势预测系统，支持每小时自动预测和参数自优化。

## 功能特点

- 🧠 **多数据源支持**: 腾讯财经、新浪财经、东方财富
- 🚀 **并发处理**: 多线程并发获取数据，5 分钟完成 300+ 股票分析
- 📊 **智能预测**: 基于趋势评分、动量因子、技术指标的综合预测
- 🔄 **自动优化**: 每 2 小时自动验证 10 支股票，自动调整参数
- 🎯 **目标准确率**: 90%+

## 安装依赖

```bash
pip install -r requirements.txt
```

**系统要求:**
- Python 3.8+
- numpy, pandas, requests

## 使用方法

### 运行预测

```bash
python src/stock_predict_hourly.py
```

### 自动验证

```bash
python src/auto_verify.py
```

### 查看预测结果

预测结果保存在 `data/` 目录下：
- `predictions.json` - 预测结果
- `performance.json` - 性能记录

## 配置参数

### 核心参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 趋势评分系数 | 0.8 | 趋势评分权重 |
| 收益率窗口 | 15 日 | 计算收益率的窗口 |
| 高置信阈值 | 1.5% | 高置信度预测阈值 |
| 中置信阈值 | 0.8% | 中置信度预测阈值 |
| 预测方向阈值 | ±0.8% | 预测涨跌阈值 |

### 自定义配置

编辑 `src/stock_predict_hourly.py` 中的配置：

```python
TREND_COEF = 0.8  # 趋势评分系数
RETURN_WINDOW = 15  # 收益率窗口
HIGH_CONF_THRESHOLD = 1.5  # 高置信阈值
MID_CONF_THRESHOLD = 0.8  # 中置信阈值
PREDICT_THRESHOLD = 0.8  # 预测方向阈值
```

## 性能指标

### v12.0 性能

| 指标 | 数值 | 说明 |
|------|------|------|
| 高置信度预测 | 63.4% | +22.7% 提升 |
| 平均预测幅度 | 2.75% | +98% 提升 |
| 方向稳定性 | 80.0% | 达标 |

## 文件说明

```
stock-predictor/
├── src/
│   ├── stock_predict_hourly.py  # 每小时预测脚本
│   └── auto_verify.py           # 自动验证脚本
├── sim_trading/                  # 模拟交易数据
├── data/                         # 预测数据
├── docs/                         # 文档
├── tests/                        # 测试
├── requirements.txt              # Python 依赖
└── README.md                     # 详细文档
```

## 输出格式

预测结果 JSON 格式：

```json
{
  "stock_code": "sz000001",
  "stock_name": "平安银行",
  "predict_change": 2.75,
  "confidence": "high",
  "trend_score": 8.5,
  "momentum": 0.03,
  "timestamp": "2026-03-16T22:00:00Z"
}
```

## 常见问题

**Q: 预测准确率是多少？**
A: v12.0 高置信度预测达到 63.4%，目标准确率 90%+

**Q: 多久更新一次预测？**
A: 每小时自动更新一次

**Q: 支持哪些股票市场？**
A: 支持 A 股（沪深两市）

**Q: 如何查看历史预测？**
A: 查看 `data/predictions.json` 文件

## 许可证

MIT License

## 作者

yun520-1

## GitHub

https://github.com/yun520-1/stock-predictor
