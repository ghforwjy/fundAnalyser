# AKShare开源金融数据接口库 - 基金数据接口完整研究报告

## 目录
1. [概述](#概述)
2. [基金基本信息接口](#基金基本信息接口)
3. [基金净值数据接口](#基金净值数据接口)
4. [基金持仓数据接口](#基金持仓数据接口)
5. [基金经理信息接口](#基金经理信息接口)
6. [基金分类和排名接口](#基金分类和排名接口)
7. [其他基金相关接口](#其他基金相关接口)
8. [总结与建议](#总结与建议)

---

## 概述

### AKShare简介
AKShare是一个基于Python的开源金融数据接口库，专注于提供中国金融市场数据。其基金数据模块主要来源于东方财富网（天天基金网）、新浪财经、雪球等权威金融数据平台。

### 主要数据源
| 数据源 | 覆盖范围 | 更新频率 |
|--------|----------|----------|
| 东方财富网(天天基金网) | 公募基金、ETF、LOF、基金经理等 | 交易日每日更新 |
| 新浪财经 | 基金规模、封闭式基金等 | 定期更新 |
| 雪球 | 基金分析、盈利概率等 | 实时/每日 |
| 中国证券投资基金业协会 | 私募基金数据 | 定期更新 |

### 安装与使用
```python
# 安装AKShare
pip install akshare --upgrade

# 导入库
import akshare as ak
import pandas as pd
```

---

## 基金基本信息接口

### 1. fund_name_em - 获取所有基金基本信息

**接口说明**
- **接口名称**: `fund_name_em`
- **数据来源**: 东方财富网-天天基金网
- **目标地址**: http://fund.eastmoney.com/fund.html
- **数据更新频率**: 每日更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 基金代码 | object | 基金的唯一标识代码 |
| 拼音缩写 | object | 基金名称的拼音缩写 |
| 基金简称 | object | 基金的简称 |
| 基金类型 | object | 基金类型(混合型、债券型等) |
| 拼音全称 | object | 基金名称的完整拼音 |

**示例代码**
```python
import akshare as ak

# 获取所有基金基本信息
fund_name_em_df = ak.fund_name_em()
print(fund_name_em_df.head())

# 筛选特定类型的基金
mixed_funds = fund_name_em_df[fund_name_em_df['基金类型'] == '混合型']
print(f"混合型基金数量: {len(mixed_funds)}")
```

**注意事项**
- 返回数据量较大(约10000+条记录)，获取时需要一定时间
- 基金代码可能包含前后端代码，使用时需注意区分

---

### 2. fund_individual_basic_info_xq - 雪球基金基本信息

**接口说明**
- **接口名称**: `fund_individual_basic_info_xq`
- **数据来源**: 雪球基金
- **目标地址**: https://danjuanfunds.com/funding/000001
- **数据更新频率**: 实时更新
- **数据可靠性**: ⭐⭐⭐⭐ 较高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码，如"000001" |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 基金名称 | object | 基金完整名称 |
| 基金类型 | object | 基金类型分类 |
| 成立日期 | object | 基金成立时间 |
| 管理公司 | object | 基金管理公司 |
| 最新净值 | float64 | 最新单位净值 |
| 累计净值 | float64 | 累计净值 |
| 基金规模 | float64 | 基金规模(亿元) |
| 基金经理 | object | 当前基金经理 |

**示例代码**
```python
import akshare as ak

# 获取单只基金基本信息
fund_info = ak.fund_individual_basic_info_xq(symbol="000001")
print(fund_info)
```

---

### 3. fund_info_index_em - 指数型基金信息

**接口说明**
- **接口名称**: `fund_info_index_em`
- **数据来源**: 东方财富网
- **数据更新频率**: 每日更新

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
包含基金代码、名称、类型、跟踪指数等详细信息

---

### 4. fund_purchase_em - 基金申购状态

**接口说明**
- **接口名称**: `fund_purchase_em`
- **数据来源**: 东方财富网
- **目标地址**: http://fund.eastmoney.com/fund.html
- **数据更新频率**: 交易日实时更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 基金代码 | object | 基金代码 |
| 基金简称 | object | 基金简称 |
| 基金类型 | object | 基金类型 |
| 最新净值/万份收益 | float64 | 最新净值 |
| 申购状态 | object | 申购状态(开放申购/限大额等) |
| 赎回状态 | object | 赎回状态 |
| 下一开放日 | object | 下一开放交易日 |
| 购买起点 | float64 | 最低购买金额 |
| 日累计限定金额 | float64 | 单日累计限额 |
| 手续费 | float64 | 手续费率(%) |

**示例代码**
```python
import akshare as ak

# 获取基金申购状态
purchase_status = ak.fund_purchase_em()
print(purchase_status.head())

# 筛选可申购的基金
available_funds = purchase_status[purchase_status['申购状态'] == '开放申购']
print(f"可申购基金数量: {len(available_funds)}")
```

---

## 基金净值数据接口

### 1. fund_open_fund_daily_em - 开放式基金每日净值

**接口说明**
- **接口名称**: `fund_open_fund_daily_em`
- **数据来源**: 东方财富网-天天基金网
- **目标地址**: http://fund.eastmoney.com/fund.html
- **数据更新频率**: 交易日每日更新(约17:00后)
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 基金代码 | object | 基金代码 |
| 基金简称 | object | 基金简称 |
| 单位净值 | float64 | 当日单位净值 |
| 累计净值 | float64 | 累计净值 |
| 日增长率 | float64 | 日涨跌幅(%) |
| 申购状态 | object | 申购状态 |
| 赎回状态 | object | 赎回状态 |
| 手续费 | float64 | 手续费率(%) |

**示例代码**
```python
import akshare as ak

# 获取所有开放式基金每日净值
daily_nav = ak.fund_open_fund_daily_em()
print(daily_nav.head())

# 查询特定基金
fund_code = "000001"
specific_fund = daily_nav[daily_nav['基金代码'] == fund_code]
print(specific_fund)
```

**注意事项**
- 数据通常在交易日晚上17:00后更新
- 返回数据包含所有开放式基金，数据量较大

---

### 2. fund_open_fund_info_em - 单只基金历史净值

**接口说明**
- **接口名称**: `fund_open_fund_info_em`
- **数据来源**: 东方财富网-天天基金网
- **目标地址**: http://fund.eastmoney.com/pingzhongdata/710001.js
- **数据更新频率**: 交易日每日更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码，如"710001" |
| indicator | str | 是 | 数据类型，见下表 |
| period | str | 否 | 时间周期(仅对累计收益率走势有效) |

**indicator参数选项**
| 参数值 | 说明 |
|--------|------|
| 单位净值走势 | 获取单位净值历史数据 |
| 累计净值走势 | 获取累计净值历史数据 |
| 累计收益率走势 | 获取累计收益率数据 |
| 同类排名走势 | 获取同类基金排名数据 |
| 同类排名百分比 | 获取同类排名百分比 |
| 分红送配详情 | 获取分红送配信息 |
| 拆分详情 | 获取基金拆分信息 |

**period参数选项**(仅对累计收益率走势有效)
| 参数值 | 说明 |
|--------|------|
| 1月 | 近1月 |
| 3月 | 近3月 |
| 6月 | 近6月 |
| 1年 | 近1年 |
| 3年 | 近3年 |
| 5年 | 近5年 |
| 今年来 | 今年以来 |
| 成立来 | 成立以来 |

**返回字段-单位净值走势**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 净值日期 | object | 日期 |
| 单位净值 | float64 | 单位净值 |
| 日增长率 | float64 | 日涨跌幅(%) |

**返回字段-累计净值走势**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 净值日期 | object | 日期 |
| 累计净值 | float64 | 累计净值 |

**返回字段-累计收益率走势**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 日期 | object | 日期 |
| 累计收益率 | float64 | 累计收益率(%) |

**示例代码**
```python
import akshare as ak

# 获取单位净值走势
nav_trend = ak.fund_open_fund_info_em(symbol="710001", indicator="单位净值走势")
print(nav_trend.head())

# 获取累计收益率走势(成立以来)
return_trend = ak.fund_open_fund_info_em(
    symbol="710001", 
    indicator="累计收益率走势", 
    period="成立来"
)
print(return_trend.head())

# 获取同类排名走势
rank_trend = ak.fund_open_fund_info_em(symbol="710001", indicator="同类排名走势")
print(rank_trend.head())

# 获取分红送配详情
dividend_info = ak.fund_open_fund_info_em(symbol="161606", indicator="分红送配详情")
print(dividend_info)
```

**注意事项**
- 查询基金时注意前后端代码问题
- 部分历史数据可能存在缺失
- 同类排名数据更新频率较低

---

### 3. fund_etf_spot_em - ETF基金实时行情

**接口说明**
- **接口名称**: `fund_etf_spot_em`
- **数据来源**: 东方财富网
- **目标地址**: https://quote.eastmoney.com/center/gridlist.html#fund_etf
- **数据更新频率**: 交易日实时更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 代码 | object | ETF代码 |
| 名称 | object | ETF名称 |
| 最新价 | float64 | 最新成交价 |
| IOPV实时估值 | float64 | 基金份额参考净值 |
| 基金折价率 | float64 | 折价率(%) |
| 涨跌额 | float64 | 涨跌金额 |
| 涨跌幅 | float64 | 涨跌幅(%) |
| 成交量 | float64 | 成交量(手) |
| 成交额 | float64 | 成交额(元) |

**示例代码**
```python
import akshare as ak

# 获取ETF实时行情
etf_spot = ak.fund_etf_spot_em()
print(etf_spot.head())

# 筛选涨幅前10的ETF
top10_etf = etf_spot.nlargest(10, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅']]
print(top10_etf)
```

**注意事项**
- 早期版本(1.15.87-1.16.32)存在返回数据限制在200条的问题，建议升级到最新版本
- IOPV是ETF的实时估值参考

---

### 4. fund_etf_hist_min_em - ETF分时行情

**接口说明**
- **接口名称**: `fund_etf_hist_min_em`
- **数据来源**: 东方财富网
- **目标地址**: https://quote.eastmoney.com/sz159707.html
- **数据更新频率**: 实时更新
- **数据可靠性**: ⭐⭐⭐⭐ 较高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | ETF代码，如"513500" |
| start_date | str | 否 | 开始日期时间，默认"1979-09-01 09:32:00" |
| end_date | str | 否 | 结束日期时间，默认"2222-01-01 09:32:00" |
| period | str | 否 | 周期，可选{'1', '5', '15', '30', '60'} |
| adjust | str | 否 | 复权调整，可选{'', 'qfq', 'hfq'} |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 时间 | object | 交易时间 |
| 开盘 | float64 | 开盘价 |
| 收盘 | float64 | 收盘价 |
| 最高 | float64 | 最高价 |
| 最低 | float64 | 最低价 |
| 成交量 | float64 | 成交量 |
| 成交额 | float64 | 成交额 |
| 均价 | float64 | 成交均价 |

**示例代码**
```python
import akshare as ak

# 获取1分钟K线数据(近5个交易日)
min_data = ak.fund_etf_hist_min_em(
    symbol="511220",
    period="1",
    adjust="",
    start_date="2024-03-20 09:30:00",
    end_date="2024-03-20 17:40:00"
)
print(min_data)
```

**注意事项**
- 1分钟数据只返回近5个交易日数据且不复权
- 该接口只能获取近期的分时数据

---

### 5. fund_lof_spot_em - LOF基金实时行情

**接口说明**
- **接口名称**: `fund_lof_spot_em`
- **数据来源**: 东方财富网
- **目标地址**: https://quote.eastmoney.com/center/gridlist.html#fund_lof
- **数据更新频率**: 交易日实时更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**返回字段**
与ETF实时行情类似，包含代码、名称、最新价、涨跌幅等字段

---

## 基金持仓数据接口

### 1. fund_portfolio_hold_em - 基金股票持仓

**接口说明**
- **接口名称**: `fund_portfolio_hold_em`
- **数据来源**: 天天基金网
- **目标地址**: https://fundf10.eastmoney.com/ccmx_000001.html
- **数据更新频率**: 季度更新(随基金季报发布)
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码，如"000001" |
| date | str | 是 | 指定年份，如"2024" |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 股票代码 | object | 持仓股票代码 |
| 股票名称 | object | 持仓股票名称 |
| 占净值比例 | float64 | 占基金净值比例(%) |
| 持股数 | float64 | 持股数量(万股) |
| 持仓市值 | float64 | 持仓市值(万元) |
| 季度 | object | 报告季度 |

**示例代码**
```python
import akshare as ak

# 获取基金股票持仓
holdings = ak.fund_portfolio_hold_em(symbol="000001", date="2024")
print(holdings.head(10))

# 分析持仓集中度
top5_ratio = holdings[holdings['季度'].str.contains('1季度')]['占净值比例'].head(5).sum()
print(f"前5大重仓股占比: {top5_ratio:.2f}%")
```

**注意事项**
- 数据按季度更新，通常滞后1-2个月
- 只能获取已发布的季报数据
- 部分基金可能不披露完整持仓

---

### 2. fund_portfolio_bond_hold_em - 基金债券持仓

**接口说明**
- **接口名称**: `fund_portfolio_bond_hold_em`
- **数据来源**: 天天基金网
- **目标地址**: https://fundf10.eastmoney.com/ccmx_000001.html
- **数据更新频率**: 季度更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码 |
| date | str | 是 | 指定年份 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 债券代码 | object | 债券代码 |
| 债券名称 | object | 债券名称 |
| 占净值比例 | float64 | 占基金净值比例(%) |
| 持仓市值 | float64 | 持仓市值(万元) |
| 季度 | object | 报告季度 |

**示例代码**
```python
import akshare as ak

# 获取债券基金持仓
bond_holdings = ak.fund_portfolio_bond_hold_em(symbol="000001", date="2023")
print(bond_holdings)
```

---

### 3. fund_portfolio_industry_allocation_em - 基金行业配置

**接口说明**
- **接口名称**: `fund_portfolio_industry_allocation_em`
- **数据来源**: 天天基金网
- **目标地址**: https://fundf10.eastmoney.com/hytz_000001.html
- **数据更新频率**: 季度更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码 |
| date | str | 是 | 指定年份 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 行业类别 | object | 行业分类名称 |
| 占净值比例 | float64 | 占基金净值比例(%) |
| 市值 | float64 | 行业持仓市值(万元) |
| 截止时间 | object | 报告截止日期 |

**示例代码**
```python
import akshare as ak

# 获取基金行业配置
industry_allocation = ak.fund_portfolio_industry_allocation_em(symbol="000001", date="2023")
print(industry_allocation)

# 分析行业集中度
manufacturing_ratio = industry_allocation[industry_allocation['行业类别'] == '制造业']['占净值比例'].values
if len(manufacturing_ratio) > 0:
    print(f"制造业配置比例: {manufacturing_ratio[0]:.2f}%")
```

---

## 基金经理信息接口

### 1. fund_manager_em - 基金经理大全

**接口说明**
- **接口名称**: `fund_manager_em`
- **数据来源**: 天天基金网
- **目标地址**: https://fund.eastmoney.com/manager/default.html
- **数据更新频率**: 每日更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 姓名 | object | 基金经理姓名 |
| 所属公司 | object | 所属基金公司 |
| 现任基金代码 | object | 现任基金代码 |
| 现任基金 | object | 现任基金名称 |
| 累计从业时间 | int64 | 累计从业天数 |
| 现任基金资产总规模 | float64 | 管理资产总规模(亿元) |
| 现任基金最佳回报 | float64 | 最佳回报(%) |

**示例代码**
```python
import akshare as ak

# 获取所有基金经理信息
managers = ak.fund_manager_em()
print(managers.head())

# 筛选特定基金公司的经理
company_managers = managers[managers['所属公司'] == '华夏基金']
print(f"华夏基金基金经理数量: {len(company_managers)}")

# 按管理规模排序
top_managers = managers.nlargest(10, '现任基金资产总规模')
print(top_managers[['姓名', '所属公司', '现任基金资产总规模']])
```

**注意事项**
- 数据量较大(约30000+条记录)
- 一位基金经理可能管理多只基金，数据中会显示多条记录

---

## 基金分类和排名接口

### 1. fund_open_fund_rank_em - 开放式基金排行

**接口说明**
- **接口名称**: `fund_open_fund_rank_em`
- **数据来源**: 东方财富网
- **目标地址**: https://fund.eastmoney.com/data/fundranking.html
- **数据更新频率**: 交易日每日更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 否 | 基金类型，默认"全部" |

**symbol参数选项**
| 参数值 | 说明 |
|--------|------|
| 全部 | 全部开放式基金 |
| 股票型 | 股票型基金 |
| 混合型 | 混合型基金 |
| 债券型 | 债券型基金 |
| 指数型 | 指数型基金 |
| QDII | QDII基金 |
| FOF | FOF基金 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 排名序号 |
| 基金代码 | object | 基金代码 |
| 基金简称 | object | 基金简称 |
| 日期 | object | 数据日期 |
| 单位净值 | float64 | 单位净值 |
| 累计净值 | float64 | 累计净值 |
| 日增长率 | float64 | 日涨跌幅(%) |
| 近1周 | float64 | 近1周收益率(%) |
| 近1月 | float64 | 近1月收益率(%) |
| 近3月 | float64 | 近3月收益率(%) |
| 近6月 | float64 | 近6月收益率(%) |
| 近1年 | float64 | 近1年收益率(%) |
| 近2年 | float64 | 近2年收益率(%) |
| 近3年 | float64 | 近3年收益率(%) |
| 今年来 | float64 | 今年以来收益率(%) |
| 成立来 | float64 | 成立以来收益率(%) |
| 手续费 | object | 手续费率 |

**示例代码**
```python
import akshare as ak

# 获取全部开放式基金排名
all_rank = ak.fund_open_fund_rank_em(symbol="全部")
print(all_rank.head())

# 获取股票型基金排名
stock_rank = ak.fund_open_fund_rank_em(symbol="股票型")
print(stock_rank.head(10))

# 按近1年收益率排序
top_performers = all_rank.nlargest(10, '近1年')
print(top_performers[['基金简称', '近1年', '近3年']])
```

---

### 2. fund_exchange_rank_em - 场内交易基金排行

**接口说明**
- **接口名称**: `fund_exchange_rank_em`
- **数据来源**: 东方财富网
- **数据更新频率**: 交易日每日更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
包含基金代码、名称、净值、涨跌幅、各周期收益率等字段

**示例代码**
```python
import akshare as ak

# 获取场内基金排行
exchange_rank = ak.fund_exchange_rank_em()
print(exchange_rank.head())
```

---

### 3. fund_money_rank_em - 货币型基金排行

**接口说明**
- **接口名称**: `fund_money_rank_em`
- **数据来源**: 东方财富网
- **目标地址**: https://fund.eastmoney.com/data/hbxfundranking.html
- **数据更新频率**: 交易日每日更新(17:00后)
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 基金代码 | object | 基金代码 |
| 基金简称 | object | 基金简称 |
| 日期 | object | 数据日期 |
| 万份收益 | float64 | 万份收益 |
| 年化收益率7日 | float64 | 7日年化收益率(%) |
| 年化收益率14日 | float64 | 14日年化收益率(%) |
| 年化收益率28日 | float64 | 28日年化收益率(%) |
| 近1月 | float64 | 近1月收益率(%) |
| 近3月 | float64 | 近3月收益率(%) |
| 近6月 | float64 | 近6月收益率(%) |
| 近1年 | float64 | 近1年收益率(%) |
| 近2年 | float64 | 近2年收益率(%) |
| 近3年 | float64 | 近3年收益率(%) |
| 近5年 | float64 | 近5年收益率(%) |
| 今年来 | float64 | 今年以来收益率(%) |
| 成立来 | float64 | 成立以来收益率(%) |

**示例代码**
```python
import akshare as ak

# 获取货币基金排行
money_rank = ak.fund_money_rank_em()
print(money_rank.head())

# 按7日年化收益率排序
top_money = money_rank.nlargest(10, '年化收益率7日')
print(top_money[['基金简称', '年化收益率7日', '万份收益']])
```

**注意事项**
- 货币基金单位净值固定为1.0000元
- 数据在交易日17:00后更新

---

### 4. fund_new_found_em - 新发基金

**接口说明**
- **接口名称**: `fund_new_found_em`
- **数据来源**: 天天基金网
- **目标地址**: https://fund.eastmoney.com/data/xinfound.html
- **数据更新频率**: 每日更新
- **数据可靠性**: ⭐⭐⭐⭐⭐ 高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| - | - | - | 无需参数 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 基金代码 | object | 基金代码 |
| 基金简称 | object | 基金简称 |
| 基金公司 | object | 基金公司 |
| 基金类型 | object | 基金类型 |
| 成立日期 | object | 成立日期 |
| 基金经理 | object | 基金经理 |
| 申购状态 | object | 申购状态 |
| 手续费 | float64 | 手续费率(%) |

**示例代码**
```python
import akshare as ak

# 获取新发基金
new_funds = ak.fund_new_found_em()
print(new_funds.head())
```

---

## 其他基金相关接口

### 1. fund_scale_open_sina - 开放式基金规模

**接口说明**
- **接口名称**: `fund_scale_open_sina`
- **数据来源**: 新浪财经
- **目标地址**: https://vip.stock.finance.sina.com.cn/fund_center/index.html
- **数据更新频率**: 定期更新
- **数据可靠性**: ⭐⭐⭐⭐ 较高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金类型 |

**symbol参数选项**
| 参数值 | 说明 |
|--------|------|
| 股票型基金 | 股票型基金规模 |
| 混合型基金 | 混合型基金规模 |
| 债券型基金 | 债券型基金规模 |
| 货币型基金 | 货币型基金规模 |
| QDII基金 | QDII基金规模 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 序号 | int64 | 序号 |
| 基金代码 | object | 基金代码 |
| 基金简称 | object | 基金简称 |
| 单位净值 | float64 | 单位净值(元) |
| 总募集规模 | float64 | 总募集规模(万份) |
| 最近总份额 | float64 | 最近总份额(份) |
| 成立日期 | object | 成立日期 |
| 基金经理 | object | 基金经理 |
| 更新日期 | object | 数据更新日期 |

---

### 2. fund_rating_ja - 基金评级(济安金信)

**接口说明**
- **接口名称**: `fund_rating_ja`
- **数据来源**: 济安金信
- **数据更新频率**: 定期更新
- **数据可靠性**: ⭐⭐⭐⭐ 较高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| date | str | 否 | 评级日期，如"20200930" |

**返回字段**
包含基金代码、名称、基金经理、基金公司、各周期涨跌幅、评级等

---

### 3. fund_individual_analysis_xq - 雪球基金分析

**接口说明**
- **接口名称**: `fund_individual_analysis_xq`
- **数据来源**: 雪球基金
- **目标地址**: https://danjuanfunds.com/funding/000001
- **数据更新频率**: 每日更新
- **数据可靠性**: ⭐⭐⭐⭐ 较高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码 |

**返回字段**
包含基金历史表现分析数据

---

### 4. fund_individual_profit_probability_xq - 基金盈利概率

**接口说明**
- **接口名称**: `fund_individual_profit_probability_xq`
- **数据来源**: 雪球基金
- **数据更新频率**: 每日更新
- **数据可靠性**: ⭐⭐⭐⭐ 较高

**输入参数**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | str | 是 | 基金代码 |

**返回字段**
| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 持有时间 | object | 持有时间周期 |
| 盈利概率 | float64 | 盈利概率(%) |
| 平均收益 | float64 | 平均收益率(%) |

**示例代码**
```python
import akshare as ak

# 获取基金盈利概率
profit_prob = ak.fund_individual_profit_probability_xq(symbol="159915")
print(profit_prob)
```

---

## 总结与建议

### AKShare基金数据接口优势

| 优势 | 说明 |
|------|------|
| 数据全面 | 覆盖公募基金、ETF、LOF、货币基金等多种类型 |
| 免费开源 | 完全免费，无需注册或积分 |
| 更新及时 | 净值数据交易日每日更新，持仓数据季度更新 |
| 使用简便 | Python接口，返回Pandas DataFrame格式 |
| 文档完善 | 官方文档详细，示例代码丰富 |

### AKShare基金数据接口局限性

| 局限性 | 说明 |
|--------|------|
| 数据延迟 | 部分数据存在1-2天延迟 |
| 历史限制 | 部分接口无法获取过于久远的历史数据 |
| 频率限制 | 频繁调用可能触发数据源限制 |
| 数据缺失 | 个别基金可能存在数据缺失情况 |
| 依赖第三方 | 数据来源于第三方平台，存在变动风险 |

### 适用场景

1. **个人投资研究**: 适合个人投资者进行基金筛选和分析
2. **量化策略回测**: 可获取历史净值数据进行策略验证
3. **投资组合监控**: 实时监控持仓基金表现
4. **基金评级分析**: 基于多维度数据进行基金评级
5. **学术研究**: 金融学术研究的数据来源

### 使用建议

1. **版本更新**: 定期升级AKShare到最新版本
   ```bash
   pip install akshare --upgrade
   ```

2. **错误处理**: 添加异常处理机制
   ```python
   import akshare as ak
   
   try:
       data = ak.fund_open_fund_daily_em()
   except Exception as e:
       print(f"数据获取失败: {e}")
   ```

3. **数据缓存**: 对于不频繁变化的数据，建议本地缓存
   ```python
   import pickle
   
   # 缓存基金列表
   fund_list = ak.fund_name_em()
   with open('fund_list.pkl', 'wb') as f:
       pickle.dump(fund_list, f)
   ```

4. **合理调用**: 避免过于频繁的API调用，尊重数据源限制

### 数据来源可靠性评级

| 数据源 | 可靠性 | 说明 |
|--------|--------|------|
| 东方财富网(天天基金网) | ⭐⭐⭐⭐⭐ | 数据权威，更新及时 |
| 新浪财经 | ⭐⭐⭐⭐ | 数据稳定，覆盖全面 |
| 雪球 | ⭐⭐⭐⭐ | 分析数据丰富 |
| 济安金信 | ⭐⭐⭐⭐ | 专业评级机构 |

---

## 参考资料

- AKShare官方文档: https://akshare.akfamily.xyz/
- 东方财富网: https://fund.eastmoney.com/
- 天天基金网: https://fund.eastmoney.com/
- 雪球基金: https://danjuanfunds.com/

---

*报告生成时间: 2025年*
*AKShare版本: 1.18+*
