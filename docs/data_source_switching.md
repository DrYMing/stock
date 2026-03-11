# 数据源切换功能文档

## 功能概述

系统现在支持多个数据源的切换，允许您从不同的CSV文件加载选股数据，同时共享同一个stock_data.db数据库。

## 架构设计

### 数据文件结构

```
src/backend/data/
├── data_sources.json           # 数据源配置文件
├── weipan_stock_returns.json   # 微盘数据源
├── dibu_stock_returns.json     # 底部数据源
└── stock_returns.json          # 旧版数据（兼容保留）
```

### 数据源配置 (data_sources.json)

```json
{
  "sources": [
    {
      "name": "weipan",
      "display_name": "微盘数据",
      "file_path": "data/weipan/数据汇总.csv",
      "data_file": "src/backend/data/weipan_stock_returns.json",
      "stats": {
        "total_stocks": 232,
        "avg_return": 13.72
      }
    },
    {
      "name": "dibu",
      "display_name": "底部数据",
      "file_path": "data/dibu/汇总csv.csv",
      "data_file": "src/backend/data/dibu_stock_returns.json",
      "stats": {
        "total_stocks": 15,
        "avg_return": 8.24
      }
    }
  ],
  "default_source": "weipan"
}
```

## 后端API

### 新增端点

#### 1. 获取所有数据源
```http
GET /api/sources
```

**响应示例：**
```json
{
  "sources": [
    {
      "name": "weipan",
      "display_name": "微盘数据",
      "file_path": "data/weipan/数据汇总.csv",
      "stats": {
        "total_stocks": 232,
        "avg_return": 13.72
      }
    }
  ],
  "current_source": "weipan"
}
```

#### 2. 切换数据源
```http
POST /api/switch-source
Content-Type: application/json

{
  "source_name": "dibu"
}
```

**响应示例：**
```json
{
  "message": "Successfully switched to dibu",
  "source": "dibu",
  "stats": {
    "total_stocks": 15,
    "avg_return": 8.24
  }
}
```

### 更新的端点

所有现有端点现在都在响应中包含 `current_source` 字段：

- `/api/stats` - 返回当前数据源的统计数据
- `/api/stocks` - 返回当前数据源的股票列表
- `/api/stocks/<code>` - 返回当前数据源的股票详情
- `/api/stocks/<code>/returns` - 返回当前数据源的股票收益率曲线
- `/api/top` - 返回当前数据源的排名数据

## 前端组件

### DataSourceSelector 组件

位置: `src/frontend/src/components/DataSourceSelector.jsx`

**功能：**
- 显示当前激活的数据源
- 下拉菜单显示所有可用数据源
- 显示每个数据源的统计信息（股票数量）
- 切换数据源后自动刷新页面

**Props:**
- `currentSource`: 当前数据源名称
- `onSourceChange`: 切换数据源时的回调函数

## 如何添加新数据源

### 步骤 1: 准备CSV文件

将新的CSV文件放入 `data/` 目录下的子文件夹中。

### 步骤 2: 处理数据

使用 `process_data_source.py` 脚本处理新数据源：

```bash
source venv/bin/activate
python scripts/process_data_source.py "data/your_folder/your_file.csv" "your_source_name"
```

**参数说明：**
- 第1个参数: CSV文件的完整路径
- 第2个参数: 数据源名称（英文标识符）

**输出：**
- 生成 `src/backend/data/your_source_name_stock_returns.json`
- 显示处理统计信息

### 步骤 3: 更新配置文件

编辑 `src/backend/data/data_sources.json`，添加新数据源：

```json
{
  "sources": [
    // ... 现有数据源 ...
    {
      "name": "your_source_name",
      "display_name": "您的数据源显示名称",
      "file_path": "data/your_folder/your_file.csv",
      "data_file": "src/backend/data/your_source_name_stock_returns.json",
      "stats": {
        "total_stocks": 股票数量,
        "avg_return": 平均收益率
      }
    }
  ],
  "default_source": "weipan"  // 设置默认数据源
}
```

### 步骤 4: 重启后端服务

```bash
# 停止当前运行的后端
# 然后重新启动
cd src/backend
source ../venv/bin/activate
python app.py
```

### 步骤 5: 刷新前端

刷新浏览器页面，新数据源会自动出现在数据源选择器中。

## 数据处理脚本

### process_data_source.py

功能：处理单个数据源并生成JSON数据文件

**使用方法：**

```bash
# 处理单个文件
python scripts/process_data_source.py <csv_file_path> <source_name>

# 扫描并处理data目录下所有CSV文件
python scripts/process_data_source.py
```

**处理逻辑：**
1. 读取CSV文件中的选股数据
2. 从stock_data.db查询对应的K线数据
3. 计算收益率（1日、2日、3日、5日、总收益率）
4. 生成日线、周线、分钟线数据
5. 保存为JSON文件

**数据格式要求：**
CSV文件必须包含以下列：
- 名称
- 代码
- 入选日期+时间
- 入选价格

## 当前可用数据源

### 微盘数据 (weipan)
- **文件**: data/weipan/数据汇总.csv
- **股票数**: 232
- **平均收益率**: 13.72%
- **胜率**: 65.52%

### 底部数据 (dibu)
- **文件**: data/dibu/汇总csv.csv
- **股票数**: 15
- **平均收益率**: 8.24%
- **胜率**: 46.67%

## 注意事项

1. **数据库共享**: 所有数据源共享同一个 `stock_data.db` 数据库
2. **数据独立性**: 每个数据源的选股数据和计算结果相互独立
3. **切换影响**: 切换数据源会影响所有股票列表和统计数据
4. **文件大小**: JSON文件可能较大，确保有足够的磁盘空间
5. **编码格式**: CSV文件应使用UTF-8编码

## 故障排查

### 问题：切换数据源后数据未更新

**解决方案**：
- 检查浏览器控制台是否有错误
- 确认后端服务正常运行
- 手动刷新浏览器页面

### 问题：新数据源未显示在下拉列表中

**解决方案**：
- 确认 `data_sources.json` 文件格式正确
- 检查JSON文件是否存在于指定路径
- 重启后端服务

### 问题：数据处理脚本报错

**解决方案**：
- 确认虚拟环境已激活：`source venv/bin/activate`
- 确认pandas已安装：`pip install pandas`
- 检查CSV文件格式是否符合要求
- 检查stock_data.db数据库是否包含所需数据
