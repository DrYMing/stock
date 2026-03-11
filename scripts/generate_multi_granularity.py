#!/usr/bin/env python3
"""
数据脚本：生成包含分钟线、日线、周线的数据
"""
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
DATA_DIR = Path(__file__).parent.parent / "data" / "weipan"
CSV_FILE = DATA_DIR / "数据汇总.csv"
DB_FILE = Path(__file__).parent.parent / "data" / "stock_data.db"
OUTPUT_DIR = Path(__file__).parent.parent / "src" / "backend" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("开始处理多时间粒度数据...")

# 1. 加载选股数据
selections_df = pd.read_csv(CSV_FILE, encoding='utf-8')
selections_df['入选日期+时间'] = pd.to_datetime(selections_df['入选日期+时间'])
print(f"加载了 {len(selections_df)} 条选股记录")

# 2. 连接数据库
conn = sqlite3.connect(DB_FILE)

# 3. 处理每只股票
results = []
all_returns = []

for idx, row in selections_df.iterrows():
    code = str(row['代码']).zfill(6)
    buy_date = row['入选日期+时间']
    buy_price = row['入选价格']
    name = row['名称']

    try:
        # 获取日线数据
        query_daily = f"SELECT * FROM stock_daily WHERE code LIKE '%{code[-6:]}' AND date >= '{buy_date.strftime('%Y-%m-%d')}' ORDER BY date"
        daily_df = pd.read_sql_query(query_daily, conn)

        if not daily_df.empty:
            daily_df['date'] = pd.to_datetime(daily_df['date'])

            # 计算实际买入价
            buy_date_str = buy_date.strftime('%Y-%m-%d')
            buy_day = daily_df[daily_df['date'].dt.strftime('%Y-%m-%d') == buy_date_str]

            if not buy_day.empty:
                actual_buy_price = buy_day.iloc[0]['close']
            else:
                actual_buy_price = daily_df.iloc[0]['open']

            # 计算收益率
            daily_df['return_rate'] = ((daily_df['close'] - actual_buy_price) / actual_buy_price * 100).round(2)

            # 准备日线数据
            time_series = []
            for _, r in daily_df.iterrows():
                time_series.append({
                    'date': r['date'].strftime('%Y-%m-%d'),
                    'open': float(r['open']),
                    'high': float(r['high']),
                    'low': float(r['low']),
                    'close': float(r['close']),
                    'volume': float(r.get('volume', 0)),
                    'return_rate': float(r['return_rate'])
                })

            # 获取周线数据
            weekly_series = []
            try:
                query_weekly = f"SELECT * FROM stock_weekly WHERE code LIKE '%{code[-6:]}' AND date >= '{buy_date.strftime('%Y-%m-%d')}' ORDER BY date LIMIT 100"
                weekly_df = pd.read_sql_query(query_weekly, conn)
                if not weekly_df.empty:
                    weekly_df['date'] = pd.to_datetime(weekly_df['date'])
                    weekly_df['return_rate'] = ((weekly_df['close'] - actual_buy_price) / actual_buy_price * 100).round(2)

                    for _, r in weekly_df.iterrows():
                        weekly_series.append({
                            'date': r['date'].strftime('%Y-%m-%d'),
                            'open': float(r['open']),
                            'high': float(r['high']),
                            'low': float(r['low']),
                            'close': float(r['close']),
                            'volume': float(r.get('volume', 0)),
                            'return_rate': float(r['return_rate'])
                        })
            except:
                pass

            # 获取分钟线数据（只取前3天，限制500条）
            minute_series = []
            try:
                end_date = buy_date + timedelta(days=3)
                query_minute = f"SELECT * FROM minute_kline WHERE code = '{code}' AND datetime >= '{buy_date.strftime('%Y-%m-%d')}' AND datetime <= '{end_date.strftime('%Y-%m-%d')}' ORDER BY datetime LIMIT 500"
                minute_df = pd.read_sql_query(query_minute, conn)
                if not minute_df.empty:
                    minute_df['datetime'] = pd.to_datetime(minute_df['datetime'])
                    minute_df['return_rate'] = ((minute_df['close'] - actual_buy_price) / actual_buy_price * 100).round(2)

                    for _, r in minute_df.iterrows():
                        minute_series.append({
                            'date': r['datetime'].strftime('%Y-%m-%d %H:%M'),
                            'open': float(r['open']),
                            'high': float(r['high']),
                            'low': float(r['low']),
                            'close': float(r['close']),
                            'volume': float(r.get('volume', 0)),
                            'return_rate': float(r['return_rate'])
                        })
            except Exception as e:
                pass

            latest_return = float(daily_df.iloc[-1]['return_rate'])
            all_returns.append(latest_return)

            # 计算买入后第1天、2天、3天、5天尾盘收益率
            # 找到买入日或之后的第一条数据
            buy_datetime = buy_date
            daily_df['dt_only'] = pd.to_datetime(daily_df['date']).dt.normalize()
            buy_dt_only = buy_datetime.normalize()

            # 找到买入日或之后的第一个数据点
            buy_candidates = daily_df[daily_df['dt_only'] >= buy_dt_only]
            if buy_candidates.empty:
                continue  # 跳过没有数据的股票

            buy_index = buy_candidates.index[0]

            # 计算各个时间点的收益率
            # 1日收益率 = 买入后第1个交易日（次日）
            # 2日收益率 = 买入后第2个交易日
            # 3日收益率 = 买入后第3个交易日
            # 5日收益率 = 买入后第5个交易日
            first_day_return = 0.0
            second_day_return = 0.0
            third_day_return = 0.0
            fifth_day_return = 0.0

            # 第1天（买入后第1个交易日 = buy_index + 1）
            if buy_index + 1 < len(daily_df):
                first_day_close = daily_df.iloc[buy_index + 1]['close']
                first_day_return = ((first_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

            # 第2天（买入后第2个交易日 = buy_index + 2）
            if buy_index + 2 < len(daily_df):
                second_day_close = daily_df.iloc[buy_index + 2]['close']
                second_day_return = ((second_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

            # 第3天（买入后第3个交易日 = buy_index + 3）
            if buy_index + 3 < len(daily_df):
                third_day_close = daily_df.iloc[buy_index + 3]['close']
                third_day_return = ((third_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

            # 第5天（买入后第5个交易日 = buy_index + 5）
            if buy_index + 5 < len(daily_df):
                fifth_day_close = daily_df.iloc[buy_index + 5]['close']
                fifth_day_return = ((fifth_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

            result = {
                'name': name,
                'code': code,
                'buy_date': buy_date.strftime('%Y-%m-%d %H:%M'),
                'buy_date_short': buy_date.strftime('%Y-%m-%d'),
                'buy_price': float(buy_price),
                'latest_price': float(daily_df.iloc[-1]['close']),
                'return_rate': latest_return,
                'first_day_return': first_day_return,
                'second_day_return': second_day_return,
                'third_day_return': third_day_return,
                'fifth_day_return': fifth_day_return,
                'max_return': float(daily_df['return_rate'].max()),
                'min_return': float(daily_df['return_rate'].min()),
                'data_points': len(daily_df),
                'time_series': time_series,
                'weekly_series': weekly_series,
                'minute_series': minute_series
            }

            results.append(result)

    except Exception as e:
        print(f"处理 {name}({code}) 时出错: {e}")

    if (idx + 1) % 20 == 0:
        print(f"已处理 {idx + 1}/{len(selections_df)} 条记录")

conn.close()

# 4. 计算统计数据
stats = {
    'total_stocks': len(results),
    'with_data': len(results),
    'without_data': len(selections_df) - len(results),
    'avg_return': round(sum(all_returns) / len(all_returns), 2) if all_returns else 0,
    'max_return': max(all_returns) if all_returns else 0,
    'min_return': min(all_returns) if all_returns else 0,
    'positive_count': len([r for r in all_returns if r > 0]),
    'negative_count': len([r for r in all_returns if r <= 0]),
    'win_rate': round(len([r for r in all_returns if r > 0]) / len(all_returns) * 100, 2) if all_returns else 0
}

# 找出最好和最差的股票
for r in results:
    if r['return_rate'] == stats['max_return']:
        stats['best_stock'] = f"{r['name']}({r['code']})"
    if r['return_rate'] == stats['min_return']:
        stats['worst_stock'] = f"{r['name']}({r['code']})"

# 5. 保存结果
output_file = OUTPUT_DIR / "stock_returns.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({'stats': stats, 'stocks': results}, f, ensure_ascii=False, indent=2)

print(f"\n✅ 处理完成!")
print(f"总股票数: {stats['total_stocks']}")
print(f"平均收益率: {stats['avg_return']:.2f}%")
print(f"最高收益率: {stats['max_return']:.2f}% ({stats.get('best_stock', 'N/A')})")
print(f"最低收益率: {stats['min_return']:.2f}% ({stats.get('worst_stock', 'N/A')})")
print(f"胜率: {stats['win_rate']:.2f}%")

# 统计数据粒度
with_daily = sum(1 for r in results if r.get('time_series'))
with_weekly = sum(1 for r in results if r.get('weekly_series'))
with_minute = sum(1 for r in results if r.get('minute_series'))

print(f"\n📊 数据粒度统计:")
print(f"日线数据: {with_daily}/{stats['total_stocks']}")
print(f"周线数据: {with_weekly}/{stats['total_stocks']}")
print(f"分钟线数据: {with_minute}/{stats['total_stocks']}")
print(f"\n💾 数据已保存到: {output_file}")
