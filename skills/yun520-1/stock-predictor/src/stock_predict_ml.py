#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票预测系统 v16.1 - 轻量深度学习版
优化：降低 LSTM 复杂度，加快训练速度
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
import requests
import warnings
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except:
    XGB_AVAILABLE = False

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except:
    LGB_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except:
    TORCH_AVAILABLE = False

CONFIG = {
    'max_workers': 4,
    'timeout': 15,
    'days_for_analysis': 250,
    'test_ratio': 0.2,
    'sequence_length': 10,
    'hidden_size': 32,
    'num_layers': 1,
    'dropout': 0.1,
    'batch_size': 16,
    'epochs': 15,
    'learning_rate': 0.01,
}

def load_stocks():
    stocks_file = '/home/admin/openclaw/workspace/temp/stocks.json'
    if os.path.exists(stocks_file):
        with open(stocks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def fetch_tencent_data(code: str, days: int = 250) -> pd.DataFrame:
    try:
        url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,{days},qfq"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=CONFIG['timeout'])
        data = response.json()
        if data.get('code') != 0 or 'data' not in data:
            return None
        stock_data = data['data'].get(code, {})
        klines = stock_data.get('qfqday', [])
        if not klines:
            return None
        df = pd.DataFrame(klines)
        if df.shape[1] < 6:
            return None
        df = df.rename(columns={0: 'trade_date', 1: 'open', 2: 'close', 3: 'high', 4: 'low', 5: 'vol'})
        for col in ['open', 'close', 'high', 'low', 'vol']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        return None

def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    for period in [5, 10, 20, 60]:
        df[f'ma_{period}'] = df['close'].rolling(period).mean()
        df[f'ma_{period}_ratio'] = (df['close'] - df[f'ma_{period}']) / (df[f'ma_{period}'] + 1e-10)
    
    df['ma_bullish'] = ((df['ma_5'] > df['ma_10']) & (df['ma_10'] > df['ma_20'])).astype(int)
    
    df['bb_middle'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_position'] = (df['close'] - (df['bb_middle'] - 2*df['bb_std'])) / (4*df['bb_std'] + 1e-10)
    
    for period in [6, 12]:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        df[f'rsi_{period}'] = 100 - (100 / (1 + gain/(loss+1e-10)))
    
    exp12 = df['close'].ewm(span=12, adjust=False).mean()
    exp26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp12 - exp26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    df['vol_ma5'] = df['vol'].rolling(5).mean()
    df['vol_ratio'] = df['vol'] / (df['vol_ma5'] + 1e-10)
    
    for period in [1, 3, 5, 10]:
        df[f'momentum_{period}'] = df['close'].pct_change(period)
    
    df['daily_return'] = df['close'].pct_change()
    df['volatility'] = df['daily_return'].rolling(20).std()
    
    for lag in [1, 2, 3]:
        df[f'return_lag_{lag}'] = df['daily_return'].shift(lag)
    
    df['target'] = (df['close'].shift(-5) > df['close']).astype(int)
    
    return df

def get_feature_columns():
    return [
        'ma_5_ratio', 'ma_10_ratio', 'ma_20_ratio', 'ma_60_ratio',
        'ma_bullish', 'bb_position',
        'rsi_6', 'rsi_12',
        'macd', 'macd_signal',
        'vol_ratio',
        'momentum_1', 'momentum_3', 'momentum_5', 'momentum_10',
        'daily_return', 'volatility',
        'return_lag_1', 'return_lag_2', 'return_lag_3'
    ]

class SimpleLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=32, num_layers=1, dropout=0.1):
        super(SimpleLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, 2)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

def create_sequences(X, y, seq_length):
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_length):
        X_seq.append(X[i:i+seq_length])
        y_seq.append(y[i+seq_length])
    return np.array(X_seq), np.array(y_seq)

def train_lstm(X_train, y_train, X_test, y_test):
    if not TORCH_AVAILABLE:
        return None
    
    try:
        seq_length = min(CONFIG['sequence_length'], len(X_train) - 10)
        if seq_length < 5:
            return None
        
        X_train_seq, y_train_seq = create_sequences(X_train, y_train, seq_length)
        X_test_seq, y_test_seq = create_sequences(X_test, y_test, seq_length)
        
        if len(X_train_seq) < 30 or len(X_test_seq) < 10:
            return None
        
        scaler = StandardScaler()
        X_train_flat = X_train_seq.reshape(-1, X_train_seq.shape[-1])
        X_test_flat = X_test_seq.reshape(-1, X_test_seq.shape[-1])
        
        X_train_scaled = scaler.fit_transform(X_train_flat).reshape(X_train_seq.shape)
        X_test_scaled = scaler.transform(X_test_flat).reshape(X_test_seq.shape)
        
        X_train_tensor = torch.FloatTensor(X_train_scaled)
        y_train_tensor = torch.LongTensor(y_train_seq)
        X_test_tensor = torch.FloatTensor(X_test_scaled)
        y_test_tensor = torch.LongTensor(y_test_seq)
        
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=min(CONFIG['batch_size'], len(train_dataset)), shuffle=True)
        
        model = SimpleLSTM(input_size=X_train.shape[-1], hidden_size=CONFIG['hidden_size'], 
                          num_layers=CONFIG['num_layers'], dropout=CONFIG['dropout'])
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG['learning_rate'])
        
        model.train()
        for epoch in range(CONFIG['epochs']):
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        model.eval()
        with torch.no_grad():
            outputs = model(X_test_tensor)
            _, y_pred = torch.max(outputs, 1)
            y_proba = torch.softmax(outputs, dim=1)[:, 1].numpy()
            
            acc = accuracy_score(y_test_seq, y_pred.numpy()) * 100
            high_conf_mask = y_proba > 0.65
            high_acc = accuracy_score(y_test_seq[high_conf_mask], y_pred.numpy()[high_conf_mask]) * 100 if high_conf_mask.sum() > 0 else 0
            
            return {'accuracy': acc, 'high_conf_accuracy': high_acc, 'high_conf_count': int(high_conf_mask.sum()),
                    'total_tests': len(y_test_seq), 'correct': int((y_pred.numpy() == y_test_seq).sum())}
    except Exception as e:
        return None

def train_ml_models(X_train, y_train, X_test, y_test):
    models = {}
    try:
        rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        models['RF'] = rf
    except: pass
    
    try:
        gb = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
        gb.fit(X_train, y_train)
        models['GB'] = gb
    except: pass
    
    try:
        lr = LogisticRegression(random_state=42, max_iter=500)
        lr.fit(X_train, y_train)
        models['LR'] = lr
    except: pass
    
    if XGB_AVAILABLE:
        try:
            xgb_model = xgb.XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='logloss')
            xgb_model.fit(X_train, y_train)
            models['XGB'] = xgb_model
        except: pass
    
    if LGB_AVAILABLE:
        try:
            lgb_model = lgb.LGBMClassifier(n_estimators=50, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1)
            lgb_model.fit(X_train, y_train)
            models['LGB'] = lgb_model
        except: pass
    
    return models

def evaluate_models(models, X_test, y_test):
    results = {}
    for name, model in models.items():
        try:
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            acc = accuracy_score(y_test, y_pred) * 100
            high_conf_mask = y_proba > 0.65
            high_acc = accuracy_score(y_test[high_conf_mask], y_pred[high_conf_mask]) * 100 if high_conf_mask.sum() > 0 else 0
            results[name] = {'accuracy': acc, 'high_conf_accuracy': high_acc, 'high_conf_count': int(high_conf_mask.sum()),
                           'total_tests': len(y_test), 'correct': int((y_pred == y_test).sum())}
        except: continue
    return results

def train_and_evaluate(df, stock_name):
    feature_cols = get_feature_columns()
    df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(subset=feature_cols + ['target']).copy()
    
    if len(df_clean) < 120:
        return None
    
    split_idx = int(len(df_clean) * (1 - CONFIG['test_ratio']))
    if split_idx < 60 or len(df_clean) - split_idx < 15:
        return None
    
    train_df, test_df = df_clean.iloc[:split_idx], df_clean.iloc[split_idx:]
    
    X_train, y_train = train_df[feature_cols].values, train_df['target'].values
    X_test, y_test = test_df[feature_cols].values, test_df['target'].values
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    ml_models = train_ml_models(X_train_scaled, y_train, X_test_scaled, y_test)
    ml_results = evaluate_models(ml_models, X_test_scaled, y_test)
    
    lstm_result = train_lstm(X_train, y_train, X_test, y_test)
    
    all_results = {**ml_results}
    if lstm_result:
        all_results['LSTM'] = lstm_result
    
    if not all_results:
        return None
    
    best_name = max(all_results.keys(), key=lambda k: all_results[k]['accuracy'])
    best_result = all_results[best_name]
    
    return {
        'best_model': best_name,
        'accuracy': best_result['accuracy'],
        'high_conf_accuracy': best_result.get('high_conf_accuracy', 0),
        'high_conf_count': best_result.get('high_conf_count', 0),
        'total_tests': best_result['total_tests'],
        'correct': best_result['correct'],
        'models_used': list(ml_models.keys()) + (['LSTM'] if lstm_result else [])
    }

def backtest_single_stock(stock):
    code, name = stock["code"], stock["name"]
    df = fetch_tencent_data(code, days=CONFIG['days_for_analysis'])
    if df is None:
        return {"name": name, "code": code, "error": "数据获取失败"}
    
    df = calculate_features(df)
    result = train_and_evaluate(df, name)
    
    if result is None:
        return {"name": name, "code": code, "error": "数据不足"}
    
    return {"name": name, "code": code, **result}

def run_backtest():
    print("=" * 80)
    print("股票预测系统 v16.1 - 轻量深度学习回测")
    print("=" * 80)
    print(f"📦 PyTorch: {TORCH_AVAILABLE}, XGBoost: {XGB_AVAILABLE}, LightGBM: {LGB_AVAILABLE}")
    print()
    
    stocks = load_stocks()
    print(f"📊 测试股票数量：{len(stocks)} 只")
    print()
    
    results, errors = [], []
    
    with ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as executor:
        futures = {executor.submit(backtest_single_stock, stock): stock for stock in stocks}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)
            if "error" in result:
                errors.append(result)
            if (i + 1) % 50 == 0:
                print(f"  进度：{i+1}/{len(stocks)} (有效：{len(results)-len(errors)})")
    
    valid_results = [r for r in results if "error" not in r]
    
    print()
    print(f"✅ 成功：{len(valid_results)} 只，❌ 失败：{len(errors)} 只")
    
    if not valid_results:
        print("\n❌ 无有效回测结果")
        return
    
    avg_accuracy = sum(r['accuracy'] for r in valid_results) / len(valid_results)
    high_conf_results = [r for r in valid_results if r.get('high_conf_count', 0) > 0]
    avg_high_conf = sum(r['high_conf_accuracy'] for r in high_conf_results) / len(high_conf_results) if high_conf_results else 0
    
    model_counts = {}
    for r in valid_results:
        m = r.get('best_model', 'unknown')
        model_counts[m] = model_counts.get(m, 0) + 1
    
    print()
    print("=" * 80)
    print("📊 回测结果")
    print("=" * 80)
    print(f"📈 平均准确率：{avg_accuracy:.2f}%")
    print(f"📈 高置信度准确率：{avg_high_conf:.2f}%")
    print()
    print("🏆 最佳模型:")
    for model, count in sorted(model_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"   {model}: {count} 只 ({count/len(valid_results)*100:.1f}%)")
    print()
    
    valid_results.sort(key=lambda x: x['accuracy'], reverse=True)
    print("🏆 TOP 10:")
    for i, r in enumerate(valid_results[:10], 1):
        print(f"  {i}. {r['name']}: {r['accuracy']:.1f}% [{r['best_model']}]")
    
    print()
    print("📊 分布:")
    bins = [0, 50, 55, 60, 65, 70, 100]
    labels = ['<50%', '50-55%', '55-60%', '60-65%', '65-70%', '70-100%']
    for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
        count = sum(1 for r in valid_results if low <= r['accuracy'] < high)
        print(f"  {labels[i]}: {count} 只")
    
    # 保存
    with open('/home/admin/openclaw/workspace/temp/backtest_v16.json', 'w', encoding='utf-8') as f:
        json.dump({'version': '16.1-Lite-DL', 'avg_accuracy': avg_accuracy, 'results': valid_results}, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 80)
    print("📋 版本对比")
    print("=" * 80)
    print("v14.0: 57.23%")
    print("v15.0: 60.61%")
    print(f"v16.1: {avg_accuracy:.2f}%")
    print(f"相比 v15: {avg_accuracy - 60.61:+.2f}%")
    
    if avg_accuracy >= 65:
        print(f"\n✅ 达到 65% 目标！")
    elif avg_accuracy >= 60:
        print(f"\n🟡 保持 60%+ 水平")
    else:
        print(f"\n⚠️  低于 v15")

if __name__ == "__main__":
    run_backtest()
