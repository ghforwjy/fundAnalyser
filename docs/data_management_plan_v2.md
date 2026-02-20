# 基金分析系统数据维护方案 V2

> 文档版本：2.0  
> 更新日期：2026-02-15  
> 核心原则：**按AKShare接口能力分类数据** - 能批量获取的归为全局数据，只能单只获取的归为分组数据

---

## 一、数据分类核心原则

### 1.1 分类标准

| 数据类型 | 定义标准 | AKShare接口特征 | 维护策略 |
|---------|---------|----------------|---------|
| **全局数据** | 可批量获取的数据 | 接口无需symbol参数，单次返回全市场数据 | 数据源管理页面统一维护 |
| **分组数据** | 只能单只获取的数据 | 接口需要symbol参数，单次返回单只基金数据 | 分组刷新时按需获取 |
| **分析数据** | 计算得出的指标 | 基于全局数据和分组数据计算 | 实时计算，不存储 |

### 1.2 关键判断依据

**为什么 fund_nav 属于分组数据而非全局数据？**
- `fund_open_fund_daily_em()` 虽然能批量获取当日净值，但**历史净值**只能单只获取
- `fund_open_fund_info_em(symbol, indicator="单位净值走势")` 需要单只基金代码
- 对于分组基金，我们需要**历史净值**来计算风险指标，所以只能单只获取
- 因此 fund_nav 应归为**分组数据**，仅获取分组内基金的历史净值

---

## 二、AKShare 接口能力分析

### 2.1 全局数据接口（批量获取）

| 接口名称 | 数据内容 | 输入参数 | 返回数量 | 对应数据表 |
|---------|---------|---------|---------|-----------|
| `fund_name_em` | 基金基本信息 | 无 | 全市场(1万+) | **fund_info** |
| `fund_open_fund_daily_em` | 当日开放式基金净值 | 无 | 全市场 | ❌ 不使用（只取当日，不取历史） |
| `fund_purchase_em` | 基金申购状态 | 无 | 全市场 | **fund_purchase_status** |
| `fund_rating_all` | 基金评级总汇 | 无 | 全市场 | **fund_rating** |
| `fund_manager_em` | 基金经理大全 | 无 | 全市场(3000+) | **fund_manager** |
| `fund_company_em` | 基金公司一览 | 无 | 全市场(100+) | **fund_company** |
| `fund_new_found_em` | 新成立基金 | 无 | 全市场 | **fund_new** |
| `fund_fh_em` | 基金分红 | year | 按年批量 | **fund_dividend** |
| `fund_cf_em` | 基金拆分 | year | 按年批量 | **fund_split** |
| `fund_fh_rank_em` | 基金分红排行 | 无 | 全市场 | **fund_dividend_rank** |
| `fund_open_fund_rank_em` | 开放式基金排行 | symbol(类型) | 按类型批量 | **fund_rank** |
| `fund_exchange_rank_em` | 场内交易基金排行 | 无 | 全市场 | **fund_exchange_rank** |
| `fund_money_rank_em` | 货币型基金排行 | 无 | 全市场 | **fund_money_rank** |
| `fund_etf_spot_em` | ETF实时行情 | 无 | 全市场 | **fund_etf_spot** |
| `fund_lof_spot_em` | LOF实时行情 | 无 | 全市场 | **fund_lof_spot** |

### 2.2 分组数据接口（单只获取）

| 接口名称 | 数据内容 | 输入参数 | 返回数量 | 对应数据表 |
|---------|---------|---------|---------|-----------|
| `fund_open_fund_info_em` | 单只基金历史净值 | symbol(基金代码) | 单只 | **fund_nav** |
| `fund_money_fund_info_em` | 货币基金历史净值 | symbol(基金代码) | 单只 | **fund_money_nav** |
| `fund_portfolio_hold_em` | 基金股票持仓 | symbol, date | 单只 | **fund_stock_holding** |
| `fund_portfolio_bond_hold_em` | 基金债券持仓 | symbol, date | 单只 | **fund_bond_holding** |
| `fund_portfolio_industry_allocation_em` | 行业配置 | symbol, date | 单只 | **fund_industry_allocation** |
| `fund_individual_analysis_xq` | 风险指标分析 | symbol(基金代码) | 单只 | **fund_risk_metrics** |
| `fund_individual_achievement_xq` | 基金业绩表现 | symbol(基金代码) | 单只 | **fund_performance** |
| `fund_individual_profit_probability_xq` | 盈利概率 | symbol(基金代码) | 单只 | **fund_profit_probability** |
| `fund_individual_detail_hold_xq` | 资产比例配置 | symbol, date | 单只 | **fund_asset_allocation** |
| `fund_overview_em` | 基金详细概况 | symbol(基金代码) | 单只 | **fund_detail_info** |
| `fund_fee_em` | 基金交易费率 | symbol, indicator | 单只 | **fund_fee** |
| `fund_etf_hist_em` | ETF历史行情 | symbol, period | 单只 | **fund_etf_hist** |
| `fund_lof_hist_em` | LOF历史行情 | symbol, period | 单只 | **fund_lof_hist** |

---

## 三、数据表分类汇总

### 3.1 全局数据表（批量同步）

| 数据表 | 同步器 | 数据源 | 状态 | 说明 |
|--------|--------|--------|------|------|
| **fund_info** | `AkshareFundInfoSyncer` | `fund_name_em` | ✅ 已实现 | 全市场基金基本信息 |
| **fund_purchase_status** | ❌ 待实现 | `fund_purchase_em` | ❌ 待开发 | 基金申购赎回状态 |
| **fund_rating** | `AkshareFundRatingSyncer` | `fund_rating_all` | ✅ 已实现 | 基金评级数据 |
| **fund_manager** | `AkshareFundManagerSyncer` | `fund_manager_em` | ✅ 已实现 | 基金经理信息 |
| **fund_company** | ❌ 待实现 | `fund_company_em` | ❌ 待开发 | 基金公司信息 |
| **fund_new** | ❌ 待实现 | `fund_new_found_em` | ❌ 待开发 | 新发基金 |
| **fund_dividend** | ❌ 待实现 | `fund_fh_em` | ❌ 待开发 | 基金分红记录 |
| **fund_split** | ❌ 待实现 | `fund_cf_em` | ❌ 待开发 | 基金拆分记录 |
| **fund_rank** | ❌ 待实现 | `fund_open_fund_rank_em` | ❌ 待开发 | 基金排行数据 |
| **fund_etf_spot** | ❌ 待实现 | `fund_etf_spot_em` | ❌ 待开发 | ETF实时行情 |
| **fund_lof_spot** | ❌ 待实现 | `fund_lof_spot_em` | ❌ 待开发 | LOF实时行情 |

**维护入口**：数据源管理页面（datasource API）  
**触发方式**：手动触发或定时任务  
**更新频率**：每日/每周（根据数据变化频率）

### 3.2 分组数据表（按需获取）

| 数据表 | 同步器 | 数据源 | 状态 | 说明 |
|--------|--------|--------|------|------|
| **fund_nav** | ❌ 待实现 | `fund_open_fund_info_em` | ❌ 待开发 | 单只基金历史净值 |
| **fund_money_nav** | ❌ 待实现 | `fund_money_fund_info_em` | ❌ 待开发 | 货币基金历史净值 |
| **fund_stock_holding** | `AkshareFundPortfolioSyncer` | `fund_portfolio_hold_em` | ✅ 已实现 | 股票持仓 |
| **fund_bond_holding** | ❌ 待实现 | `fund_portfolio_bond_hold_em` | ❌ 待开发 | 债券持仓 |
| **fund_industry_allocation** | ❌ 待实现 | `fund_portfolio_industry_allocation_em` | ❌ 待开发 | 行业配置 |
| **fund_asset_allocation** | ❌ 待实现 | `fund_individual_detail_hold_xq` | ❌ 待开发 | 资产配置比例 |
| **fund_risk_metrics** | ❌ 待实现 | `fund_individual_analysis_xq` | ❌ 待开发 | 风险指标（夏普比率、最大回撤等） |
| **fund_performance** | ❌ 待实现 | `fund_individual_achievement_xq` | ❌ 待开发 | 业绩表现（多周期收益、排名） |
| **fund_profit_probability** | ❌ 待实现 | `fund_individual_profit_probability_xq` | ❌ 待开发 | 盈利概率 |
| **fund_detail_info** | ❌ 待实现 | `fund_overview_em` | ❌ 待开发 | 基金详细概况 |
| **fund_fee** | ❌ 待实现 | `fund_fee_em` | ❌ 待开发 | 交易费率 |
| **fund_etf_hist** | ❌ 待实现 | `fund_etf_hist_em` | ❌ 待开发 | ETF历史行情 |
| **fund_lof_hist** | ❌ 待实现 | `fund_lof_hist_em` | ❌ 待开发 | LOF历史行情 |

**维护入口**：分组管理页面 - 刷新按钮（portfolio API）  
**触发方式**：导入基金到分组后，点击刷新按钮  
**更新频率**：按需（仅获取分组内基金的数据）

### 3.3 分析数据（实时计算）

| 分析指标 | 计算方式 | 状态 | 说明 |
|----------|----------|------|------|
| 持仓收益/收益率 | 实时计算 | ✅ 已实现 | 基于持仓成本和最新净值 |
| 组合收益率 | 实时计算 | ✅ 已实现 | 加权平均计算 |
| 风险调整后收益 | 实时计算 | ❌ 待开发 | 基于风险指标计算 |
| 投资建议评分 | 实时计算 | ❌ 待开发 | 综合多维度指标 |

**维护入口**：投资建议按钮（新增 analysis API）  
**触发方式**：点击"投资建议"按钮时实时计算  
**存储策略**：不存储，实时计算返回

---

## 四、数据流向图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AKShare 数据源层                               │
├─────────────────────────────────────────────────────────────────────────┤
│  【批量接口】                    │  【单只接口】                          │
│  fund_name_em                  │  fund_open_fund_info_em                │
│  fund_purchase_em              │  fund_portfolio_hold_em                │
│  fund_rating_all               │  fund_individual_analysis_xq           │
│  fund_manager_em               │  fund_individual_achievement_xq        │
│  fund_company_em               │  fund_individual_profit_probability_xq │
│  fund_open_fund_rank_em        │  fund_overview_em                      │
│  fund_etf_spot_em              │  ...                                   │
└─────────────────────────────────────────────────────────────────────────┘
              │                                  │
              ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  【全局数据层】- 批量同步，全市场数据        │  【分组数据层】- 按需获取，仅分组内基金  │
├─────────────────────────────────────────────────────────────────────────┤
│  fund_info                     │  fund_nav                              │
│  fund_purchase_status          │  fund_stock_holding                    │
│  fund_rating                   │  fund_bond_holding                     │
│  fund_manager                  │  fund_industry_allocation              │
│  fund_company                  │  fund_risk_metrics                     │
│  fund_rank                     │  fund_performance                      │
│  fund_etf_spot                 │  fund_profit_probability               │
│  ...                           │  ...                                   │
└─────────────────────────────────────────────────────────────────────────┘
              │                                  │
              └──────────────┬───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        【分析数据层】- 实时计算                          │
├─────────────────────────────────────────────────────────────────────────┤
│  持仓收益  │  组合收益率  │  风险调整后收益  │  投资建议评分              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 五、实施计划

### 5.1 第一阶段：完善全局数据同步器

| 优先级 | 数据表 | 同步器 | 说明 |
|--------|--------|--------|------|
| 高 | fund_purchase_status | AkshareFundPurchaseStatusSyncer | 申购状态，每日更新 |
| 中 | fund_company | AkshareFundCompanySyncer | 基金公司信息 |
| 中 | fund_rank | AkshareFundRankSyncer | 基金排行数据 |
| 低 | fund_dividend | AkshareFundDividendSyncer | 基金分红记录 |
| 低 | fund_etf_spot | AkshareFundEtfSpotSyncer | ETF实时行情 |

### 5.2 第二阶段：完善分组数据同步器（核心）

| 优先级 | 数据表 | 同步器 | 说明 |
|--------|--------|--------|------|
| **高** | **fund_nav** | **AkshareFundNavSyncer** | **历史净值，风险计算基础** |
| **高** | **fund_risk_metrics** | **AkshareFundRiskMetricsSyncer** | **风险指标（夏普、回撤）** |
| **高** | **fund_performance** | **AkshareFundPerformanceSyncer** | **业绩表现数据** |
| 中 | fund_bond_holding | AkshareFundBondHoldingSyncer | 债券持仓 |
| 中 | fund_industry_allocation | AkshareFundIndustryAllocationSyncer | 行业配置 |
| 中 | fund_profit_probability | AkshareFundProfitProbabilitySyncer | 盈利概率 |
| 低 | fund_detail_info | AkshareFundDetailInfoSyncer | 基金详细概况 |
| 低 | fund_fee | AkshareFundFeeSyncer | 交易费率 |

### 5.3 第三阶段：实现分析功能

| 优先级 | 功能 | 说明 |
|--------|------|------|
| 高 | 投资建议按钮 | 基于风险指标和业绩数据生成建议 |
| 中 | 组合风险分析 | 计算组合整体风险指标 |
| 中 | 业绩归因分析 | 分析组合收益来源 |

---

## 六、关键设计决策

### 6.1 为什么 fund_nav 是分组数据？

**原因**：
1. AKShare 获取**历史净值**只能单只获取（`fund_open_fund_info_em`）
2. 全市场1万+只基金，每只基金历史净值可能数千条，全部获取数据量巨大
3. 用户只关心分组内的基金，按需获取更高效
4. 分组刷新时并发获取分组内基金的历史净值

### 6.2 分组刷新时获取哪些数据？

当用户在分组页面点击"刷新"时，系统应该：

1. **获取历史净值**（fund_nav）- 用于计算收益和风险
2. **获取风险指标**（fund_risk_metrics）- 夏普比率、最大回撤等
3. **获取业绩表现**（fund_performance）- 多周期收益、同类排名
4. **获取持仓数据**（fund_stock_holding）- 股票持仓明细
5. **获取行业配置**（fund_industry_allocation）- 行业分布

这些数据都是**单只接口**，所以只能对分组内的基金逐一获取。

### 6.3 全局数据的作用

全局数据主要用于：
1. **基金搜索** - 从全市场基金中筛选
2. **基础信息展示** - 基金名称、类型、公司等
3. **初步筛选** - 基于评级、排行等批量数据筛选基金
4. **分组导入** - 用户从全局基金列表中选择基金加入分组

---

## 七、总结

### 7.1 核心原则重申

1. **能批量获取的 → 全局数据** - 在数据源管理页面维护
2. **只能单只获取的 → 分组数据** - 在分组刷新时按需获取
3. **计算得出的 → 分析数据** - 实时计算，不存储

### 7.2 当前状态

**全局数据（已实现）**：
- ✅ fund_info - 基金基本信息
- ✅ fund_rating - 基金评级
- ✅ fund_manager - 基金经理

**分组数据（已实现）**：
- ✅ fund_stock_holding - 股票持仓

**待实现（高优先级）**：
- ⏳ fund_nav - 历史净值（分组数据）
- ⏳ fund_risk_metrics - 风险指标（分组数据）
- ⏳ fund_performance - 业绩表现（分组数据）

### 7.3 下一步行动

1. **立即开发**：fund_nav 同步器（单只获取历史净值）
2. **紧随其后**：fund_risk_metrics 同步器（风险指标）
3. **同步开发**：fund_performance 同步器（业绩表现）
4. **集成测试**：将上述同步器集成到分组刷新流程

---

*本文档基于AKShare接口能力重新设计，确保数据获取效率最大化*
