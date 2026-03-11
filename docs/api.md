# API 文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **CORS**: 已启用，支持跨域请求

## 接口列表

### 1. 健康检查

检查 API 服务是否正常运行。

**请求**
```http
GET /api/health
```

**响应**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

**状态码**
- 200 OK

---

### 2. 获取统计数据

获取整体统计信息，包括总股票数、平均收益率、最高/最低收益率等。

**请求**
```http
GET /api/stats
```

**响应示例**
```json
{
  "total_stocks": 232,
  "with_data": 232,
  "without_data": 0,
  "avg_return": 13.94,
  "max_return": 201.39,
  "min_return": -28.24,
  "best_stock": "迈为股份(300751)",
  "worst_stock": "珠海冠宇(688772)",
  "positive_count": 148,
  "negative_count": 84,
  "win_rate": 63.79
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| total_stocks | number | 总股票数 |
| with_data | number | 有K线数据的股票数 |
| without_data | number | 无K线数据的股票数 |
| avg_return | number | 平均收益率（%） |
| max_return | number | 最高收益率（%） |
| min_return | number | 最低收益率（%） |
| best_stock | string | 表现最好的股票 |
| worst_stock | string | 表现最差的股票 |
| positive_count | number | 盈利股票数 |
| negative_count | number | 亏损股票数 |
| win_rate | number | 胜率（%） |

**状态码**
- 200 OK

---

### 3. 获取股票列表

获取股票列表，支持分页、排序和搜索。

**请求**
```http
GET /api/stocks?page=1&page_size=50&sort_by=return_rate&order=desc&search=迈为
```

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | number | 否 | 1 | 页码 |
| page_size | number | 否 | 50 | 每页数量 |
| sort_by | string | 否 | return_rate | 排序字段：return_rate, name, buy_date |
| order | string | 否 | desc | 排序方向：asc, desc |
| search | string | 否 | - | 搜索关键词（股票名称或代码） |

**响应示例**
```json
{
  "stocks": [
    {
      "name": "迈为股份",
      "code": "300751",
      "buy_date": "2025-12-18 14:46",
      "buy_price": 157.51,
      "latest_price": 474.95,
      "return_rate": 201.39,
      "max_return": 201.39,
      "min_return": -2.85,
      "data_points": 30
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 232,
    "total_pages": 5
  }
}
```

**字段说明**

**stocks 数组**

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 股票名称 |
| code | string | 股票代码 |
| buy_date | string | 买入日期时间 |
| buy_price | number | 买入价格 |
| latest_price | number | 最新价格 |
| return_rate | number | 当前收益率（%） |
| max_return | number | 最高收益率（%） |
| min_return | number | 最低收益率（%） |
| data_points | number | 数据点数量 |

**pagination 对象**

| 字段 | 类型 | 说明 |
|------|------|------|
| page | number | 当前页码 |
| page_size | number | 每页数量 |
| total | number | 总记录数 |
| total_pages | number | 总页数 |

**状态码**
- 200 OK

---

### 4. 获取股票详情

获取单只股票的完整信息，包括时间序列数据。

**请求**
```http
GET /api/stocks/:code
```

**URL 参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码（如：300751） |

**响应示例**
```json
{
  "name": "迈为股份",
  "code": "300751",
  "buy_date": "2025-12-18 14:46",
  "buy_price": 157.51,
  "latest_price": 474.95,
  "return_rate": 201.39,
  "max_return": 201.39,
  "min_return": -2.85,
  "data_points": 30,
  "time_series": [
    {
      "date": "2025-12-18",
      "price": 157.51,
      "return_rate": 0.0
    },
    {
      "date": "2025-12-19",
      "price": 162.3,
      "return_rate": 3.04
    }
  ]
}
```

**字段说明**

**time_series 数组**

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期 |
| price | number | 收盘价 |
| return_rate | number | 当日收益率（%） |

**状态码**
- 200 OK
- 404 Not Found（股票不存在）

**错误响应**
```json
{
  "error": "Stock not found"
}
```

---

### 5. 获取股票收益率曲线

获取单只股票的收益率时间序列数据，用于绘制曲线图。

**请求**
```http
GET /api/stocks/:code/returns
```

**URL 参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码（如：300751） |

**响应示例**
```json
{
  "code": "300751",
  "name": "迈为股份",
  "buy_date": "2025-12-18 14:46",
  "buy_price": 157.51,
  "time_series": [
    {
      "date": "2025-12-18",
      "price": 157.51,
      "return_rate": 0.0
    },
    {
      "date": "2025-12-19",
      "price": 162.3,
      "return_rate": 3.04
    }
  ]
}
```

**状态码**
- 200 OK
- 404 Not Found（股票不存在）

---

### 6. 获取 Top 榜单

获取表现最好或最差的股票榜单。

**请求**
```http
GET /api/top?limit=10&sort_by=return_rate&order=desc
```

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | number | 否 | 10 | 返回数量 |
| sort_by | string | 否 | return_rate | 排序字段：return_rate, max_return, min_return |
| order | string | 否 | desc | 排序方向：asc, desc |

**响应示例**
```json
[
  {
    "name": "迈为股份",
    "code": "300751",
    "buy_date": "2025-12-18 14:46",
    "buy_price": 157.51,
    "latest_price": 474.95,
    "return_rate": 201.39,
    "max_return": 201.39,
    "min_return": -2.85,
    "data_points": 30
  }
]
```

**状态码**
- 200 OK

---

## 错误处理

所有错误响应格式：

```json
{
  "error": "错误信息描述"
}
```

**常见错误**

| 状态码 | 错误信息 | 说明 |
|--------|----------|------|
| 404 | Stock not found | 股票不存在 |
| 500 | Internal server error | 服务器内部错误 |

---

## 使用示例

### JavaScript (Axios)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// 获取统计数据
const stats = await axios.get(`${API_BASE_URL}/stats`);

// 获取股票列表（第2页，按收益率降序）
const stocks = await axios.get(`${API_BASE_URL}/stocks`, {
  params: {
    page: 2,
    sort_by: 'return_rate',
    order: 'desc'
  }
});

// 获取股票详情
const detail = await axios.get(`${API_BASE_URL}/stocks/300751`);

// 搜索股票
const results = await axios.get(`${API_BASE_URL}/stocks`, {
  params: { search: '迈为' }
});

// 获取 Top 10
const top10 = await axios.get(`${API_BASE_URL}/top`, {
  params: { limit: 10, order: 'desc' }
});
```

### cURL

```bash
# 健康检查
curl http://localhost:5000/api/health

# 获取统计数据
curl http://localhost:5000/api/stats

# 获取股票列表
curl "http://localhost:5000/api/stocks?page=1&page_size=10"

# 获取股票详情
curl http://localhost:5000/api/stocks/300751

# 搜索股票
curl "http://localhost:5000/api/stocks?search=迈为"

# 获取 Top 10
curl "http://localhost:5000/api/top?limit=10&order=desc"
```

### Python (requests)

```python
import requests

API_BASE_URL = 'http://localhost:5000/api'

# 获取统计数据
stats = requests.get(f'{API_BASE_URL}/stats').json()

# 获取股票列表
stocks = requests.get(f'{API_BASE_URL}/stocks', params={
    'page': 1,
    'sort_by': 'return_rate',
    'order': 'desc'
}).json()

# 获取股票详情
detail = requests.get(f'{API_BASE_URL}/stocks/300751').json()
```

---

## 性能考虑

### 响应时间

- `/health`: < 10ms
- `/stats`: < 50ms
- `/stocks`: < 100ms (50条记录)
- `/stocks/:code`: < 50ms
- `/top`: < 100ms (10条记录)

### 优化建议

1. **分页查询**：建议每页不超过100条记录
2. **缓存**：统计数据可以缓存5分钟
3. **压缩**：生产环境启用 gzip 压缩

---

## 版本历史

### v1.0.0 (2026-01-31)

初始版本，包含以下功能：
- 健康检查
- 统计数据
- 股票列表（分页、排序、搜索）
- 股票详情
- 收益率曲线
- Top榜单

---

## 变更日志

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-01-31 | 1.0.0 | 初始版本 |
