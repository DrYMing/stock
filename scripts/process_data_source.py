#!/usr/bin/env python3
"""
多数据源处理脚本：支持从不同CSV文件处理数据
"""
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
DB_FILE = DATA_DIR / "stock_data.db"
OUTPUT_DIR = Path(__file__).parent.parent / "src" / "backend" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def process_data_source(csv_file_path, source_name):
    """
    处理单个数据源
    csv_file_path: CSV文件的完整路径
    source_name: 数据源名称
    """
    print(f"\n开始处理数据源: {source_name}")
    print(f"CSV文件: {csv_file_path}")

    if not Path(csv_file_path).exists():
        print(f"❌ 文件不存在: {csv_file_path}")
        return None

    # 读取选股数据
    try:
        # 先读取文件内容，替换中文标点符号
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 替换中文标点符号为英文逗号
            content = content.replace('，', ',').replace('、', ',')
            # 使用StringIO读取处理后的内容
            from io import StringIO
            selections_df = pd.read_csv(StringIO(content), encoding='utf-8')

        # 规范化列名：去除列名中的空格
        selections_df.columns = selections_df.columns.str.replace(' ', '')
    except Exception as e:
        print(f"❌ 读取CSV失败: {e}")
        return None

    # 检查必需列
    required_columns = ['名称', '代码', '入选日期+时间', '入选价格']
    missing_cols = [col for col in required_columns if col not in selections_df.columns]
    if missing_cols:
        print(f"❌ CSV缺少必需列: {missing_cols}")
        return None

    selections_df['入选日期+时间'] = pd.to_datetime(selections_df['入选日期+时间'])

    # 连接数据库
    conn = sqlite3.connect(DB_FILE)

    # 处理每只股票
    results = []
    all_returns = []
    all_first_day_returns = []
    all_second_day_returns = []
    all_third_day_returns = []
    all_fifth_day_returns = []
    processed_count = 0
    skipped_count = 0

    for idx, row in selections_df.iterrows():
        code = str(row['代码']).zfill(6)
        buy_date = row['入选日期+时间']
        buy_price = row['入选价格']
        name = row['名称']

        try:
            # 获取日线数据
            query_daily = f"SELECT * FROM daily_kline WHERE code LIKE '%{code[-6:]}' AND date >= '{buy_date.strftime('%Y-%m-%d')}' ORDER BY date"
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
                    query_weekly = f"SELECT * FROM weekly_kline WHERE code LIKE '%{code[-6:]}' AND date >= '{buy_date.strftime('%Y-%m-%d')}' ORDER BY date LIMIT 100"
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

                # 获取分钟线数据
                minute_series = []
                try:
                    end_date = buy_date + timedelta(days=3)
                    query_minute = f"SELECT * FROM minute_kline WHERE code = '{code}' AND datetime >= '{buy_date.strftime('%Y-%m-%d')}' AND datetime <= '{end_date.strftime('%Y-%m-%d')}' ORDER BY datetime LIMIT 500"
                    minute_df = pd.read_sql_query(query_minute, conn)
                    if not minute_df.empty:
                        # 处理特殊格式的datetime: "2026-01-29 20260129093500000"
                        # 只取第二部分的前14位（去掉微秒）
                        minute_df['datetime_clean'] = minute_df['datetime'].apply(
                            lambda x: str(x).split()[-1][:14] if ' ' in str(x) else str(x)[:14]
                        )
                        minute_df['datetime'] = pd.to_datetime(minute_df['datetime_clean'], format='%Y%m%d%H%M%S', errors='coerce')
                        minute_df['return_rate'] = ((minute_df['close'] - actual_buy_price) / actual_buy_price * 100).round(2)

                        for _, r in minute_df.iterrows():
                            if pd.notna(r['datetime']):
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
                    print(f"  获取分钟线数据失败 {name}({code}): {e}")

                latest_return = float(daily_df.iloc[-1]['return_rate'])
                all_returns.append(latest_return)

                # 计算各个时间点的收益率
                buy_datetime = buy_date
                daily_df['dt_only'] = pd.to_datetime(daily_df['date']).dt.normalize()
                buy_dt_only = buy_datetime.normalize()

                buy_candidates = daily_df[daily_df['dt_only'] >= buy_dt_only]
                if buy_candidates.empty:
                    continue

                buy_index = buy_candidates.index[0]

                first_day_return = 0.0
                second_day_return = 0.0
                third_day_return = 0.0
                fifth_day_return = 0.0

                if buy_index + 1 < len(daily_df):
                    first_day_close = daily_df.iloc[buy_index + 1]['close']
                    first_day_return = ((first_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

                if buy_index + 2 < len(daily_df):
                    second_day_close = daily_df.iloc[buy_index + 2]['close']
                    second_day_return = ((second_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

                if buy_index + 3 < len(daily_df):
                    third_day_close = daily_df.iloc[buy_index + 3]['close']
                    third_day_return = ((third_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

                if buy_index + 5 < len(daily_df):
                    fifth_day_close = daily_df.iloc[buy_index + 5]['close']
                    fifth_day_return = ((fifth_day_close - actual_buy_price) / actual_buy_price * 100).round(2)

                # 收集分日收益率用于统计
                all_first_day_returns.append(first_day_return)
                all_second_day_returns.append(second_day_return)
                all_third_day_returns.append(third_day_return)
                all_fifth_day_returns.append(fifth_day_return)

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
                processed_count += 1

        except Exception as e:
            print(f"处理 {name}({code}) 时出错: {e}")
            skipped_count += 1

        if (idx + 1) % 20 == 0:
            print(f"  已处理 {idx + 1}/{len(selections_df)} 条记录")

    conn.close()

    # 计算统计数据
    stats = {
        'total_stocks': processed_count,
        'with_data': processed_count,
        'without_data': skipped_count,
        'avg_return': round(sum(all_returns) / len(all_returns), 2) if all_returns else 0,
        'avg_first_day_return': round(sum(all_first_day_returns) / len(all_first_day_returns), 2) if all_first_day_returns else 0,
        'avg_second_day_return': round(sum(all_second_day_returns) / len(all_second_day_returns), 2) if all_second_day_returns else 0,
        'avg_third_day_return': round(sum(all_third_day_returns) / len(all_third_day_returns), 2) if all_third_day_returns else 0,
        'avg_fifth_day_return': round(sum(all_fifth_day_returns) / len(all_fifth_day_returns), 2) if all_fifth_day_returns else 0,
        'max_return': max(all_returns) if all_returns else 0,
        'min_return': min(all_returns) if all_returns else 0,
        'positive_count': len([r for r in all_returns if r > 0]),
        'negative_count': len([r for r in all_returns if r <= 0]),
        'win_rate': round(len([r for r in all_returns if r > 0]) / len(all_returns) * 100, 2) if all_returns else 0,
        'first_day_win_rate': round(len([r for r in all_first_day_returns if r > 0]) / len(all_first_day_returns) * 100, 2) if all_first_day_returns else 0,
        'second_day_win_rate': round(len([r for r in all_second_day_returns if r > 0]) / len(all_second_day_returns) * 100, 2) if all_second_day_returns else 0,
        'third_day_win_rate': round(len([r for r in all_third_day_returns if r > 0]) / len(all_third_day_returns) * 100, 2) if all_third_day_returns else 0,
        'fifth_day_win_rate': round(len([r for r in all_fifth_day_returns if r > 0]) / len(all_fifth_day_returns) * 100, 2) if all_fifth_day_returns else 0
    }

    # 找出最好和最差的股票
    for r in results:
        if r['return_rate'] == stats['max_return']:
            stats['best_stock'] = f"{r['name']}({r['code']})"
        if r['return_rate'] == stats['min_return']:
            stats['worst_stock'] = f"{r['name']}({r['code']})"

    # 保存结果
    output_file = OUTPUT_DIR / f"{source_name}_stock_returns.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'stats': stats, 'stocks': results}, f, ensure_ascii=False, indent=2)

    print(f"✅ {source_name} 处理完成!")
    print(f"   总股票数: {stats['total_stocks']}")
    print(f"   平均收益率: {stats['avg_return']:.2f}%")
    print(f"   胜率: {stats['win_rate']:.2f}%")
    print(f"   数据已保存到: {output_file}")

    return {
        'source_name': source_name,
        'stats': stats,
        'file_path': str(output_file)
    }


def main():
    """主函数：扫描数据目录并处理所有CSV"""
    print("=" * 60)
    print("多数据源处理工具")
    print("=" * 60)

    # 如果提供了命令行参数，处理指定的文件
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        source_name = sys.argv[2] if len(sys.argv) > 2 else Path(csv_path).stem
        result = process_data_source(csv_path, source_name)
        if result:
            print(f"\n✅ 数据源 '{result['source_name']}' 处理完成!")
            print(f"文件路径: {result['file_path']}")
            print(f"可以用于前端切换: {result['source_name']}")
        return

    # 否则，扫描data目录查找所有CSV文件
    print("\n扫描数据目录...")

    csv_files = []
    for csv_file in DATA_DIR.rglob("*.csv"):
        print(f"  发现: {csv_file.relative_to(DATA_DIR)}")
        csv_files.append(csv_file)

    if not csv_files:
        print("❌ 未找到任何CSV文件")
        return

    print(f"\n共找到 {len(csv_files)} 个CSV文件")

    # 处理每个CSV文件
    sources = []
    for csv_file in csv_files:
        source_name = csv_file.stem  # 使用文件名作为数据源名称
        result = process_data_source(str(csv_file), source_name)
        if result:
            sources.append(result)

    # 生成数据源配置文件
    sources_config = {
        'sources': [
            {
                'name': source['source_name'],
                'display_name': source['source_name'].replace('_', ' '),
                'file_path': str(csv_file),
                'data_file': source['file_path'],
                'stats': source['stats']
            }
            for source, csv_file in zip(sources, csv_files)
        ],
        'default_source': sources[0]['name'] if sources else None
    }

    config_file = OUTPUT_DIR / "data_sources.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sources_config, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 所有数据源处理完成!")
    print(f"配置文件: {config_file}")
    print(f"可用数据源: {len(sources)}")

    for source in sources:
        print(f"  - {source['source_name']}: {source['stats']['total_ststocks']} 只股票")


if __name__ == "__main__":
    main()
