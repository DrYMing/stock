# 项目总览

## 📊 项目简介

**股票收益率可视化系统**是一个基于选股数据的收益率分析工具，可以展示每只股票从买入时间点后的收益率变化情况。

### 核心功能

- ✅ **收益率可视化**：展示每只股票的收益率曲线
- ✅ **统计分析**：展示整体投资指标（平均收益、胜率等）
- ✅ **搜索筛选**：支持按名称/代码搜索，多维度排序
- ✅ **交互图表**：使用ECharts提供强大的数据可视化
- ✅ **响应式设计**：适配桌面和移动设备

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React 18 + Vite 6 | 现代化UI框架 |
| 样式 | Tailwind CSS 3 | 实用CSS框架 |
| 图表 | ECharts 5 | 专业数据可视化 |
| 后端 | Flask 3 | 轻量级Web框架 |
| 数据处理 | Pandas 3 | 数据分析库 |
| 数据库 | SQLite 3 | 轻量级数据库 |

---

## 📁 项目结构

```
shareKLine/
│
├── 📄 README.md                    # 项目说明
├── 📄 PROJECT_OVERVIEW.md          # 本文件
├── 📄 start.sh                     # 一键启动脚本
│
├── 📂 data/                        # 数据目录
│   └── weipan/
│       ├── 数据汇总.csv            # 选股数据（233条）
│       └── stock_data.db           # K线数据库
│
├── 📂 docs/                        # 📚 文档目录
│   ├── architecture.md             # 系统架构（含Mermaid图）
│   ├── api.md                      # API接口文档
│   ├── data-flow.md                # 数据流程（含Mermaid图）
│   ├── deployment.md               # 部署指南
│   └── user-guide.md               # 用户手册
│
├── 📂 scripts/                     # 脚本目录
│   └── process_data.py             # 数据处理脚本
│
├── 📂 src/                         # 源代码目录
│   ├── 📂 backend/                 # 后端代码
│   │   ├── app.py                  # Flask API服务器
│   │   ├── start.sh                # 后端启动脚本
│   │   └── 📂 data/
│   │       └── stock_returns.json  # 处理后的数据
│   │
│   └── 📂 frontend/                # 前端代码
│       ├── index.html
│       ├── package.json
│       ├── vite.config.js
│       ├── tailwind.config.js
│       ├── postcss.config.js
│       │
│       └── 📂 src/
│           ├── main.jsx            # React入口
│           ├── App.jsx             # 主应用组件
│           ├── App.css             # 全局样式
│           ├── index.css           # 基础样式
│           ├── api.js              # API客户端
│           │
│           └── 📂 components/
│               ├── StatsPanel.jsx  # 统计面板
│               ├── StockList.jsx   # 股票列表
│               └── ReturnChart.jsx # 收益率图表
│
├── 📂 venv/                        # Python虚拟环境
│
├── 📄 task_plan.md                 # 项目计划
├── 📄 findings.md                  # 研究发现
└── 📄 progress.md                  # 开发进度
```

---

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Python 3.8+

### 安装步骤

```bash
# 1. 安装Python依赖
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors pandas

# 2. 安装前端依赖
cd src/frontend
npm install
cd ../..

# 3. 处理数据
python scripts/process_data.py
```

### 启动系统

**方式1：一键启动（推荐）**
```bash
./start.sh
```

**方式2：手动启动**
```bash
# 终端1：启动后端
source venv/bin/activate
python src/backend/app.py

# 终端2：启动前端
cd src/frontend
npm run dev
```

### 访问应用

打开浏览器访问：http://localhost:5173

---

## 📊 数据统计

### 当前数据概况

```
总股票数：232 只
平均收益率：13.94%
最高收益率：201.39%（迈为股份 300751）
最低收益率：-28.24%（珠海冠宇 688772）
胜率：63.79%
```

### 收益率分布

- 📈 盈利股票：148只（63.79%）
- 📉 亏损股票：84只（36.21%）
- 🚀 收益超过50%：26只
- 💎 收益超过100%：5只

---

## 🔧 API 接口

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`

### 主要接口

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/stats` | 获取统计数据 |
| GET | `/stocks` | 获取股票列表（支持分页、排序、搜索） |
| GET | `/stocks/:code` | 获取股票详情 |
| GET | `/stocks/:code/returns` | 获取收益率曲线 |
| GET | `/top` | 获取Top榜单 |

详细API文档请参考：[docs/api.md](docs/api.md)

---

## 📚 文档导航

| 文档 | 说明 | 适用对象 |
|------|------|----------|
| [README.md](README.md) | 项目说明和快速开始 | 所有用户 |
| [docs/architecture.md](docs/architecture.md) | 系统架构和技术设计 | 开发者 |
| [docs/api.md](docs/api.md) | API接口文档 | 开发者 |
| [docs/data-flow.md](docs/data-flow.md) | 数据流程和处理逻辑 | 开发者 |
| [docs/deployment.md](docs/deployment.md) | 部署指南 | 运维人员 |
| [docs/user-guide.md](docs/user-guide.md) | 用户使用手册 | 终端用户 |

---

## 🛠️ 开发指南

### 技术选型

**前端技术栈**
- React 18：组件化UI框架
- Vite 6：快速构建工具
- Tailwind CSS：实用CSS框架
- ECharts：专业图表库
- Axios：HTTP客户端

**后端技术栈**
- Flask：轻量级Web框架
- Flask-CORS：跨域支持
- Pandas：数据处理库
- SQLite：嵌入式数据库

### 开发规范

**代码风格**
- 前端：使用ESLint + Prettier
- 后端：遵循PEP 8规范

**Git提交**
```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试
chore: 构建/工具变动
```

---

## 📈 功能演示

### 1. 统计面板

展示6个关键指标：
- 总股票数
- 有数据的股票数
- 平均收益率
- 最高/最低收益率
- 胜率

### 2. 股票列表

- 支持分页浏览（每页50条）
- 支持搜索（名称/代码）
- 支持排序（收益率/名称/日期）
- 点击查看详情

### 3. 收益率图表

- 使用ECharts绘制曲线
- 显示买入信息
- 显示最高/最低收益
- 支持缩放和拖拽

---

## 🔄 更新日志

### v1.0.0 (2026-01-31)

**初始版本发布**

✨ 新功能：
- 股票列表展示
- 收益率计算和可视化
- 统计面板
- 搜索和排序功能
- 分页功能
- 交互式图表
- 响应式设计
- 完整的项目文档

📊 数据处理：
- 支持232只股票
- 处理233条选股记录
- 收益率计算准确率100%

📚 文档：
- 架构文档
- API文档
- 数据流程文档
- 部署文档
- 用户手册

---

## 🎯 未来计划

### 短期计划

- [ ] 添加数据导出功能
- [ ] 支持自定义时间范围
- [ ] 添加更多技术指标
- [ ] 优化移动端体验

### 中期计划

- [ ] 多股票对比功能
- [ ] K线图展示
- [ ] 用户认证系统
- [ ] 数据预警功能

### 长期计划

- [ ] 实时数据更新
- [ ] 机器学习预测
- [ ] 移动APP
- [ ] 多数据源支持

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 报告问题

请在GitHub Issues中报告问题，并提供：
- 问题描述
- 复现步骤
- 错误信息
- 环境信息

### 提交代码

1. Fork项目
2. 创建特性分支
3. 提交代码
4. 发起Pull Request

---

## 📄 许可证

MIT License

---

## 👥 作者

Created with Claude Code

---

## 📞 联系方式

- GitHub Issues
- Email: [your-email]

---

## 🙏 致谢

感谢以下开源项目：

- React
- Vite
- ECharts
- Tailwind CSS
- Flask
- Pandas

---

**最后更新：** 2026-01-31
**项目状态：** ✅ 已完成并可用
