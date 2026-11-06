#!/usr/bin/env python3
"""
Flask后端API：提供股票数据接口，支持多数据源切换
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 数据目录
DATA_DIR = Path(__file__).parent / "data"
SOURCES_CONFIG = DATA_DIR / "data_sources.json"


def load_data_source(source_name=None):
    """加载指定数据源的数据"""
    # 读取数据源配置
    try:
        with open(SOURCES_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        # 如果配置文件不存在，创建默认配置
        default_file = Path(__file__).parent / "data" / "stock_returns.json"
        if default_file.exists():
            config = {
                'sources': [{
                    'name': 'default',
                    'display_name': '默认数据',
                    'data_file': str(default_file)
                }],
                'default_source': 'default'
            }
            with open(SOURCES_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        else:
            return None, None

    # 确定使用的数据源
    if source_name is None:
        source_name = config.get('default_source', config['sources'][0]['name'] if config['sources'] else 'default')

    # 查找对应的数据源
    source = next((s for s in config['sources'] if s['name'] == source_name), None)
    if not source:
        return None, None

    # 加载数据文件
    data_file = Path(source['data_file'])
    if not data_file.exists():
        return None, None

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return source, data


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'API is running'})


@app.route('/api/sources', methods=['GET'])
def get_data_sources():
    """获取所有可用的数据源"""
    try:
        with open(SOURCES_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 返回数据源列表（不包含完整数据，只返回摘要信息）
        sources_summary = []
        for s in config['sources']:
            sources_summary.append({
                'name': s['name'],
                'display_name': s.get('display_name', s['name']),
                'file_path': s.get('file_path', ''),
                'stats': s.get('stats', {})
            })

        return jsonify({
            'sources': sources_summary,
            'current_source': config.get('default_source')
        })
    except FileNotFoundError:
        return jsonify({'sources': [], 'current_source': None})


@app.route('/api/switch-source', methods=['POST'])
def switch_data_source():
    """切换数据源"""
    data = request.get_json()
    source_name = data.get('source_name')

    if not source_name:
        return jsonify({'error': 'Missing source_name parameter'}), 400

    try:
        with open(SOURCES_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 检查数据源是否存在
        source = next((s for s in config['sources'] if s['name'] == source_name), None)
        if not source:
            return jsonify({'error': f'Data source "{source_name}" not found'}), 404

        # 更新默认数据源
        config['default_source'] = source_name

        with open(SOURCES_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return jsonify({
            'message': f'Successfully switched to {source_name}',
            'source': source_name,
            'stats': source.get('stats', {})
        })
    except FileNotFoundError:
        return jsonify({'error': 'Data sources configuration not found'}), 404


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取当前数据源的统计数据（支持筛选）"""
    source, data = load_data_source()
    if not data:
        return jsonify({'error': 'No data available'}), 404

    stocks = data['stocks']

    # 获取筛选参数（与stocks API保持一致）
    search = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    # 应用与stocks API相同的筛选逻辑
    if search:
        stocks = [s for s in stocks if search.lower() in s['name'].lower() or search in s['code']]
    if min_price is not None:
        stocks = [s for s in stocks if s['buy_price'] >= min_price]
    if max_price is not None:
        stocks = [s for s in stocks if s['buy_price'] <= max_price]
    if start_date:
        stocks = [s for s in stocks if s['buy_date_short'] >= start_date]
    if end_date:
        stocks = [s for s in stocks if s['buy_date_short'] <= end_date]

    # 如果没有筛选条件，返回预计算的stats
    if not search and min_price is None and max_price is None and not start_date and not end_date:
        return jsonify(data['stats'])

    # 否则动态计算筛选后的统计数据
    if not stocks:
        return jsonify({
            'total_stocks': 0,
            'with_data': 0,
            'without_data': 0,
            'avg_return': 0,
            'avg_first_day_return': 0,
            'avg_second_day_return': 0,
            'avg_third_day_return': 0,
            'avg_fifth_day_return': 0,
            'max_return': 0,
            'min_return': 0,
            'positive_count': 0,
            'negative_count': 0,
            'win_rate': 0,
            'first_day_win_rate': 0,
            'second_day_win_rate': 0,
            'third_day_win_rate': 0,
            'fifth_day_win_rate': 0
        })

    # 计算各项统计
    returns = [s['return_rate'] for s in stocks]
    first_day_returns = [s.get('first_day_return', 0) for s in stocks]
    second_day_returns = [s.get('second_day_return', 0) for s in stocks]
    third_day_returns = [s.get('third_day_return', 0) for s in stocks]
    fifth_day_returns = [s.get('fifth_day_return', 0) for s in stocks]

    stats = {
        'total_stocks': len(stocks),
        'with_data': len(stocks),
        'without_data': 0,
        'avg_return': round(sum(returns) / len(returns), 2),
        'avg_first_day_return': round(sum(first_day_returns) / len(first_day_returns), 2),
        'avg_second_day_return': round(sum(second_day_returns) / len(second_day_returns), 2),
        'avg_third_day_return': round(sum(third_day_returns) / len(third_day_returns), 2),
        'avg_fifth_day_return': round(sum(fifth_day_returns) / len(fifth_day_returns), 2),
        'max_return': max(returns),
        'min_return': min(returns),
        'positive_count': len([r for r in returns if r > 0]),
        'negative_count': len([r for r in returns if r <= 0]),
        'win_rate': round(len([r for r in returns if r > 0]) / len(returns) * 100, 2),
        'first_day_win_rate': round(len([r for r in first_day_returns if r > 0]) / len(first_day_returns) * 100, 2),
        'second_day_win_rate': round(len([r for r in second_day_returns if r > 0]) / len(second_day_returns) * 100, 2),
        'third_day_win_rate': round(len([r for r in third_day_returns if r > 0]) / len(third_day_returns) * 100, 2),
        'fifth_day_win_rate': round(len([r for r in fifth_day_returns if r > 0]) / len(fifth_day_returns) * 100, 2)
    }

    # 找出最好和最差的股票
    sorted_stocks = sorted(stocks, key=lambda x: x['return_rate'])
    if sorted_stocks:
        worst = sorted_stocks[0]
        best = sorted_stocks[-1]
        stats['best_stock'] = f"{best['name']}({best['code']})"
        stats['worst_stock'] = f"{worst['name']}({worst['code']})"

    return jsonify(stats)


@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取当前数据源的股票列表"""
    source, data = load_data_source()
    if not data:
        return jsonify({'error': 'No data available'}), 404

    stocks = data['stocks']

    # 获取筛选参数
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))
    sort_by = request.args.get('sort_by', 'return_rate')
    order = request.args.get('order', 'desc')
    search = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    # 搜索过滤
    if search:
        stocks = [s for s in stocks if search.lower() in s['name'].lower() or search in s['code']]

    # 价格区间过滤
    if min_price is not None:
        stocks = [s for s in stocks if s['buy_price'] >= min_price]
    if max_price is not None:
        stocks = [s for s in stocks if s['buy_price'] <= max_price]

    # 买入日期过滤
    if start_date:
        stocks = [s for s in stocks if s['buy_date_short'] >= start_date]
    if end_date:
        stocks = [s for s in stocks if s['buy_date_short'] <= end_date]

    # 排序
    reverse = order == 'desc'
    if sort_by == 'return_rate':
        stocks.sort(key=lambda x: x['return_rate'], reverse=reverse)
    elif sort_by == 'first_day_return':
        stocks.sort(key=lambda x: x.get('first_day_return', 0), reverse=reverse)
    elif sort_by == 'second_day_return':
        stocks.sort(key=lambda x: x.get('second_day_return', 0), reverse=reverse)
    elif sort_by == 'third_day_return':
        stocks.sort(key=lambda x: x.get('third_day_return', 0), reverse=reverse)
    elif sort_by == 'fifth_day_return':
        stocks.sort(key=lambda x: x.get('fifth_day_return', 0), reverse=reverse)
    elif sort_by == 'name':
        stocks.sort(key=lambda x: x['name'], reverse=reverse)
    elif sort_by == 'buy_date':
        stocks.sort(key=lambda x: x['buy_date'], reverse=reverse)

    # 分页
    total = len(stocks)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_stocks = stocks[start:end]

    return jsonify({
        'current_source': source['name'] if source else 'unknown',
        'stocks': paginated_stocks,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': (total + page_size - 1) // page_size
        }
    })


@app.route('/api/stocks/<code>', methods=['GET'])
def get_stock_detail(code):
    """获取单只股票详情"""
    source, data = load_data_source()
    if not data:
        return jsonify({'error': 'No data available'}), 404

    stock = next((s for s in data['stocks'] if s['code'] == code), None)

    if stock:
        return jsonify({
            'current_source': source['name'] if source else 'unknown',
            'stock': stock
        })
    else:
        return jsonify({'error': 'Stock not found'}), 404


@app.route('/api/stocks/<code>/returns', methods=['GET'])
def get_stock_returns(code):
    """获取股票收益率曲线"""
    source, data = load_data_source()
    if not data:
        return jsonify({'error': 'No data available'}), 404

    stock = next((s for s in data['stocks'] if s['code'] == code), None)

    if stock:
        return jsonify({
            'current_source': source['name'] if source else 'unknown',
            'code': stock['code'],
            'name': stock['name'],
            'buy_date': stock['buy_date'],
            'buy_price': stock['buy_price'],
            'time_series': stock['time_series']
        })
    else:
        return jsonify({'error': 'Stock not found'}), 404


@app.route('/api/top', methods=['GET'])
def get_top_stocks():
    """获取表现最好/最差的股票"""
    source, data = load_data_source()
    if not data:
        return jsonify({'error': 'No data available'}), 404

    stocks = data['stocks']

    limit = int(request.args.get('limit', 10))
    sort_by = request.args.get('sort_by', 'return_rate')
    order = request.args.get('order', 'desc')

    # 排序
    reverse = order == 'desc'
    stocks.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

    return jsonify({
        'current_source': source['name'] if source else 'unknown',
        'stocks': stocks[:limit]
    })


if __name__ == '__main__':
    print("启动 Flask API 服务器（支持多数据源）...")
    print("API 端点:")
    print("  GET /api/health - 健康检查")
    print("  GET /api/sources - 获取所有数据源")
    print("  POST /api/switch-source - 切换数据源")
    print("  GET /api/stats - 获取统计数据")
    print("  GET /api/stocks - 股票列表")
    print("  GET /api/stocks/<code> - 股票详情")
    print("  GET /api/stocks/<code>/returns - 收益率曲线")
    print("  GET /api/top - 表现最好/最差的股票")
    print("\n服务器运行在: http://localhost:8007")
    app.run(debug=True, host='0.0.0.0', port=8007)
