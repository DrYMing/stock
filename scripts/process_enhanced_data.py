#!/usr/bin/env python3
"""
增强数据处理脚本：支持多时间粒度数据
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data" / "weipan"
CSV_FILE = DATA_DIR / "数据汇总.csv"
DB_FILE = Path(__file__).parent.parent / "data" / "stock_data.db"
OUTPUT_DIR = Path(__file__).parent.parent / "src" / "backend" / "data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_stock_selections():
    """加载选股数据"""
    df = pd.read_csv(CSV_FILE, encoding='utf-8')
    df['入选日期+时间'] = pd.to_datetime(df['入选日期+时间'])

    def add_market_prefix(code):
        code_str = str(code).zfill(6)
        if code_str.startswith('6'):
            return f'sh.{code_str}'
        else:
            return f'sz.{code_str}'

    df['code_with_prefix'] = df['代码'].apply(add_market_prefix)
    df['code_padded'] = df['代码'].apply(lambda x: str(x).zfill(6))

    return df


def get_stock_data_by_granularity(code, code_with_prefix, start_date, conn, granularity='daily'):
    """根据时间粒度获取K线数据"""
    granularity_map = {
        'daily': 'stock_daily',
        'weekly': 'stock_weekly',
        'minute': 'minute_kline'
    }

    table_name = granularity_map.get(granularity, 'stock_daily')

    # 构建查询
    if granularity == 'minute':
        # 分钟线数据格式不同，需要特殊处理
        queries = [
            f"SELECT * FROM {table_name} WHERE code = '{code}' AND date >= '{start_date}' ORDER BY date",
            f"SELECT * FROM {table_name} WHERE code LIKE '%{code[-6:]}' AND date >= '{start_date}' ORDER BY date"
        ]
    else:
        queries = [
            f"SELECT * FROM {table_name} WHERE code = '{code}' AND date >= '{start_date}' ORDER BY date",
            f"SELECT * FROM {table_name} WHERE code = '{code_with_prefix}' AND date >= '{start_date}' ORDER BY date",
            f"SELECT * FROM {table_name} WHERE code LIKE '%{code[-6:]}' AND date >= '{start_date}' ORDER BY date"
        ]

    for query in queries:
        try:
            df = pd.read_sql_query(query, conn)
            if not df.empty:
                return df
        except Exception as e:
            continue

    return None


def calculate_returns(stock_df, buy_price, buy_date):
    """计算收益率"""
    if stock_df is None or stock_df.empty:
        return None, None

    # 确定日期列名
    date_column = 'datetime' if 'datetime' in stock_df.columns else 'date'
    stock_df[date_column] = pd.to_datetime(stock_df[date_column])
    stock_df = stock_df.sort_values(date_column)

    # 找到买入日的价格
    buy_date_str = buy_date.strftime('%Y-%m-%d')
    buy_day_data = stock_df[stock_df[date_column].dt.strftime('%Y-%m-%d') == buy_date_str]

    if not buy_day_data.empty:
        actual_buy_price = buy_day_data.iloc[0]['close']
    else:
        next_day_data = stock_df[stock_df[date_column] > buy_date]
        if not next_day_data.empty:
            actual_buy_price = next_day_data.iloc[0]['open']
        else:
            actual_buy_price = buy_price

    # 计算收益率
    stock_df['return_rate'] = ((stock_df['close'] - actual_buy_price) / actual_buy_price * 100).round(2)

    # 统一日期格式为date列
    if date_column == 'datetime':
        stock_df['date'] = stock_df['datetime']

    return stock_df, actual_buy_price, actual_buy_price


def format_time_series(stock_df, granularity='daily'):
    """格式化时间序列数据"""
    if granularity == 'minute':
        return [
            {
                'date': row['datetime'].strftime('%Y-%m-%d %H:%M') if pd.notna(row.get('datetime')) else row['date'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row.get('volume', 0)),
                'return_rate': float(row['return_rate'])
            }
            for _, row in stock_df.iterrows()
        ]
    else:
        return [
            {
                'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row.get('volume', 0)),
                'return_rate': float(row['return_rate'])
            }
            for _, row in stock_df.iterrows()
        ]


def process_enhanced_data():
    """处理增强的多时间粒度数据"""
    print("开始处理多时间粒度数据...")

    selections_df = load_stock_selections()
    print(f"加载了 {len(selections_df)} 条选股记录")

    conn = sqlite3.connect(DB_FILE)

    results = []
    stats = {
        'total_stocks': 0,
        'with_data': 0,
        'without_data': 0,
        'avg_return': 0,
        'max_return': -999,
        'min_return': 999,
        'best_stock': None,
        'worst_stock': None
    }

    all_returns = []

    for idx, row in selections_df.iterrows():
        code = str(row['代码']).zfill(6)
        code_with_prefix = row['code_with_prefix']
        buy_date = row['入选日期+时间']
        buy_price = row['入选价格']
        name = row['名称']

        # 获取日线数据
        daily_df = get_stock_data_by_granularity(code, code_with_prefix, buy_date, conn, 'daily')

        if daily_df is not None and not daily_df.empty:
            daily_df, actual_buy_price = calculate_returns(daily_df, buy_price, buy_date)

            if daily_df is not None:
                latest_return = float(daily_df.iloc[-1]['return_rate'])
                all_returns.append(latest_return)

                if latest_return > stats['max_return']:
                    stats['max_return'] = latest_return
                    stats['best_stock'] = f"{name}({code})"
                if latest_return < stats['min_return']:
                    stats['min_return'] = latest_return
                    stats['worst_stock'] = f"{name}({code})"

                # 准备基础数据
                result = {
                    'name': name,
                    'code': code,
                    'buy_date': buy_date.strftime('%Y-%m-%d %H:%M'),
                    'buy_date_short': buy_date.strftime('%Y-%m-%d'),
                    'buy_price': float(buy_price),
                    'latest_price': float(daily_df.iloc[-1]['close']),
                    'return_rate': latest_return,
                    'max_return': float(daily_df['return_rate'].max()),
                    'min_return': float(daily_df['return_rate'].min()),
                    'data_points': len(daily_df)
                }

                # 添加日线数据
                result['time_series'] = format_time_series(daily_df, 'daily')

                # 获取周线数据（可选）
                weekly_df = get_stock_data_by_granularity(code, code_with_prefix, buy_date, conn, 'weekly')
                if weekly_df is not None and not weekly_df.empty:
                    weekly_df, _ = calculate_returns(weekly_df, actual_buy_price, buy_date)
                    result['weekly_series'] = format_time_series(weekly_df, 'weekly')
                else:
                    result['weekly_series'] = []

                # 获取分钟线数据（限制数量，避免数据太大）
                minute_df = get_stock_data_by_granularity(code, code_with_prefix, buy_date, conn, 'minute')
                if minute_df is not None and not minute_df.empty:
                    # 只取买入后前10个交易日的分钟线数据
                    end_date = buy_date + timedelta(days=10)
                    minute_df = minute_df[minute_df['date'] <= pd.Timestamp(end_date)]
                    minute_df, _ = calculate_returns(minute_df, actual_buy_price, buy_date)
                    # 限制最多1000条数据
                    if len(minute_df) > 1000:
                        minute_df = minute_df.tail(1000)
                    result['minute_series'] = format_time_series(minute_df, 'minute')
                else:
                    result['minute_series'] = []

                results.append(result)
                stats['with_data'] += 1
        else:
            stats['without_data'] += 1
            print(f"警告: {name}({code}) 没有找到K线数据")

        stats['total_stocks'] += 1

        if (idx + 1) % 10 == 0:
            print(f"已处理 {idx + 1}/{len(selections_df)} 条记录")

    conn.close()

    # 计算统计数据
    if all_returns:
        stats['avg_return'] = round(sum(all_returns) / len(all_returns), 2)
        stats['positive_count'] = len([r for r in all_returns if r > 0])
        stats['negative_count'] = len([r for r in all_returns if r <= 0])
        stats['win_rate'] = round(stats['positive_count'] / len(all_returns) * 100, 2)

    # 保存结果
    output_file = OUTPUT_DIR / "stock_returns.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': stats,
            'stocks': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n处理完成!")
    print(f"总股票数: {stats['total_stocks']}")
    print(f"有数据: {stats['with_data']}")
    print(f"无数据: {stats['without_data']}")
    print(f"平均收益率: {stats['avg_return']:.2f}%")
    print(f"最高收益率: {stats['max_return']:.2f}% ({stats['best_stock']})")
    print(f"最低收益率: {stats['min_return']:.2f}% ({stats['worst_stock']})")
    print(f"胜率: {stats.get('win_rate', 0):.2f}%")

    # 统计不同粒度数据的可用性
    with_daily = sum(1 for r in results if len(r.get('time_series', [])) > 0)
    with_weekly = sum(1 for r in results if len(r.get('weekly_series', [])) > 0)
    with_minute = sum(1 for r in results if len(r.get('minute_series', [])) > 0)

    print(f"\n数据粒度统计:")
    print(f"日线数据: {with_daily}/{stats['with_data']}")
    print(f"周线数据: {with_weekly}/{stats['with_data']}")
    print(f"分钟线数据: {with_minute}/{stats['with_data']}")

    print(f"\n数据已保存到: {output_file}")

    return stats, results


if __name__ == "__main__":
    process_enhanced_data()
