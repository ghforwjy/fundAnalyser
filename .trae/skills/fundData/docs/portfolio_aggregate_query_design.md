# 组合聚合查询接口设计方案

## 一、问题分析

| 接口 | 自动刷新 | 新鲜度判断 |
|------|---------|-----------|
| `get_fund_nav` | ✅ 有 | 最新净值日期 >= 最近交易日（使用交易日历） |
| `get_fund_holdings` | ✅ 有 | 当天查询过就不再查询 |
| `get_fund_risk_and_return` | ❌ 无 | 直接查数据库，不触发同步 |

**问题**：`get_fund_risk_and_return` 没有自动刷新机制，只是从数据库查询，不会触发数据同步。

---

## 二、数据新鲜度机制

### 2.1 交易日历

使用 AKShare 交易日历接口（`tool_trade_date_hist_sina`），自动识别节假日：

```python
# 获取最近交易日
from database import get_latest_trade_day, is_trade_day

latest_trade_day = get_latest_trade_day()  # 返回最近的交易日
is_today_trade_day = is_trade_day()  # 判断今天是否是交易日
```

### 2.2 净值数据新鲜度

| 基金类型 | 判断逻辑 |
|---------|---------|
| 普通基金 | 最新净值日期 >= 最近交易日 |
| QDII基金 | 最新净值日期 >= 最近交易日-1天 |

**QDII基金特殊处理**：QDII基金投资海外市场，净值延迟一天公布。

### 2.3 持仓数据新鲜度

持仓数据季度更新，**当天查询过就不再查询**：

```python
# 使用 fund_data_meta 表记录查询时间
meta_key = f'holdings_{fund_code}'
# 如果当天已查询过，直接返回缓存
```

### 2.4 跳过行业配置的基金类型

以下基金类型没有股票行业配置，自动跳过查询：
- 债券型-混合一级
- 债券型-长债
- 债券型-中短债
- 债券型-可转债
- 指数型-其他（黄金ETF等）
- 货币型

---

## 三、风险收益指标自动刷新设计

### 数据特点
- 数据来源：AKShare 的 `fund_individual_analysis_xq`（风险指标）和 `fund_individual_achievement_xq`（业绩表现）
- 更新频率：每日更新
- 有效期：**12小时**（与 portfolio_design.md 中设计一致）

### 新鲜度判断逻辑

```
判断条件                          | 操作
--------------------------------|------
无数据                          | 调用 sync_group_risk_metrics + sync_group_performance
update_time 为空                | 需要同步
update_time 距今 > 12小时       | 需要同步
update_time 距今 <= 12小时      | 使用缓存
```

### 实现要点

1. 检查 `fund_risk_metrics` 表的 `update_time` 字段
2. 检查 `fund_performance` 表的 `update_time` 字段
3. 两个表都新鲜才使用缓存，否则触发同步

---

## 三、聚合查询接口设计

### 新增函数：`get_portfolio_funds_full(portfolio_id)`

**功能**：一次性获取组合内所有基金的完整信息

### 返回字段

| 分类 | 字段 |
|------|------|
| 基本信息 | fund_code, fund_name, fund_type, company_name |
| 持仓信息 | buy_date, buy_nav, shares, amount, notes |
| 最新净值 | unit_nav, nav_date, daily_return |
| 实时计算指标 | market_value, cost, profit_loss, profit_rate, **available_cash** |
| 收益指标 | return_1m, return_6m, return_1y |
| 风险指标 | max_drawdown_1y, sharpe_ratio_1y, annual_volatility_1y |
| 排名信息 | rank_in_category, rank_category |
| 持仓股票 | top_holdings（前5大持仓） |

**实时计算指标说明**：
- `market_value`: 市值 = shares × unit_nav
- `cost`: 成本 = shares × buy_nav  
- `profit_loss`: 盈亏 = (unit_nav - buy_nav) × shares
- `profit_rate`: 收益率 = (unit_nav - buy_nav) / buy_nav × 100%
- `available_cash`: 可用现金 = total_sell_amount - total_buy_amount（根据交易记录实时计算）
  - **基础数据来源**：`portfolio_transaction` 表
  - **计算逻辑**：汇总所有买入交易的金额（`transaction_type='BUY'`）和卖出交易的金额（`transaction_type='SELL'`），计算差额
  - **实现函数**：`calculate_fund_available_cash(portfolio_id, fund_code)` in `portfolio_manager.py`

### 自动刷新逻辑

1. 遍历组合内所有基金
2. 对每只基金调用 `get_fund_nav`（自动刷新净值）
3. 对每只基金调用 `get_fund_holdings`（自动刷新持仓）
4. 对每只基金调用改进后的 `get_fund_risk_and_return`（自动刷新风险收益）
5. 汇总返回完整数据

---

## 四、需要修改的文件

| 文件 | 修改内容 |
|------|---------|
| `smart_fund_data.py` | 1. 为 `get_fund_risk_and_return` 添加自动刷新逻辑<br>2. 新增 `get_portfolio_funds_full` 聚合查询函数 |
| `SKILL.md` | 添加新接口文档说明 |

---

## 五、接口调用示例

```python
from smart_fund_data import get_portfolio_funds_full

# 获取组合完整信息（自动刷新所有数据）
result = get_portfolio_funds_full(portfolio_id=2)

# 返回格式
{
    'portfolio_id': 2,
    'portfolio_name': '持仓组合',
    'fund_count': 20,
    'funds': [
        {
            'fund_code': '018957',
            'fund_name': '中航机遇领航混合发起C',
            'fund_type': '混合型',
            'unit_nav': 3.5993,
            'nav_date': '2026-02-13',
            'daily_return': -2.66,
            'return_1m': 5.23,
            'return_1y': 45.67,
            'max_drawdown_1y': -15.32,
            'sharpe_ratio_1y': 1.85,
            'top_holdings': [...]
        },
        ...
    ]
}
```

---

## 六、实现步骤

1. 在 `smart_fund_data.py` 中添加 `_is_risk_data_fresh()` 函数判断风险数据新鲜度
2. 修改 `get_fund_risk_and_return()` 添加自动刷新逻辑
3. 新增 `get_portfolio_funds_full()` 聚合查询函数
4. 更新 `SKILL.md` 文档
