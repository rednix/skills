# 股票预测系统 v12.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Accuracy](https://img.shields.io/badge/target-90%25-green.svg)]()

基于多因子分析的股票走势预测系统，支持每小时自动预测和参数自优化。

## 🌟 特性

- **多数据源支持**: 腾讯财经、新浪财经、东方财富
- **并发处理**: 多线程并发获取数据，5 分钟完成 300+ 股票分析
- **智能预测**: 基于趋势评分、动量因子、技术指标的综合预测
- **自动优化**: 每 2 小时自动验证 10 支股票，自动调整参数
- **目标准确率**: 90%+

## 📊 v12.0 更新

### 核心改进
- ✅ 趋势评分系数提高：0.5 → 0.8
- ✅ 收益率窗口延长：10 日 → 15 日（减少噪音）
- ✅ 新增动量因子：5 日动量捕捉中期趋势
- ✅ 置信度阈值优化：高置信>1.5%，中置信>0.8%
- ✅ 预测方向阈值：±1% → ±0.8%（更敏感）

### 性能提升
| 指标 | v11.0 | v12.0 | 提升 |
|------|-------|-------|------|
| 高置信度预测 | 40.7% | 63.4% | +22.7% |
| 平均预测幅度 | 1.39% | 2.75% | +98% |
| 方向稳定性 | - | 80.0% | 达标 |

## 🚀 快速开始

### 环境要求

```bash
Python 3.8+
pip install -r requirements.txt
```

### 安装依赖

```bash
pip install numpy pandas requests
```

### 运行预测

```bash
# 手动运行一次预测
python src/stock_predict_hourly.py

# 设置定时任务（每 2 小时）
crontab -e
# 添加：0 */2 * * * cd /path/to/stock-predictor && python src/stock_predict_hourly.py
```

### 自动验证与优化

```bash
# 运行自动验证（每 2 小时验证 10 支股票）
python src/auto_verify.py
```

## 📁 项目结构

```
stock-predictor/
├── src/                          # 源代码
│   ├── stock_predict_hourly.py   # 小时预测主程序 (v12.0)
│   ├── stock_predict_ml.py       # 机器学习预测
│   └── run_sim.py                # 模拟交易
├── data/                         # 数据文件
│   └── stocks.json               # 监控股票列表 (346 只)
├── predictions/                  # 预测结果输出
│   ├── YYYY-MM-DD.json           # 每日预测
│   └── YYYY-MM-DD_HH-00.json     # 每小时预测
├── temp/                         # 临时文件
│   ├── auto_verify.py            # 自动验证脚本
│   └── optimization_params.json  # 优化参数
├── docs/                         # 文档
│   └── report.md                 # 验证报告
├── requirements.txt              # 依赖
├── README.md                     # 本文件
└── LICENSE                       # MIT 许可证
```

## 📈 预测原理

### 核心公式

```python
# 趋势评分
trend_score = 0
if close > ma5: trend_score += 1
if close > ma20: trend_score += 1
if close > ma60: trend_score += 1
if rsi > 50: trend_score += 0.5
if macd > macd_signal: trend_score += 0.5

# 动量因子 (v12.0 新增)
momentum_5d = (close / close_5d_ago - 1) * 100
momentum_factor = momentum_5d * 0.3

# 预测涨跌幅
predicted_change = mean_return * 1.5 + (trend_score * 0.8) + momentum_factor
```

### 技术指标

| 指标 | 说明 | 参数 |
|------|------|------|
| MA5/20/60 | 移动平均线 | 5/20/60 日 |
| RSI | 相对强弱指标 | 14 日 |
| MACD | 指数平滑异同移动平均线 | 12/26/9 |
| Momentum | 动量因子 | 5 日 |

## 🎯 配置说明

### stocks.json 格式

```json
[
  {"code": "sh600519", "name": "贵州茅台", "ts_code": "600519"},
  {"code": "sz300750", "name": "宁德时代", "ts_code": "300750"}
]
```

### 预测输出格式

```json
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "current_price": 1460.18,
  "predicted_change": 1.65,
  "predicted_price": 1484.23,
  "direction": "上涨",
  "signal": "🟢",
  "confidence": "中",
  "ma5": 1413.54,
  "ma20": 1445.95,
  "rsi": 48.41,
  "macd": -5.7453,
  "trend_score": 3,
  "momentum_5d": 2.75
}
```

## 📊 验证结果

### 2026-03-16 验证数据

| 时间 | 样本数 | 准确率 | 版本 |
|------|--------|--------|------|
| 20:30 | 100 | 80.0% | v12.0 |
| 20:33 | 10 | 80.0% | v12.0 |

### 长期目标

- [ ] 平均准确率稳定在 85%+ (1 周)
- [ ] 平均准确率达到 90% (1 月)
- [ ] 高置信度预测占比>50%
- [ ] 大幅误差 (>5%) <10%

## ⚠️ 风险提示

1. **不构成投资建议**: 本系统仅供学习研究，不构成任何投资建议
2. **市场风险**: 股市有风险，投资需谨慎
3. **数据延迟**: 公开数据源可能存在 15 分钟延迟
4. **模型局限**: 预测模型无法应对突发事件和政策变化

## 📝 更新日志

### v12.0 (2026-03-16)
- 🎯 提高趋势权重 (0.5→0.8)
- 📊 延长收益率窗口 (10→15 日)
- ✨ 新增动量因子
- 🔧 优化置信度阈值
- 📈 高置信度预测提升 22.7%

### v11.0 (2026-03-15)
- 扩展股票列表至 346 只
- 多数据源支持
- 并发请求优化
- 自动重试机制

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

- GitHub Issues: 提交问题和建议
- Email: your-email@example.com

---

**免责声明**: 本软件仅供学习和研究使用，不构成任何投资建议。使用本软件进行的任何投资行为，风险自负。
