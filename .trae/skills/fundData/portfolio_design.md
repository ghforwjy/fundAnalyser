# 组合管理功能设计文档

## 概述

组合管理功能分为两个部分：
1. **组合管理** - 对组合本身的增删改查
2. **成分基金管理** - 对组合内基金的增删改查

---

## 一、数据库表结构

### 1. 组合表 (portfolio)

```sql
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 成分基金表 (portfolio_fund)

#### 基础字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| id | INTEGER | ✅ | 主键 |
| portfolio_id | INTEGER | ✅ | 所属组合ID |
| fund_code | VARCHAR(10) | ✅ | 基金代码 |
| fund_name | VARCHAR(100) | ❌ | 基金名称（冗余） |
| buy_date | DATE | ❌ | 买入日期 |
| buy_nav | DECIMAL(10,4) | ❌ | 买入净值（摊薄成本净值） |
| shares | DECIMAL(15,4) | ❌ | 持有份额（当前） |
| notes | TEXT | ❌ | 备注 |

**说明**：
- `buy_nav` 存储摊薄后的成本净值
- 导入盈亏时计算：`buy_nav = (current_value - profit_loss) / shares`
- 成本通过 `buy_nav × shares` 实时计算
- 盈亏通过 `latest_nav × shares - buy_nav × shares` 实时计算，不再存储`profit_loss`字段
- `amount`字段已废弃，成本通过 `buy_nav × shares` 实时计算

#### 收益指标字段（来自 fund_performance）

| 字段 | 类型 | 说明 |
|-----|------|------|
| return_1m | DECIMAL(8,4) | 近1月收益率 |
| return_6m | DECIMAL(8,4) | 近半年收益率 |
| return_1y | DECIMAL(8,4) | 近1年收益率 |

#### 风险指标字段（来自 fund_risk_metrics）

| 字段 | 类型 | 说明 |
|-----|------|------|
| max_drawdown_1y | DECIMAL(8,4) | 近1年最大回撤 |
| sharpe_ratio_1y | DECIMAL(8,4) | 近1年夏普比率 |
| annual_volatility_1y | DECIMAL(8,4) | 近1年年化波动率 |

#### 排名字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| rank_in_category | VARCHAR(20) | 同类最新排名（如 "12/345"） |
| rank_category | VARCHAR(50) | 排名所属分类（如 "混合型-偏股"） |

#### 元数据字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |
| metrics_update_time | DATETIME | 指标更新时间 |

#### 完整SQL

```sql
CREATE TABLE portfolio_fund (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    
    -- 持仓信息
    buy_date DATE,
    buy_nav DECIMAL(10,4),  -- 摊薄成本净值
    shares DECIMAL(15,4),
    -- amount DECIMAL(15,2),  -- 已废弃，成本通过 buy_nav × shares 计算
    notes TEXT,
    
    -- 收益指标
    return_1m DECIMAL(8,4),
    return_6m DECIMAL(8,4),
    return_1y DECIMAL(8,4),
    
    -- 风险指标
    max_drawdown_1y DECIMAL(8,4),
    sharpe_ratio_1y DECIMAL(8,4),
    annual_volatility_1y DECIMAL(8,4),
    
    -- 排名
    rank_in_category VARCHAR(20),
    rank_category VARCHAR(50),
    
    -- 元数据
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    metrics_update_time DATETIME,
    
    UNIQUE(portfolio_id, fund_code),
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
);
```

### 3. 持仓历史记录表 (holding_history)

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| id | INTEGER | ✅ | 主键 |
| portfolio_id | INTEGER | ✅ | 所属组合ID |
| fund_code | VARCHAR(10) | ✅ | 基金代码 |
| record_date | DATE | ✅ | 记录日期 |
| shares | DECIMAL(15,4) | ✅ | 持有份额（快照） |
| nav | DECIMAL(10,4) | ❌ | 当日净值 |
| shares_change | DECIMAL(15,4) | ❌ | 份额变化（与上次记录对比） |
| notes | TEXT | ❌ | 备注 |
| create_time | DATETIME | ✅ | 记录创建时间 |

**注意**：市值（market_value）不存储，实时计算：`shares × nav` |

#### 完整SQL

```sql
CREATE TABLE holding_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    fund_code VARCHAR(10) NOT NULL,
    record_date DATE NOT NULL,
    shares DECIMAL(15,4) NOT NULL,
    nav DECIMAL(10,4),
    shares_change DECIMAL(15,4),
    notes TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(portfolio_id, fund_code, record_date),
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
);

CREATE INDEX idx_holding_history_portfolio_fund ON holding_history(portfolio_id, fund_code);
CREATE INDEX idx_holding_history_date ON holding_history(record_date);
```

#### 设计说明

1. **快照模式**：每次记录保存当时的份额快照，而非变化值
2. **差额计算**：shares_change 在插入时自动计算（当前份额 - 上次记录份额）
3. **便于复盘**：可直接查看任意时间点的持仓情况
4. **唯一约束**：同一基金同一天只能有一条记录

---

## 二、接口设计

### 1. 组合管理接口

| 函数 | 说明 | 参数 |
|-----|------|------|
| `create_portfolio(name, description)` | 创建组合 | name, description(可选) |
| `delete_portfolio(portfolio_id)` | 删除组合 | portfolio_id |
| `rename_portfolio(portfolio_id, new_name)` | 重命名组合 | portfolio_id, new_name |
| `update_portfolio_description(portfolio_id, description)` | 更新描述 | portfolio_id, description |
| `list_portfolios()` | 查询所有组合 | 无 |
| `get_portfolio(portfolio_id)` | 获取组合详情 | portfolio_id |

### 2. 成分基金管理接口

| 函数 | 说明 | 参数 |
|-----|------|------|
| `add_fund_to_portfolio(portfolio_id, fund_code, ...)` | 添加成分基金 | portfolio_id, fund_code, buy_date, buy_nav, shares, notes |
| `add_funds_to_portfolio(portfolio_id, fund_codes, exclude_money_market)` | 批量添加成分基金 | portfolio_id, fund_codes, exclude_money_market(默认True，排除货币基金) |
| `remove_fund_from_portfolio(portfolio_id, fund_code)` | 移除成分基金 | portfolio_id, fund_code |
| `update_portfolio_fund(portfolio_id, fund_code, **kwargs)` | 更新成分基金 | portfolio_id, fund_code, 可更新字段 |
| `list_portfolio_funds(portfolio_id)` | 查询组合成分基金 | portfolio_id |
| `refresh_portfolio_fund_metrics(portfolio_id, fund_code)` | 刷新基金指标 | portfolio_id, fund_code |
| `refresh_portfolio_metrics(portfolio_id)` | 刷新组合所有基金指标 | portfolio_id |

### 3. 持仓历史记录接口

| 函数 | 说明 | 参数 |
|-----|------|------|
| `record_holding(portfolio_id, fund_code, shares, record_date, notes)` | 记录持仓快照 | portfolio_id, fund_code, shares, record_date(可选，默认今天), notes |
| `get_holding_history(portfolio_id, fund_code, start_date, end_date)` | 查询持仓历史 | portfolio_id, fund_code(可选), start_date(可选), end_date(可选) |
| `get_latest_holding(portfolio_id, fund_code)` | 获取最近一次持仓记录 | portfolio_id, fund_code |
| `import_holdings_from_file(portfolio_id, file_path)` | 从文件批量导入持仓 | portfolio_id, file_path |

### 4. 持仓计算接口

| 函数 | 说明 | 参数 |
|-----|------|------|
| `get_shares_at_date(portfolio_id, fund_code, target_date)` | 获取指定日期的份额 | portfolio_id, fund_code, target_date |
| `get_market_value_at_date(portfolio_id, fund_code, target_date)` | 获取指定日期的市值 | portfolio_id, fund_code, target_date |
| `get_portfolio_value_at_date(portfolio_id, target_date)` | 获取组合在指定日期的总市值 | portfolio_id, target_date |
| `calculate_profit_loss(portfolio_id, fund_code, from_date, to_date)` | 计算指定时间段盈亏 | portfolio_id, fund_code, from_date, to_date(可选，默认当前) |
| `get_portfolio_profit_loss_report(portfolio_id, from_date, to_date)` | 获取组合盈亏报告 | portfolio_id, from_date, to_date(可选，默认当前) |

---

## 三、指标分类与刷新机制

### 3.1 数据库保存的指标（存储在 portfolio_fund 表）

以下指标存储在数据库中，通过 `metrics_update_time` 字段管理新鲜度（12小时有效期）：

| 指标字段 | 来源表 | 说明 |
|---------|--------|------|
| `return_1m` | fund_performance | 近1月收益率 |
| `return_6m` | fund_performance | 近半年收益率 |
| `return_1y` | fund_performance | 近1年收益率 |
| `max_drawdown_1y` | fund_risk_metrics | 近1年最大回撤 |
| `sharpe_ratio_1y` | fund_risk_metrics | 近1年夏普比率 |
| `annual_volatility_1y` | fund_risk_metrics | 近1年年化波动率 |
| `rank_in_category` | fund_performance | 同类排名（如"12/345"） |
| `rank_category` | fund_info.fund_type | 排名所属分类 |

**刷新触发点**：
1. `get_portfolio_funds_full()` 函数中自动检查并刷新（基于`metrics_update_time`）
2. `refresh_portfolio_metrics(portfolio_id)` 批量刷新接口
3. `refresh_portfolio_fund_metrics(portfolio_id, fund_code)` 单只基金刷新接口

**刷新逻辑**：
```
if metrics_update_time is None:
    需要更新
elif now - metrics_update_time > 12小时:
    需要更新
else:
    使用缓存
```

### 3.2 实时计算的指标（不存数据库）

以下指标在查询时实时计算，不存储在数据库中：

| 指标 | 计算公式 | 计算时机 |
|------|---------|---------|
| 市值 (market_value) | `shares × unit_nav` | 查询时实时计算 |
| 成本 (cost) | `shares × buy_nav` | 查询时实时计算 |
| 盈亏 (profit_loss) | `(unit_nav - buy_nav) × shares` | 查询时实时计算 |
| 收益率 (return_rate) | `(unit_nav - buy_nav) / buy_nav × 100%` | 查询时实时计算 |
| 可用现金 (available_cash) | `total_sell_amount - total_buy_amount` | 查询时实时计算 |

**说明**：
- 实时计算确保盈亏数据始终基于最新净值
- 避免存储冗余数据导致的数据不一致问题
- `buy_nav` 是摊薄后的成本净值，通过交易记录或盈亏导入计算得出
- **可用现金**：根据交易记录实时计算，正数表示净卖出（有可用现金），负数表示净买入（有投入成本）

**可用现金详细说明**：
- **基础数据来源**：`portfolio_transaction` 表的交易记录
  - `total_buy_amount`: 所有买入交易的 `amount` 字段之和（`transaction_type='BUY'`）
  - `total_sell_amount`: 所有卖出交易的 `amount` 字段之和（`transaction_type='SELL'`）
- **计算算法**：
  ```
  1. 查询该基金的所有买入交易记录
     SELECT SUM(amount) FROM portfolio_transaction 
     WHERE portfolio_id=? AND fund_code=? AND transaction_type='BUY'
  
  2. 查询该基金的所有卖出交易记录
     SELECT SUM(amount) FROM portfolio_transaction 
     WHERE portfolio_id=? AND fund_code=? AND transaction_type='SELL'
  
  3. 计算可用现金
     available_cash = total_sell_amount - total_buy_amount
  ```
- **结果解释**：
  - `available_cash > 0`: 净卖出，有可用现金（卖出所得大于买入投入）
  - `available_cash < 0`: 净买入，有投入成本（买入投入大于卖出所得）
  - `available_cash = 0`: 买卖平衡（或无任何交易记录）
- **接口实现**：`calculate_fund_available_cash(portfolio_id, fund_code)` 函数

### 3.3 设计说明

1. **指标字段来源**：收益和风险指标从 `fund_performance` 和 `fund_risk_metrics` 表同步获取
2. **指标更新**：提供独立的 `refresh_*` 接口，可按需更新指标数据
3. **冗余存储**：指标字段冗余存储在成分基金表中，便于快速查询和排序
4. **周期选择**：近1月、近半年、近1年三个常用周期
5. **排名说明**：rank_in_category 为该基金在其所属类型中的最新排名，rank_category 为排名所属分类
6. **货币基金过滤**：批量添加成分基金时，默认排除货币基金（exclude_money_market=True），可通过参数关闭

---

## 四、数据更新策略

### 1. 数据分类与更新原则

| 数据类型 | 更新触发条件 | 数据来源 | 更新方式 |
|---------|-------------|---------|---------|
| 持仓信息（buy_date, buy_nav, shares） | 用户手动更新或盈亏导入时计算 | 用户输入或盈亏导入计算 | 手动调用 update_portfolio_fund 或 import_profit_data |
| 收益指标（return_1m, return_6m, return_1y） | 按需刷新 | fund_performance 表 | 调用 refresh_* 接口 |
| 风险指标（max_drawdown_1y, sharpe_ratio_1y, annual_volatility_1y） | 按需刷新 | fund_risk_metrics 表 | 调用 refresh_* 接口 |
| 排名信息（rank_in_category, rank_category） | 按需刷新 | fund_performance 表 | 调用 refresh_* 接口 |

### 2. 交易日历

使用 AKShare 交易日历接口（`tool_trade_date_hist_sina`），自动识别节假日：

| 函数 | 说明 |
|------|------|
| `sync_trade_calendar(force)` | 同步交易日历数据 |
| `is_trade_day(check_date)` | 判断是否为交易日 |
| `get_latest_trade_day(before_date)` | 获取最近的交易日 |

交易日历数据覆盖到2026年12月31日，自动识别春节、国庆等节假日。

### 3. 数据新鲜度判断算法

#### 净值数据新鲜度

| 基金类型 | 判断条件 | 操作 |
|---------|---------|------|
| 普通基金 | 最新净值日期 >= 最近交易日 | 使用缓存 |
| 普通基金 | 最新净值日期 < 最近交易日 | 需要更新 |
| QDII基金 | 最新净值日期 >= 最近交易日-1天 | 使用缓存 |
| QDII基金 | 最新净值日期 < 最近交易日-1天 | 需要更新 |

**QDII基金特殊处理**：QDII基金投资海外市场，净值延迟一天公布。

#### 持仓数据新鲜度

| 判断条件 | 操作 |
|---------|------|
| 当天已查询过（fund_data_meta 记录） | 使用缓存，不发起API请求 |
| 当天未查询过 | 从AKShare获取 |

**说明**：持仓数据季度更新，无需频繁刷新。

#### 收益指标新鲜度

| 判断条件 | 操作 |
|---------|------|
| metrics_update_time 为空 | 需要更新 |
| metrics_update_time 距今超过 12 小时 | 需要更新 |
| metrics_update_time 距今在 12 小时内 | 使用缓存，不发起API请求 |

#### 风险指标新鲜度

| 判断条件 | 操作 |
|---------|------|
| metrics_update_time 为空 | 需要更新 |
| metrics_update_time 距今超过 12 小时 | 需要更新 |
| metrics_update_time 距今在 12 小时内 | 使用缓存，不发起API请求 |

#### 排名信息新鲜度

| 判断条件 | 操作 |
|---------|------|
| metrics_update_time 为空 | 需要更新 |
| metrics_update_time 距今超过 12 小时 | 需要更新 |
| metrics_update_time 距今在 12 小时内 | 使用缓存，不发起API请求 |

### 4. 跳过行业配置的基金类型

以下基金类型没有股票行业配置，自动跳过查询：
- 债券型-混合一级
- 债券型-长债
- 债券型-中短债
- 债券型-可转债
- 指数型-其他（黄金ETF等）
- 货币型

### 5. 智能刷新流程

```
刷新流程：
1. 查询组合内所有成分基金的 metrics_update_time
2. 筛选需要更新的基金：
   - metrics_update_time 为空 → 需要更新
   - 当前时间 - metrics_update_time > 12小时 → 需要更新
   - 当前时间 - metrics_update_time <= 12小时 → 跳过
3. 对需要更新的基金：
   - 从 fund_performance 表获取收益数据
   - 从 fund_risk_metrics 表获取风险指标
   - 更新 portfolio_fund 表的指标字段
   - 更新 metrics_update_time 为当前时间
4. 返回更新统计：
   - 已更新数量
   - 使用缓存数量
   - 更新失败的基金（如有）
```

### 4. 刷新接口行为

| 接口 | 行为 |
|-----|------|
| `refresh_portfolio_fund_metrics(portfolio_id, fund_code)` | 强制刷新单只基金指标，忽略新鲜度判断 |
| `refresh_portfolio_metrics(portfolio_id)` | 智能刷新，只更新过期数据 |
| `refresh_portfolio_metrics(portfolio_id, force=True)` | 强制刷新所有基金指标 |

### 5. 数据依赖关系

```
portfolio_fund 指标数据依赖链：

portfolio_fund.return_*  ←  fund_performance.period_return
portfolio_fund.max_drawdown_1y  ←  fund_risk_metrics.max_drawdown
portfolio_fund.sharpe_ratio_1y  ←  fund_risk_metrics.sharpe_ratio
portfolio_fund.annual_volatility_1y  ←  fund_risk_metrics.annual_volatility
portfolio_fund.rank_in_category  ←  fund_performance.rank_in_category
```

**注意**：如果 fund_performance 或 fund_risk_metrics 表中没有对应基金的数据，需要先调用 sync_group_performance 或 sync_group_risk_metrics 同步数据。

---

## 五、持仓计算算法

### 1. 份额查询算法

**目的**：获取指定日期的份额（基于快照记录）

```
算法：get_shares_at_date(portfolio_id, fund_code, target_date)

输入：组合ID、基金代码、目标日期
输出：目标日期的份额

步骤：
1. 查询 holding_history 表，获取该基金在 target_date 当天或之前最近的记录
2. 返回该记录的 shares 字段

SQL：
  SELECT shares FROM holding_history 
  WHERE portfolio_id = ? AND fund_code = ? AND record_date <= ?
  ORDER BY record_date DESC LIMIT 1
```

### 2. 市值计算算法

**目的**：计算任意时间点的持仓市值

```
算法：get_market_value_at_date(portfolio_id, fund_code, target_date)

输入：组合ID、基金代码、目标日期
输出：目标日期的市值

步骤：
1. 调用 get_shares_at_date() 获取目标日期的份额
2. 查询 fund_nav 表，获取目标日期的净值
   - 如果目标日期没有净值数据，取该日期之前最近的净值
3. 计算市值 = 份额 × 净值

公式：
  market_value = shares_at_date × nav_at_date
```

### 3. 盈亏计算算法

**目的**：计算从某时间点到当前（或指定时间点）的盈亏

```
算法：calculate_profit_loss(portfolio_id, fund_code, from_date, to_date)

输入：组合ID、基金代码、起始日期、结束日期（可选，默认当前）
输出：盈亏报告

步骤：
1. 获取起始日期份额：shares_from = get_shares_at_date(from_date)
2. 获取结束日期份额：shares_to = get_shares_at_date(to_date)
3. 获取起始日期净值：nav_from = get_nav_at_date(from_date)
4. 获取结束日期净值：nav_to = get_nav_at_date(to_date)
5. 计算市值：
   value_from = shares_from × nav_from
   value_to = shares_to × nav_to
6. 计算期间份额变化总额：
   查询 holding_history 表，获取 from_date 到 to_date 之间的所有记录
   total_shares_change = Σ(shares_change) where from_date < record_date <= to_date
7. 计算盈亏：
   profit_loss = value_to - value_from
   注：如果期间有加仓/减仓，盈亏计算需要考虑份额变化

返回：
{
    "fund_code": "000001",
    "fund_name": "华夏成长",
    "from_date": "2025-01-01",
    "to_date": "2026-02-15",
    "shares_from": 1000.00,
    "shares_to": 1500.00,
    "nav_from": 1.500,
    "nav_to": 1.600,
    "value_from": 15000.00,
    "value_to": 24000.00,
    "shares_change": 500.00,
    "profit_loss": 9000.00
}
```

### 4. 组合盈亏报告算法

**目的**：计算整个组合的盈亏情况

```
算法：get_portfolio_profit_loss_report(portfolio_id, from_date, to_date)

输入：组合ID、起始日期、结束日期（可选）
输出：组合盈亏报告

步骤：
1. 查询组合内所有成分基金
2. 对每只基金调用 calculate_profit_loss()
3. 汇总计算：
   - 总起始市值
   - 总结束市值
   - 总盈亏

返回：
{
    "portfolio_id": 1,
    "portfolio_name": "我的组合",
    "from_date": "2025-01-01",
    "to_date": "2026-02-15",
    "total_value_from": 100000.00,
    "total_value_to": 130000.00,
    "total_profit_loss": 30000.00,
    "funds": [
        {
            "fund_code": "000001",
            "fund_name": "华夏成长",
            "value_from": 15000.00,
            "value_to": 24000.00,
            "profit_loss": 9000.00
        },
        ...
    ]
}
```

### 5. 盈亏数据导入算法

**目的**：从外部导入盈亏数据，反算成本净值（buy_nav）并更新持仓信息

```
算法：import_profit_data(portfolio_id, profit_data, import_mode)

输入：组合ID、盈亏数据列表、导入模式（覆盖/累加）
输出：导入结果统计

输入数据格式：
{
    "fund_code": "000001",      // 基金代码
    "fund_name": "华夏成长",   // 基金名称（可选）
    "current_value": 10000,     // 当前市值
    "profit_loss": 1000         // 盈亏金额（仅用于计算成本净值，不存储）
}

计算步骤：
1. 计算成本：cost = current_value - profit_loss
2. 计算份额（假设净值为1）：shares = current_value / 1.0
3. 计算成本净值（摊薄）：buy_nav = cost / shares

导入逻辑（覆盖模式）：
1. 查询该基金是否已存在
2. 如果存在且为覆盖模式：
   - 更新 portfolio_fund 表：
     * shares = 计算的份额
     * buy_nav = 成本净值（摊薄后）
3. 如果不存在：
   - 插入新记录到 portfolio_fund 表

导入逻辑（累加模式）：
1. 查询该基金现有数据（shares, buy_nav）
2. 累加计算：
   * old_cost = old_shares × old_buy_nav
   * new_cost = current_value - profit_loss
   * total_shares = old_shares + new_shares
   * total_cost = old_cost + new_cost
   * accumulated_buy_nav = total_cost / total_shares
3. 更新 portfolio_fund 表

核心公式：
  成本 = 当前市值 - 盈亏
  份额 = 当前市值 / 1.0（假设）
  成本净值(buy_nav) = 成本 / 份额 = (当前市值 - 盈亏) / 当前市值

盈亏实时计算（不存储）：
  市值 = latest_nav × shares
  成本 = buy_nav × shares
  盈亏 = 市值 - 成本 = (latest_nav - buy_nav) × shares
  收益率 = (latest_nav - buy_nav) / buy_nav × 100%

注意：
- 只存储buy_nav（摊薄成本净值），不存储profit_loss
- 盈亏、收益率都通过实时计算得出，随净值变化而更新
- `amount`字段已废弃，成本通过 `buy_nav × shares` 实时计算
```

### 6. 记录持仓快照流程

```
流程：record_holding(portfolio_id, fund_code, shares, record_date, notes)

步骤：
1. 如果 record_date 为空，使用当前日期
2. 查询该基金上一次的持仓记录：
   SELECT shares FROM holding_history 
   WHERE portfolio_id = ? AND fund_code = ? AND record_date < ?
   ORDER BY record_date DESC LIMIT 1
3. 计算份额变化：
   shares_change = shares - last_shares (如果无上次记录，shares_change = NULL)
4. 获取当日净值：
   nav = get_nav_at_date(record_date)
5. 计算市值（不存储，仅用于返回）：
   market_value = shares × nav
6. 插入记录：
   INSERT INTO holding_history (
       portfolio_id, fund_code, record_date, shares, nav, shares_change, notes
   ) VALUES (...)
7. 同步更新 portfolio_fund 表的当前份额：
   UPDATE portfolio_fund SET shares = ?, update_time = NOW()
8. 返回记录
```

---

## 六、交易维护算法

### 1. 核心公式

#### 买入交易

**输入参数：**
- 原持仓数量：`old_shares`
- 原成本净值：`old_buy_nav`
- 买入份额：`buy_shares`
- 买入投入金额：`buy_amount`

**计算公式：**
```
新持仓数量 = 原持仓数量 + 买入份额
            new_shares = old_shares + buy_shares

新成本净值 = (原持仓数量 × 原成本净值 + 买入投入金额) / 新持仓数量
            new_buy_nav = (old_shares × old_buy_nav + buy_amount) / new_shares
```

**示例：**
- 原持仓：1000份，成本净值1.5元
- 买入：500份，投入金额800元
- 新持仓：1000 + 500 = 1500份
- 新成本净值：(1000 × 1.5 + 800) / 1500 = 2300 / 1500 = 1.5333元

#### 卖出交易

**输入参数：**
- 原持仓数量：`old_shares`
- 原成本净值：`old_buy_nav`
- 卖出份额：`sell_shares`
- 卖出获得金额：`sell_amount`

**计算公式：**
```
新持仓数量 = 原持仓数量 - 卖出份额
            new_shares = old_shares - sell_shares

新成本净值 = (原持仓数量 × 原成本净值 - 卖出获得金额) / 新持仓数量
            new_buy_nav = (old_shares × old_buy_nav - sell_amount) / new_shares

现金增加额 = 卖出获得金额
```

**示例：**
- 原持仓：1500份，成本净值1.5333元
- 卖出：300份，获得金额500元
- 新持仓：1500 - 300 = 1200份
- 新成本净值：(1500 × 1.5333 - 500) / 1200 = 1800 / 1200 = 1.5元
- 现金增加：500元

**特殊情况：**
- 全部卖出时（new_shares = 0），清空成本净值，删除持仓记录
- 成本净值不能为负数，如果计算结果为负则设为0

### 2. 交易记录表

```sql
CREATE TABLE portfolio_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    fund_code VARCHAR(10) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,  -- BUY/SELL
    transaction_date DATE NOT NULL,
    shares DECIMAL(15,4) NOT NULL,          -- 交易份额
    amount DECIMAL(15,2) NOT NULL,          -- 交易金额
    nav DECIMAL(10,4),                      -- 交易时净值（仅记录，不参与计算）
    fee DECIMAL(10,2) DEFAULT 0,            -- 手续费
    notes TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
);
```

### 3. 现金管理

组合表增加现金字段：
```sql
ALTER TABLE portfolio ADD COLUMN cash DECIMAL(15,2) DEFAULT 0;
```

**现金变动规则：**
- 卖出交易：现金增加 = 卖出获得金额
- 买入交易：不减少现金（假设使用外部资金）
- 手动调整：可直接修改现金余额

### 4. 接口列表

| 接口 | 功能 | 关键参数 |
|-----|------|---------|
| `record_buy_transaction()` | 记录买入 | portfolio_id, fund_code, shares, amount |
| `record_sell_transaction()` | 记录卖出 | portfolio_id, fund_code, shares, amount |
| `get_portfolio_transactions()` | 查询交易记录 | portfolio_id, fund_code(可选), type(可选) |
| `update_portfolio_cash()` | 更新现金 | portfolio_id, cash |
| `get_portfolio_cash()` | 获取现金 | portfolio_id |

---

## 七、变更记录

| 日期 | 版本 | 变更内容 |
|-----|------|---------|
| 2026-02-15 | v0.1 | 初始设计文档 |
| 2026-02-15 | v0.2 | 简化周期：保留近1月、近半年、近1年；排名改为同类最新排名 |
| 2026-02-15 | v0.3 | 新增 rank_category 字段，记录排名所属分类 |
| 2026-02-15 | v0.4 | 新增批量添加接口，默认排除货币基金 |
| 2026-02-15 | v0.5 | 新增数据更新策略章节：数据分类、新鲜度判断算法、智能刷新流程 |
| 2026-02-15 | v0.6 | 新鲜度有效期从24小时改为12小时 |
| 2026-02-15 | v0.7 | 新增持仓变化记录表、持仓计算算法（份额还原、市值计算、盈亏计算） |
| 2026-02-15 | v0.8 | 重构持仓历史表：改为快照模式，直接记录份额而非变化值，简化算法 |
| 2026-02-16 | v0.9 | 新增交易日历机制：使用AKShare交易日历接口，自动识别节假日 |
| 2026-02-16 | v1.0 | 优化数据新鲜度机制：QDII基金净值延迟处理、持仓数据当天查过不再查询、跳过无效行业配置查询 |
| 2026-02-17 | v1.2 | 盈亏改为实时计算，不再存储`profit_loss`字段；导入盈亏只计算并存储`buy_nav`（摊薄成本净值）|
| 2026-02-17 | v1.3 | 新增交易维护功能：买入/卖出交易记录、成本净值自动计算、现金管理 |
| 2026-02-17 | v1.4 | 完善指标分类文档：明确区分数据库存储指标和实时计算指标，统一`amount`字段废弃说明 |
