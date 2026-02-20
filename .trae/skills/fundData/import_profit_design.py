"""
导入持仓收益功能设计方案
"""

## 一、数据库结构设计

### 1. 扩展 portfolio_fund 表

需要在现有的 portfolio_fund 表中添加以下字段：

```sql
-- 持仓收益相关字段
ALTER TABLE portfolio_fund ADD COLUMN current_profit DECIMAL(15,2);       -- 当前持仓收益（累计）
ALTER TABLE portfolio_fund ADD COLUMN cost_nav DECIMAL(10,4);           -- 成本净值（倒推计算）
ALTER TABLE portfolio_fund ADD COLUMN profit_update_time DATETIME;       -- 收益更新时间
ALTER TABLE portfolio_fund ADD COLUMN profit_source VARCHAR(20);         -- 收益数据来源
```

### 2. 新增导入记录表

```sql
-- 导入盈亏记录表
CREATE TABLE portfolio_profit_import (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    fund_code VARCHAR(10) NOT NULL,
    import_date DATE NOT NULL,          -- 导入日期（数据所属日期）
    market_value DECIMAL(15,2),          -- 当前市值（持有金额）
    profit_amount DECIMAL(15,2),         -- 持仓收益（盈亏金额）
    profit_rate DECIMAL(8,4),            -- 持仓收益率（如 0.5725 表示 57.25%）
    source_type VARCHAR(20),             --