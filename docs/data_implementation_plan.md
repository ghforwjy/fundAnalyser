# 基金数据维护实施方案

> 文档版本：1.1  
> 创建日期：2026-02-15  
> 更新日期：2026-02-15  
> 基于：数据维护方案V2  
> 状态：**阶段一、阶段二已完成**

---

## 一、现状分析

### 1.1 已实现的全局数据同步器

| 数据表 | 同步器 | 状态 | 接口 |
|--------|--------|------|------|
| fund_info | AkshareFundInfoSyncer | ✅ 已实现 | fund_name_em |
| fund_rating | AkshareFundRatingSyncer | ✅ 已实现 | fund_rating_all |
| fund_manager | AkshareFundManagerSyncer | ✅ 已实现 | fund_manager_em |
| fund_company | AkshareFundCompanySyncer | ✅ 已实现 | fund_company_em |
| fund_dividend | AkshareFundDivSyncer | ✅ 已实现 | fund_fh_em |
| fund_scale | AkshareFundScaleSyncer | ✅ 已实现 | fund_scale_open_sina |
| fund_nav | AkshareFundNavSyncer | ⚠️ 部分实现 | fund_open_fund_daily_em(当日) |

### 1.2 缺失的全局数据同步器

| 数据表 | 状态 | AKShare接口 | 优先级 |
|--------|------|-------------|--------|
| fund_purchase_status | ❌ 待实现 | fund_purchase_em | 高 |
| fund_rank | ❌ 待实现 | fund_open_fund_rank_em | 中 |
| fund_etf_spot | ❌ 待实现 | fund_etf_spot_em | 低 |
| fund_lof_spot | ❌ 待实现 | fund_lof_spot_em | 低 |
| fund_split | ❌ 待实现 | fund_cf_em | 低 |

### 1.3 已实现的分组数据同步器

| 数据表 | 同步器 | 状态 | 说明 |
|--------|--------|------|------|
| fund_stock_holding | AkshareFundPortfolioSyncer | ⚠️ 需改造 | 当前是全局同步，需改为分组按需 |

### 1.4 缺失的分组数据同步器

| 数据表 | 状态 | AKShare接口 | 优先级 |
|--------|------|-------------|--------|
| fund_nav(历史) | ❌ 待实现 | fund_open_fund_info_em | **高** |
| fund_risk_metrics | ❌ 待实现 | fund_individual_analysis_xq | **高** |
| fund_performance | ❌ 待实现 | fund_individual_achievement_xq | **高** |
| fund_bond_holding | ❌ 待实现 | fund_portfolio_bond_hold_em | 中 |
| fund_industry_allocation | ❌ 待实现 | fund_portfolio_industry_allocation_em | 中 |
| fund_asset_allocation | ❌ 待实现 | fund_individual_detail_hold_xq | 中 |
| fund_profit_probability | ❌ 待实现 | fund_individual_profit_probability_xq | 中 |
| fund_detail_info | ❌ 待实现 | fund_overview_em | 低 |
| fund_fee | ❌ 待实现 | fund_fee_em | 低 |
| fund_etf_hist | ❌ 待实现 | fund_etf_hist_em | 低 |
| fund_lof_hist | ❌ 待实现 | fund_lof_hist_em | 低 |

---

## 二、增量获取机制设计

### 2.1 核心原则

1. **基于数据库已有数据**决定从API获取什么数据
2. **重叠窗口策略**：多取3-7天数据确保完整性，避免边界数据遗漏
3. **INSERT OR REPLACE**：重叠数据更新，新数据插入
4. **避免全量重新获取**：每次只获取必要的数据范围

### 2.2 全局数据增量策略

| 数据类型 | 增量策略 | 重叠窗口 | 说明 |
|----------|----------|----------|------|
| fund_info | 全量对比更新 | 无 | 基金数量变化，对比后更新 |
| fund_purchase_status | 全量覆盖 | 无 | 每日状态可能全变 |
| fund_rating | 按日期增量 | 7天 | 评级变化不频繁 |
| fund_rank | 全量覆盖 | 无 | 排行每日都变 |
| fund_dividend | 按年增量 | 当年 | 每年数据独立 |
| fund_split | 按年增量 | 当年 | 每年数据独立 |

### 2.3 分组数据增量策略

| 数据类型 | 增量策略 | 重叠窗口 | 更新频率 |
|----------|----------|----------|----------|
| fund_nav(历史) | 按日期增量 | 3天 | 每日 |
| fund_risk_metrics | 按日期增量 | 7天 | 每周 |
| fund_performance | 按日期增量 | 7天 | 每周 |
| fund_stock_holding | 按季度增量 | 当前季度 | 每季度 |
| fund_bond_holding | 按季度增量 | 当前季度 | 每季度 |
| fund_industry_allocation | 按季度增量 | 当前季度 | 每季度 |

### 2.4 重叠窗口算法

```python
def calculate_fetch_range(fund_code: str, table: str) -> Tuple[str, str]:
    """
    计算数据获取范围
    
    Returns:
        (start_date, end_date): 需要获取的数据范围
    """
    # 查询数据库最新日期
    latest_date = query_db_latest_date(fund_code, table)
    
    if not latest_date:
        # 无历史数据：获取最近2年
        start_date = today - 730 days
    else:
        # 有历史数据：从最新日期-重叠窗口开始
        overlap_days = get_overlap_days(table)  # 3天或7天
        start_date = latest_date - overlap_days
    
    end_date = today
    return (start_date, end_date)
```

---

## 三、实施计划

### 阶段一：完善全局数据（第1-2周）

#### 任务1.1：实现 fund_purchase_status 同步器

**文件**：`backend/syncers/akshare_fund_purchase_status_syncer.py`

**接口**：`fund_purchase_em()` - 获取全市场基金申购赎回状态

**数据表结构**：
```sql
CREATE TABLE IF NOT EXISTS fund_purchase_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    purchase_status VARCHAR(20),  -- 申购状态
    redeem_status VARCHAR(20),    -- 赎回状态
    data_date DATE,               -- 数据日期
    UNIQUE(fund_code, data_date)
);
```

**增量策略**：每日全量覆盖（状态可能全变）

#### 任务1.2：实现 fund_rank 同步器

**文件**：`backend/syncers/akshare_fund_rank_syncer.py`

**接口**：`fund_open_fund_rank_em()` - 获取基金排行数据

**数据表结构**：
```sql
CREATE TABLE IF NOT EXISTS fund_rank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    rank_type VARCHAR(20),        -- 排行类型
    rank_value INTEGER,           -- 排名
    return_1m DECIMAL(8,4),       -- 近1月收益
    return_3m DECIMAL(8,4),       -- 近3月收益
    return_6m DECIMAL(8,4),       -- 近6月收益
    return_1y DECIMAL(8,4),       -- 近1年收益
    data_date DATE,
    UNIQUE(fund_code, rank_type, data_date)
);
```

#### 任务1.3：更新前端数据源管理页面

**文件**：`app/src/pages/DataManage/DataSource.tsx`

**修改内容**：
1. 在 `tables-status` 接口响应中增加新表
2. 在同步逻辑中处理新表
3. 添加同步选项UI

#### 任务1.4：更新后端API

**文件**：`backend/api/sync.py`

**修改内容**：
1. 添加新同步器的导入
2. 添加新同步API端点
3. 更新 `tables-status` 接口返回

---

### 阶段二：核心分组数据（第3-4周）

#### 任务2.1：创建分组数据同步器基类

**文件**：`backend/syncers/group/base_group_syncer.py`

**功能**：
1. 提供分组数据同步的通用方法
2. 实现重叠窗口算法
3. 提供并发控制

#### 任务2.2：实现 GroupFundNavSyncer（历史净值）

**文件**：`backend/syncers/group/group_fund_nav_syncer.py`

**接口**：`fund_open_fund_info_em(symbol, indicator="单位净值走势")`

**增量策略**：
- 查询数据库该基金的最新净值日期
- 从最新日期-3天开始获取到今天
- 使用 INSERT OR REPLACE 写入

**并发策略**：
- 分组内基金并发获取（限制最大并发数5）
- 每只基金独立处理

#### 任务2.3：实现 GroupFundRiskMetricsSyncer（风险指标）

**文件**：`backend/syncers/group/group_fund_risk_metrics_syncer.py`

**接口**：`fund_individual_analysis_xq(symbol)`

**数据内容**：
- 夏普比率
- 最大回撤
- 波动率
- Beta系数
- Alpha系数

**增量策略**：
- 查询数据库最新日期
- 超过7天未更新则重新获取
- 重叠窗口7天

#### 任务2.4：实现 GroupFundPerformanceSyncer（业绩表现）

**文件**：`backend/syncers/group/group_fund_performance_syncer.py`

**接口**：`fund_individual_achievement_xq(symbol)`

**数据内容**：
- 多周期收益率（1月、3月、6月、1年、3年、5年）
- 同类排名
- 四分位排名

**增量策略**：同风险指标

#### 任务2.5：改造 fund_stock_holding 同步器

**文件**：`backend/syncers/group/group_fund_stock_holding_syncer.py`

**改造内容**：
1. 从全局同步改为分组按需同步
2. 只获取分组内基金的持仓数据
3. 按季度增量获取

#### 任务2.6：更新分组刷新API

**文件**：`backend/api/portfolio.py`

**新增端点**：`POST /api/portfolio/groups/{group_id}/refresh`

**请求参数**：
```json
{
  "data_types": ["nav", "risk", "performance", "holding"],
  "force_update": false
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "nav_updated": 10,
    "risk_updated": 10,
    "performance_updated": 10,
    "holding_updated": 5,
    "errors": []
  }
}
```

#### 任务2.7：更新前端分组页面

**文件**：`app/src/pages/Portfolio/index.tsx`

**修改内容**：
1. 增强刷新按钮功能
2. 添加刷新选项对话框
3. 显示刷新进度和结果

---

### 阶段三：扩展分组数据（第5-6周）

#### 任务3.1：实现债券持仓同步器

**文件**：`backend/syncers/group/group_fund_bond_holding_syncer.py`

**接口**：`fund_portfolio_bond_hold_em(symbol, date)`

#### 任务3.2：实现行业配置同步器

**文件**：`backend/syncers/group/group_fund_industry_allocation_syncer.py`

**接口**：`fund_portfolio_industry_allocation_em(symbol, date)`

#### 任务3.3：实现资产配置同步器

**文件**：`backend/syncers/group/group_fund_asset_allocation_syncer.py`

**接口**：`fund_individual_detail_hold_xq(symbol, date)`

#### 任务3.4：实现盈利概率同步器

**文件**：`backend/syncers/group/group_fund_profit_probability_syncer.py`

**接口**：`fund_individual_profit_probability_xq(symbol)`

---

### 阶段四：优化和测试（第7-8周）

#### 任务4.1：数据完整性检查

**文件**：`backend/services/data_integrity_service.py`

**功能**：
1. 检测数据断点
2. 自动回补缺失数据
3. 数据质量报告

#### 任务4.2：并发控制优化

**优化内容**：
1. 分组内基金并发数限制
2. API调用频率控制
3. 错误重试机制

#### 任务4.3：编写测试用例

**文件**：`backend/tests/test_group_syncers.py`

**测试内容**：
1. 增量获取逻辑测试
2. 重叠窗口算法测试
3. 并发控制测试
4. 错误处理测试

---

## 四、文件创建清单

### 4.1 后端文件

```
backend/syncers/
├── akshare_fund_purchase_status_syncer.py    # 新增
├── akshare_fund_rank_syncer.py               # 新增
├── akshare_fund_etf_spot_syncer.py           # 新增（低优先级）
├── akshare_fund_lof_spot_syncer.py           # 新增（低优先级）
├── akshare_fund_split_syncer.py              # 新增（低优先级）
└── group/
    ├── __init__.py                           # 新增
    ├── base_group_syncer.py                  # 新增
    ├── group_fund_nav_syncer.py              # 新增
    ├── group_fund_risk_metrics_syncer.py     # 新增
    ├── group_fund_performance_syncer.py      # 新增
    ├── group_fund_stock_holding_syncer.py    # 新增
    ├── group_fund_bond_holding_syncer.py     # 新增（中优先级）
    ├── group_fund_industry_allocation_syncer.py  # 新增（中优先级）
    ├── group_fund_asset_allocation_syncer.py     # 新增（中优先级）
    ├── group_fund_profit_probability_syncer.py   # 新增（中优先级）
    ├── group_fund_detail_info_syncer.py          # 新增（低优先级）
    └── group_fund_fee_syncer.py                  # 新增（低优先级）

backend/services/
└── data_integrity_service.py                 # 新增

backend/tests/
└── test_group_syncers.py                     # 新增
```

### 4.2 前端文件

```
app/src/pages/Portfolio/
├── components/
│   └── RefreshDialog.tsx                     # 新增（刷新选项对话框）
└── index.tsx                                 # 修改（增强刷新功能）

app/src/services/
└── api.ts                                    # 修改（添加新API调用）
```

### 4.3 修改的后端文件

```
backend/syncers/__init__.py                   # 修改（添加新同步器导入）
backend/api/sync.py                           # 修改（添加新API端点）
backend/api/portfolio.py                      # 修改（添加分组刷新API）
backend/services/portfolio_service.py         # 修改（扩展刷新逻辑）
```

---

## 五、数据库表创建SQL

### 5.1 全局数据表

```sql
-- 基金申购赎回状态
CREATE TABLE IF NOT EXISTS fund_purchase_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    purchase_status VARCHAR(20),
    redeem_status VARCHAR(20),
    data_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, data_date)
);

-- 基金排行
CREATE TABLE IF NOT EXISTS fund_rank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    rank_type VARCHAR(20),
    rank_value INTEGER,
    return_1m DECIMAL(8,4),
    return_3m DECIMAL(8,4),
    return_6m DECIMAL(8,4),
    return_1y DECIMAL(8,4),
    data_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, rank_type, data_date)
);

-- ETF实时行情
CREATE TABLE IF NOT EXISTS fund_etf_spot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    latest_price DECIMAL(10,4),
    change_pct DECIMAL(8,4),
    volume DECIMAL(15,2),
    amount DECIMAL(15,2),
    data_time DATETIME,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, data_time)
);

-- LOF实时行情
CREATE TABLE IF NOT EXISTS fund_lof_spot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    latest_price DECIMAL(10,4),
    change_pct DECIMAL(8,4),
    volume DECIMAL(15,2),
    amount DECIMAL(15,2),
    data_time DATETIME,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, data_time)
);

-- 基金拆分
CREATE TABLE IF NOT EXISTS fund_split (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    split_date DATE,
    split_ratio VARCHAR(20),
    year VARCHAR(4),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, split_date)
);
```

### 5.2 分组数据表

```sql
-- 风险指标
CREATE TABLE IF NOT EXISTS fund_risk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    volatility DECIMAL(8,4),
    beta DECIMAL(8,4),
    alpha DECIMAL(8,4),
    data_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, data_date)
);

-- 业绩表现
CREATE TABLE IF NOT EXISTS fund_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    return_1m DECIMAL(8,4),
    return_3m DECIMAL(8,4),
    return_6m DECIMAL(8,4),
    return_1y DECIMAL(8,4),
    return_3y DECIMAL(8,4),
    return_5y DECIMAL(8,4),
    rank_in_category INTEGER,
    quartile_rank INTEGER,
    data_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, data_date)
);

-- 债券持仓
CREATE TABLE IF NOT EXISTS fund_bond_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    bond_code VARCHAR(20),
    bond_name VARCHAR(100),
    nav_ratio DECIMAL(8,4),
    market_value DECIMAL(15,2),
    quarter VARCHAR(10),
    report_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, bond_code, quarter)
);

-- 行业配置
CREATE TABLE IF NOT EXISTS fund_industry_allocation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    industry_name VARCHAR(50),
    nav_ratio DECIMAL(8,4),
    market_value DECIMAL(15,2),
    change_pct DECIMAL(8,4),
    quarter VARCHAR(10),
    report_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, industry_name, quarter)
);

-- 资产配置
CREATE TABLE IF NOT EXISTS fund_asset_allocation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    stock_ratio DECIMAL(8,4),
    bond_ratio DECIMAL(8,4),
    cash_ratio DECIMAL(8,4),
    other_ratio DECIMAL(8,4),
    quarter VARCHAR(10),
    report_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, quarter)
);

-- 盈利概率
CREATE TABLE IF NOT EXISTS fund_profit_probability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    hold_period VARCHAR(20),
    profit_probability DECIMAL(8,4),
    avg_return DECIMAL(8,4),
    data_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, hold_period, data_date)
);

-- 基金详情
CREATE TABLE IF NOT EXISTS fund_detail_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL UNIQUE,
    invest_strategy TEXT,
    risk_level VARCHAR(20),
    benchmark_index VARCHAR(100),
    establish_date DATE,
    establish_scale DECIMAL(15,2),
    latest_scale DECIMAL(15,2),
    manager_name VARCHAR(50),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金费率
CREATE TABLE IF NOT EXISTS fund_fee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fee_type VARCHAR(20),
    fee_value DECIMAL(8,4),
    fee_desc VARCHAR(100),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, fee_type)
);
```

---

## 六、API接口设计

### 6.1 全局数据同步API

```
POST /api/sync/fund-purchase-status
POST /api/sync/fund-rank
POST /api/sync/fund-etf-spot
POST /api/sync/fund-lof-spot
POST /api/sync/fund-split
```

### 6.2 分组数据刷新API

```
POST /api/portfolio/groups/{group_id}/refresh

Request:
{
  "data_types": ["nav", "risk", "performance", "holding"],
  "force_update": false
}

Response:
{
  "success": true,
  "data": {
    "nav_updated": 10,
    "nav_inserted": 50,
    "risk_updated": 10,
    "performance_updated": 10,
    "holding_updated": 5,
    "errors": []
  }
}
```

---

## 七、注意事项

1. **并发控制**：分组内基金并发获取时，限制最大并发数为5，避免对AKShare服务器造成压力

2. **错误处理**：单只基金获取失败不应影响其他基金，记录错误继续处理

3. **事务管理**：每只基金的数据写入应独立事务，避免一只基金失败导致整批回滚

4. **数据校验**：写入前校验数据完整性，如净值必须大于0，日期格式正确等

5. **日志记录**：详细记录每次同步的统计信息，便于排查问题

---

## 八、验收标准

1. **全局数据**：所有高、中优先级全局数据表可通过数据源管理页面正常同步
2. **分组数据**：分组页面刷新按钮可正常获取历史净值、风险指标、业绩表现
3. **增量机制**：重复刷新时，只获取新增或更新的数据，不会全量重新获取
4. **数据完整性**：重叠窗口策略确保边界数据不会遗漏
5. **性能要求**：10只基金的分组刷新完成时间不超过30秒

---

*本文档为实施方案，具体代码实现需参照各阶段任务执行。*
