-- ============================================================
-- 基金分红表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_dividend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    ann_date DATE,              -- 公告日期
    imp_anndate DATE,           -- 分红实施公告日
    base_date DATE,             -- 分配收益基准日
    div_proc VARCHAR(20),       -- 方案进度
    record_date DATE,           -- 权益登记日
    ex_date DATE,               -- 除息日
    pay_date DATE,              -- 派息日
    earpay_date DATE,           -- 收益支付日
    net_ex_date DATE,           -- 净值除权日
    div_cash DECIMAL(10,6),     -- 每股派息(元)
    base_unit DECIMAL(12,2),    -- 基准基金份额(万份)
    ear_distr DECIMAL(15,2),    -- 可分配收益(元)
    ear_amount DECIMAL(15,2),   -- 收益分配金额(元)
    account_date DATE,          -- 红利再投资到账日
    base_year VARCHAR(10),      -- 份额基准年度
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, ex_date),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
);

-- 基金分红表索引
CREATE INDEX IF NOT EXISTS idx_div_fund_code ON fund_dividend(fund_code);
CREATE INDEX IF NOT EXISTS idx_div_ann_date ON fund_dividend(ann_date);
CREATE INDEX IF NOT EXISTS idx_div_ex_date ON fund_dividend(ex_date);
CREATE INDEX IF NOT EXISTS idx_div_pay_date ON fund_dividend(pay_date);
