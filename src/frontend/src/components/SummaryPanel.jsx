/**
 * 数据汇总面板组件 - 显示分日平均收益率和胜率
 */

function SummaryPanel({ stats, filtered }) {
  if (!stats) return null;

  const returnData = [
    {
      label: '总平均收益率',
      value: stats.avg_return,
      color: stats.avg_return >= 0 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '平均1日收益率',
      value: stats.avg_first_day_return,
      color: stats.avg_first_day_return >= 0 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '平均2日收益率',
      value: stats.avg_second_day_return,
      color: stats.avg_second_day_return >= 0 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '平均3日收益率',
      value: stats.avg_third_day_return,
      color: stats.avg_third_day_return >= 0 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '平均5日收益率',
      value: stats.avg_fifth_day_return,
      color: stats.avg_fifth_day_return >= 0 ? 'text-red-600' : 'text-green-600'
    }
  ];

  const winRateData = [
    {
      label: '总胜率',
      value: stats.win_rate,
      color: stats.win_rate >= 50 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '1日胜率',
      value: stats.first_day_win_rate,
      color: stats.first_day_win_rate >= 50 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '2日胜率',
      value: stats.second_day_win_rate,
      color: stats.second_day_win_rate >= 50 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '3日胜率',
      value: stats.third_day_win_rate,
      color: stats.third_day_win_rate >= 50 ? 'text-red-600' : 'text-green-600'
    },
    {
      label: '5日胜率',
      value: stats.fifth_day_win_rate,
      color: stats.fifth_day_win_rate >= 50 ? 'text-red-600' : 'text-green-600'
    }
  ];

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">📊 数据汇总</h3>
        {filtered && (
          <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
            基于筛选结果
          </span>
        )}
      </div>

      {/* 平均收益率 */}
      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2 font-medium">平均收益率</div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {returnData.map((item, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-3 text-center">
              <div className="text-xs text-gray-500 mb-1">{item.label}</div>
              <div className={`text-xl font-bold ${item.color}`}>
                {item.value >= 0 ? '+' : ''}{item.value}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 胜率 */}
      <div>
        <div className="text-sm text-gray-600 mb-2 font-medium">胜率（盈利占比）</div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {winRateData.map((item, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-3 text-center">
              <div className="text-xs text-gray-500 mb-1">{item.label}</div>
              <div className={`text-xl font-bold ${item.color}`}>
                {item.value}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SummaryPanel;
