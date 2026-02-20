# 基金数据平台 v2.0

完整的前后端整合基金数据管理和分析平台，参考akshare和tushare专业表设计，实现真实数据调用。

## 项目架构

```
fund_platform/
├── backend/              # Python FastAPI 后端
│   ├── main.py          # API主入口
│   ├── database.py      # 数据库操作
│   ├── data_collector.py # 数据采集(akshare/tushare)
│   ├── metrics_calculator.py # 指标计算
│   └── requirements.txt # Python依赖
├── database/            # 数据库文件
│   └── fund_database_complete.sql # 完整数据库设计
├── app/                 # React前端 (已整合)
└── start.py            # 启动脚本
```

## 数据库设计

### 基础数据层 (Raw Data)
- `fund_basic_info` - 基金基本信息
- `fund_nav_history` - 基金净值历史
- `fund_stock_holding` - 股票持仓
- `fund_bond_holding` - 债券持仓
- `fund_industry_allocation` - 行业配置
- `fund_manager_info` - 基金经理
- `fund_company_info` - 基金公司
- `fund_scale_history` - 规模变动
- `fund_dividend` - 分红信息
- `fund_rating` - 基金评级

### 业务指标层 (Business)
- `fund_return_metrics` - 收益率指标
- `fund_risk_metrics` - 风险指标
- `fund_risk_adjusted_metrics` - 风险调整收益
- `fund_holding_analysis` - 持仓分析
- `fund_performance_rank` - 业绩排名
- `fund_tags` - 基金标签

### 系统管理
- `data_source_config` - 数据源配置
- `data_update_log` - 更新日志
- `data_sync_status` - 同步状态

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖 (在项目根目录)
cd ../app
npm install
```

### 2. 初始化数据库

```bash
cd fund_platform
python start.py init
```

### 3. 测试数据源连接

```bash
python start.py test
```

### 4. 启动后端服务

```bash
# 开发模式
python start.py start --reload

# 生产模式
python start.py start
```

后端服务将在 http://localhost:8000 启动

### 5. 启动前端

```bash
cd app
npm run dev
```

前端将在 http://localhost:5173 启动

## API 接口文档

启动后端后访问: http://localhost:8000/docs

### 主要接口

#### 数据源管理
- `GET /api/datasource` - 获取数据源配置
- `POST /api/datasource/{name}/test` - 测试连接
- `POST /api/datasource/{name}/config` - 更新配置

#### 数据同步
- `GET /api/sync/status` - 同步状态
- `POST /api/sync/fund-basic` - 同步基金基本信息
- `POST /api/sync/fund-nav` - 同步净值数据
- `GET /api/sync/logs` - 同步日志

#### 数据库管理
- `GET /api/db/tables` - 获取所有表
- `GET /api/db/tables/{name}` - 表详情
- `GET /api/db/tables/{name}/data` - 表数据

#### 基金查询
- `GET /api/funds` - 基金列表
- `GET /api/funds/{code}` - 基金详情
- `GET /api/funds/{code}/nav` - 净值历史
- `GET /api/funds/{code}/holdings` - 持仓
- `GET /api/funds/{code}/industry` - 行业配置

#### 指标计算
- `POST /api/metrics/calculate/{code}` - 计算单只基金指标
- `POST /api/metrics/calculate-batch` - 批量计算

## 数据源配置

### AKShare (默认)
- 免费开源
- 无需配置
- 数据来源于东方财富、天天基金网

### Tushare Pro
- 需要Token
- 已配置Token: `9ded475d6d868719be0e28dc24c633938d3b4ac84e4a06b2ae1fed19`
- 数据更专业、更全面

## 功能特性

### 数据管理
- ✅ 数据源配置和连接测试
- ✅ 数据库表结构查看
- ✅ 表数据浏览(分页、排序、筛选)
- ✅ 数据同步状态监控
- ✅ 同步日志查看

### 基金分析
- ✅ 基金列表(分页、筛选、排序)
- ✅ 基金详情(基本信息、费率、业绩基准)
- ✅ 历史净值走势
- ✅ 风险指标(夏普比率、最大回撤等)
- ✅ 持仓分析(集中度、行业分布)
- ✅ 基金经理信息

## 技术栈

### 后端
- Python 3.8+
- FastAPI - Web框架
- SQLite - 数据库
- AKShare/Tushare - 数据源
- NumPy/Pandas - 数据处理

### 前端
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui

## 开发计划

- [x] 数据库设计 (参考akshare/tushare)
- [x] 后端API开发
- [x] 数据采集模块
- [x] 指标计算模块
- [x] 前端界面开发
- [x] 前后端整合
- [ ] 数据自动同步任务
- [ ] 基金组合分析
- [ ] 更多可视化图表

## 许可证

MIT License
