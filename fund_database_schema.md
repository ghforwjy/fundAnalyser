# 基金数据库设计方案 (SQLite)

## 一、数据库概述

本数据库设计用于存储和管理基金相关的全量数据，包括：
- 基金基本信息
- 基金净值历史数据
- 基金持仓明细
- 基金经理信息
- 基金分类和主题标签
- 基金统计指标

## 二、ER图设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           基金数据库 ER 图                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │   fund_info     │         │  fund_manager   │         │ manager_fund_   │
    │  (基金基本信息)  │◄────────│  (基金经理信息)  │◄────────│    history      │
    └────────┬────────┘         └─────────────────┘         │(基金经理任职史) │
             │                                               └─────────────────┘
             │ 1:N
             ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │  fund_nav       │         │fund_stock_holding         │fund_bond_holding│
    │ (基金净值数据)   │         │ (基金股票持仓)   │         │ (基金债券持仓)   │
    └─────────────────┘         └─────────────────┘         └─────────────────┘
             │
             │ 1:N
             ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │ fund_statistics │         │  fund_category  │         │   fund_tags     │
    │ (基金统计指标)   │         │  (基金分类关联)  │◄────────│  (基金主题标签)  │
    └─────────────────┘         └─────────────────┘         └─────────────────┘
             │                           │
             │ 1:N                       │ N:1
             ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ data_update_log │         │  category_dict  │
    │  (更新日志表)    │         │  (分类字典表)    │
    └─────────────────┘         └─────────────────┘
```

## 三、表结构设计

### 3.1 基金基本信息表 (fund_info)

存储基金的基本属性信息，是核心主表。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| fund_code | VARCHAR(10) | PRIMARY KEY | 基金代码（唯一标识） |
| fund_name | VARCHAR(100) | NOT NULL | 基金全称 |
| fund_abbr | VARCHAR(50) | | 基金简称 |
| fund_type | VARCHAR(20) | NOT NULL | 基金类型（股票型/债券型/混合型/货币型/指数型/QDII/FOF） |
| sub_type | VARCHAR(30) | | 基金子类型 |
| establish_date | DATE | | 成立日期 |
| manager_company | VARCHAR(100) | | 基金管理人 |
| custodian | VARCHAR(100) | | 基金托管人 |
| benchmark | VARCHAR(200) | | 业绩比较基准 |
| manage_fee_rate | DECIMAL(5,4) | | 管理费率（如0.0150表示1.50%） |
| custodian_fee_rate | DECIMAL(5,4) | | 托管费率 |
| risk_level | TINYINT | CHECK(1-5) | 风险等级（1-5级） |
| min_purchase_amount | DECIMAL(12,2) | | 最低申购金额 |
| status | VARCHAR(10) | DEFAULT '正常' | 基金状态（正常/暂停/清盘） |
| invest_style | VARCHAR(50) | | 投资风格（成长型/价值型/平衡型） |
| invest_scope | TEXT | | 投资范围描述 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录更新时间 |

**索引设计：**
```sql
CREATE INDEX idx_fund_type ON fund_info(fund_type);
CREATE INDEX idx_fund_company ON fund_info(manager_company);
CREATE INDEX idx_risk_level ON fund_info(risk_level);
CREATE INDEX idx_fund_status ON fund_info(status);
```

---

### 3.2 基金净值数据表 (fund_nav)

存储基金每日净值数据，数据量大，需要高效的时间范围查询。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| nav_date | DATE | NOT NULL | 净值日期 |
| unit_nav | DECIMAL(10,4) | NOT NULL | 单位净值 |
| accum_nav | DECIMAL(10,4) | | 累计净值 |
| daily_return | DECIMAL(8,4) | | 日增长率（%） |
| subscribe_status | VARCHAR(10) | | 申购状态（开放/暂停/限制） |
| redeem_status | VARCHAR(10) | | 赎回状态 |
| dividend | DECIMAL(10,4) | DEFAULT 0 | 每份分红金额 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(fund_code, nav_date)  -- 同一基金同一天只能有一条记录
```

**索引设计：**
```sql
CREATE INDEX idx_nav_fund_code ON fund_nav(fund_code);
CREATE INDEX idx_nav_date ON fund_nav(nav_date);
CREATE INDEX idx_nav_fund_date ON fund_nav(fund_code, nav_date);  -- 复合索引，用于时间范围查询
CREATE INDEX idx_nav_return ON fund_nav(daily_return);  -- 用于收益率排序查询
```

---

### 3.3 基金股票持仓表 (fund_stock_holding)

存储基金季度股票持仓明细。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| report_date | DATE | NOT NULL | 报告期（如2024-03-31） |
| stock_code | VARCHAR(10) | NOT NULL | 股票代码 |
| stock_name | VARCHAR(50) | | 股票名称 |
| nav_ratio | DECIMAL(6,2) | | 占净值比例（%） |
| share_count | BIGINT | | 持股数量（股） |
| market_value | DECIMAL(15,2) | | 持仓市值（元） |
| rank_num | SMALLINT | | 持仓排名（前十大重仓） |
| sector | VARCHAR(30) | | 所属行业 |
| change_type | VARCHAR(10) | | 变动类型（新增/增持/减持/不变） |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(fund_code, report_date, stock_code)  -- 同一基金同一报告期同一股票唯一
```

**索引设计：**
```sql
CREATE INDEX idx_stock_fund_code ON fund_stock_holding(fund_code);
CREATE INDEX idx_stock_report_date ON fund_stock_holding(report_date);
CREATE INDEX idx_stock_code ON fund_stock_holding(stock_code);
CREATE INDEX idx_stock_fund_report ON fund_stock_holding(fund_code, report_date);
CREATE INDEX idx_stock_sector ON fund_stock_holding(sector);
```

---

### 3.4 基金债券持仓表 (fund_bond_holding)

存储基金季度债券持仓明细。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| report_date | DATE | NOT NULL | 报告期 |
| bond_code | VARCHAR(20) | NOT NULL | 债券代码 |
| bond_name | VARCHAR(100) | | 债券名称 |
| bond_type | VARCHAR(30) | | 债券类型（国债/金融债/企业债等） |
| nav_ratio | DECIMAL(6,2) | | 占净值比例（%） |
| market_value | DECIMAL(15,2) | | 持仓市值（元） |
| rank_num | SMALLINT | | 持仓排名 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(fund_code, report_date, bond_code)
```

**索引设计：**
```sql
CREATE INDEX idx_bond_fund_code ON fund_bond_holding(fund_code);
CREATE INDEX idx_bond_report_date ON fund_bond_holding(report_date);
CREATE INDEX idx_bond_fund_report ON fund_bond_holding(fund_code, report_date);
```

---

### 3.5 基金经理信息表 (fund_manager)

存储基金经理基本信息。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| manager_id | VARCHAR(20) | PRIMARY KEY | 基金经理ID |
| manager_name | VARCHAR(50) | NOT NULL | 基金经理姓名 |
| gender | CHAR(1) | | 性别 |
| education | VARCHAR(20) | | 学历 |
| entry_date | DATE | | 入行日期 |
| company | VARCHAR(100) | | 所属公司 |
| introduction | TEXT | | 基金经理简介 |
| invest_style | VARCHAR(50) | | 投资风格 |
| total_scale | DECIMAL(15,2) | | 管理总规模（亿元） |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录更新时间 |

**索引设计：**
```sql
CREATE INDEX idx_manager_name ON fund_manager(manager_name);
CREATE INDEX idx_manager_company ON fund_manager(company);
```

---

### 3.6 基金经理任职历史表 (manager_fund_history)

存储基金经理管理基金的任职历史（多对多关系）。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| manager_id | VARCHAR(20) | NOT NULL, FK | 基金经理ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| start_date | DATE | NOT NULL | 任职开始日期 |
| end_date | DATE | | 任职结束日期（NULL表示现任） |
| tenure_return | DECIMAL(8,2) | | 任职期间收益率（%） |
| is_current | BOOLEAN | DEFAULT 1 | 是否现任 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(manager_id, fund_code, start_date)  -- 同一基金经理同一基金同一开始日期唯一
CHECK (end_date IS NULL OR end_date >= start_date)
```

**索引设计：**
```sql
CREATE INDEX idx_mfh_manager ON manager_fund_history(manager_id);
CREATE INDEX idx_mfh_fund ON manager_fund_history(fund_code);
CREATE INDEX idx_mfh_current ON manager_fund_history(is_current);
CREATE INDEX idx_mfh_dates ON manager_fund_history(start_date, end_date);
```

---

### 3.7 基金分类字典表 (category_dict)

存储基金分类的标准定义。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| category_id | INTEGER | PRIMARY KEY AUTOINCREMENT | 分类ID |
| category_code | VARCHAR(20) | UNIQUE NOT NULL | 分类代码 |
| category_name | VARCHAR(50) | NOT NULL | 分类名称 |
| parent_id | INTEGER | FK | 父分类ID（支持多级分类） |
| category_level | TINYINT | NOT NULL | 分类级别（1=一级，2=二级，3=三级） |
| description | VARCHAR(200) | | 分类描述 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**索引设计：**
```sql
CREATE INDEX idx_cat_parent ON category_dict(parent_id);
CREATE INDEX idx_cat_level ON category_dict(category_level);
```

---

### 3.8 基金分类关联表 (fund_category)

存储基金与分类的多对多关系。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| category_id | INTEGER | NOT NULL, FK | 分类ID |
| is_primary | BOOLEAN | DEFAULT 0 | 是否主要分类 |
| assign_date | DATE | | 分类分配日期 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(fund_code, category_id)
```

**索引设计：**
```sql
CREATE INDEX idx_fc_fund ON fund_category(fund_code);
CREATE INDEX idx_fc_category ON fund_category(category_id);
CREATE INDEX idx_fc_primary ON fund_category(is_primary);
```

---

### 3.9 基金主题标签表 (fund_tags)

存储基金的主题标签（如科技、医药、消费等）。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| tag_name | VARCHAR(30) | NOT NULL | 标签名称 |
| tag_type | VARCHAR(20) | | 标签类型（行业/主题/策略/风格） |
| confidence | DECIMAL(3,2) | DEFAULT 1.00 | 置信度（0-1） |
| source | VARCHAR(20) | | 标签来源（人工/算法） |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(fund_code, tag_name)
CHECK(confidence BETWEEN 0 AND 1)
```

**索引设计：**
```sql
CREATE INDEX idx_tag_fund ON fund_tags(fund_code);
CREATE INDEX idx_tag_name ON fund_tags(tag_name);
CREATE INDEX idx_tag_type ON fund_tags(tag_type);
```

---

### 3.10 基金统计指标表 (fund_statistics)

存储基金的各种统计指标（收益率、风险指标等）。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| fund_code | VARCHAR(10) | NOT NULL, FK | 基金代码 |
| calc_date | DATE | NOT NULL | 计算日期 |
| period_type | VARCHAR(10) | NOT NULL | 周期类型（1M/3M/6M/1Y/3Y/5Y/ALL） |
| **收益率指标** ||||
| return_rate | DECIMAL(8,2) | | 区间收益率（%） |
| annualized_return | DECIMAL(8,2) | | 年化收益率（%） |
| excess_return | DECIMAL(8,2) | | 超额收益率（相对基准） |
| **风险指标** ||||
| max_drawdown | DECIMAL(8,2) | | 最大回撤（%） |
| volatility | DECIMAL(6,2) | | 波动率（%） |
| downside_volatility | DECIMAL(6,2) | | 下行波动率（%） |
| var_95 | DECIMAL(8,2) | | 风险价值VaR（95%置信度） |
| **风险调整收益指标** ||||
| sharpe_ratio | DECIMAL(6,2) | | 夏普比率 |
| sortino_ratio | DECIMAL(6,2) | | 索提诺比率 |
| calmar_ratio | DECIMAL(6,2) | | 卡玛比率 |
| treynor_ratio | DECIMAL(6,2) | | 特雷诺比率 |
| information_ratio | DECIMAL(6,2) | | 信息比率 |
| **其他指标** ||||
| alpha | DECIMAL(8,4) | | 阿尔法 |
| beta | DECIMAL(6,4) | | 贝塔 |
| win_rate | DECIMAL(5,2) | | 胜率（%） |
| profit_loss_ratio | DECIMAL(6,2) | | 盈亏比 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**约束：**
```sql
UNIQUE(fund_code, calc_date, period_type)
```

**索引设计：**
```sql
CREATE INDEX idx_stat_fund ON fund_statistics(fund_code);
CREATE INDEX idx_stat_date ON fund_statistics(calc_date);
CREATE INDEX idx_stat_period ON fund_statistics(period_type);
CREATE INDEX idx_stat_fund_period ON fund_statistics(fund_code, period_type);
CREATE INDEX idx_stat_sharpe ON fund_statistics(sharpe_ratio);
CREATE INDEX idx_stat_return ON fund_statistics(return_rate);
```

---

### 3.11 数据更新日志表 (data_update_log)

记录数据更新历史，便于追踪和审计。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| table_name | VARCHAR(50) | NOT NULL | 更新的表名 |
| update_type | VARCHAR(20) | NOT NULL | 更新类型（FULL/INCREMENTAL） |
| start_time | DATETIME | NOT NULL | 更新开始时间 |
| end_time | DATETIME | | 更新结束时间 |
| record_count | INTEGER | | 更新记录数 |
| status | VARCHAR(20) | | 状态（SUCCESS/FAILED/RUNNING） |
| message | TEXT | | 更新信息/错误信息 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**索引设计：**
```sql
CREATE INDEX idx_log_table ON data_update_log(table_name);
CREATE INDEX idx_log_time ON data_update_log(start_time);
CREATE INDEX idx_log_status ON data_update_log(status);
```

---

## 四、表关系图（详细版）

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              表关系详细说明                                   │
└──────────────────────────────────────────────────────────────────────────────┘

fund_info (基金基本信息)
    ├── 1:N ──► fund_nav (基金净值数据)
    │              PK: (fund_code, nav_date)
    │
    ├── 1:N ──► fund_stock_holding (基金股票持仓)
    │              PK: (fund_code, report_date, stock_code)
    │
    ├── 1:N ──► fund_bond_holding (基金债券持仓)
    │              PK: (fund_code, report_date, bond_code)
    │
    ├── 1:N ──► fund_statistics (基金统计指标)
    │              PK: (fund_code, calc_date, period_type)
    │
    ├── 1:N ──► fund_category (基金分类关联)
    │              PK: (fund_code, category_id)
    │              N:1 ──► category_dict (分类字典)
    │
    ├── 1:N ──► fund_tags (基金主题标签)
    │              PK: (fund_code, tag_name)
    │
    └── 1:N ──► manager_fund_history (基金经理任职历史)
                   PK: (manager_id, fund_code, start_date)
                   N:1 ──► fund_manager (基金经理信息)

```

## 五、数据更新策略

### 5.1 增量更新策略

对于净值数据等高频更新数据，采用增量更新策略：

1. **首次全量导入**：导入历史全部数据
2. **日常增量更新**：
   - 查询数据库中最新日期
   - 只导入新日期的数据
   - 使用 `INSERT OR REPLACE` 处理可能的重叠数据

### 5.2 持仓数据更新策略

持仓数据按季度更新：

1. **报告期识别**：每年4个报告期（3-31, 6-30, 9-30, 12-31）
2. **增量更新**：只更新最新报告期的数据
3. **历史数据保留**：保留所有历史报告期数据用于分析

### 5.3 统计指标计算策略

统计指标定期批量计算：

1. **每日收盘后**：计算当日收益率相关指标
2. **每周/每月**：批量计算风险指标（需要历史数据窗口）
3. **使用事务**：确保数据一致性

### 5.4 更新SQL示例

```sql
-- 净值数据增量更新示例
INSERT OR REPLACE INTO fund_nav 
(fund_code, nav_date, unit_nav, accum_nav, daily_return, subscribe_status, redeem_status)
VALUES (?, ?, ?, ?, ?, ?, ?);

-- 批量更新统计指标（使用事务）
BEGIN TRANSACTION;
    DELETE FROM fund_statistics 
    WHERE fund_code = ? AND calc_date = ? AND period_type = ?;
    
    INSERT INTO fund_statistics 
    (fund_code, calc_date, period_type, return_rate, sharpe_ratio, max_drawdown, ...)
    VALUES (?, ?, ?, ?, ?, ?, ...);
COMMIT;
```

## 六、查询优化建议

### 6.1 常用查询场景及优化

| 查询场景 | 优化建议 |
|----------|----------|
| 查询某基金历史净值 | 使用 `fund_code + nav_date` 复合索引 |
| 查询某日期所有基金净值 | 使用 `nav_date` 单列索引 |
| 查询基金持仓变化 | 使用 `fund_code + report_date` 复合索引 |
| 按收益率排序 | 在 `fund_statistics` 表建立 `return_rate` 索引 |
| 查询某主题的所有基金 | 使用 `fund_tags` 表的 `tag_name` 索引 |
| 时间范围查询 | 使用 `BETWEEN` 配合复合索引 |

### 6.2 分页查询优化

```sql
-- 推荐：使用游标分页（对于大数据量）
SELECT * FROM fund_nav 
WHERE fund_code = '000001' AND nav_date < '2024-01-01'
ORDER BY nav_date DESC
LIMIT 100;

-- 避免：使用 OFFSET 进行深分页
-- SELECT * FROM fund_nav LIMIT 1000000, 100;  -- 性能差
```

### 6.3 聚合查询优化

```sql
-- 使用索引覆盖查询
SELECT nav_date, unit_nav, daily_return 
FROM fund_nav 
WHERE fund_code = '000001' 
AND nav_date BETWEEN '2023-01-01' AND '2023-12-31';

-- 预计算常用聚合值（存储在 fund_statistics 表中）
SELECT * FROM fund_statistics 
WHERE fund_code = '000001' AND period_type = '1Y';
```

## 七、SQLite特定优化技巧

### 7.1 数据库配置优化

```sql
-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 设置缓存大小（页数，每页约4KB）
PRAGMA cache_size = -64000;  -- 约256MB缓存

-- 设置临时存储为内存
PRAGMA temp_store = MEMORY;

-- 设置同步模式（权衡性能和数据安全）
PRAGMA synchronous = NORMAL;  -- 推荐设置

-- 设置日志模式
PRAGMA journal_mode = WAL;  -- 写前日志，提高并发性能

-- 设置页大小
PRAGMA page_size = 4096;
```

### 7.2 批量插入优化

```sql
-- 使用事务批量插入
BEGIN TRANSACTION;
    INSERT INTO fund_nav VALUES (...);
    INSERT INTO fund_nav VALUES (...);
    -- ... 更多插入
COMMIT;

-- 使用预编译语句（在应用程序中）
-- 关闭自动提交，手动控制事务
```

### 7.3 查询优化

```sql
-- 使用 EXPLAIN QUERY PLAN 分析查询
EXPLAIN QUERY PLAN 
SELECT * FROM fund_nav WHERE fund_code = '000001';

-- 使用 ANALYZE 更新统计信息
ANALYZE;

-- 使用 VACUUM 整理数据库
VACUUM;
```

### 7.4 数据类型选择

| 数据类型 | 适用场景 | 说明 |
|----------|----------|------|
| INTEGER | ID、计数、日期存储 | 使用Unix时间戳存储日期 |
| REAL | 浮点计算 | 避免精度问题 |
| NUMERIC/DECIMAL | 货币金额 | 使用定点数存储 |
| TEXT | 字符串 | 使用UTF-8编码 |
| BLOB | 二进制数据 | 存储图片等 |

### 7.5 存储优化

```sql
-- 使用 WITHOUT ROWID 优化查询表（小表）
CREATE TABLE category_dict (
    category_code VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(50)
) WITHOUT ROWID;

-- 使用 STRICT 表（SQLite 3.37+）
CREATE TABLE fund_info (
    fund_code TEXT PRIMARY KEY,
    fund_name TEXT NOT NULL,
    manage_fee_rate REAL
) STRICT;
```

## 八、数据完整性约束

### 8.1 外键约束

```sql
-- 基金净值表外键
ALTER TABLE fund_nav ADD CONSTRAINT fk_nav_fund 
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) 
    ON DELETE CASCADE ON UPDATE CASCADE;

-- 持仓表外键
ALTER TABLE fund_stock_holding ADD CONSTRAINT fk_stock_fund 
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) 
    ON DELETE CASCADE;

-- 基金经理任职历史外键
ALTER TABLE manager_fund_history ADD CONSTRAINT fk_mfh_manager 
    FOREIGN KEY (manager_id) REFERENCES fund_manager(manager_id);
    
ALTER TABLE manager_fund_history ADD CONSTRAINT fk_mfh_fund 
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code);
```

### 8.2 检查约束

```sql
-- 风险等级检查
ALTER TABLE fund_info ADD CONSTRAINT chk_risk_level 
    CHECK (risk_level BETWEEN 1 AND 5);

-- 费率检查
ALTER TABLE fund_info ADD CONSTRAINT chk_fee_rate 
    CHECK (manage_fee_rate >= 0 AND manage_fee_rate <= 1);

-- 日期有效性检查
ALTER TABLE manager_fund_history ADD CONSTRAINT chk_dates 
    CHECK (end_date IS NULL OR end_date >= start_date);
```

## 九、备份和恢复策略

### 9.1 备份策略

```sql
-- 在线备份（使用备份API）
-- 在应用程序中使用 sqlite3_backup_init()

-- 命令行备份
-- sqlite3 fund.db ".backup 'fund_backup.db'"

-- 导出为SQL
-- sqlite3 fund.db ".dump" > fund_backup.sql
```

### 9.2 恢复策略

```sql
-- 从备份恢复
-- sqlite3 fund_backup.db ".backup 'fund.db'"

-- 从SQL导入
-- sqlite3 fund.db < fund_backup.sql
```

## 十、扩展设计

### 10.1 支持的数据扩展

| 扩展表 | 用途 |
|--------|------|
| fund_dividend | 基金分红记录 |
| fund_split | 基金拆分记录 |
| fund_scale | 基金规模历史 |
| fund_shareholder | 基金持有人结构 |
| fund_transaction_fee | 交易费率表 |
| fund_notice | 基金公告信息 |
| fund_rating | 基金评级信息 |

### 10.2 视图设计

```sql
-- 基金基本信息视图
CREATE VIEW v_fund_basic AS
SELECT 
    f.fund_code,
    f.fund_name,
    f.fund_type,
    f.risk_level,
    f.manager_company,
    m.manager_name,
    m.total_scale
FROM fund_info f
LEFT JOIN manager_fund_history mf ON f.fund_code = mf.fund_code AND mf.is_current = 1
LEFT JOIN fund_manager m ON mf.manager_id = m.manager_id;

-- 最新净值视图
CREATE VIEW v_latest_nav AS
SELECT 
    fund_code,
    unit_nav,
    accum_nav,
    daily_return,
    nav_date
FROM fund_nav
WHERE (fund_code, nav_date) IN (
    SELECT fund_code, MAX(nav_date) 
    FROM fund_nav 
    GROUP BY fund_code
);
```

---

## 附录A: 常用查询示例

### A.1 查询基金基本信息
```sql
SELECT * FROM fund_info WHERE fund_code = '000001';
```

### A.2 查询基金历史净值
```sql
SELECT * FROM fund_nav 
WHERE fund_code = '000001' 
AND nav_date BETWEEN '2023-01-01' AND '2023-12-31'
ORDER BY nav_date;
```

### A.3 查询基金最新持仓
```sql
SELECT * FROM fund_stock_holding 
WHERE fund_code = '000001' 
AND report_date = (SELECT MAX(report_date) FROM fund_stock_holding WHERE fund_code = '000001')
ORDER BY nav_ratio DESC;
```

### A.4 查询某主题的所有基金
```sql
SELECT DISTINCT f.* FROM fund_info f
JOIN fund_tags t ON f.fund_code = t.fund_code
WHERE t.tag_name = '科技';
```

### A.5 查询收益率排名前10的基金
```sql
SELECT f.fund_code, f.fund_name, s.return_rate, s.sharpe_ratio
FROM fund_statistics s
JOIN fund_info f ON s.fund_code = f.fund_code
WHERE s.period_type = '1Y'
ORDER BY s.return_rate DESC
LIMIT 10;
```

---

*文档版本: 1.0*
*设计日期: 2024年*
*数据库引擎: SQLite 3.35+*
