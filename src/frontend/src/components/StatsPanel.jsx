/**
 * 统计面板组件
 */

function StatsPanel({ stats }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="text-sm text-gray-600 mb-1">总股票数</div>
        <div className="text-2xl font-bold text-gray-800">{stats.total_stocks}</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="text-sm text-gray-600 mb-1">有数据</div>
        <div className="text-2xl font-bold text-green-600">{stats.with_data}</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="text-sm text-gray-600 mb-1">平均收益率</div>
        <div className={`text-2xl font-bold ${stats.avg_return >= 0 ? 'text-red-600' : 'text-green-600'}`}>
          {stats.avg_return >= 0 ? '+' : ''}{stats.avg_return}%
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="text-sm text-gray-600 mb-1">最高收益率</div>
        <div className="text-2xl font-bold text-red-600">+{stats.max_return}%</div>
        <div className="text-xs text-gray-500 truncate">{stats.best_stock}</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="text-sm text-gray-600 mb-1">最低收益率</div>
        <div className="text-2xl font-bold text-green-600">{stats.min_return}%</div>
        <div className="text-xs text-gray-500 truncate">{stats.worst_stock}</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="text-sm text-gray-600 mb-1">胜率</div>
        <div className="text-2xl font-bold text-blue-600">{stats.win_rate}%</div>
        <div className="text-xs text-gray-500">
          {stats.positive_count}赚 / {stats.negative_count}亏
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;
