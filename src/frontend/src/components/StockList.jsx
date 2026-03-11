/**
 * 股票列表组件
 */

function StockList({ stocks, onSelectStock, selectedStock, showFirstDay, showSecondDay, showThirdDay, showFifthDay }) {
  if (stocks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        没有找到匹配的股票
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1200px]">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-3 text-gray-600 font-semibold text-sm">代码</th>
            <th className="text-left py-3 px-3 text-gray-600 font-semibold text-sm">名称</th>
            <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">买入价</th>
            <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">现价</th>
            <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">收益率</th>
            {showFirstDay && <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">1日</th>}
            {showSecondDay && <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">2日</th>}
            {showThirdDay && <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">3日</th>}
            {showFifthDay && <th className="text-right py-3 px-3 text-gray-600 font-semibold text-sm">5日</th>}
            <th className="text-left py-3 px-3 text-gray-600 font-semibold text-sm">买入日期</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr
              key={stock.code}
              onClick={() => onSelectStock(stock)}
              className={`border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors ${
                selectedStock?.code === stock.code ? 'bg-blue-100' : ''
              }`}
            >
              <td className="py-3 px-3 text-gray-800 text-sm">{stock.code}</td>
              <td className="py-3 px-3 text-gray-800 font-medium text-sm">{stock.name}</td>
              <td className="py-3 px-3 text-right text-gray-600 text-sm">¥{stock.buy_price.toFixed(2)}</td>
              <td className="py-3 px-3 text-right text-gray-800 text-sm">¥{stock.latest_price.toFixed(2)}</td>
              <td className={`py-3 px-3 text-right font-semibold text-sm ${
                stock.return_rate >= 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {stock.return_rate >= 0 ? '+' : ''}{stock.return_rate.toFixed(2)}%
              </td>
              {showFirstDay && (
                <td className={`py-3 px-3 text-right font-semibold text-sm ${
                  stock.first_day_return >= 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {stock.first_day_return >= 0 ? '+' : ''}{stock.first_day_return.toFixed(2)}%
                </td>
              )}
              {showSecondDay && (
                <td className={`py-3 px-3 text-right font-semibold text-sm ${
                  stock.second_day_return >= 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {stock.second_day_return >= 0 ? '+' : ''}{stock.second_day_return.toFixed(2)}%
                </td>
              )}
              {showThirdDay && (
                <td className={`py-3 px-3 text-right font-semibold text-sm ${
                  stock.third_day_return >= 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {stock.third_day_return >= 0 ? '+' : ''}{stock.third_day_return.toFixed(2)}%
                </td>
              )}
              {showFifthDay && (
                <td className={`py-3 px-3 text-right font-semibold text-sm ${
                  stock.fifth_day_return >= 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {stock.fifth_day_return >= 0 ? '+' : ''}{stock.fifth_day_return.toFixed(2)}%
                </td>
              )}
              <td className="py-3 px-3 text-gray-600 text-xs">{stock.buy_date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default StockList;
