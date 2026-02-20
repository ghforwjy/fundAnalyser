---
description: AKShare基金数据管理工具。维护SQLite数据库中的全局基金数据（批量同步）和分组基金数据（按需获取）。当用户需要同步基金数据、查询基金信息或管理基金数据时调用此skill。
---

# fundData

AKShare基金数据管理工具，提供基金数据同步、查询和管理功能。

## 快速开始

```python
from smart_fund_data import (
    query_funds_nav,           # 查询基金净值
    get_fund_nav,              # 获取单只基金净值
    get_fund_holdings,         # 获取基金持仓
    format_holdings_report,    # 格式化持仓报告
    get_fund_risk_and_return,  # 获取风险指标和收益率
    get_portfolio_funds_full,  # 聚合查询组合完整信息
    format_portfolio_report,   # 格式化组合报告
    get_value_averaging_report_text,  # 市值定投报告
    get_take_profit_advice,    # 获取止盈建议（支持波段捡回）
    get_take_profit_report,    # 获取止盈报告
    list_take_profit_templates,  # 止盈模板管理
    get_fund_take_profit_config,  # 基金止盈配置
    execute_buy_back_transaction,  # 执行波段捡回交易
)

from risk_metrics_calculator import (
    calculate_fund_risk_metrics,      # 计算单只基金风险指标
    calculate_portfolio_risk_metrics, # 计算组合风险指标
    compare_with_xueqiu,              # 对比自计算与雪球数据
)

from portfolio_manager import (
    create_portfolio,           # 创建组合
    list_portfolios,            # 查询所有组合
    add_funds_to_portfolio,     # 添加成分基金（支持单只或批量）
    get_portfolio_profit_loss_report,  # 获取盈亏报告
    record_buy_transaction,     # 记录买入交易
    record_sell_transaction,    # 记录卖出交易
    get_portfolio_transactions, # 查询交易记录
    update_portfolio_cash,      # 更新现金余额
    get_portfolio_cash,         # 获取现金余额
    calculate_fund_available_cash,     # 计算成分基金可用现金（实时）
    get_portfolio_funds_available_cash, # 获取组合所有基金可用现金（实时）
)
```

## 接口列表

### 基金查询

| 函数 | 说明 | 示例 |
|-----|------|------|
| `query_funds_nav(keyword, fund_type, company, force_update)` | 批量查询基金净值 | `query_funds_nav(keyword='中航')` |
| `get_fund_nav(fund_code, force_update)` | 获取单只基金最新净值 | `get_fund_nav('000001')` |

### 持仓查询

| 函数 | 说明 | 示例 |
|-----|------|------|
| `get_fund_holdings(fund_code, top_n, quarter, force_update)` | 获取基金持仓 | `get_fund_holdings('018956')` |
| `format_holdings_report(holdings_data)` | 格式化持仓报告 | `format_holdings_report(data)` |

### 风险收益

| 函数 | 说明 | 示例 |
|-----|------|------|
| `get_fund_risk_and_return(fund_code, keyword, period, force_update)` | 获取风险指标和收益率（检查新鲜度，过期自动刷新） | `get_fund_risk_and_return('000001')` |
| `get_max_drawdown(fund_code, keyword, period)` | 获取最大回撤 | `get_max_drawdown('000001', period='近1年')` |

### 风险指标计算（自计算）

| 函数 | 说明 | 示例 |
|-----|------|------|
| `calculate_fund_risk_metrics(fund_code, period, force_update)` | 计算单只基金风险指标 | `calculate_fund_risk_metrics('000001', '近1年')` |
| `calculate_portfolio_risk_metrics(portfolio_id, force_update)` | 计算组合内所有基金风险指标 | `calculate_portfolio_risk_metrics(portfolio_id=2)` |
| `compare_with_xueqiu(calc_result, xueqiu_data)` | 对比自计算与雪球数据 | `compare_with_xueqiu(calc, xq)` |

### 组合聚合查询

| 函数 | 说明 | 示例 |
|-----|------|------|
| `get_portfolio_funds_full(portfolio_id, portfolio_name, force_update)` | 聚合查询组合完整信息（自动刷新） | `get_portfolio_funds_full(portfolio_id=2)` |
| `format_portfolio_report(portfolio_data)` | 格式化组合报告 | `format_portfolio_report(data)` |

### 市值定投

| 函数 | 说明 | 示例 |
|-----|------|------|
| `calculate_value_averaging_plan(fund_code, current_holding, simulate)` | 计算市值定投方案 | `calculate_value_averaging_plan('000001', 50000)` |
| `get_value_averaging_report_text(fund_code, current_holding, simulate)` | 获取格式化报告 | `get_value_averaging_report_text('000001', 50000)` |

### 止盈建议

| 函数 | 说明 | 示例 |
|-----|------|------|
| `get_take_profit_advice(portfolio_id)` | 获取组合止盈建议（支持波段捡回） | `get_take_profit_advice(1)` |
| `get_take_profit_report(portfolio_id)` | 获取格式化止盈报告 | `get_take_profit_report(1)` |

### 波段捡回交易

| 函数 | 说明 | 示例 |
|-----|------|------|
| `execute_buy_back_transaction(portfolio_id, fund_code, target_sell_transaction_id, shares, amount, ...)` | 执行波段捡回交易，自动标记卖单为已回收 | `execute_buy_back_transaction(1, '000001', 123, 1000, 1200.00, nav=1.20)` |

### 止盈模板管理

| 函数 | 说明 | 示例 |
|-----|------|------|
| `list_take_profit_templates()` | 获取所有止盈参数模板 | `list_take_profit_templates()` |
| `get_take_profit_template(template_id)` | 获取单个模板详情 | `get_take_profit_template(1)` |
| `get_default_take_profit_template()` | 获取默认模板 | `get_default_take_profit_template()` |
| `create_take_profit_template(name, ...)` | 创建新模板（支持波段捡回参数） | `create_take_profit_template(name='我的模板', first_threshold=0.25, enable_buy_back=True)` |
| `update_take_profit_template(template_id, ...)` | 更新模板 | `update_take_profit_template(1, enable_buy_back=True, buy_back_threshold=0.20)` |
| `delete_take_profit_template(template_id)` | 删除模板 | `delete_take_profit_template(1)` |
| `set_default_take_profit_template(template_id)` | 设置默认模板 | `set_default_take_profit_template(1)` |

### 基金止盈配置

| 函数 | 说明 | 示例 |
|-----|------|------|
| `get_fund_take_profit_config(portfolio_id, fund_code)` | 获取基金的止盈配置 | `get_fund_take_profit_config(1, '000001')` |
| `set_fund_take_profit_template(portfolio_id, fund_code, template_id)` | 为基金设置模板 | `set_fund_take_profit_template(1, '000001', 2)` |
| `set_fund_take_profit_custom_params(portfolio_id, fund_code, ...)` | 设置自定义参数（支持波段捡回） | `set_fund_take_profit_custom_params(1, '000001', enable_buy_back=True, buy_back_threshold=0.20)` |
| `reset_fund_take_profit_config(portfolio_id, fund_code)` | 重置基金配置 | `reset_fund_take_profit_config(1, '000001')` |
| `get_portfolio_take_profit_configs(portfolio_id)` | 获取组合所有基金配置 | `get_portfolio_take_profit_configs(1)` |

### 数据同步

| 函数 | 说明 | 示例 |
|-----|------|------|
| `FundDataSkill().sync_fund_info()` | 同步基金基本信息 | - |
| `FundDataSkill().sync_fund_rating()` | 同步基金评级 | - |
| `FundDataSkill().sync_fund_manager()` | 同步基金经理 | - |
| `FundDataSkill().sync_group_nav(fund_codes)` | 同步指定基金净值 | - |
| `FundDataSkill().sync_group_holdings(fund_codes)` | 同步指定基金持仓 | - |

### 组合管理

| 函数 | 说明 | 示例 |
|-----|------|------|
| `create_portfolio(name, description)` | 创建组合 | `create_portfolio('我的组合')` |
| `delete_portfolio(portfolio_id)` | 删除组合 | `delete_portfolio(1)` |
| `list_portfolios()` | 查询所有组合 | `list_portfolios()` |
| `get_portfolio(portfolio_id)` | 获取组合详情 | `get_portfolio(1)` |

### 成分基金管理

| 函数 | 说明 | 示例 |
|-----|------|------|
| `add_funds_to_portfolio(portfolio_id, holdings, exclude_money_market)` | 添加成分基金（支持单只或批量，自动记录持仓历史） | `add_funds_to_portfolio(1, {'000001': {'shares': 1000, 'buy_date': '2025-12-31'}})` |
| `list_portfolio_funds(portfolio_id)` | 查询成分基金 | `list_portfolio_funds(1)` |
| `get_portfolio_profit_loss_report(portfolio_id, from_date, to_date)` | 获取盈亏报告 | `get_portfolio_profit_loss_report(1, '2025-01-01')` |

### 盈亏数据导入

| 函数 | 说明 | 示例 |
|-----|------|------|
| `import_profit_data(portfolio_id, profit_data, import_date, import_mode, source_type)` | 导入盈亏数据（支持覆盖/累加模式） | `import_profit_data(1, [{'fund_code': '000001', 'current_value': 10000, 'profit_loss': 1000}], import_mode='overwrite')` |
| `import_profit_data_from_table(table_data, portfolio_id, import_mode)` | 从表格数据导入盈亏 | `import_profit_data_from_table([{'code': '000001', 'name': '华夏成长', 'amount': 10000, 'profit': 1000}], 1)` |

### 交易维护

| 函数 | 说明 | 示例 |
|-----|------|------|
| `record_buy_transaction(portfolio_id, fund_code, shares, amount, ...)` | 记录买入交易，自动计算新成本净值 | `record_buy_transaction(1, '000001', shares=1000, amount=1500)` |
| `record_sell_transaction(portfolio_id, fund_code, shares, amount, ...)` | 记录卖出交易，自动更新成本和现金 | `record_sell_transaction(1, '000001', shares=500, amount=800)` |
| `get_portfolio_transactions(portfolio_id, ...)` | 查询组合交易记录 | `get_portfolio_transactions(1, fund_code='000001')` |
| `update_portfolio_cash(portfolio_id, cash)` | 更新组合现金余额 | `update_portfolio_cash(1, 10000)` |
| `get_portfolio_cash(portfolio_id)` | 获取组合现金余额 | `get_portfolio_cash(1)` |

### 成分基金可用现金（实时计算）

| 函数 | 说明 | 示例 |
|-----|------|------|
| `calculate_fund_available_cash(portfolio_id, fund_code)` | 计算单只成分基金的可用现金（卖出所得 - 买入投入，实时计算不存储） | `calculate_fund_available_cash(1, '000001')` |
| `get_portfolio_funds_available_cash(portfolio_id)` | 获取组合内所有成分基金的可用现金 | `get_portfolio_funds_available_cash(1)` |

**前端显示说明：**
- 可用现金字段通过 `get_portfolio_funds_full()` 聚合查询返回，在 `PositionManage` 页面表格中显示为"可用现金"列
- 正数显示为绿色（净卖出），负数显示为红色（净投入）
- 字段路径：`funds[].available_cash`
- 相关字段：`total_buy_amount`（总买入金额）、`total_sell_amount`（总卖出金额）

### 标签管理

| 函数 | 说明 | 示例 |
|-----|------|------|
| `create_tag(name, category, color)` | 创建新标签 | `create_tag('新能源', '行业主题', '#10b981')` |
| `update_tag(tag_id, **fields)` | 更新标签信息 | `update_tag(1, name='新能源汽车', color='#22c55e')` |
| `delete_tag(tag_id)` | 删除标签 | `delete_tag(1)` |
| `get_all_tags(category)` | 获取所有标签（可按分类筛选） | `get_all_tags()` 或 `get_all_tags('行业主题')` |
| `search_tags(keyword)` | 模糊搜索标签 | `search_tags('新能')` |
| `get_tag_categories()` | 获取所有标签分类 | `get_tag_categories()` |
| `get_fund_tags(fund_code)` | 获取基金的标签列表 | `get_fund_tags('000001')` |
| `set_fund_tags(fund_code, tag_ids)` | 批量设置基金标签（覆盖式） | `set_fund_tags('000001', [1, 2, 3])` |
| `add_fund_tag(fund_code, tag_id)` | 给基金添加单个标签 | `add_fund_tag('000001', 1)` |
| `remove_fund_tag(fund_code, tag_id)` | 移除基金的单个标签 | `remove_fund_tag('000001', 1)` |
| `get_funds_by_tag(tag_id)` | 获取拥有指定标签的所有基金 | `get_funds_by_tag(1)` |
| `get_all_fund_tags()` | 获取所有基金的标签映射 | `get_all_fund_tags()` |

## 使用示例

### 查询基金净值

```python
# 按关键词查询
results = query_funds_nav(keyword='中航')
for r in results:
    print(f"{r['fund_code']} {r['fund_name']}: {r['unit_nav']}")

# 按类型和公司筛选
results = query_funds_nav(fund_type='股票', company='易方达')
```

### 查询基金持仓

```python
# 通过基金代码
holdings = get_fund_holdings('018956')
print(format_holdings_report(holdings))

# 通过基金名称关键词
holdings = get_fund_holdings('中航机遇领航')
```

### 聚合查询组合完整信息

```python
# 获取组合完整信息（自动刷新净值、持仓、风险收益指标）
result = get_portfolio_funds_full(portfolio_id=2)

# 按名称查询
result = get_portfolio_funds_full(portfolio_name='持仓组合')

# 强制刷新所有数据
result = get_portfolio_funds_full(portfolio_id=2, force_update=True)

# 格式化输出
print(format_portfolio_report(result))
```

### 市值定投方案

```python
# 计算定投方案
report = get_value_averaging_report_text('000001', 50000)
print(report)
```

### 交易维护

```python
# 记录买入交易
# 公式：新成本 = (原数量×原成本 + 买入投入金额) / (原数量 + 买入数量)
result = record_buy_transaction(
    portfolio_id=1,
    fund_code='000001',
    shares=1000,        # 买入份额
    amount=1500,        # 买入投入金额
    transaction_date='2026-02-17',
    notes='定投买入'
)
print(f"新持仓: {result['new_total_shares']}份, 新成本净值: {result['new_buy_nav']}")

# 记录卖出交易
# 公式：新成本 = (原数量×原成本 - 卖出获得金额) / (原数量 - 卖出数量)
result = record_sell_transaction(
    portfolio_id=1,
    fund_code='000001',
    shares=500,         # 卖出份额
    amount=800,         # 卖出获得金额
    transaction_date='2026-02-17',
    notes='部分止盈'
)
print(f"剩余持仓: {result['new_total_shares']}份, 现金增加: {result['cash_added']}")

# 查询交易记录
transactions = get_portfolio_transactions(
    portfolio_id=1,
    fund_code='000001',           # 可选：筛选特定基金
    transaction_type='BUY'        # 可选：筛选买入/卖出
)

# 管理组合现金
update_portfolio_cash(1, 10000)   # 设置现金余额
cash_info = get_portfolio_cash(1) # 查询现金余额

# 查询成分基金可用现金（实时计算）
# 可用现金 = 所有卖出交易获得金额 - 所有买入交易投入金额
cash_info = calculate_fund_available_cash(1, '000001')
print(f"可用现金: {cash_info['available_cash']}")  # 正数表示净卖出，负数表示净买入

# 批量查询组合内所有基金的可用现金
all_cash = get_portfolio_funds_available_cash(1)
for fund in all_cash['funds']:
    print(f"{fund['fund_code']}: 可用现金 {fund['available_cash']}")

# 聚合查询中会自动包含可用现金字段
portfolio_full = get_portfolio_funds_full(portfolio_id=1)
for fund in portfolio_full['funds']:
    if 'available_cash' in fund:
        print(f"{fund['fund_code']} 可用现金: {fund['available_cash']}")
```

### 标签管理

```python
from tag_manager import (
    create_tag, update_tag, delete_tag,
    get_all_tags, search_tags, get_tag_categories,
    get_fund_tags, set_fund_tags, add_fund_tag, remove_fund_tag
)

# 创建标签
tag1 = create_tag('新能源', '行业主题', '#10b981')
tag2 = create_tag('半导体', '行业主题', '#f59e0b')
tag3 = create_tag('医药', '行业主题', '#ef4444')

# 查看所有标签
all_tags = get_all_tags()
for tag in all_tags:
    print(f"{tag['id']}: {tag['name']} ({tag['category']})")

# 搜索标签
results = search_tags('新能')  # 模糊匹配

# 获取标签分类
categories = get_tag_categories()  # ['行业主题', '投资风格', ...]

# 给基金打标签
add_fund_tag('000001', tag1['data']['id'])  # 添加单个标签
add_fund_tag('000001', tag2['data']['id'])

# 批量设置标签（覆盖式）
set_fund_tags('000001', [1, 2, 3])  # 设置基金只有这3个标签

# 查询基金标签
fund_tags = get_fund_tags('000001')
for tag in fund_tags:
    print(f"- {tag['name']} ({tag['category']})")

# 移除标签
remove_fund_tag('000001', 1)

# 更新标签信息
update_tag(1, name='新能源汽车', color='#22c55e')

# 删除标签（会自动移除所有关联）
delete_tag(3)
```

## 详细文档

- 数据新鲜度机制、智能缓存等详细说明请参阅 [README.md](./README.md)
- 组合管理功能设计请参阅 [portfolio_design.md](./portfolio_design.md)
- 组合聚合查询接口设计请参阅 [docs/portfolio_aggregate_query_design.md](./docs/portfolio_aggregate_query_design.md)
- 风险指标计算设计请参阅 [docs/risk_metrics_calculation_design.md](./docs/risk_metrics_calculation_design.md)
- **标签管理功能设计请参阅 [docs/tag_management_design.md](./docs/tag_management_design.md)**
- **投资算法设计请参阅 [invest_methods.md](./invest_methods.md)**
- **止盈建议设计请参阅 [docs/Take_Profit_design.md](./docs/Take_Profit_design.md)**
