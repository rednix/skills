#!/usr/bin/env python3
import json
import os
from datetime import datetime

with open('/home/admin/openclaw/workspace/sim_trading/portfolio.json', 'r') as f:
    portfolio = json.load(f)

latest_pred = None
today = datetime.now().strftime('%Y-%m-%d')
for h in range(12, -1, -1):
    f_path = f'/home/admin/openclaw/workspace/predictions/{today}_{h:02d}-00.json'
    if os.path.exists(f_path):
        with open(f_path, 'r') as fp:
            latest_pred = json.load(fp)
        print(f'📊 数据源：{f_path}')
        break

if not latest_pred:
    print('❌ 未找到预测数据')
    exit()

print()
print('=' * 70)
print('📈 持仓实时更新')
print('=' * 70)
print()

total_market_value = 0
positions = portfolio.get('positions', {})

header = f"{'代码':<10} {'名称':<15} {'股数':>10} {'成本':>10} {'现价':>10} {'浮盈':>14}"
print(header)
print('-' * 70)

for code, pos in positions.items():
    current_price = pos['avg_price']
    for p in latest_pred.get('predictions', []):
        if p.get('stock_code') == code:
            current_price = p.get('current_price', pos['avg_price'])
            break
    
    market_value = pos['shares'] * current_price
    total_market_value += market_value
    cost = pos['shares'] * pos['avg_price']
    profit = market_value - cost
    profit_pct = profit / cost * 100 if cost > 0 else 0
    
    sign = '+' if profit >= 0 else ''
    print(f"{code:<10} {pos.get('name', ''):<15} {pos['shares']:>10} ¥{pos['avg_price']:>8.2f} ¥{current_price:>8.2f} {sign}{profit:>10.2f} ({sign}{profit_pct:.1f}%)")

print('-' * 70)
print(f"{'持仓合计':<27} {'':>10} ¥{total_market_value:>10,.2f}")
print()

cash = portfolio.get('cash', 0)
total_assets = cash + total_market_value
total_return = (total_assets - portfolio.get('initial_cash', 100000)) / portfolio.get('initial_cash', 100000) * 100

print('=' * 70)
print('💰 账户总览')
print('=' * 70)
print(f'💵 可用现金：¥{cash:,.2f}')
print(f'📈 持仓市值：¥{total_market_value:,.2f}')
print(f'💎 总资产：¥{total_assets:,.2f}')
print(f'📊 总收益：{total_return:+.2f}%')
print(f'📊 今日盈亏：¥{total_assets - 99964.80:+,.2f}')
print()

print('=' * 70)
print('🚀 预测涨幅 TOP5 (持仓股)')
print('=' * 70)

holding_codes = list(positions.keys())
holding_preds = []
for p in latest_pred.get('predictions', []):
    if p.get('stock_code') in holding_codes:
        holding_preds.append(p)

holding_preds.sort(key=lambda x: x.get('predicted_change', 0), reverse=True)

for i, p in enumerate(holding_preds[:5], 1):
    code = p.get('stock_code')
    name = p.get('stock_name', '')
    change = p.get('predicted_change', 0)
    sign = '+' if change >= 0 else ''
    print(f"{i}. {name} ({code}): {sign}{change:.2f}%")

print()
