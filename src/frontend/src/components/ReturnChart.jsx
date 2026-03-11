import { useEffect, useRef } from 'react';
import ReactECharts from 'echarts-for-react';

/**
 * 收益率图表组件
 */

function ReturnChart({ stock }) {
  const chartRef = useRef(null);

  if (!stock) return null;

  // 准备图表数据
  const dates = stock.time_series?.map(d => d.date) || [];
  const returns = stock.time_series?.map(d => d.return_rate) || [];
  const prices = stock.time_series?.map(d => d.price) || [];

  // 图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>';
        params.forEach(param => {
          result += `${param.marker} ${param.seriesName}: ${param.value}%<br/>`;
        });
        return result;
      }
    },
    legend: {
      data: ['收益率']
    },
    grid: [
      {
        left: '10%',
        right: '10%',
        top: '15%',
        height: '50%'
      }
    ],
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { onZero: false },
      splitLine: { show: false },
      min: 'dataMin',
      max: 'dataMax',
      axisPointer: {
        z: 100
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitArea: {
        show: true
      },
      axisLabel: {
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      }
    },
    series: [
      {
        name: '收益率',
        type: 'line',
        data: returns,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#3b82f6'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(59, 130, 246, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(59, 130, 246, 0.05)'
              }
            ]
          }
        },
        markLine: {
          symbol: ['none', 'none'],
          data: [
            { yAxis: 0, lineStyle: { color: '#ef4444', type: 'solid' } }
          ]
        }
      }
    ]
  };

  return (
    <div>
      {/* 股票信息 */}
      <div className="mb-4 pb-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">{stock.name}</h3>
        <div className="text-sm text-gray-600 mb-2">代码: {stock.code}</div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-600">买入价:</span>
            <span className="ml-2 font-medium">¥{stock.buy_price.toFixed(2)}</span>
          </div>
          <div>
            <span className="text-gray-600">现价:</span>
            <span className="ml-2 font-medium">¥{stock.latest_price.toFixed(2)}</span>
          </div>
          <div>
            <span className="text-gray-600">收益率:</span>
            <span className={`ml-2 font-semibold ${stock.return_rate >= 0 ? 'text-red-600' : 'text-green-600'}`}>
              {stock.return_rate >= 0 ? '+' : ''}{stock.return_rate.toFixed(2)}%
            </span>
          </div>
          <div>
            <span className="text-gray-600">买入日期:</span>
            <span className="ml-2">{stock.buy_date.split(' ')[0]}</span>
          </div>
        </div>
      </div>

      {/* ECharts 图表 */}
      <ReactECharts
        ref={chartRef}
        option={option}
        style={{ height: '300px' }}
        notMerge={true}
        lazyUpdate={true}
      />

      {/* 统计信息 */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-red-50 rounded-lg p-3">
          <div className="text-red-800 font-medium">最高收益率</div>
          <div className="text-2xl font-bold text-red-600">+{stock.max_return.toFixed(2)}%</div>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-green-800 font-medium">最低收益率</div>
          <div className="text-2xl font-bold text-green-600">{stock.min_return.toFixed(2)}%</div>
        </div>
      </div>
    </div>
  );
}

export default ReturnChart;
