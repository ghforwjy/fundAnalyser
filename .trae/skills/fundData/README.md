# FundData Skill 详细设计文档

## 目录

1. [功能概述](#功能概述)
2. [数据分类](#数据分类)
3. [智能缓存机制](#智能缓存机制)
4. [数据库结构](#数据库结构)
5. [实现架构](#实现架构)

---

## 功能概述

FundData是一个基于AKShare的基金数据管理工具，自动维护SQLite数据库，提供：

1. **全局数据维护** - 批量同步全市场基金数据
2. **分组数据维护** - 按需获取指定基金代码的详细数据
3. **数据查询** - 提供结构化的基金数据查询能力
4. **市值定投** - 提供市值定投方案计算

---

## 数据分类

### 全局数据（批量同步）

| 数据类型 | 说明 | AKShare接口 |
|---------|------|------------|
| fund_info | 基金基本信息 | fund_name_em |
| fund_purchase_status | 申购赎回状态 | fund_purchase_em |
| fund_rating | 基金评级 | fund_rating_all |
| fund_manager | 基金经理 | fund_manager_em |
| fund_company | 基金公司 | 从fund_manager提取 |
| fund_dividend | 基金分红 | fund_fh_em |
| fund_split | 基金拆分 | fund_cf_em |
| fund_rank | 基金排行 | fund_open_fund_rank_em |

### 分组数据（按需获取）

| 数据类型 | 说明 | AKShare接口 |
|---------|------|------------|
| fund_nav | 历史净值 | fund_open_fund_info_em |
| fund_stock_holding | 股票持仓 | fund_portfolio_hold_em |
| fund_bond_holding | 债券持仓 | fund_portfolio_bond_hold_em |
| fund_industry_allocation | 行业配置 | fund_portfolio_industry_allocation_em |
| fund_risk_metrics | 风险指标 | fund_individual_analysis_xq |
| fund_performance | 业绩表现 | fund_individual_achievement_xq |

---

## 智能缓存机制

### 数据缓存策略总览

| 数据类型 | 存储表 | 存储位置 | 有效期 | 新鲜度判断逻辑 | 自动更新时机 |
|---------|-------|---------|-------|---------------|-------------|
| 交易日历 | trade_calendar | fund_data.db | 年度 | 数据覆盖到当前日期之后 | 年度更新 |
| 基金基本信息 | fund_info | fund_data.db | 7天 | 检查update_time是否在7天内 | 后端启动时自动检查并更新 |
| 基金评级 | fund_rating | fund_data.db | 无限期 | 手动同步，建议每日更新 | - |
| 基金经理 | fund_manager | fund_data.db | 无限期 | 手动同步，建议每日更新 | - |
| 基金净值 | fund_nav | fund_data.db | 24小时 | 检查最新净值日期是否为最近交易日 | 查询时自动检查并更新 |
| QDII净值 | fund_nav | fund_data.db | 24小时 | 检查最新净值日期是否为最近交易日-1天 | 查询时自动检查并更新 |
| 股票持仓 | fund_stock_holding | fund_data.db | 按季度 | 当天查询过就不再查询 | 查询时自动检查并更新 |
| 债券持仓 | fund_bond_holding | fund_data.db | 按季度 | 当天查询过就不再查询 | 查询时自动检查并更新 |
| 行业配置 | fund_industry_allocation | fund_data.db | 按季度 | 当天查询过就不再查询 | 查询时自动检查并更新 |
| 指数参考基准 | index_benchmark | fund_data.db | 1年 | 检查更新时间是否在365天内 | 市场阶段变化时更新 |
| 市场阶段 | market_phase_record | fund_data.db | 无限期 | 检查阶段是否变化，变化时重新计算 | - |
| 基金平均月收益率 | 内存缓存 | 内存 | 30天 | 首次计算后缓存 | 缓存期内直接使用 |

### 数据新鲜度判断逻辑

#### 0. 交易日历

使用 AKShare 交易日历接口，自动识别节假日，而非简单的周六日判断。

#### 1. 净值数据

| 判断条件 | 操作 |
|---------|------|
| 最新净值日期 >= 最近交易日 | 使用缓存，不发起API请求 |
| 最新净值日期 < 最近交易日 | 从AKShare获取更新 |
| 无数据 | 从AKShare获取 |

**QDII基金特殊处理**：QDII基金净值延迟一天，判断时使用最近交易日-1天

#### 2. 持仓数据

当天查询过就不再重复查询（持仓数据季度更新，无需频繁刷新）。

#### 3. 跳过行业配置的基金类型

以下基金类型没有股票行业配置，自动跳过查询：
- 债券型-混合一级
- 债券型-长债
- 债券型-中短债
- 债券型-可转债
- 指数型-其他（黄金ETF等）
- 货币型



#### 4. 指数参考基准（市值定投用）

| 判断条件 | 操作 |
|---------|------|
| 市场阶段变化 | 重新计算并保存基准 |
| 市场阶段未变化 + 数据在1年有效期内 | 使用缓存 |
| 市场阶段未变化 + 数据超过1年 | 重新计算并保存基准 |

**存储内容**：
- 沪深300ETF在各市场阶段的平均月收益率
- 中证500ETF在各市场阶段的平均月收益率
- 样本月数、标准差等统计信息

#### 5. 全局数据

| 数据类型 | 建议更新频率 | 更新方式 | 自动更新 |
|---------|-------------|---------|---------|
| fund_info | 每日 | `skill.sync_fund_info()` | 后端启动时自动检查（7天有效期） |
| fund_rating | 每日 | `skill.sync_fund_rating()` | - |
| fund_manager | 每日 | `skill.sync_fund_manager()` | - |
| fund_company | 每日 | `skill.sync_fund_company()` | - |

#### 6. 市值定投计算缓存

| 数据类型 | 缓存位置 | 有效期 | 说明 |
|---------|---------|-------|------|
| 基金平均月收益率 | 内存 | 30天 | 按基金代码+市场阶段缓存 |
| 指数参考基准 | 数据库 | 1年 | 按指数代码+市场阶段缓存 |

**缓存策略说明**：
- 首次计算某基金平均月收益率时，从数据库查询历史净值计算并缓存
- 缓存期内（30天）直接使用缓存值，无需重复查询和计算
- 后端重启后缓存清空，首次计算时会重新生成

### 后端启动自动检查

后端服务启动时会自动执行以下检查（非阻塞，后台线程）：

```
1. 检查 fund_info 表最新更新时间
2. 如果超过7天未更新：
   - 自动调用 skill.sync_fund_info() 同步基金基本信息
   - 在后台执行，不影响服务启动
3. 如果7天内已更新：
   - 跳过同步，使用现有数据
```

**日志输出示例**：
```
[启动检查] fund_info表记录数: 26167, 最后更新: 1天前
[启动检查] 基金基本信息新鲜度正常，跳过同步
```

### 智能批量更新算法

批量更新净值数据时，采用以下优化策略：

```
算法流程：
1. 一次性查询所有基金的最新净值日期（单次SQL查询）
2. 确定目标日期（最近工作日）
3. 筛选需要更新的基金：
   - 无数据基金 → 需要更新
   - 最新日期 < 目标日期 → 需要更新
   - 最新日期 = 目标日期 → 跳过，不发起API请求
4. 只对需要更新的基金发起API请求
```

**优化效果**：
- 减少不必要的API调用
- 已是最新数据的基金直接跳过
- 单次SQL查询获取所有基金的最新日期

### 使用示例

**场景1：首次查询中航基金净值**
```python
results = query_funds_nav(company='中航', fund_type='股票')
# 输出: [SmartFund] 智能更新分析:
#       - 目标日期: 2026-02-14
#       - 无数据基金: 15 只
#       - 需要更新: 15 只
#       - 已是最新: 0 只 (跳过API请求)
```

**场景2：再次查询（使用缓存）**
```python
results = query_funds_nav(company='中航', fund_type='股票')
# 输出: [SmartFund] 智能更新分析:
#       - 目标日期: 2026-02-14
#       - 无数据基金: 0 只
#       - 需要更新: 0 只
#       - 已是最新: 15 只 (跳过API请求)
```

---

## 投资算法

投资算法的详细设计文档请参阅：[invest_methods.md](./invest_methods.md)

包含：
- 市值定投法（Value Averaging）

---

## 数据库结构

### 全局数据表

**fund_info** - 基金基本信息
```sql
CREATE TABLE fund_info (
    fund_code VARCHAR(10) PRIMARY KEY,
    fund_name VARCHAR(100) NOT NULL,
    fund_full_name VARCHAR(200),
    fund_type VARCHAR(50),
    pinyin_abbr VARCHAR(50),
    pinyin_full VARCHAR(100),
    company_name VARCHAR(100),
    establish_date DATE,
    status VARCHAR(20),
    data_source VARCHAR(20),
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**fund_rating** - 基金评级
```sql
CREATE TABLE fund_rating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    rating_agency VARCHAR(50),
    rating_3y INTEGER,
    rating_5y INTEGER,
    rating_date DATE,
    UNIQUE(fund_code, rating_agency)
);
```

**fund_manager** - 基金经理
```sql
CREATE TABLE fund_manager (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_name VARCHAR(50) NOT NULL,
    company_name VARCHAR(100),
    fund_code VARCHAR(10),
    tenure_days INTEGER,
    total_scale DECIMAL(15,4),
    best_return DECIMAL(8,4),
    UNIQUE(manager_name, fund_code)
);
```

### 分组数据表

**fund_nav** - 历史净值
```sql
CREATE TABLE fund_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    nav_date DATE NOT NULL,
    unit_nav DECIMAL(10,4),
    accum_nav DECIMAL(10,4),
    daily_return DECIMAL(8,4),
    UNIQUE(fund_code, nav_date)
);
```

**fund_stock_holding** - 股票持仓
```sql
CREATE TABLE fund_stock_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    stock_code VARCHAR(10),
    stock_name VARCHAR(50),
    hold_ratio DECIMAL(8,4),
    hold_value DECIMAL(15,4),
    quarter VARCHAR(50),
    UNIQUE(fund_code, report_date, stock_code)
);
```

**fund_risk_metrics** - 风险指标
```sql
CREATE TABLE fund_risk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    period VARCHAR(20) NOT NULL,
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    volatility DECIMAL(8,4),
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, period)
);
```

### 元数据表

**fund_data_meta** - 数据同步状态
```sql
CREATE TABLE fund_data_meta (
    table_name VARCHAR(50) PRIMARY KEY,
    last_sync_time DATETIME,
    record_count INTEGER DEFAULT 0,
    last_sync_status VARCHAR(20),
    last_error TEXT
);
```

**index_benchmark** - 指数参考基准（市值定投用）
```sql
CREATE TABLE index_benchmark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_code VARCHAR(10) NOT NULL,
    index_name VARCHAR(50),
    market_phase VARCHAR(20) NOT NULL,
    avg_monthly_return DECIMAL(8,4),
    monthly_return_std DECIMAL(8,4),
    sample_months INTEGER,
    data_start_date DATE,
    data_end_date DATE,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_code, market_phase)
);
```

**market_phase_record** - 市场阶段记录
```sql
CREATE TABLE market_phase_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_name VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current INTEGER DEFAULT 0,
    confirmed_date DATE,
    data_source TEXT,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(phase_name, start_date)
);
```

---

## 实现架构

```
.trae/skills/fundData/
├── SKILL.md                    # 接口文档（简洁版）
├── README.md                   # 本文件（详细设计文档）
├── fund_data_skill.py          # Skill主入口
├── smart_fund_data.py          # 智能查询接口
├── value_averaging.py          # 市值定投模块
├── database.py                 # 数据库管理
├── syncers/                    # 同步器模块
│   ├── __init__.py
│   ├── base_syncer.py          # 基础同步器
│   ├── global_syncers.py       # 全局数据同步器
│   └── group_syncers.py        # 分组数据同步器
├── queries/                    # 查询模块
│   ├── __init__.py
│   └── fund_queries.py         # 基金查询
└── utils/
    ├── __init__.py
    └── helpers.py              # 工具函数
```

---

## 注意事项

1. **频率限制**：AKShare接口有访问频率限制，分组数据同步时会自动添加延迟
2. **数据更新**：全局数据建议每日同步一次，分组数据按需同步
3. **错误处理**：单只基金同步失败不会影响其他基金
4. **数据库位置**：默认使用 `fund_data.db`

## 依赖要求

```
akshare >= 1.15.0
pandas >= 2.0.0
sqlite3
```

## 相关文档

- [ComfyUI 安装与配置指南](./COMFYUI_GUIDE.md) - 包含 ComfyUI 安装、RunningHub 节点安装和千问 VAE 模型下载说明
- [投资方法说明](./invest_methods.md) - 包含市值定投法等投资策略详细说明
