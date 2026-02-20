# Tushare 公募基金数据接口文档

> 文档来源：https://tushare.pro/document/2?doc_id=18
> 整理时间：2026-02-14
> 更新时间：2026-02-14

## 概述

在Tushare Pro基金数据模块里面，提供公募基金和私募基金两部分数据，数据来源于网络公开渠道和第三方合作伙伴。当前阶段上线部分公募基金数据，包括基金基础信息、基金净值、基金分红等常规数据。

---

## 接口列表

| 接口名称 | 接口代码 | 描述 | 积分要求 |
|---------|---------|------|---------|
| 公募基金列表 | fund_basic | 获取公募基金数据列表，包括场内和场外基金 | 2000积分 |
| 公募基金公司 | fund_company | 获取公募基金管理人列表 | 1500积分 |
| 公募基金净值 | fund_nav | 获取公募基金净值数据 | 2000积分 |
| 场内基金日线行情 | fund_daily | 获取ETF行情每日收盘后成交数据 | 5000积分 |
| 公募基金分红 | fund_div | 获取公募基金分红数据 | 400积分 |
| 公募基金持仓数据 | fund_portfolio | 获取公募基金持仓数据，季度更新 | 5000积分 |
| 基金经理 | fund_manager | 获取公募基金经理数据，包括基金经理简历等 | 500积分 |
| 基金规模数据 | fund_share | 获取基金规模数据，包含上海和深圳ETF基金 | 2000积分 |

---

## 1. 公募基金列表 (fund_basic)

### 接口描述
获取公募基金数据列表，包括场内和场外基金。单次最大可以提取15000条数据，5000积分以上权限更高。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ts_code | str | N | 基金代码 |
| market | str | N | 交易市场: E场内 O场外（默认E） |
| status | str | N | 存续状态 D摘牌 I发行 L上市中 |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | 基金代码 |
| name | str | 简称 |
| management | str | 管理人 |
| custodian | str | 托管人 |
| fund_type | str | 投资类型 |
| found_date | str | 成立日期 |
| due_date | str | 到期日期 |
| list_date | str | 上市时间 |
| issue_date | str | 发行日期 |
| delist_date | str | 退市日期 |
| issue_amount | float | 发行份额(亿) |
| m_fee | float | 管理费 |
| c_fee | float | 托管费 |
| duration_year | float | 存续期 |
| p_value | float | 面值 |
| min_amount | float | 起点金额(万元) |
| exp_return | float | 预期收益率 |
| benchmark | str | 业绩比较基准 |
| status | str | 存续状态D摘牌 I发行 L已上市 |
| invest_type | str | 投资风格 |
| type | str | 基金类型 |
| trustee | str | 受托人 |
| purc_startdate | str | 日常申购起始日 |
| redm_startdate | str | 日常赎回起始日 |
| market | str | E场内O场外 |

### 接口示例

```python
pro = ts.pro_api()

# 获取场内基金列表
df = pro.fund_basic(market='E')

# 获取场外基金列表
df = pro.fund_basic(market='O')

# 获取指定基金信息
df = pro.fund_basic(ts_code='150008.SZ')
```

### 数据样例

```
    ts_code             name         management  custodian      fund_type found_date  
1   512850.SH    中信建投北京50ETF     中信建投基金      招商银行       股票型   20180927   
2   168601.SZ    汇安裕阳三年定期开放       汇安基金    中国光大银行       混合型   20180927 
3   512860.SH    华安中国A股ETF       华安基金    中国农业银行       股票型   20180927   
4   159960.SZ    恒生国企             平安大华基金      中国银行       股票型   20180921   
5   501062.SH    南方瑞合三年           南方基金    中国建设银行       混合型   20180906   
```

---

## 2. 公募基金公司 (fund_company)

### 接口描述
获取公募基金管理人列表，一次可以提取全部数据。

### 输入参数
无，可提取全部

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| name | str | 基金公司名称 |
| shortname | str | 简称 |
| short_enname | str | 英文缩写 |
| province | str | 省份 |
| city | str | 城市 |
| address | str | 注册地址 |
| phone | str | 电话 |
| office | str | 办公地址 |
| website | str | 公司网址 |
| chairman | str | 法人代表 |
| manager | str | 总经理 |
| reg_capital | float | 注册资本 |
| setup_date | str | 成立日期 |
| end_date | str | 公司终止日期 |
| employees | float | 员工总数 |
| main_business | str | 主要产品及业务 |
| org_code | str | 组织机构代码 |
| credit_code | str | 统一社会信用代码 |

### 接口示例

```python
pro = ts.pro_api()

df = pro.fund_company()
```

### 数据样例

```
                  name                   shortname          province   city  
0           北京广能投资基金管理有限公司        广能基金       北京    北京市   
1               平安银行股份有限公司        平安银行       广东    深圳市   
2               宏源证券股份有限公司        宏源证券       新疆  乌鲁木齐市   
3               陕西省国际信托股份有限公司         陕国投       陕西    西安市   
4               东北证券股份有限公司        东北证券       吉林    长春市   
```

---

## 3. 公募基金净值 (fund_nav)

### 接口描述
获取公募基金净值数据。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ts_code | str | N | TS基金代码（二选一） |
| nav_date | str | N | 净值日期（二选一） |
| market | str | N | E场内 O场外 |
| start_date | str | N | 净值开始日期 |
| end_date | str | N | 净值结束日期 |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | TS代码 |
| ann_date | str | 公告日期 |
| nav_date | str | 净值日期 |
| unit_nav | float | 单位净值 |
| accum_nav | float | 累计净值 |
| accum_div | float | 累计分红 |
| net_asset | float | 资产净值 |
| total_netasset | float | 合计资产净值 |
| adj_nav | float | 复权单位净值 |

### 接口示例

```python
pro = ts.pro_api()

# 获取指定基金的净值数据
df = pro.fund_nav(ts_code='165509.SZ')

# 获取指定日期的净值数据
df = pro.fund_nav(nav_date='20240115')

# 获取指定日期范围的净值数据
df = pro.fund_nav(ts_code='165509.SZ', start_date='20240101', end_date='20240131')
```

### 数据样例

```
      ts_code  ann_date  nav_date  unit_nav  accum_nav accum_div  
0   165509.SZ  20181019  20181018     1.104      1.587      None   
1   165509.SZ  20181018  20181017     1.110      1.587      None   
2   165509.SZ  20181017  20181016     1.110      1.587      None   
3   165509.SZ  20181016  20181015     1.110      1.587      None   
4   165509.SZ  20181013  20181012     1.110      1.587      None   
```

---

## 4. 场内基金日线行情 (fund_daily)

### 接口描述
获取ETF行情每日收盘后成交数据，历史超过10年。单次最大2000行记录，可以根据ETF代码和日期循环获取历史，总量不限制。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ts_code | str | N | 基金代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | TS代码 |
| trade_date | str | 交易日期 |
| open | float | 开盘价(元) |
| high | float | 最高价(元) |
| low | float | 最低价(元) |
| close | float | 收盘价(元) |
| pre_close | float | 昨收盘价(元) |
| change | float | 涨跌额(元) |
| pct_chg | float | 涨跌幅(%) |
| vol | float | 成交量(手) |
| amount | float | 成交额(千元) |

### 接口示例

```python
pro = ts.pro_api()

# 获取沪深300ETF华夏2025年以来的行情
df = pro.fund_daily(ts_code='510330.SH', start_date='20250101', end_date='20250618', 
                    fields='trade_date,open,high,low,close,vol,amount')

# 获取指定日期的所有ETF行情
df = pro.fund_daily(trade_date='20240115')
```

### 数据样例

```
   trade_date   open   high    low  close         vol       amount
0     20250618  4.008  4.024  3.996  4.017   382896.00   153574.446
1     20250617  4.015  4.022  4.000  4.014   440272.04   176617.125
2     20250616  4.000  4.018  3.996  4.015   423526.00   169788.251
3     20250613  4.023  4.028  3.992  4.004  1216787.53   487632.318
4     20250612  4.023  4.039  4.005  4.032   574727.00   231356.321
```

---

## 5. 公募基金分红 (fund_div)

### 接口描述
获取公募基金分红数据。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ann_date | str | N | 公告日（以下参数四选一） |
| ex_date | str | N | 除息日 |
| pay_date | str | N | 派息日 |
| ts_code | str | N | 基金代码 |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | TS代码 |
| ann_date | str | 公告日期 |
| imp_anndate | str | 分红实施公告日 |
| base_date | str | 分配收益基准日 |
| div_proc | str | 方案进度 |
| record_date | str | 权益登记日 |
| ex_date | str | 除息日 |
| pay_date | str | 派息日 |
| earpay_date | str | 收益支付日 |
| net_ex_date | str | 净值除权日 |
| div_cash | float | 每股派息(元) |
| base_unit | float | 基准基金份额(万份) |
| ear_distr | float | 可分配收益(元) |
| ear_amount | float | 收益分配金额(元) |
| account_date | str | 红利再投资到账日 |
| base_year | str | 份额基准年度 |

### 接口示例

```python
pro = ts.pro_api()

# 获取指定公告日期的分红数据
df = pro.fund_div(ann_date='20181018')

# 获取指定基金的分红数据
df = pro.fund_div(ts_code='161618.OF')

# 获取指定除息日的分红数据
df = pro.fund_div(ex_date='20181022')
```

### 数据样例

```
    ts_code  ann_date imp_anndate base_date div_proc record_date   ex_date  
0  161618.OF  20181018    20181018  20180928       实施    20181022  20181022   
1  161619.OF  20181018    20181018  20180928       实施    20181022  20181022   
2  005485.OF  20181018    20181018  20181015       实施    20181022  20181022   

   pay_date  div_cash    base_unit    ear_distr
0  20181024    0.0170   14982.2740   5018943.83
1  20181024    0.0150    2894.7015    823800.02
2  20181024    0.0180  101004.4450  18689411.19
```

---

## 6. 公募基金持仓数据 (fund_portfolio)

### 接口描述
获取公募基金持仓数据，季度更新。5000积分以上每分钟请求200次，8000积分以上每分钟请求500次。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ts_code | str | N | 基金代码 (ts_code,ann_date,period至少输入一个参数) |
| symbol | str | N | 股票代码 |
| ann_date | str | N | 公告日期（YYYYMMDD格式） |
| period | str | N | 季度（每个季度最后一天的日期，比如20131231表示2013年年报） |
| start_date | str | N | 报告期开始日期（YYYYMMDD格式） |
| end_date | str | N | 报告期结束日期（YYYYMMDD格式） |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | TS基金代码 |
| ann_date | str | 公告日期 |
| end_date | str | 截止日期 |
| symbol | str | 股票代码 |
| mkv | float | 持有股票市值(元) |
| amount | float | 持有股票数量（股） |
| stk_mkv_ratio | float | 占股票市值比 |
| stk_float_ratio | float | 占流通股本比例 |

### 接口示例

```python
pro = ts.pro_api()

# 获取指定基金的持仓数据
df = pro.fund_portfolio(ts_code='001753.OF')

# 获取指定报告期的持仓数据
df = pro.fund_portfolio(period='20231231')

# 获取指定股票被哪些基金持有
df = pro.fund_portfolio(symbol='600519.SH')
```

### 数据样例

```
    ts_code  ann_date  end_date     symbol          mkv    amount  stk_mkv_ratio  stk_float_ratio
0  001753.OF  20180823  20180630  603019.SH   3130994.46   68258.0           4.37            0.01
1  001753.OF  20180718  20180630  600845.SH   3594140.00  136400.0           5.02            0.02
2  001753.OF  20180718  20180630  600596.SH   5428107.30  335690.0           7.57            0.05
3  001753.OF  20180718  20180630  600588.SH   3811672.65  155515.0           5.32            0.01
4  001753.OF  20180718  20180630  600271.SH   3770284.00  149200.0           5.26            0.01
```

---

## 7. 基金经理 (fund_manager)

### 接口描述
获取公募基金经理数据，包括基金经理简历等。单次最大5000条，支持分页提取数据。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ts_code | str | N | 基金代码，支持多只基金，逗号分隔 |
| ann_date | str | N | 公告日期，格式：YYYYMMDD |
| name | str | N | 基金经理姓名 |
| offset | int | N | 开始行数 |
| limit | int | N | 每页行数 |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | 基金代码 |
| ann_date | str | 公告日期 |
| name | str | 基金经理姓名 |
| gender | str | 性别 |
| birth_year | str | 出生年份 |
| edu | str | 学历 |
| nationality | str | 国籍 |
| begin_date | str | 任职日期 |
| end_date | str | 离任日期 |
| resume | str | 简历 |

### 接口示例

```python
pro = ts.pro_api()

# 单只基金
df = pro.fund_manager(ts_code='150018.SZ')

# 多只基金
df = pro.fund_manager(ts_code='150018.SZ,150008.SZ')

# 按姓名查询
df = pro.fund_manager(name='张凯')
```

### 数据样例

```
    ts_code  ann_date   name  gender birth_year edu nationality begin_date  end_date                                             resume
0  150018.SZ  20100508   周毅      M       None  硕士          美国   20100507      None  CFA，硕士学位；毕业于北京大学，美国南卡罗莱纳大学，美国约翰霍普金斯大学。曾任美国普华永道...
1  150018.SZ  20190831   张凯      M       None  硕士          中国   20190829      None  CFA，硕士学位，毕业于清华大学。2009年7月加盟银华基金管理有限公司，从事量化策略研发和...
2  150018.SZ  20100927  路志刚      M       1969  博士          中国   20100507  20100927  暨南大学金融学博士。曾任广东建设实业集团公司财务主管，广州证券有限公司发行部、营业部经理，金...
```

---

## 8. 基金规模数据 (fund_share)

### 接口描述
获取基金规模数据，包含上海和深圳ETF基金。单次最大提取2000行数据。

### 输入参数

| 名称 | 类型 | 必选 | 描述 |
|-----|------|-----|------|
| ts_code | str | N | TS基金代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| market | str | N | 市场代码（SH上交所，SZ深交所） |

### 输出参数

| 名称 | 类型 | 描述 |
|-----|------|------|
| ts_code | str | 基金代码，支持多只基金同时提取，用逗号分隔 |
| trade_date | str | 交易（变动）日期，格式YYYYMMDD |
| fd_share | float | 基金份额（万） |

### 接口示例

```python
pro = ts.pro_api()

# 单只基金
df = pro.fund_share(ts_code='150018.SZ')

# 多只基金
df = pro.fund_share(ts_code='150018.SZ,150008.SZ')

# 按日期范围查询
df = pro.fund_share(ts_code='150018.SZ', start_date='20200101', end_date='20200228')

# 按市场查询
df = pro.fund_share(market='SH', trade_date='20200214')
```

### 数据样例

```
        ts_code trade_date  fd_share
0     150018.SZ   20200214  206733.2898
1     150018.SZ   20200213  209274.0911
2     150018.SZ   20200212  211859.8666
3     150018.SZ   20200211  215224.2959
4     150018.SZ   20200210  216739.3881
...         ...        ...          ...
1995  150018.SZ   20111129  319525.0658
1996  150018.SZ   20111128  317324.2829
1997  150018.SZ   20111125  317324.2131
1998  150018.SZ   20111124  316113.2233
1999  150018.SZ   20111123  314305.3576
```

---

## 本地数据库与Tushare接口对照分析

### 已实现的同步器

| 本地数据表 | Tushare接口 | 同步器实现 | 状态 |
|-----------|------------|-----------|------|
| fund_info | fund_basic | FundInfoSyncer | ✅ 已实现 |
| fund_nav | fund_nav | FundNavSyncer | ✅ 已实现 |

### 待实现的同步器

| 本地数据表 | Tushare接口 | 同步器实现 | 状态 | 说明 |
|-----------|------------|-----------|------|------|
| fund_stock_holding | fund_portfolio | ❌ 未实现 | 待开发 | 基金股票持仓数据 |
| fund_manager | fund_manager | ❌ 未实现 | 待开发 | 基金经理信息 |
| manager_fund_history | fund_manager | ❌ 未实现 | 待开发 | 经理任职历史（可从fund_manager提取） |
| fund_bond_holding | - | ❌ 无接口 | 无法实现 | Tushare暂无债券持仓接口 |
| fund_statistics | - | ❌ 需计算 | 本地计算 | 需基于净值数据本地计算 |
| fund_div (无表) | fund_div | ❌ 未实现 | 待开发 | 基金分红数据，需建表 |
| fund_daily (无表) | fund_daily | ❌ 未实现 | 待开发 | ETF日线行情，需建表 |
| fund_company (无表) | fund_company | ❌ 未实现 | 待开发 | 基金公司信息，需建表 |
| fund_share (无表) | fund_share | ❌ 未实现 | 待开发 | 基金规模数据，需建表 |

### 建议优先级

1. **高优先级** 
   - fund_portfolio（基金持仓）：核心分析数据
   - fund_manager（基金经理）：已有对应数据库表

2. **中优先级** 
   - fund_div（基金分红）：影响净值计算
   - fund_share（基金规模）：规模变动分析

3. **低优先级** 
   - fund_company（基金公司）
   - fund_daily（ETF行情）

---

## 注意事项

1. **积分要求**：不同接口需要不同积分，建议至少5000积分以获得更好的调用频率
2. **日期格式**：所有日期参数格式统一为YYYYMMDD，如：20240115
3. **频率限制**：积分低的用户可能遇到timeout，建议在循环中增加重试机制
4. **数据来源标注**：使用Tushare数据需在产品中标注"数据来源：Tushare数据"
5. **分页查询**：fund_manager接口支持分页，大数据量时需使用offset和limit参数
