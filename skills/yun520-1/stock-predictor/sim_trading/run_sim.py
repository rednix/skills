#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票预测实盘模拟测试系统 v1.0
基于 v16.1 模型预测结果进行模拟交易
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
BASE_DIR = Path('/home/admin/openclaw/workspace/sim_trading')
PREDICTIONS_DIR = Path('/home/admin/openclaw/workspace/predictions')
CONFIG_FILE = BASE_DIR / 'config.json'
PORTFOLIO_FILE = BASE_DIR / 'portfolio.json'
TRANSACTIONS_FILE = BASE_DIR / 'transactions.json'
DAILY_REPORT_FILE = BASE_DIR / 'daily_report.json'
PERFORMANCE_FILE = BASE_DIR / 'performance.json'

def load_json(filepath, default=None):
    """加载 JSON 文件"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default else {}

def save_json(filepath, data):
    """保存 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_latest_prediction():
    """获取最新预测数据"""
    today = datetime.now().strftime('%Y-%m-%d')
    hour = datetime.now().hour
    # 找最新的小时预测文件
    for h in range(hour, -1, -1):
        file = PREDICTIONS_DIR / f"{today}_{h:02d}-00.json"
        if os.path.exists(file):
            return load_json(file)
    # 如果今天没有，找昨天
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    file = PREDICTIONS_DIR / f"{yesterday}.json"
    if os.path.exists(file):
        return load_json(file)
    return None

def calculate_buy_amount(price, cash, max_pct, fees):
    """计算可买入股数"""
    max_amount = cash * max_pct
    shares = int(max_amount / price / 100) * 100  # 100 股的整数倍
    if shares < 100:
        return 0
    cost = shares * price * (1 + fees['commission_rate'])
    cost = max(cost, fees.get('min_commission', 5))
    if cost > cash:
        shares = int((cash / price / 100) - 1) * 100
    return max(0, shares)

def init_account():
    """初始化模拟账户"""
    config = load_json(CONFIG_FILE)
    
    portfolio = {
        'cash': config['account']['initial_capital'],
        'initial_cash': config['account']['initial_capital'],
        'positions': {},  # {stock_code: {shares, avg_price, buy_date, predicted_price}}
        'frozen_cash': 0  # 已挂单未成交的资金
    }
    
    transactions = {
        'history': []  # {date, type, stock_code, stock_name, shares, price, amount, fee, reason}
    }
    
    performance = {
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'daily_returns': [],
        'trades': 0,
        'wins': 0,
        'losses': 0,
        'total_profit': 0
    }
    
    save_json(PORTFOLIO_FILE, portfolio)
    save_json(TRANSACTIONS_FILE, transactions)
    save_json(PERFORMANCE_FILE, performance)
    
    print("=" * 60)
    print("✅ 模拟账户初始化完成")
    print("=" * 60)
    print(f"💰 初始资金：¥{config['account']['initial_capital']:,.2f}")
    print(f"📅 开始日期：{performance['start_date']}")
    print(f"📁 数据目录：{BASE_DIR}")
    print()
    
    return portfolio

def execute_daily_trading():
    """执行每日交易"""
    portfolio = load_json(PORTFOLIO_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    performance = load_json(PERFORMANCE_FILE)
    config = load_json(CONFIG_FILE)
    pred_data = get_latest_prediction()
    
    if not pred_data:
        print("❌ 未找到预测数据")
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    print("=" * 60)
    print(f"📊 模拟交易执行 - {today}")
    print("=" * 60)
    print()
    
    # 1. 检查持仓，卖出到期股票
    print("📤 检查到期持仓...")
    positions_to_sell = []
    for code, pos in portfolio['positions'].items():
        buy_date = datetime.strptime(pos['buy_date'], '%Y-%m-%d')
        hold_days = (datetime.now() - buy_date).days
        
        # 持有 5 天后卖出
        if hold_days >= 5:
            positions_to_sell.append(code)
            print(f"  到期卖出：{code} (持有{hold_days}天)")
    
    # 2. 获取预测，选择买入标的
    print("\n📥 分析预测数据...")
    predictions = pred_data.get('predictions', [])
    
    # 筛选高置信度且预测涨幅>2% 的股票
    buy_candidates = []
    for p in predictions:
        if 'error' in p:
            continue
        pred_change = p.get('predicted_change', 0) / 100
        confidence = p.get('confidence', '低')
        
        if pred_change > config['strategy']['buy_threshold'] and confidence in ['高', '中']:
            buy_candidates.append({
                'code': p.get('stock_code'),
                'name': p.get('stock_name'),
                'price': p.get('current_price'),
                'predicted_change': pred_change,
                'predicted_price': p.get('predicted_price')
            })
    
    # 按预测涨幅排序
    buy_candidates.sort(key=lambda x: x['predicted_change'], reverse=True)
    print(f"  找到 {len(buy_candidates)} 个高置信度买入候选")
    
    # 3. 执行卖出
    cash_after_sell = portfolio['cash']
    for code in positions_to_sell:
        pos = portfolio['positions'][code]
        # 获取当前价格 (用预测的当前价近似)
        current_price = None
        for p in predictions:
            if p.get('stock_code') == code:
                current_price = p.get('current_price')
                break
        
        if not current_price:
            print(f"  ⚠️  无法获取 {code} 当前价格，跳过")
            continue
        
        # 计算盈亏
        shares = pos['shares']
        avg_price = pos['avg_price']
        sell_amount = shares * current_price
        fee = sell_amount * config['fees']['commission_rate'] + sell_amount * config['fees']['stamp_tax']
        fee = max(fee, config['fees'].get('min_commission', 5))
        net_amount = sell_amount - fee
        
        profit = net_amount - (shares * avg_price)
        profit_rate = profit / (shares * avg_price) * 100
        
        # 更新账户
        cash_after_sell += net_amount
        del portfolio['positions'][code]
        
        # 记录交易
        transactions['history'].append({
            'date': today,
            'type': 'sell',
            'stock_code': code,
            'stock_name': pos.get('name', code),
            'shares': shares,
            'price': current_price,
            'amount': sell_amount,
            'fee': fee,
            'profit': profit,
            'profit_rate': profit_rate,
            'reason': f'持有{pos["hold_days"]}天到期'
        })
        
        # 更新绩效
        performance['trades'] += 1
        if profit > 0:
            performance['wins'] += 1
            performance['total_profit'] += profit
        else:
            performance['losses'] += 1
        
        status = "✅" if profit > 0 else "❌"
        print(f"  {status} 卖出 {code}: ¥{current_price:.2f} × {shares}股, 盈亏：{profit:+.2f}元 ({profit_rate:+.2f}%)")
    
    portfolio['cash'] = cash_after_sell
    
    # 4. 执行买入
    print("\n💰 执行买入...")
    available_cash = portfolio['cash']
    max_per_stock = available_cash * config['limits']['max_position_pct']
    stocks_to_buy = min(len(buy_candidates), config['limits']['max_stocks'] - len(portfolio['positions']))
    
    bought_count = 0
    for candidate in buy_candidates[:stocks_to_buy]:
        code = candidate['code']
        name = candidate['name']
        price = candidate['price']
        
        # 检查是否已持仓
        if code in portfolio['positions']:
            continue
        
        # 计算买入股数
        shares = calculate_buy_amount(price, available_cash, config['limits']['max_position_pct'], config['fees'])
        if shares < 100:
            continue
        
        # 计算费用
        buy_amount = shares * price
        fee = buy_amount * config['fees']['commission_rate']
        fee = max(fee, config['fees'].get('min_commission', 5))
        total_cost = buy_amount + fee
        
        if total_cost > available_cash:
            continue
        
        # 执行买入
        portfolio['cash'] -= total_cost
        available_cash -= total_cost
        portfolio['positions'][code] = {
            'name': name,
            'shares': shares,
            'avg_price': price,
            'buy_date': today,
            'predicted_price': candidate['predicted_price'],
            'hold_days': 0
        }
        
        # 记录交易
        transactions['history'].append({
            'date': today,
            'type': 'buy',
            'stock_code': code,
            'stock_name': name,
            'shares': shares,
            'price': price,
            'amount': buy_amount,
            'fee': fee,
            'reason': f"预测涨幅{candidate['predicted_change']*100:.1f}%"
        })
        
        bought_count += 1
        print(f"  ✅ 买入 {name}: ¥{price:.2f} × {shares}股, 花费：¥{total_cost:,.2f}")
    
    # 5. 计算总资产
    total_stock_value = 0
    for code, pos in portfolio['positions'].items():
        # 用预测价估算当前价值
        for p in predictions:
            if p.get('stock_code') == code:
                total_stock_value += pos['shares'] * p.get('current_price', pos['avg_price'])
                break
    
    total_assets = portfolio['cash'] + total_stock_value
    total_return = (total_assets - portfolio['initial_cash']) / portfolio['initial_cash'] * 100
    
    # 6. 保存数据
    portfolio['total_stock_value'] = total_stock_value
    portfolio['total_assets'] = total_assets
    portfolio['total_return'] = total_return
    
    # 记录每日收益
    performance['daily_returns'].append({
        'date': today,
        'total_assets': total_assets,
        'cash': portfolio['cash'],
        'stock_value': total_stock_value,
        'daily_return': total_return,
        'positions_count': len(portfolio['positions']),
        'bought': bought_count,
        'sold': len(positions_to_sell)
    })
    
    save_json(PORTFOLIO_FILE, portfolio)
    save_json(TRANSACTIONS_FILE, transactions)
    save_json(PERFORMANCE_FILE, performance)
    
    # 7. 输出汇总
    print()
    print("=" * 60)
    print("📊 今日汇总")
    print("=" * 60)
    print(f"💰 现金：¥{portfolio['cash']:,.2f}")
    print(f"📈 持仓市值：¥{total_stock_value:,.2f}")
    print(f"💎 总资产：¥{total_assets:,.2f}")
    print(f"📊 总收益：{total_return:+.2f}%")
    print(f"📦 持仓数量：{len(portfolio['positions'])} 只")
    print(f"📝 今日买入：{bought_count} 只，卖出：{len(positions_to_sell)} 只")
    print(f"📈 累计交易：{performance['trades']} 笔 (胜：{performance['wins']}, 负：{performance['losses']})")
    if performance['trades'] > 0:
        win_rate = performance['wins'] / performance['trades'] * 100
        print(f"🎯 胜率：{win_rate:.1f}%")
    print()
    
    return portfolio

def show_portfolio():
    """显示持仓"""
    portfolio = load_json(PORTFOLIO_FILE)
    
    if not portfolio:
        print("❌ 账户未初始化")
        return
    
    print("=" * 60)
    print("📦 当前持仓")
    print("=" * 60)
    print(f"💰 现金：¥{portfolio.get('cash', 0):,.2f}")
    print(f"📈 持仓市值：¥{portfolio.get('total_stock_value', 0):,.2f}")
    print(f"💎 总资产：¥{portfolio.get('total_assets', 0):,.2f}")
    print(f"📊 总收益：{portfolio.get('total_return', 0):+.2f}%")
    print()
    
    if portfolio.get('positions'):
        print("持仓明细:")
        print(f"{'代码':<10} {'名称':<15} {'股数':>10} {'成本':>10} {'现价':>10} {'盈亏':>12}")
        print("-" * 60)
        for code, pos in portfolio['positions'].items():
            # 简单估算盈亏
            estimated_value = pos['shares'] * pos.get('predicted_price', pos['avg_price'])
            cost = pos['shares'] * pos['avg_price']
            profit = estimated_value - cost
            profit_rate = profit / cost * 100
            print(f"{code:<10} {pos.get('name', ''):<15} {pos['shares']:>10} ¥{pos['avg_price']:>8.2f} ¥{pos.get('predicted_price', 0):>8.2f} {profit:>+10.2f} ({profit_rate:+.1f}%)")
    else:
        print("暂无持仓")
    print()

def show_performance():
    """显示绩效"""
    performance = load_json(PERFORMANCE_FILE)
    
    if not performance:
        print("❌ 无绩效数据")
        return
    
    print("=" * 60)
    print("📊 绩效统计")
    print("=" * 60)
    print(f"📅 开始日期：{performance.get('start_date', 'N/A')}")
    print(f"📈 累计交易：{performance.get('trades', 0)} 笔")
    print(f"✅ 盈利：{performance.get('wins', 0)} 笔")
    print(f"❌ 亏损：{performance.get('losses', 0)} 笔")
    
    trades = performance.get('trades', 0)
    if trades > 0:
        win_rate = performance.get('wins', 0) / trades * 100
        print(f"🎯 胜率：{win_rate:.1f}%")
        avg_profit = performance.get('total_profit', 0) / trades
        print(f"💰 平均每笔盈利：¥{avg_profit:.2f}")
    
    # 每日收益走势
    daily = performance.get('daily_returns', [])
    if daily:
        print()
        print("近期收益:")
        for d in daily[-10:]:  # 最近 10 天
            print(f"  {d['date']}: {d['daily_return']:+.2f}% (资产：¥{d['total_assets']:,.2f})")
    print()

def main():
    if len(sys.argv) < 2:
        print("用法：python3 run_sim.py [--init|--daily|--portfolio|--performance]")
        print()
        print("  --init        初始化模拟账户")
        print("  --daily       执行每日交易")
        print("  --portfolio   查看持仓")
        print("  --performance 查看绩效")
        return
    
    action = sys.argv[1]
    
    if action == '--init':
        init_account()
    elif action == '--daily':
        execute_daily_trading()
    elif action == '--portfolio':
        show_portfolio()
    elif action == '--performance':
        show_performance()
    else:
        print(f"❌ 未知命令：{action}")

if __name__ == "__main__":
    main()
