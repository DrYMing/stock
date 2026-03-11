import { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';

/**
 * K线图组件
 * 支持时间区间选择、时间粒度切换、买入点标记
 */

function KlineChart({ stock }) {
  const [timeRange, setTimeRange] = useState('1M'); // 1W, 1M, 3M, ALL
  const [granularity, setGranularity] = useState('daily'); // minute, daily, weekly

  if (!stock) return null;

  // 根据粒度选择数据源
  const getDataByGranularity = () => {
    switch (granularity) {
      case 'weekly':
        return stock.weekly_series || [];
      case 'minute':
        return stock.minute_series || [];
      case 'daily':
      default:
        return stock.time_series || [];
    }
  };

  // 获取时间序列数据
  const allData = getDataByGranularity();

  // 根据时间范围过滤数据
  const getFilteredData = () => {
    if (!allData || allData.length === 0) return [];

    const buyDate = new Date(stock.buy_date_short || stock.buy_date.split(' ')[0]);

    // ALL：显示所有数据
    if (timeRange === 'ALL') {
      return allData.filter(d => new Date(d.date) >= buyDate);
    }

    // 计算结束日期
    let endDate;
    switch (timeRange) {
      case '1W':
        endDate = new Date(buyDate.getTime() + 7 * 24 * 60 * 60 * 1000);
        break;
      case '1M':
        endDate = new Date(buyDate.getTime() + 30 * 24 * 60 * 60 * 1000);
        break;
      case '3M':
        endDate = new Date(buyDate.getTime() + 90 * 24 * 60 * 60 * 1000);
        break;
      default:
        return allData.filter(d => new Date(d.date) >= buyDate);
    }

    // 过滤数据：从买入日到结束日期
    return allData.filter(d => {
      const date = new Date(d.date);
      return date >= buyDate && date <= endDate;
    });
  };

  const filteredData = getFilteredData();

  // 查找买入点索引
  const buyDateStr = stock.buy_date_short || stock.buy_date.split(' ')[0];
  const buyIndex = filteredData.findIndex(d => d.date === buyDateStr);

  // 准备K线数据
  const dates = filteredData.map(d => d.date);
  const klineData = filteredData.map(d => [d.open, d.close, d.low, d.high]);
  const volumes = filteredData.map(d => d.volume);

  // 准备标记点数据
  const markPointData = [];
  if (buyIndex >= 0) {
    markPointData.push({
      name: '买入点',
      coord: [buyIndex, filteredData[buyIndex].close],
      value: '买入',
      itemStyle: {
        color: '#ef4444'
      },
      symbol: 'arrow',
      symbolSize: 20,
      label: {
        show: true,
        position: 'top',
        formatter: '买入: ¥' + filteredData[buyIndex].close.toFixed(2)
      }
    });
  }

  // ECharts 配置
  const option = {
    animation: false,
    legend: {
      data: ['K线', '成交量'],
      top: 10
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function (params) {
        const kline = params[0];
        const volume = params[1];

        let result = kline.axisValue + '<br/>';
        result += `开盘: ¥${kline.data[1]}<br/>`;
        result += `收盘: ¥${kline.data[2]}<br/>`;
        result += `最低: ¥${kline.data[3]}<br/>`;
        result += `最高: ¥${kline.data[4]}<br/>`;
        if (volume) {
          result += `成交量: ${(volume.data / 10000).toFixed(2)}万`;
        }
        result += `<br/>收益率: ${((kline.data[2] - stock.buy_price) / stock.buy_price * 100).toFixed(2)}%`;

        return result;
      }
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        top: '15%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '70%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        },
        axisLabel: {
          formatter: '¥{value}'
        },
        splitLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        itemStyle: {
          color: '#ef4444',           // 阳线颜色（涨）
          color0: '#10b981',          // 阴线颜色（跌）
          borderColor: '#ef4444',     // 阳线边框
          borderColor0: '#10b981'     // 阴线边框
        },
        markPoint: {
          data: markPointData
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: function (params) {
            const dataIndex = params.dataIndex;
            if (dataIndex === 0) return '#3b82f6';
            return klineData[dataIndex][1] > klineData[dataIndex][0] ? '#ef4444' : '#10b981';
          }
        }
      }
    ]
  };

  return (
    <div>
      {/* 控制面板 */}
      <div className="mb-4 flex flex-wrap gap-2">
        {/* 时间区间选择 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">区间:</span>
          <button
            onClick={() => setTimeRange('1W')}
            className={`px-3 py-1 text-sm rounded-lg ${
              timeRange === '1W'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            1周
          </button>
          <button
            onClick={() => setTimeRange('1M')}
            className={`px-3 py-1 text-sm rounded-lg ${
              timeRange === '1M'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            1月
          </button>
          <button
            onClick={() => setTimeRange('3M')}
            className={`px-3 py-1 text-sm rounded-lg ${
              timeRange === '3M'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            3月
          </button>
          <button
            onClick={() => setTimeRange('ALL')}
            className={`px-3 py-1 text-sm rounded-lg ${
              timeRange === 'ALL'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            全部
          </button>
        </div>

        {/* 时间粒度选择 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">粒度:</span>
          <button
            onClick={() => setGranularity('daily')}
            className={`px-3 py-1 text-sm rounded-lg ${
              granularity === 'daily'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            日线
          </button>
          <button
            onClick={() => setGranularity('weekly')}
            disabled={!stock.weekly_series || stock.weekly_series.length === 0}
            className={`px-3 py-1 text-sm rounded-lg ${
              granularity === 'weekly'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } ${!stock.weekly_series || stock.weekly_series.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            周线
          </button>
          <button
            onClick={() => setGranularity('minute')}
            disabled={!stock.minute_series || stock.minute_series.length === 0}
            className={`px-3 py-1 text-sm rounded-lg ${
              granularity === 'minute'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } ${!stock.minute_series || stock.minute_series.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
            title={(!stock.minute_series || stock.minute_series.length === 0) ? "暂无分钟线数据" : ""}
          >
            分钟线
          </button>
        </div>
      </div>

      {/* K线图 */}
      <ReactECharts
        key={`${timeRange}-${granularity}`}  // 添加粒度到key以强制重新渲染
        option={option}
        style={{ height: '450px' }}
        notMerge={true}
        lazyUpdate={false}  // 改为false以立即更新
      />

      {/* 图例说明 */}
      <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500"></div>
          <span>阳线（上涨）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500"></div>
          <span>阴线（下跌）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 transform rotate-45"></div>
          <span>买入点</span>
        </div>
      </div>

      {/* 数据统计 */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-blue-800 font-medium">买入价格</div>
          <div className="text-xl font-bold text-blue-600">¥{stock.buy_price.toFixed(2)}</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-gray-800 font-medium">当前价格</div>
          <div className="text-xl font-bold text-gray-800">
            ¥{stock.latest_price.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
}

export default KlineChart;
