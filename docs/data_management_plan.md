# 基金分析系统数据维护方案

> 文档版本：1.0  
> 更新日期：2026-02-15  
> 作者：AI Assistant

---

## 一、数据分类体系

根据业务需求，我们将数据分为三大类：

### 1.1 全局数据（Global Data）
**定义**：所有基金的基础数据，不针对特定分组或持仓
**特点**：
- 数据量大（全市场基金）
- 更新频率相对固定
- 可被所有分组共享使用

### 1.2 分组基金数据（Portfolio Data）
**定义**：用户导入到不同分组的基金，需要更详细的数据
**特点**：
- 数据量小（仅关注/持有的基金）
- 需要更详细的分析指标
- 与用户持仓和交易相关

### 1.3 分析数据（Analysis Data）
**定义**：基于前两类数据计算得出的投资分析指标
**特点**：
- 实时计算或按需计算
- 用于投资建议和决策支持
- 不直接存储原始数据，而是计算结果

---

## 二、当前数据维护现状分析

### 2.1 全局数据维护现状

| 数据表 | 同步器 | 数据源 | 维护方式 | 状态 | 说明 |
|--------|--------|--------|----------|------|------|
| fund_info | AkshareFundInfoSyncer | AKShare fund_name_em | 数据源维护-批量同步 | ✅ 已实现 | 全市场基金基本信息，约1万+只基金 |
| fund_nav | AkshareFundNavSyncer | AKShare fund_open_fund_daily_em | 数据源维护-批量同步 | ✅ 已实现 | 每日全市场基金净值 |
| fund_rating | AkshareFundRatingSyncer | AKShare fund_rating_all | 数据源维护-批量同步 | ✅ 已实现 | 基金评级数据 |
| fund_manager | AkshareFundManagerSyncer | AKShare fund_manager_em | 数据源维护-批量同步 | ✅ 已实现 | 基金经理信息 |
| fund_company | ❌ 未实现 | AKShare fund_company_em | 数据源维护-批量同步 | ❌ 待开发 | 基金公司信息 |
| fund_scale | ❌ 未实现 | AKShare fund_scale_open_sina | 数据源维护-批量同步 | ❌ 待开发 | 基金规模数据 |
| fund_dividend | ❌ 未实现 | AKShare fund_fh_em | 数据源维护-批量同步 | ❌ 待开发 | 基金分红数据 |

### 2.2 分组基金数据维护现状

| 数据表 | 维护方式 | 状态 | 说明 |
|--------|----------|------|------|
| fund_groups | 应用层管理 | ✅ 已实现 | 分组基本信息 |
| fund_group_members | 应用层管理 | ✅ 已实现 | 分组与基金关联 |
| fund_positions | 应用层管理 | ✅ 已实现 | 持仓记录 |
| fund_transactions | 应用层管理 | ✅ 已实现 | 交易流水 |
| fund_stock_holding | AkshareFundPortfolioSyncer | ✅ 已实现 | 基金股票持仓（按分组获取） |
| fund_bond_holding | ❌ 未实现 | ❌ 待开发 | 基金债券持仓 |
| fund_industry_allocation | ❌ 未实现 | ❌ 待开发 | 行业配置数据 |
| fund_risk_metrics | ❌ 未实现 | ❌ 待开发 | 风险指标数据（夏普比率、最大回撤等） |
| fund_performance | ❌ 未实现 | ❌ 待开发 | 业绩表现数据 |

### 2.3 分析数据维护现状

| 分析指标 | 计算方式 | 状态 | 说明 |
|----------|----------|------|------|
| 持仓收益/收益率 | 实时计算 | ✅ 已实现 | 基于持仓成本和最新净值计算 |
| 组合汇总 | 实时计算 | ✅ 已实现 | 分组持仓汇总统计 |
| 投资建议指标 | ❌ 未实现 | ❌ 待开发 | 需要设计计算逻辑 |

---

## 三、AKShare 风险指标与业绩数据API分析

### 3.1 可用的风险指标API

根据AKShare文档，以下API提供基金风险指标和业绩数据：

#### 3.1.1 fund_individual_analysis_xq - 基金数据分析（雪球）
**数据内容**：
| 字段 | 说明 | 用途 |
|------|------|------|
| 周期 | 近1年/近3年/近5年 | 时间维度 |
| 较同类风险收益比 | 百分比 | 与同类基金对比 |
| 较同类抗风险波动 | 百分比 | 与同类基金对比 |
| 年化波动率 | 百分比 | 风险指标 |
| 年化夏普比率 | 数值 | 风险调整后收益 |
| 最大回撤 | 百分比 | 风险指标 |

**获取方式**：单只基金查询  
**接口**：`ak.fund_individual_analysis_xq(symbol="000001")`

#### 3.1.2 fund_individual_achievement_xq - 基金业绩（雪球）
**数据内容**：
| 字段 | 说明 | 用途 |
|------|------|------|
| 业绩类型 | 年度业绩/阶段业绩 | 分类 |
| 周期 | 成立以来/今年来/近1月等 | 时间维度 |
| 本产品区间收益 | 百分比 | 收益表现 |
| 本产品最大回撤 | 百分比 | 风险指标 |
| 周期收益同类排名 | 排名/总数 | 相对表现 |

**获取方式**：单只基金查询  
**接口**：`ak.fund_individual_achievement_xq(symbol="000001")`

#### 3.1.3 fund_individual_profit_probability_xq - 基金盈利概率
**数据内容**：
| 字段 | 说明 | 用途 |
|------|------|------|
| 持有时长 | 满6个月/满1年/满2年/满3年 | 投资期限 |
| 盈利概率 | 百分比 | 投资建议参考 |
| 平均收益 | 百分比 | 预期收益参考 |

**获取方式**：单只基金查询  
**接口**：`ak.fund_individual_profit_probability_xq(symbol="000001")`

#### 3.1.4 fund_open_fund_rank_em - 开放式基金排行
**数据内容**：
| 字段 | 说明 | 用途 |
|------|------|------|
| 近1周/1月/3月/6月/1年/2年/3年 | 收益率 | 多周期业绩对比 |
| 今年来/成立来 | 收益率 | 长期业绩 |
| 日增长率 | 百分比 | 短期表现 |

**获取方式**：批量获取全市场  
**接口**：`ak.fund_open_fund_rank_em(symbol="全部")`

### 3.2 数据存储方案设计

#### 3.2.1 新建表：fund_risk_metrics（基金风险指标表）

```sql
CREATE TABLE fund_risk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    
    -- 时间周期
    period VARCHAR(20) NOT NULL,  -- '近1年', '近3年', '近5年'
    
    -- 风险指标
    annual_volatility DECIMAL(8,4),      -- 年化波动率(%)
    max_drawdown DECIMAL(8,4),           -- 最大回撤(%)
    sharpe_ratio DECIMAL(8,4),           -- 年化夏普比率
    
    -- 同类对比
    risk_return_rank DECIMAL(8,4),       -- 较同类风险收益比(%)
    risk_resistance_rank DECIMAL(8,4),   -- 较同类抗风险波动(%)
    
    -- 收益表现
    period_return DECIMAL(8,4),          -- 区间收益(%)
    category_rank VARCHAR(50),           -- 同类排名，如 "128/7671"
    
    -- 元数据
    data_date DATE,                      -- 数据日期
    data_source VARCHAR(20) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(fund_code, period, data_date)
);

CREATE INDEX idx_risk_fund ON fund_risk_metrics(fund_code);
CREATE INDEX idx_risk_period ON fund_risk_metrics(period);
```

#### 3.2.2 新建表：fund_profit_probability（基金盈利概率表）

```sql
CREATE TABLE fund_profit_probability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    
    -- 持有时长
    holding_period VARCHAR(20) NOT NULL,  -- '满6个月', '满1年', '满2年', '满3年'
    
    -- 盈利概率
    profit_probability DECIMAL(8,4),      -- 盈利概率(%)
    avg_return DECIMAL(8,4),              -- 平均收益(%)
    
    -- 元数据
    data_date DATE,
    data_source VARCHAR(20) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(fund_code, holding_period, data_date)
);

CREATE INDEX idx_profit_fund ON fund_profit_probability(fund_code);
```

#### 3.2.3 新建表：fund_performance（基金业绩表）

```sql
CREATE TABLE fund_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    fund_name VARCHAR(100),
    
    -- 业绩类型
    performance_type VARCHAR(20),         -- '年度业绩', '阶段业绩'
    period VARCHAR(20) NOT NULL,          -- '成立以来', '今年来', '2023', '近1月'等
    
    -- 业绩数据
    period_return DECIMAL(8,4),           -- 区间收益(%)
    max_drawdown DECIMAL(8,4),            -- 最大回撤(%)
    category_rank VARCHAR(50),            -- 同类排名
    
    -- 元数据
    data_date DATE,
    data_source VARCHAR(20) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(fund_code, period, data_date)
);

CREATE INDEX idx_perf_fund ON fund_performance(fund_code);
CREATE INDEX idx_perf_period ON fund_performance(period);
```

---

## 四、数据维护策略设计

### 4.1 全局数据维护策略

| 数据类型 | 维护方式 | 触发时机 | 更新频率 | 备注 |
|----------|----------|----------|----------|------|
| fund_info | 数据源批量同步 | 手动触发/定时任务 | 每周1次 | 基金基本信息变化较少 |
| fund_nav | 数据源批量同步 | 手动触发/定时任务 | 每日1次 | 交易日16:00-23:00更新 |
| fund_rating | 数据源批量同步 | 手动触发 | 每月1次 | 评级数据更新不频繁 |
| fund_manager | 数据源批量同步 | 手动触发 | 每周1次 | 经理变动相对频繁 |
| fund_company | 数据源批量同步 | 手动触发 | 每月1次 | 公司信息稳定 |
| fund_scale | 数据源批量同步 | 手动触发 | 每周1次 | 规模数据变化较快 |
| fund_dividend | 数据源批量同步 | 手动触发 | 每季度1次 | 分红数据季度更新 |

**维护入口**：数据源管理页面（datasource API）

### 4.2 分组基金数据维护策略

| 数据类型 | 维护方式 | 触发时机 | 更新频率 | 备注 |
|----------|----------|----------|----------|------|
| fund_stock_holding | 分组刷新时获取 | 导入分组后点击刷新 | 按需 | 仅获取分组内基金持仓 |
| fund_bond_holding | 分组刷新时获取 | 导入分组后点击刷新 | 按需 | 仅获取分组内基金持仓 |
| fund_industry_allocation | 分组刷新时获取 | 导入分组后点击刷新 | 按需 | 仅获取分组内基金行业配置 |
| fund_risk_metrics | 分组刷新时获取 | 导入分组后点击刷新 | 按需 | 仅获取分组内基金风险指标 |
| fund_performance | 分组刷新时获取 | 导入分组后点击刷新 | 按需 | 仅获取分组内基金业绩 |
| fund_profit_probability | 分组刷新时获取 | 导入分组后点击刷新 | 按需 | 仅获取分组内基金盈利概率 |

**维护入口**：分组管理页面 - 刷新按钮（portfolio API）

### 4.3 分析数据维护策略

| 分析指标 | 计算方式 | 触发时机 | 说明 |
|----------|----------|----------|------|
| 持仓收益 | 实时计算 | 查看持仓时 | 基于持仓成本和最新净值 |
| 组合收益率 | 实时计算 | 查看组合时 | 加权平均计算 |
| 投资建议指标 | 实时计算 | 点击"投资建议"按钮 | 基于风险指标和业绩数据计算 |

**维护入口**：投资建议按钮（新增API）

---

## 五、数据流向图

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据源层 (AKShare)                        │
├─────────────────────────────────────────────────────────────────┤
│  fund_name_em  │  fund_open_fund_daily_em  │  fund_rating_all  │
│  fund_manager  │  fund_company_em          │  fund_scale_*     │
│  fund_fh_em    │  fund_portfolio_hold_em   │  fund_individual_*│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      全局数据层 (批量同步)                        │
├─────────────────────────────────────────────────────────────────┤
│  fund_info  │  fund_nav  │  fund_rating  │  fund_manager       │
│  fund_company(待) │ fund_scale(待) │ fund_dividend(待)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      分组数据层 (按需获取)                        │
├─────────────────────────────────────────────────────────────────┤
│  fund_groups  │  fund_group_members  │  fund_positions        │
│  fund_transactions │ fund_stock_holding │ fund_bond_holding(待) │
│  fund_industry_allocation(待) │ fund_risk_metrics(待)          │
│  fund_performance(待) │ fund_profit_probability(待)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      分析数据层 (实时计算)                        │
├─────────────────────────────────────────────────────────────────┤
│  持仓收益  │  组合收益率  │  风险调整后收益  │  投资建议指标(待)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、实施计划

### 6.1 第一阶段：完善全局数据（已完成）
- ✅ fund_info 同步器
- ✅ fund_nav 同步器
- ✅ fund_rating 同步器
- ✅ fund_manager 同步器

### 6.2 第二阶段：完善分组数据（当前）
- ✅ fund_stock_holding 同步器
- ⏳ fund_bond_holding 同步器
- ⏳ fund_industry_allocation 同步器
- ⏳ fund_risk_metrics 同步器（新增）
- ⏳ fund_performance 同步器（新增）
- ⏳ fund_profit_probability 同步器（新增）

### 6.3 第三阶段：实现分析功能（待规划）
- ⏳ 投资建议按钮
- ⏳ 风险指标计算
- ⏳ 组合分析报表

### 6.4 第四阶段：优化与扩展（待规划）
- ⏳ 定时任务自动同步
- ⏳ 数据缓存优化
- ⏳ 历史数据归档

---

## 七、数据表汇总

### 7.1 已存在的数据表

| 表名 | 用途 | 记录数预估 |
|------|------|-----------|
| fund_info | 基金基本信息 | 10,000+ |
| fund_nav | 基金净值历史 | 数百万 |
| fund_rating | 基金评级 | 10,000+ |
| fund_manager | 基金经理 | 3,000+ |
| fund_groups | 基金分组 | < 100 |
| fund_group_members | 分组基金关联 | < 1,000 |
| fund_positions | 持仓记录 | < 1,000 |
| fund_transactions | 交易流水 | < 10,000 |
| fund_stock_holding | 股票持仓 | 数十万 |

### 7.2 待创建的数据表

| 表名 | 用途 | 记录数预估 | 优先级 |
|------|------|-----------|--------|
| fund_company | 基金公司信息 | 100+ | 低 |
| fund_scale | 基金规模 | 10,000+ | 中 |
| fund_dividend | 基金分红 | 数十万 | 中 |
| fund_bond_holding | 债券持仓 | 数十万 | 高 |
| fund_industry_allocation | 行业配置 | 数十万 | 高 |
| **fund_risk_metrics** | **风险指标** | **< 1,000** | **高** |
| **fund_performance** | **业绩表现** | **< 1,000** | **高** |
| **fund_profit_probability** | **盈利概率** | **< 1,000** | **高** |

---

## 八、总结

### 8.1 当前状态
- 全局数据基础架构已完成，可以批量获取全市场基金数据
- 分组数据架构已完成，支持用户创建分组、导入基金、记录持仓和交易
- 持仓刷新功能已实现，可以从AKShare获取最新净值

### 8.2 下一步行动
1. **高优先级**：实现风险指标同步器（fund_risk_metrics）
   - 创建数据表
   - 实现 AkshareFundRiskMetricsSyncer
   - 集成到分组刷新流程

2. **高优先级**：实现业绩数据同步器（fund_performance）
   - 创建数据表
   - 实现 AkshareFundPerformanceSyncer
   - 集成到分组刷新流程

3. **中优先级**：实现盈利概率同步器（fund_profit_probability）
   - 创建数据表
   - 实现 AkshareFundProfitProbabilitySyncer

4. **中优先级**：实现债券持仓和行业配置同步器
   - 完善基金持仓分析能力

5. **低优先级**：实现基金公司、规模、分红同步器
   - 完善全局数据覆盖范围

### 8.3 设计原则
1. **全局数据批量获取**：通过数据源管理页面统一维护
2. **分组数据按需获取**：仅在基金导入分组后，点击刷新时获取
3. **分析数据实时计算**：投资建议等指标按需计算，不存储中间结果
4. **数据一致性**：分组刷新时同时更新净值、持仓、风险指标等相关数据

---

*本文档将根据实际开发进度持续更新*
