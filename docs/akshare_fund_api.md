# AKShare 公募基金数据接口文档

> 文档来源：https://akshare.akfamily.xyz/data/fund/fund_public.html
> 整理日期：2026-02-14

---

## 目录

1. [基金基本信息](#1-基金基本信息)
2. [基金行情](#2-基金行情)
3. [基金净值](#3-基金净值)
4. [分红送配](#4-分红送配)
5. [基金排行](#5-基金排行)
6. [基金持仓](#6-基金持仓)
7. [基金评级](#7-基金评级)
8. [基金经理](#8-基金经理)
9. [新发基金](#9-新发基金)
10. [基金规模](#10-基金规模)
11. [基金公司](#11-基金公司)
12. [基金转换](#12-基金转换)

---

## 1. 基金基本信息

### 1.1 fund_name_em - 基金基本信息（东方财富）

**接口说明**：东方财富网-天天基金网-基金数据-所有基金的基本信息数据

**限量**：单次返回当前时刻所有历史数据

**输入参数**：无

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 基金代码 | object | - |
| 拼音缩写 | object | - |
| 基金简称 | object | - |
| 基金类型 | object | - |
| 拼音全称 | object | - |

**接口示例**：
```python
import akshare as ak
fund_name_em_df = ak.fund_name_em()
print(fund_name_em_df)
```

---

### 1.2 fund_individual_basic_info_xq - 基金基本信息（雪球）

**接口说明**：雪球基金-基金详情

**限量**：单次返回单只基金基本信息

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码，如 "000001" |
| timeout | float | 超时参数，默认 None |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| item | object | 项目名 |
| value | object | 项目值 |

**接口示例**：
```python
import akshare as ak
fund_individual_basic_info_xq_df = ak.fund_individual_basic_info_xq(symbol="000001")
print(fund_individual_basic_info_xq_df)
```

**返回数据项**：基金代码、基金名称、基金全称、成立时间、最新规模、基金公司、基金经理、托管银行、基金类型、评级机构、基金评级、投资策略、投资目标、业绩比较基准

---

### 1.3 fund_info_index_em - 基金基本信息-指数型

**接口说明**：东方财富网-天天基金网-基金数据-基金基本信息-指数型

**限量**：单次返回当前时刻所有历史数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 可选："全部", "沪深指数", "行业主题", "大盘指数", "中盘指数", "小盘指数", "股票指数", "债券指数" |
| indicator | str | 可选："全部", "被动指数型", "增强指数型" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 基金代码 | object | - |
| 基金名称 | object | - |
| 单位净值 | float64 | - |
| 日期 | object | - |
| 日增长率 | float64 | 单位：% |
| 近1周/1月/3月/6月/1年/2年/3年 | float64 | 单位：% |
| 今年来 | float64 | 单位：% |
| 成立来 | float64 | 单位：% |
| 手续费 | float64 | 单位：% |
| 起购金额 | object | - |
| 跟踪标的 | object | - |
| 跟踪方式 | object | - |

**接口示例**：
```python
import akshare as ak
fund_info_index_em_df = ak.fund_info_index_em(symbol="沪深指数", indicator="增强指数型")
print(fund_info_index_em_df)
```

---

### 1.4 fund_purchase_em - 基金申购状态

**接口说明**：东方财富网站-天天基金网-基金数据-基金申购状态

**限量**：单次返回当前时刻所有历史数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | object | - |
| 基金代码 | object | - |
| 基金简称 | object | - |
| 基金类型 | object | - |
| 最新净值/万份收益 | float64 | - |
| 最新净值/万份收益-报告时间 | object | - |
| 申购状态 | object | - |
| 赎回状态 | object | - |
| 下一开放日 | object | - |
| 购买起点 | float64 | - |
| 日累计限定金额 | float64 | - |
| 手续费 | float64 | 单位：% |

**接口示例**：
```python
import akshare as ak
fund_purchase_em_df = ak.fund_purchase_em()
print(fund_purchase_em_df)
```

---

## 2. 基金行情

### 2.1 fund_etf_spot_em - ETF基金实时行情（东财）

**接口说明**：东方财富-ETF 实时行情

**限量**：单次返回所有数据

**输出参数**（部分关键字段）：

| 名称 | 类型 | 描述 |
|------|------|------|
| 代码 | object | - |
| 名称 | object | - |
| 最新价 | float64 | - |
| IOPV实时估值 | float64 | - |
| 基金折价率 | float64 | 单位：% |
| 涨跌额 | float64 | - |
| 涨跌幅 | float64 | 单位：% |
| 成交量 | float64 | - |
| 成交额 | float64 | - |
| 开盘价/最高价/最低价/昨收 | float64 | - |
| 换手率 | float64 | - |
| 主力净流入-净额/净占比 | float64 | - |
| 流通市值/总市值 | int64 | - |
| 数据日期 | object | - |
| 更新时间 | object | - |

**接口示例**：
```python
import akshare as ak
fund_etf_spot_em_df = ak.fund_etf_spot_em()
print(fund_etf_spot_em_df)
```

---

### 2.2 fund_etf_category_ths - 基金实时行情（同花顺）

**接口说明**：同花顺理财-基金数据-每日净值-实时行情

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 可选："股票型", "债券型", "混合型", "ETF", "LOF", "QDII", "保本型", "指数型", ""(全部) |
| date | str | 默认返回当前最新数据 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码 | object | - |
| 基金名称 | object | - |
| 当前-单位净值/累计净值 | float64 | - |
| 前一日-单位净值/累计净值 | float64 | - |
| 增长值/增长率 | float64 | - |
| 赎回状态/申购状态 | object | - |
| 最新-交易日/单位净值/累计净值 | object/float64 | - |
| 基金类型 | object | - |
| 查询日期 | object | - |

**接口示例**：
```python
import akshare as ak
fund_etf_category_ths_df = ak.fund_etf_category_ths(symbol="ETF", date="20240620")
print(fund_etf_category_ths_df)
```

---

### 2.3 fund_lof_spot_em - LOF基金实时行情（东财）

**接口说明**：东方财富-LOF 实时行情

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 代码 | object | - |
| 名称 | object | - |
| 最新价/涨跌额/涨跌幅 | float64 | - |
| 成交量/成交额 | float64 | - |
| 开盘价/最高价/最低价/昨收 | float64 | - |
| 换手率 | float64 | - |
| 流通市值/总市值 | int64 | - |

**接口示例**：
```python
import akshare as ak
fund_lof_spot_em_df = ak.fund_lof_spot_em()
print(fund_lof_spot_em_df)
```

---

### 2.4 fund_etf_hist_min_em - ETF基金分时行情（东财）

**接口说明**：东方财富-ETF 分时行情（只能获取近期的分时数据）

**限量**：单次返回指定 ETF、频率、复权调整和时间区间的分时数据，1分钟数据只返回近5个交易日且不复权

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | ETF代码，如 '513500' |
| start_date | str | 开始日期时间，如 "1979-09-01 09:32:00" |
| end_date | str | 结束日期时间，如 "2222-01-01 09:32:00" |
| period | str | 可选：'1', '5', '15', '30', '60' |
| adjust | str | 可选：''(不复权), 'qfq'(前复权), 'hfq'(后复权) |

**输出参数（1分钟数据）**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 时间 | object | - |
| 开盘/收盘/最高/最低 | float64 | - |
| 成交量/成交额 | float64 | - |
| 均价 | float64 | - |

**输出参数（其他周期）**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 时间 | object | - |
| 开盘/收盘/最高/最低 | float64 | - |
| 涨跌幅/涨跌额 | float64 | - |
| 成交量/成交额 | float64 | - |
| 振幅/换手率 | float64 | 单位：% |

**接口示例**：
```python
import akshare as ak
# 1分钟数据
fund_etf_hist_min_em_df = ak.fund_etf_hist_min_em(symbol="511220", period="1", adjust="", start_date="2024-03-20 09:30:00", end_date="2024-03-20 17:40:00")
print(fund_etf_hist_min_em_df)

# 其他周期
fund_etf_hist_min_em_df = ak.fund_etf_hist_min_em(symbol="513500", period="5", adjust="hfq", start_date="2023-12-11 09:32:00", end_date="2023-12-11 17:40:00")
print(fund_etf_hist_min_em_df)
```

---

### 2.5 fund_etf_hist_em - ETF基金历史行情（东财）

**接口说明**：东方财富-ETF 行情，历史数据按日频率更新

**限量**：单次返回指定 ETF、指定周期和指定日期间的历史行情日频率数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | ETF代码，如 '159707' |
| period | str | 可选：'daily', 'weekly', 'monthly' |
| start_date | str | 开始日期，如 '20000101' |
| end_date | str | 结束日期，如 '20230104' |
| adjust | str | ''(不复权), 'qfq'(前复权), 'hfq'(后复权) |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 日期 | object | - |
| 开盘/收盘/最高/最低 | float64 | - |
| 成交量 | int64 | - |
| 成交额 | float64 | - |
| 振幅 | float64 | - |
| 涨跌幅/涨跌额 | float64 | - |
| 换手率 | float64 | - |

**接口示例**：
```python
import akshare as ak
fund_etf_hist_em_df = ak.fund_etf_hist_em(symbol="513500", period="daily", start_date="20000101", end_date="20230201", adjust="")
print(fund_etf_hist_em_df)
```

---

### 2.6 fund_lof_hist_em - LOF基金历史行情（东财）

**接口说明**：东方财富-LOF 行情，历史数据按日频率更新

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | LOF代码，如 '166009' |
| period | str | 可选：'daily', 'weekly', 'monthly' |
| start_date | str | 开始日期 |
| end_date | str | 结束日期 |
| adjust | str | ''(不复权), 'qfq'(前复权), 'hfq'(后复权) |

**输出参数**：同 fund_etf_hist_em

**接口示例**：
```python
import akshare as ak
fund_lof_hist_em_df = ak.fund_lof_hist_em(symbol="166009", period="daily", start_date="20000101", end_date="20230703", adjust="")
print(fund_lof_hist_em_df)
```

---

## 3. 基金净值

### 3.1 fund_open_fund_daily_em - 开放式基金-实时数据

**接口说明**：东方财富网-天天基金网-基金数据，每个交易日 16:00-23:00 更新当日的最新开放式基金净值数据

**限量**：单次返回当前时刻所有历史数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 基金代码 | str | - |
| 基金简称 | str | - |
| 单位净值/累计净值 | float | 随时间变动 |
| 前交易日-单位净值/累计净值 | float | 随时间变动 |
| 日增长值/日增长率 | float | - |
| 申购状态/赎回状态 | str | - |
| 手续费 | str | 单位：% |

**接口示例**：
```python
import akshare as ak
fund_open_fund_daily_em_df = ak.fund_open_fund_daily_em()
print(fund_open_fund_daily_em_df)
```

---

### 3.2 fund_open_fund_info_em - 开放式基金-历史数据

**接口说明**：东方财富网-天天基金网-基金数据-具体基金信息

**限量**：单次返回当前时刻所有历史数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码，如 "710001" |
| indicator | str | 指标类型，参见下表 |
| period | str | 只对"累计收益率走势"有效，可选："1月", "3月", "6月", "1年", "3年", "5年", "今年来", "成立来" |

**indicator 参数一览表**：

| 参数名称 | 备注 |
|----------|------|
| 单位净值走势 | - |
| 累计净值走势 | - |
| 累计收益率走势 | 需配合 period 参数 |
| 同类排名走势 | - |
| 同类排名百分比 | - |
| 分红送配详情 | - |
| 拆分详情 | - |

**接口示例**：
```python
import akshare as ak
# 单位净值走势
fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="710001", indicator="单位净值走势")
print(fund_open_fund_info_em_df)

# 累计收益率走势
fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="710001", indicator="累计收益率走势", period="成立来")
print(fund_open_fund_info_em_df)
```

---

### 3.3 fund_money_fund_daily_em - 货币型基金-实时数据

**接口说明**：东方财富网-天天基金网-基金数据-货币型基金收益，每个交易日 16:00～23:00 更新

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 基金代码/基金简称 | str | - |
| 当前交易日-万份收益/7日年化%/单位净值 | float | - |
| 前一交易日-万份收益/7日年化%/单位净值 | float | - |
| 日涨幅 | str | - |
| 成立日期/基金经理/手续费 | str | - |
| 可购全部 | str | - |

**接口示例**：
```python
import akshare as ak
fund_money_fund_daily_em_df = ak.fund_money_fund_daily_em()
print(fund_money_fund_daily_em_df)
```

---

### 3.4 fund_money_fund_info_em - 货币型基金-历史数据

**接口说明**：东方财富网-天天基金网-基金数据-货币型基金-历史净值

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码，如 "000009" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 净值日期 | object | - |
| 每万份收益 | float64 | - |
| 7日年化收益率 | float64 | - |
| 申购状态/赎回状态 | object | - |

**接口示例**：
```python
import akshare as ak
fund_money_fund_info_em_df = ak.fund_money_fund_info_em(symbol="000009")
print(fund_money_fund_info_em_df)
```

---

## 4. 分红送配

### 4.1 fund_etf_dividend_sina - 基金累计分红（新浪）

**接口说明**：新浪财经-基金-ETF 基金-累计分红

**限量**：单次返回所有历史数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 如 "sh510050" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 日期 | object | 除权除息日 |
| 累计分红 | float64 | - |

**接口示例**：
```python
import akshare as ak
fund_etf_dividend_sina_df = ak.fund_etf_dividend_sina(symbol="sh510050")
print(fund_etf_dividend_sina_df)
```

---

### 4.2 fund_fh_em - 基金分红

**接口说明**：天天基金网-基金数据-分红送配-基金分红

**限量**：单次返回所有历史数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| year | str | 年份，最早支持 1999 年 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 权益登记日/除息日期 | object | - |
| 分红 | float64 | 单位：元/份 |
| 分红发放日 | object | - |

**接口示例**：
```python
import akshare as ak
fund_fh_em_df = ak.fund_fh_em(year="2025")
print(fund_fh_em_df)
```

---

### 4.3 fund_cf_em - 基金拆分

**接口说明**：天天基金网-基金数据-分红送配-基金拆分

**限量**：单次返回所有历史数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| year | str | 年份，最早支持 2005 年 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 拆分折算日 | object | - |
| 拆分类型 | object | - |
| 拆分折算 | float64 | 单位：每份 |

**接口示例**：
```python
import akshare as ak
fund_cf_em_df = ak.fund_cf_em(year="2025")
print(fund_cf_em_df)
```

---

### 4.4 fund_fh_rank_em - 基金分红排行

**接口说明**：天天基金网-基金数据-分红送配-基金分红排行

**限量**：单次返回所有历史数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 累计分红 | float64 | 单位：元/份 |
| 累计次数 | int64 | - |
| 成立日期 | object | - |

**接口示例**：
```python
import akshare as ak
fund_fh_rank_em_df = ak.fund_fh_rank_em()
print(fund_fh_rank_em_df)
```

---

## 5. 基金排行

### 5.1 fund_open_fund_rank_em - 开放式基金排行

**接口说明**：东方财富网-数据中心-开放式基金排行

**限量**：单次返回当前时刻所有数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 可选："全部", "股票型", "混合型", "债券型", "指数型", "QDII", "FOF" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 日期 | object | - |
| 单位净值/累计净值 | float64 | - |
| 日增长率 | float64 | 单位：% |
| 近1周/1月/3月/6月/1年/2年/3年 | float64 | 单位：% |
| 今年来/成立来 | float64 | 单位：% |
| 手续费 | object | - |

**接口示例**：
```python
import akshare as ak
fund_open_fund_rank_em_df = ak.fund_open_fund_rank_em(symbol="全部")
print(fund_open_fund_rank_em_df)
```

---

### 5.2 fund_exchange_rank_em - 场内交易基金排行榜

**接口说明**：东方财富网-数据中心-场内交易基金排行榜，每个交易日 17 点后更新

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 类型 | object | - |
| 日期 | object | - |
| 单位净值/累计净值 | float64 | - |
| 近1周/1月/3月/6月/1年/2年/3年 | float64 | 单位：% |
| 今年来/成立来 | float64 | 单位：% |
| 成立日期 | object | - |

**接口示例**：
```python
import akshare as ak
fund_exchange_rank_em_df = ak.fund_exchange_rank_em()
print(fund_exchange_rank_em_df)
```

---

### 5.3 fund_money_rank_em - 货币型基金排行

**接口说明**：东方财富网-数据中心-货币型基金排行，每个交易日 17 点后更新

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 日期 | object | - |
| 万份收益 | float64 | 单位：% |
| 年化收益率7日/14日/28日 | float64 | 单位：% |
| 近1月/3月/6月/1年/2年/3年/5年 | float64 | 单位：% |
| 今年来/成立来 | float64 | 单位：% |
| 手续费 | object | - |

**接口示例**：
```python
import akshare as ak
fund_money_rank_em_df = ak.fund_money_rank_em()
print(fund_money_rank_em_df)
```

---

### 5.4 fund_hk_rank_em - 香港基金排行

**接口说明**：东方财富网-数据中心-基金排行-香港基金排行

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 币种 | object | - |
| 日期 | object | - |
| 单位净值 | float64 | - |
| 日增长率 | float64 | 单位：% |
| 近1周/1月/3月/6月/1年/2年/3年 | float64 | 单位：% |
| 今年来/成立来 | float64 | 单位：% |
| 可购买 | object | - |
| 香港基金代码 | object | 用于查询历史净值数据 |

**接口示例**：
```python
import akshare as ak
fund_hk_rank_em_df = ak.fund_hk_rank_em()
print(fund_hk_rank_em_df)
```

---

## 6. 基金持仓

### 6.1 fund_portfolio_hold_em - 基金持仓

**接口说明**：天天基金网-基金档案-投资组合-基金持仓

**限量**：单次返回指定 symbol 和 date 的所有持仓数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码，如 "000001" |
| date | str | 指定年份，如 "2024" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 股票代码/股票名称 | object | - |
| 占净值比例 | float64 | 单位：% |
| 持股数 | float64 | 单位：万股 |
| 持仓市值 | float64 | 单位：万元 |
| 季度 | object | - |

**接口示例**：
```python
import akshare as ak
fund_portfolio_hold_em_df = ak.fund_portfolio_hold_em(symbol="000001", date="2024")
print(fund_portfolio_hold_em_df)
```

---

### 6.2 fund_portfolio_bond_hold_em - 债券持仓

**接口说明**：天天基金网-基金档案-投资组合-债券持仓

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码 |
| date | str | 指定年份 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 债券代码/债券名称 | object | - |
| 占净值比例 | float64 | 单位：% |
| 持仓市值 | float64 | 单位：万元 |
| 季度 | object | - |

**接口示例**：
```python
import akshare as ak
fund_portfolio_bond_hold_em_df = ak.fund_portfolio_bond_hold_em(symbol="000001", date="2023")
print(fund_portfolio_bond_hold_em_df)
```

---

### 6.3 fund_portfolio_industry_allocation_em - 行业配置

**接口说明**：天天基金网-基金档案-投资组合-行业配置

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码 |
| date | str | 指定年份 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 行业类别 | object | - |
| 占净值比例 | float64 | 单位：% |
| 市值 | float64 | 单位：万元 |
| 截止时间 | object | - |

**接口示例**：
```python
import akshare as ak
fund_portfolio_industry_allocation_em_df = ak.fund_portfolio_industry_allocation_em(symbol="000001", date="2023")
print(fund_portfolio_industry_allocation_em_df)
```

---

### 6.4 fund_individual_detail_hold_xq - 基金持仓资产比例（雪球）

**接口说明**：雪球基金-基金详情-基金持仓-详情

**限量**：单次返回单只基金指定日期的持仓大类资产比例

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码，如 "000001" |
| date | str | 季度日期，如 "20231231" |
| timeout | float | 超时参数，默认 None |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 资产类型 | object | - |
| 仓位占比 | float64 | 单位：% |

**接口示例**：
```python
import akshare as ak
fund_individual_detail_hold_xq_df = ak.fund_individual_detail_hold_xq(symbol="002804", date="20231231")
print(fund_individual_detail_hold_xq_df)
```

---

## 7. 基金评级

### 7.1 fund_rating_all - 基金评级总汇

**接口说明**：天天基金网-基金评级-基金评级总汇

**限量**：单次返回所有基金评级数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 代码/简称 | object | - |
| 基金经理/基金公司 | object | - |
| 5星评级家数 | int64 | - |
| 上海证券/招商证券/济安金信/晨星评级 | float64 | - |
| 手续费 | float64 | - |
| 类型 | object | - |

**接口示例**：
```python
import akshare as ak
fund_rating_all_df = ak.fund_rating_all()
print(fund_rating_all_df)
```

---

### 7.2 fund_rating_sh - 上海证券评级

**接口说明**：天天基金网-基金评级-上海证券评级

**限量**：单次返回指定交易日的所有基金评级数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| date | str | 查询日期，如 '20230630' |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 代码/简称 | object | - |
| 基金经理/基金公司 | object | - |
| 3年期评级-3年评级/较上期 | int64/float64 | - |
| 5年期评级-5年评级/较上期 | float64 | - |
| 单位净值/日期/日增长率 | float64/object | - |
| 近1年/3年/5年涨幅 | float64 | 单位：% |
| 手续费/类型 | object | - |

**接口示例**：
```python
import akshare as ak
fund_rating_sh_df = ak.fund_rating_sh(date='20230630')
print(fund_rating_sh_df)
```

---

### 7.3 fund_rating_zs - 招商证券评级

**接口说明**：天天基金网-基金评级-招商证券评级

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| date | str | 查询日期，如 '20230331' |

**输出参数**：类似 fund_rating_sh

**接口示例**：
```python
import akshare as ak
fund_rating_zs_df = ak.fund_rating_zs(date='20230331')
print(fund_rating_zs_df)
```

---

### 7.4 fund_rating_ja - 济安金信评级

**接口说明**：天天基金网-基金评级-济安金信评级

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| date | str | 查询日期，如 '20200930' |

**输出参数**：类似 fund_rating_sh

**接口示例**：
```python
import akshare as ak
fund_rating_ja_df = ak.fund_rating_ja(date='20200930')
print(fund_rating_ja_df)
```

---

## 8. 基金经理

### 8.1 fund_manager_em - 基金经理大全

**接口说明**：天天基金网-基金数据-基金经理大全

**限量**：单次返回所有基金经理数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 姓名 | object | - |
| 所属公司 | object | - |
| 现任基金代码/现任基金 | object | - |
| 累计从业时间 | int64 | 单位：天 |
| 现任基金资产总规模 | float64 | 单位：亿元 |
| 现任基金最佳回报 | float64 | 单位：% |

**接口示例**：
```python
import akshare as ak
fund_manager_em_df = ak.fund_manager_em()
print(fund_manager_em_df)
```

---

## 9. 新发基金

### 9.1 fund_new_found_em - 新成立基金

**接口说明**：天天基金网-基金数据-新发基金-新成立基金

**限量**：单次返回所有新发基金数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 基金代码/基金简称 | object | - |
| 发行公司 | object | - |
| 基金类型 | object | - |
| 集中认购期 | object | - |
| 募集份额 | float64 | 单位：亿份 |
| 成立日期 | object | - |
| 成立来涨幅 | float64 | 单位：% |
| 基金经理 | object | - |
| 申购状态 | object | - |
| 优惠费率 | float64 | 单位：% |

**接口示例**：
```python
import akshare as ak
fund_new_found_em_df = ak.fund_new_found_em()
print(fund_new_found_em_df)
```

---

## 10. 基金规模

### 10.1 fund_scale_open_sina - 开放式基金规模

**接口说明**：基金数据中心-基金规模-开放式基金

**限量**：单次返回指定 symbol 的基金规模数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 可选："股票型基金", "混合型基金", "债券型基金", "货币型基金", "QDII基金" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金代码/基金简称 | object | - |
| 单位净值 | float64 | 单位：元 |
| 总募集规模 | float64 | 单位：万份 |
| 最近总份额 | float64 | 单位：份 |
| 成立日期 | object | - |
| 基金经理 | object | - |
| 更新日期 | object | - |

**接口示例**：
```python
import akshare as ak
fund_scale_open_sina_df = ak.fund_scale_open_sina(symbol='股票型基金')
print(fund_scale_open_sina_df)
```

---

### 10.2 fund_scale_close_sina - 封闭式基金规模

**接口说明**：基金数据中心-基金规模-封闭式基金

**限量**：单次返回所有封闭式基金的基金规模数据

**输出参数**：同 fund_scale_open_sina

**接口示例**：
```python
import akshare as ak
fund_scale_close_sina_df = ak.fund_scale_close_sina()
print(fund_scale_close_sina_df)
```

---

## 11. 基金公司

### 11.1 fund_company_em - 基金公司一览

**接口说明**：天天基金网-基金数据-基金公司一览

**限量**：单次返回所有基金公司的数据

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 基金公司 | object | - |
| 成立日期 | object | - |
| 管理规模 | float64 | 单位：亿元 |
| 基金数量 | int64 | - |
| 经理人数 | int64 | - |
| 天相评级 | int64 | - |
| 简介 | object | - |

**接口示例**：
```python
import akshare as ak
fund_company_em_df = ak.fund_company_em()
print(fund_company_em_df)
```

---

## 12. 基金转换

### 12.1 fund_convert_em - 基金转换

**接口说明**：天天基金网-基金数据-基金转换

**限量**：单次返回所有基金转换的数据

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| fund_code | str | 基金代码，如 "000001" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 序号 | int64 | - |
| 转出基金代码/名称 | object | - |
| 转入基金代码/名称 | object | - |
| 转换费率 | float64 | - |

**接口示例**：
```python
import akshare as ak
fund_convert_em_df = ak.fund_convert_em(fund_code="000001")
print(fund_convert_em_df)
```

---

## 附录：其他实用接口

### fund_value_estimation_em - 净值估算

**接口说明**：东方财富网-数据中心-净值估算

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 可选：'全部', '股票型', '混合型', '债券型', '指数型', 'QDII', 'ETF联接', 'LOF', '场内交易基金' |

**接口示例**：
```python
import akshare as ak
fund_value_estimation_em_df = ak.fund_value_estimation_em(symbol="混合型")
print(fund_value_estimation_em_df)
```

---

### fund_individual_achievement_xq - 基金业绩（雪球）

**接口说明**：雪球基金-基金详情-基金业绩-详情

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码 |
| timeout | float | 超时参数 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 业绩类型 | object | - |
| 周期 | object | - |
| 本产品区间收益 | float64 | 单位：% |
| 本产品最大回撤 | float64 | 单位：% |
| 周期收益同类排名 | object | - |

**接口示例**：
```python
import akshare as ak
fund_individual_achievement_xq_df = ak.fund_individual_achievement_xq(symbol="000001")
print(fund_individual_achievement_xq_df)
```

---

### fund_individual_analysis_xq - 基金数据分析（雪球）

**接口说明**：雪球基金-基金详情-数据分析，数据来源于蛋卷基金API

**数据来源**：https://danjuanfunds.com/djapi/fund/base/quote/data/index/analysis/{fund_code}

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码 |
| timeout | float | 超时参数 |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 周期 | object | 统计周期：近1年、近3年、近5年 |
| 较同类风险收益比 | int64 | 综合统计基金承担风险获取收益的性价比排名，单位：% |
| 较同类抗风险波动 | int64 | 综合统计基金抗风险波动能力排名，单位：% |
| 年化波动率 | float64 | 基金的年化波动幅度，数值越小波动越小，单位：% |
| 年化夏普比率 | float64 | 每承受一单位总风险产生的超额收益，数值越大越好 |
| 最大回撤 | float64 | 净值走到最低点时的收益率回撤幅度最大值，单位：% |

**字段含义详解**：

| 字段 | 含义 | 计算方式 |
|------|------|---------|
| 较同类风险收益比 | 风险收益性价比排名 | 取基金夏普比率的同类（二级分类）排名计算 |
| 较同类抗风险波动 | 抗风险波动能力排名 | 取基金年化波动率与基金区间内最大回撤数据的同类排名均值计算 |
| 年化波动率 | 基金年化波动幅度 | 代表基金的风险水平，数值越小波动越小 |
| 年化夏普比率 | 风险调整后收益 | 每承受一单位总风险产生的超额收益，数值越大越好 |
| 最大回撤 | 最大亏损幅度 | 从任一历史时点往后推，净值走到最低点时的收益率回撤幅度最大值 |

**注意事项**：

1. **数据可用性**：成立时间较短的基金（通常少于半年）可能没有风险指标数据，此时接口会抛出异常
2. **异常处理**：当 `index_data_list` 为空时，表示该基金无风险指标数据，应捕获 `KeyError` 异常
3. **数据更新频率**：每日更新

**接口示例**：
```python
import akshare as ak

# 正常获取数据
fund_individual_analysis_xq_df = ak.fund_individual_analysis_xq(symbol="000001")
print(fund_individual_analysis_xq_df)

# 处理无数据情况
try:
    df = ak.fund_individual_analysis_xq(symbol="021489")
    print(df)
except KeyError as e:
    if 'index_data_list' in str(e):
        print("该基金无风险指标数据（可能成立时间较短）")
    else:
        raise
```

**返回示例**：
```
   周期  较同类风险收益比  较同类抗风险波动  年化波动率  年化夏普比率  最大回撤
0  近1年        53        59  22.48    1.55  12.48
1  近3年        52        59  19.60    0.16  34.42
2  近5年        29        54  19.97   -0.31  55.07
```

---

### fund_overview_em - 基金基本概况

**接口说明**：天天基金-基金档案-基本概况

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码，如 "015641" |

**输出参数**：基金全称、基金简称、基金代码、基金类型、发行日期、成立日期/规模、资产规模、份额规模、基金管理人、基金托管人、基金经理人、成立来分红、管理费率、托管费率、销售服务费率、最高认购费率、业绩比较基准、跟踪标的

**接口示例**：
```python
import akshare as ak
fund_overview_em_df = ak.fund_overview_em(symbol="015641")
print(fund_overview_em_df)
```

---

### fund_fee_em - 基金交易费率

**接口说明**：天天基金-基金档案-购买信息

**输入参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| symbol | str | 基金代码 |
| indicator | str | 可选："交易状态", "申购与赎回金额", "交易确认日", "运作费用", "认购费率（前端）", "认购费率（后端）", "申购费率（前端）", "赎回费率" |

**输出参数**：

| 名称 | 类型 | 描述 |
|------|------|------|
| 费用类型 | object | - |
| 条件或名称 | object | - |
| 费用 | float64 | - |

**接口示例**：
```python
import akshare as ak
fund_fee_em_df = ak.fund_fee_em(symbol="015641", indicator="认购费率")
print(fund_fee_em_df)
```

---

## 数据使用建议

### 1. 基金基础信息获取流程
```
fund_name_em() → 获取所有基金列表 → 选择目标基金 → fund_overview_em() 获取详细信息
```

### 2. 基金净值数据获取流程
```
fund_open_fund_daily_em() → 获取当日所有开放式基金净值
或
fund_open_fund_info_em(symbol, indicator="单位净值走势") → 获取单只基金历史净值
```

### 3. 基金持仓分析流程
```
fund_portfolio_hold_em(symbol, date) → 股票持仓
fund_portfolio_bond_hold_em(symbol, date) → 债券持仓
fund_portfolio_industry_allocation_em(symbol, date) → 行业配置
```

### 4. 基金筛选流程
```
fund_open_fund_rank_em(symbol="混合型") → 获取排行数据 → 按业绩指标筛选
```

---

## 注意事项

1. **数据更新时间**：
   - 开放式基金净值：每个交易日 16:00-23:00 更新
   - 货币型基金收益：每个交易日 16:00～23:00 更新
   - 场内交易基金排行：每个交易日 17 点后更新

2. **频率限制**：
   - 部分接口有访问频率限制，建议合理控制请求频率
   - 分时数据（1分钟）只返回近5个交易日数据

3. **复权说明**：
   - 前复权（qfq）：保持当前价格不变，将历史价格进行增减
   - 后复权（hfq）：保证历史价格不变，调整当前的股票价格
   - 量化投资研究中普遍采用后复权数据

4. **数据准确性**：
   - 数据来源于东方财富、同花顺、雪球等第三方平台
   - 建议与官方渠道数据进行核对
