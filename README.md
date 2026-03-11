# 股票收益率可视化系统

这是一个基于 React + Vite + Flask 的股票数据可视化系统，用于展示从选股买入时间点后的收益率情况。

## 功能特性

- 📊 **收益率可视化**：展示每只股票从买入时间点后的收益率曲线
- 📈 **交互式图表**：使用 ECharts 提供强大的数据可视化
- 🔍 **搜索筛选**：支持按股票名称、代码搜索，支持多种排序方式
- 📱 **响应式设计**：适配桌面和移动设备
- 🎯 **统计面板**：展示整体统计数据（平均收益、最高/最低收益、胜率等）

## 技术栈

### 前端
- React 18
- Vite 6
- ECharts (echarts-for-react)
- Tailwind CSS
- Axios

### 后端
- Python Flask
- Flask-CORS
- Pandas
- SQLite

## 项目结构

```
shareKLine/
├── data/
│   └── weipan/
│       ├── 数据汇总.csv          # 选股数据
│       └── stock_data.db         # K线数据
├── docs/                         # 文档目录
├── scripts/
│   └── process_data.py           # 数据处理脚本
├── src/
│   ├── backend/
│   │   ├── app.py               # Flask API 服务器
│   │   ├── start.sh             # 启动脚本
│   │   └── data/
│   │       └── stock_returns.json  # 处理后的数据
│   └── frontend/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.js
│       ├── tailwind.config.js
│       ├── src/
│       │   ├── main.jsx
│       │   ├── App.jsx
│       │   ├── App.css
│       │   ├── api.js           # API 客户端
│       │   ├── index.css
│       │   └── components/
│       │       ├── StatsPanel.jsx    # 统计面板
│       │       ├── StockList.jsx     # 股票列表
│       │       └── ReturnChart.jsx   # 收益率图表
│       └── public/
├── venv/                         # Python 虚拟环境
├── task_plan.md                  # 项目计划
├── findings.md                   # 研究发现
└── progress.md                   # 进度日志
```

## 快速开始

### 1. 环境准备

确保已安装：
- Node.js 18+
- Python 3.8+

### 2. 安装依赖

```bash
# 安装 Python 依赖
source venv/bin/activate
pip install flask flask-cors pandas

# 安装前端依赖
cd src/frontend
npm install
```

### 3. 数据处理

```bash
# 处理数据并生成 JSON
source venv/bin/activate
python scripts/process_data.py
```

### 4. 启动服务

**终端 1 - 启动后端 API：**
```bash
source venv/bin/activate
python src/backend/app.py
```

**终端 2 - 启动前端开发服务器：**
```bash
cd src/frontend
npm run dev
```

### 5. 访问应用

打开浏览器访问：http://localhost:5173

## API 接口

### 基础 URL
```
http://localhost:5000/api
```

### 可用接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /stats | 获取统计数据 |
| GET | /stocks | 获取股票列表（支持分页、排序、搜索） |
| GET | /stocks/:code | 获取单只股票详情 |
| GET | /stocks/:code/returns | 获取股票收益率曲线 |
| GET | /top | 获取表现最好/最差的股票 |

### 查询参数

**stocks 接口：**
- `page`: 页码（默认：1）
- `page_size`: 每页数量（默认：50）
- `sort_by`: 排序字段（return_rate, name, buy_date）
- `order`: 排序方向（asc, desc）
- `search`: 搜索关键词（股票名称或代码）

**top 接口：**
- `limit`: 返回数量（默认：10）
- `sort_by`: 排序字段
- `order`: 排序方向

## 数据说明

### 输入数据

**数据汇总.csv：**
- 列名：名称、代码、入选日期+时间、入选价格
- 包含选股时间和买入价格信息

**stock_data.db：**
- 表：stock_daily, stock_weekly, minute_kline 等
- 包含 OHLC 价格数据和技术指标

### 输出数据

**stock_returns.json：**
```json
{
  "stats": {
    "total_stocks": 232,
    "with_data": 232,
    "avg_return": 13.94,
    "max_return": 201.39,
    "min_return": -28.24,
    "win_rate": 63.79
  },
  "stocks": [
    {
      "name": "股票名称",
      "code": "股票代码",
      "buy_date": "买入日期",
      "buy_price": 买入价格,
      "latest_price": 最新价格,
      "return_rate": 收益率,
      "max_return": 最高收益率,
      "min_return": 最低收益率,
      "time_series": [
        {
          "date": "日期",
          "price": 价格,
          "return_rate": 收益率
        }
      ]
    }
  ]
}
```

## 开发说明

### 修改 API 地址

编辑 `src/frontend/src/api.js`，修改 `API_BASE_URL`：

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### 构建生产版本

```bash
cd src/frontend
npm run build
```

构建产物在 `src/frontend/dist` 目录。

## 数据统计

当前数据概况：
- 总股票数：232 只
- 平均收益率：13.94%
- 最高收益率：201.39%（迈为股份 300751）
- 最低收益率：-28.24%（珠海冠宇 688772）
- 胜率：63.79%

## 故障排除

### 后端无法启动
- 检查 Python 虚拟环境是否激活
- 确认依赖已正确安装
- 检查端口 5000 是否被占用

### 前端无法连接后端
- 确认后端服务已启动
- 检查 API 地址配置是否正确
- 查看浏览器控制台错误信息

### 数据处理失败
- 确认 data/weipan/ 目录下有数据文件
- 检查数据库文件是否完整
- 查看错误日志了解详情

## 许可证

MIT

## 作者

Created with Claude Code
