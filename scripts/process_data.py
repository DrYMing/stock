#!/usr/bin/env python3
"""
数据处理脚本：读取选股数据和K线数据，计算收益率
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data" / "weipan"
CSV_FILE = DATA_DIR / "数据汇总.csv"
DB_FILE = Path(__file__).parent.parent / "data" / "stock_data.db"  # 更新数据库路径
OUTPUT_DIR = Path(__file__).parent.parent / "src" / "backend" / "data"

# 创建输出目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_stock_selections():
    """加载选股数据"""
    df = pd.read_csv(CSV_FILE, encoding='utf-8')
    df['入选日期+时间'] = pd.to_datetime(df['入选日期+时间'])

    # 添加市场前缀辅助列
    def add_market_prefix(code):
        code_str = str(code).zfill(6)
        if code_str.startswith('6'):
            return f'sh.{code_str}'
        else:
            return f'sz.{code_str}'

    df['code_with_prefix'] = df['代码'].apply(add_market_prefix)
    df['code_padded'] = df['代码'].apply(lambda x: str(x).zfill(6))

    return df


def get_stock_data_from_db(code, code_with_prefix, start_date, conn):
    """从数据库获取股票K线数据"""
    # 尝试多种代码格式
    queries = [
        f"SELECT * FROM stock_daily WHERE code = '{code}' AND date >= '{start_date}' ORDER BY date",
        f"SELECT * FROM stock_daily WHERE code = '{code_with_prefix}' AND date >= '{start_date}' ORDER BY date",
        f"SELECT * FROM stock_daily WHERE code LIKE '%{code[-6:]}' AND date >= '{start_date}' ORDER BY date"
    ]

    for query in queries:
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            return df

    return None


def calculate_returns(stock_df, buy_price, buy_date):
    """计算收益率"""
    if stock_df is None or stock_df.empty:
        return None

    stock_df['date'] = pd.to_datetime(stock_df['date'])
    stock_df = stock_df.sort_values('date')

    # 找到买入日的收盘价
    buy_date_str = buy_date.strftime('%Y-%m-%d')
    buy_day_data = stock_df[stock_df['date'].dt.strftime('%Y-%m-%d') == buy_date_str]

    if not buy_day_data.empty:
        actual_buy_price = buy_day_data.iloc[0]['close']
    else:
        # 如果买入日没有数据，使用次日开盘价
        next_day_data = stock_df[stock_df['date'] > buy_date]
        if not next_day_data.empty:
            actual_buy_price = next_day_data.iloc[0]['open']
        else:
            actual_buy_price = buy_price

    # 计算收益率
    stock_df['return_rate'] = ((stock_df['close'] - actual_buy_price) / actual_buy_price * 100).round(2)

    # 计算累计收益率
    stock_df['cumulative_return'] = stock_df['return_rate'].values

    # 添加买入信息
    stock_df['buy_price'] = actual_buy_price
    stock_df['buy_date'] = buy_date.strftime('%Y-%m-%d')

    return stock_df


def process_all_stocks():
    """处理所有股票数据"""
    print("开始处理数据...")

    # 加载选股数据
    selections_df = load_stock_selections()
    print(f"加载了 {len(selections_df)} 条选股记录")

    # 连接数据库
    conn = sqlite3.connect(DB_FILE)

    # 处理每条选股记录
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

        # 获取K线数据
        stock_df = get_stock_data_from_db(code, code_with_prefix, buy_date, conn)

        if stock_df is not None and not stock_df.empty:
            # 计算收益率
            stock_df = calculate_returns(stock_df, buy_price, buy_date)

            if stock_df is not None:
                # 获取最新收益率
                latest_return = stock_df.iloc[-1]['return_rate']

                # 更新统计信息
                all_returns.append(latest_return)
                if latest_return > stats['max_return']:
                    stats['max_return'] = latest_return
                    stats['best_stock'] = f"{name}({code})"
                if latest_return < stats['min_return']:
                    stats['min_return'] = latest_return
                    stats['worst_stock'] = f"{name}({code})"

                # 准备结果数据
                result = {
                    'name': name,
                    'code': code,
                    'buy_date': buy_date.strftime('%Y-%m-%d %H:%M'),
                    'buy_price': float(buy_price),
                    'latest_price': float(stock_df.iloc[-1]['close']),
                    'return_rate': float(latest_return),
                    'max_return': float(stock_df['return_rate'].max()),
                    'min_return': float(stock_df['return_rate'].min()),
                    'data_points': len(stock_df)
                }

                # 添加时间序列数据（包含OHLC）
                result['time_series'] = [
                    {
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': float(row.get('volume', 0)),
                        'return_rate': float(row['return_rate'])
                    }
                    for _, row in stock_df.iterrows()
                ]

                # 保存原始买入日期（字符串和日期对象）
                result['buy_date_original'] = buy_date.strftime('%Y-%m-%d %H:%M')
                result['buy_date_short'] = buy_date.strftime('%Y-%m-%d')

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
    print(f"\n数据已保存到: {output_file}")

    return stats, results


if __name__ == "__main__":
    process_all_stocks()
