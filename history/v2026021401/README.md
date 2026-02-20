# 基金基础数据库搭建方案

## 📋 项目简介

本项目提供了一套完整的基金基础数据数据库搭建方案，使用Python + SQLite技术栈，数据源采用免费的AKShare（主）和Tushare Pro（备用），帮助用户快速构建自己的基金数据分析平台。

## 🎯 核心功能

- ✅ **基金净值数据** - 历史净值、每日更新、任意时间段查询
- ✅ **基金持仓数据** - 季度持仓明细、调仓分析、集中度计算
- ✅ **基金基本信息** - 基金分类、主题标签、费率信息
- ✅ **基金经理信息** - 经理履历、任职历史、业绩评估
- ✅ **统计指标计算** - 收益率、最大回撤、夏普比率等风险指标
- ✅ **数据自动更新** - 支持定时任务，增量更新

## 📁 文件清单

| 文件 | 说明 | 大小 |
|------|------|------|
| `基金数据库搭建完整方案.md` | 完整设计方案文档 | ~50KB |
| `快速启动指南.md` | 快速上手指南 | ~20KB |
| `fund_database_create.sql` | 数据库创建SQL脚本 | ~19KB |
| `akshare_fund_interfaces.md` | AKShare接口详细文档 | ~35KB |
| `tushare_fund_interfaces.md` | Tushare Pro接口文档 | ~25KB |
| `fund_database_schema.md` | 数据库设计详细说明 | ~26KB |
| `fund_analysis_methods.md` | 基金分析方法文档 | ~30KB |
| `fund_analyzer.py` | 基金分析Python实现 | ~15KB |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install akshare pandas numpy tushare
```

### 2. 创建数据库

```bash
sqlite3 fund.db < fund_database_create.sql
```

### 3. 采集数据

```python
import akshare as ak
import sqlite3

# 连接数据库
conn = sqlite3.connect('fund.db')

# 采集基金基本信息
fund_df = ak.fund_name_em()
fund_df.to_sql('fund_info', conn, if_exists='append', index=False)

print(f"✓ 成功采集 {len(fund_df)} 只基金信息")
conn.close()
```

### 4. 计算指标

```python
import sqlite3
import pandas as pd

# 获取净值数据
conn = sqlite3.connect('fund.db')
nav_df = pd.read_sql("SELECT * FROM fund_nav WHERE fund_code='000001'", conn)

# 计算收益率
cumulative_return = (nav_df['unit_nav'].iloc[-1] / nav_df['unit_nav'].iloc[0]) - 1
print(f"累计收益率: {cumulative_return:.2%}")

conn.close()
```

## 📊 数据源对比

| 特性 | AKShare | Tushare Pro |
|------|---------|-------------|
| **费用** | 完全免费 | 积分制（部分免费） |
| **数据覆盖** | 公募基金、ETF、LOF、货币基金 | 公募基金为主 |
| **更新频率** | 交易日每日更新 | 每日更新 |
| **使用门槛** | 低（无需注册） | 中（需注册Token） |
| **推荐指数** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**建议**: 以AKShare为主数据源，Tushare Pro作为数据校验和补充。

## 🏗️ 数据库架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   fund_info     │    │  fund_manager   │    │ manager_fund_   │
│  (基金基本信息)  │    │  (基金经理信息)  │    │    history      │
└────────┬────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  fund_nav       │    │fund_stock_holding│    │fund_bond_holding│
│ (基金净值数据)   │    │ (基金股票持仓)   │    │ (基金债券持仓)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ fund_statistics │    │  fund_category  │    │   fund_tags     │
│ (基金统计指标)   │    │  (基金分类关联)  │    │  (基金主题标签)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 支持的分析指标

### 收益率指标
- 累计收益率
- 年化收益率
- 区间收益率（任意时间段）

### 风险指标
- 最大回撤及持续期
- 波动率（年化）
- 下行标准差
- VaR/CVaR

### 风险调整收益
- 夏普比率 (Sharpe Ratio)
- 索提诺比率 (Sortino Ratio)
- 卡玛比率 (Calmar Ratio)
- 特雷诺比率 (Treynor Ratio)
- 信息比率 (Information Ratio)

### 持仓分析
- 持仓集中度（前10/5/3大）
- 行业配置分析
- 调仓检测
- 换手率估算

## 🔧 常用操作

### 查询基金基本信息
```sql
SELECT fund_code, fund_abbr, fund_type, manager_company
FROM fund_info
WHERE fund_type = '股票型'
LIMIT 10;
```

### 查询净值数据
```sql
SELECT nav_date, unit_nav, daily_return
FROM fund_nav
WHERE fund_code = '000001'
ORDER BY nav_date DESC
LIMIT 10;
```

### 查询收益率排名
```sql
SELECT fund_code, cumulative_return, annualized_return
FROM fund_statistics
WHERE period = '1Y'
ORDER BY cumulative_return DESC
LIMIT 10;
```

## 📅 更新频率建议

| 数据类型 | 更新频率 | 建议时间 |
|----------|----------|----------|
| 基金基本信息 | 每周一次 | 周末 |
| 基金净值 | 每日 | 19:00后 |
| 基金持仓 | 季度更新 | 季报披露后 |
| 基金经理信息 | 每周一次 | 周末 |
| 统计指标 | 每日 | 净值更新后 |

## ⚙️ 自动化设置

### Linux/Mac (crontab)
```bash
# 编辑crontab
crontab -e

# 每日19:30更新净值
30 19 * * * cd /path/to/fund && python3 daily_update.py >> update.log 2>&1
```

### Windows (任务计划程序)
1. 创建任务计划
2. 设置触发器：每天19:30
3. 设置操作：运行 `python daily_update.py`

## 🛠️ 性能优化

### 数据库优化
```sql
-- 启用WAL模式
PRAGMA journal_mode = WAL;

-- 设置缓存大小
PRAGMA cache_size = 10000;
```

### 索引优化
```sql
-- 净值表索引
CREATE INDEX idx_nav_fund_date ON fund_nav(fund_code, nav_date DESC);

-- 持仓表索引
CREATE INDEX idx_holding_fund_report ON fund_stock_holding(fund_code, report_date DESC);
```

## 📚 文档导航

- **新手入门**: [快速启动指南.md](快速启动指南.md)
- **完整方案**: [基金数据库搭建完整方案.md](基金数据库搭建完整方案.md)
- **接口文档**: 
  - [akshare_fund_interfaces.md](akshare_fund_interfaces.md)
  - [tushare_fund_interfaces.md](tushare_fund_interfaces.md)
- **数据库设计**: [fund_database_schema.md](fund_database_schema.md)
- **分析方法**: [fund_analysis_methods.md](fund_analysis_methods.md)

## ❓ 常见问题

### Q: 数据采集速度慢怎么办？
**A:** 
- 使用批量插入替代单条插入
- 只采集需要的基金，而非全市场
- 使用多线程/多进程加速

### Q: 数据重复如何处理？
**A:**
```sql
DELETE FROM fund_nav
WHERE rowid NOT IN (
    SELECT MAX(rowid)
    FROM fund_nav
    GROUP BY fund_code, nav_date
);
```

### Q: 如何备份数据库？
**A:**
```bash
sqlite3 fund.db ".backup 'fund_backup.db'"
```

## 🔄 更新日志

### v1.0 (2026-02-13)
- ✅ 初始版本发布
- ✅ 完整数据库设计方案
- ✅ AKShare/Tushare Pro接口文档
- ✅ 基金分析指标计算方法
- ✅ Python实现代码

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至：your.email@example.com

---

**免责声明**: 本项目仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。
