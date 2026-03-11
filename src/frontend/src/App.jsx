import { useState, useEffect } from 'react';
import { api } from './api';
import StockList from './components/StockList';
import StatsPanel from './components/StatsPanel';
import SummaryPanel from './components/SummaryPanel';
import ReturnChart from './components/ReturnChart';
import KlineChart from './components/KlineChart';
import DataSourceSelector from './components/DataSourceSelector';
import './App.css';

function App() {
  const [stats, setStats] = useState(null);
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('return'); // 'return' or 'kline'
  const [currentSource, setCurrentSource] = useState('weipan');

  // 状态管理
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [sortBy, setSortBy] = useState('return_rate');
  const [order, setOrder] = useState('desc');
  const [search, setSearch] = useState('');
  const [totalPages, setTotalPages] = useState(1);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // 列显示控制
  const [showFirstDay, setShowFirstDay] = useState(true);
  const [showSecondDay, setShowSecondDay] = useState(true);
  const [showThirdDay, setShowThirdDay] = useState(true);
  const [showFifthDay, setShowFifthDay] = useState(true);

  // 计算是否有筛选条件
  const isFiltered = search || minPrice || maxPrice || startDate || endDate;

  // 初始化时获取当前数据源
  useEffect(() => {
    const initSource = async () => {
      try {
        const data = await api.getDataSources();
        if (data.current_source) {
          setCurrentSource(data.current_source);
        }
      } catch (err) {
        console.error('Failed to get current source:', err);
      }
    };
    initSource();
  }, []);

  // 加载统计数据
  useEffect(() => {
    const loadStats = async () => {
      try {
        const params = {};

        // 添加筛选参数
        if (search) params.search = search;
        if (minPrice) params.min_price = parseFloat(minPrice);
        if (maxPrice) params.max_price = parseFloat(maxPrice);
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const data = await api.getStats(params);
        setStats(data);
      } catch (err) {
        setError('加载统计数据失败: ' + err.message);
      }
    };
    loadStats();
  }, [currentSource, search, minPrice, maxPrice, startDate, endDate]);

  // 加载股票列表
  useEffect(() => {
    const loadStocks = async () => {
      setLoading(true);
      try {
        const params = {
          page,
          page_size: pageSize,
          sort_by: sortBy,
          order,
          search
        };

        // 添加价格区间参数
        if (minPrice) params.min_price = parseFloat(minPrice);
        if (maxPrice) params.max_price = parseFloat(maxPrice);

        // 添加日期区间参数
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const data = await api.getStocks(params);
        setStocks(data.stocks);
        setTotalPages(data.pagination.total_pages);
      } catch (err) {
        setError('加载股票列表失败: ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    loadStocks();
  }, [page, pageSize, sortBy, order, search, minPrice, maxPrice, startDate, endDate, currentSource]);

  // 选择股票
  const handleSelectStock = async (stock) => {
    setSelectedStock(stock);
  };

  // 切换数据源
  const handleSourceChange = (sourceName) => {
    setCurrentSource(sourceName);
    setPage(1);
    setSelectedStock(null);
    setMinPrice('');
    setMaxPrice('');
    setStartDate('');
    setEndDate('');
  };

  // 排序处理
  const handleSort = (field) => {
    if (sortBy === field) {
      setOrder(order === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setOrder('desc');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 头部 */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold mb-2">📈 股票收益率可视化</h1>
              <p className="text-blue-100">基于选股数据的收益率分析系统</p>
            </div>
            <DataSourceSelector
              currentSource={currentSource}
              onSourceChange={handleSourceChange}
            />
          </div>
        </div>
      </header>

      {/* 主内容 */}
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* 统计面板 */}
        {stats && <StatsPanel stats={stats} />}

        {/* 数据汇总面板 - 分日平均收益率 */}
        {stats && <SummaryPanel stats={stats} filtered={isFiltered} />}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 股票列表 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">股票列表</h2>
                <input
                  type="text"
                  placeholder="搜索股票名称或代码..."
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setPage(1);
                  }}
                />
              </div>

              {/* 价格区间筛选 */}
              <div className="mb-3 pb-3 border-b border-gray-200">
                <div className="text-xs text-gray-500 mb-2">买入价格区间（元）:</div>
                <div className="flex gap-4 items-center flex-wrap">
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-700">最低价:</label>
                    <input
                      type="number"
                      placeholder="不限"
                      className="w-24 px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      value={minPrice}
                      onChange={(e) => {
                        setMinPrice(e.target.value);
                        setPage(1);
                      }}
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-700">最高价:</label>
                    <input
                      type="number"
                      placeholder="不限"
                      className="w-24 px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      value={maxPrice}
                      onChange={(e) => {
                        setMaxPrice(e.target.value);
                        setPage(1);
                      }}
                    />
                  </div>
                  {(minPrice || maxPrice) && (
                    <button
                      onClick={() => {
                        setMinPrice('');
                        setMaxPrice('');
                        setPage(1);
                      }}
                      className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300 transition-colors"
                    >
                      清除价格筛选
                    </button>
                  )}
                </div>
              </div>

              {/* 日期区间筛选 */}
              <div className="mb-3 pb-3 border-b border-gray-200">
                <div className="text-xs text-gray-500 mb-2">买入日期区间:</div>
                <div className="flex gap-4 items-center flex-wrap">
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-700">开始日期:</label>
                    <input
                      type="date"
                      className="px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      value={startDate}
                      onChange={(e) => {
                        setStartDate(e.target.value);
                        setPage(1);
                      }}
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-700">结束日期:</label>
                    <input
                      type="date"
                      className="px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      value={endDate}
                      onChange={(e) => {
                        setEndDate(e.target.value);
                        setPage(1);
                      }}
                    />
                  </div>
                  {(startDate || endDate) && (
                    <button
                      onClick={() => {
                        setStartDate('');
                        setEndDate('');
                        setPage(1);
                      }}
                      className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300 transition-colors"
                    >
                      清除日期筛选
                    </button>
                  )}
                </div>
              </div>

              {/* 列显示控制 */}
              <div className="mb-3 pb-3 border-b border-gray-200">
                <div className="text-xs text-gray-500 mb-2">显示列:</div>
                <div className="flex gap-4 flex-wrap">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showFirstDay}
                      onChange={(e) => setShowFirstDay(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">1日</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showSecondDay}
                      onChange={(e) => setShowSecondDay(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">2日</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showThirdDay}
                      onChange={(e) => setShowThirdDay(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">3日</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showFifthDay}
                      onChange={(e) => setShowFifthDay(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">5日</span>
                  </label>
                </div>
              </div>

              {/* 排序控制 */}
              <div className="mb-4">
                <div className="text-xs text-gray-500 mb-2">按收益率排序:</div>
                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={() => handleSort('return_rate')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'return_rate'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    总收益 {sortBy === 'return_rate' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                  <button
                    onClick={() => handleSort('first_day_return')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'first_day_return'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    1日 {sortBy === 'first_day_return' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                  <button
                    onClick={() => handleSort('second_day_return')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'second_day_return'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    2日 {sortBy === 'second_day_return' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                  <button
                    onClick={() => handleSort('third_day_return')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'third_day_return'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    3日 {sortBy === 'third_day_return' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                  <button
                    onClick={() => handleSort('fifth_day_return')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'fifth_day_return'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    5日 {sortBy === 'fifth_day_return' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                  <button
                    onClick={() => handleSort('name')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'name'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    名称 {sortBy === 'name' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                  <button
                    onClick={() => handleSort('buy_date')}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      sortBy === 'buy_date'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    日期 {sortBy === 'buy_date' && (order === 'desc' ? '↓' : '↑')}
                  </button>
                </div>
              </div>

              {loading ? (
                <div className="text-center py-12 text-gray-500">加载中...</div>
              ) : (
                <StockList
                  stocks={stocks}
                  onSelectStock={handleSelectStock}
                  selectedStock={selectedStock}
                  showFirstDay={showFirstDay}
                  showSecondDay={showSecondDay}
                  showThirdDay={showThirdDay}
                  showFifthDay={showFifthDay}
                />
              )}

              {/* 分页控制 */}
              <div className="flex justify-center items-center gap-2 mt-6">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600"
                >
                  上一页
                </button>
                <span className="text-gray-700">
                  第 {page} / {totalPages} 页
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>

          {/* 图表区域 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">图表</h2>

                {/* 图表类型切换 */}
                {selectedStock && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setChartType('return')}
                      className={`px-3 py-1 text-sm rounded-lg ${
                        chartType === 'return'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      收益率
                    </button>
                    <button
                      onClick={() => setChartType('kline')}
                      className={`px-3 py-1 text-sm rounded-lg ${
                        chartType === 'kline'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      K线图
                    </button>
                  </div>
                )}
              </div>

              {selectedStock ? (
                chartType === 'return' ? (
                  <ReturnChart stock={selectedStock} />
                ) : (
                  <KlineChart stock={selectedStock} />
                )
              ) : (
                <div className="text-center py-12 text-gray-500">
                  请从左侧选择一只股票查看图表
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* 页脚 */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-400">
          <p>股票数据可视化系统 - 数据来源：data/weipan</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
