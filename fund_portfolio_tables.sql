-- ============================================================
-- 基金分组和持仓管理数据库表结构
-- ============================================================

-- 开启外键约束
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. 基金分组表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,             -- 分组名称
    description TEXT,                       -- 分组描述
    color VARCHAR(20) DEFAULT '#3b82f6',    -- 分组颜色标识
    sort_order INTEGER DEFAULT 0,           -- 排序顺序
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金分组表索引
CREATE INDEX IF NOT EXISTS idx_group_name ON fund_groups(name);
CREATE INDEX IF NOT EXISTS idx_group_sort ON fund_groups(sort_order);

-- ============================================================
-- 2. 分组与基金关联表（一个基金可以属于多个分组）
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    fund_code VARCHAR(10) NOT NULL,
    notes TEXT,                             -- 备注
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, fund_code),
    FOREIGN KEY (group_id) REFERENCES fund_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
);

-- 分组基金关联表索引
CREATE INDEX IF NOT EXISTS idx_member_group ON fund_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_member_fund ON fund_group_members(fund_code);

-- ============================================================
-- 3. 持仓记录表（表示当前持有的基金）
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    group_id INTEGER,                       -- 所属分组（可选）
    total_shares DECIMAL(15,4) DEFAULT 0,   -- 总持有份额
    total_cost DECIMAL(15,4) DEFAULT 0,     -- 总成本
    avg_cost_price DECIMAL(10,4) DEFAULT 0, -- 平均成本单价
    first_buy_date DATE,                    -- 首次买入日期
    last_buy_date DATE,                     -- 最后买入日期
    notes TEXT,                             -- 备注
    is_active BOOLEAN DEFAULT 1,            -- 是否活跃
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES fund_groups(id) ON DELETE SET NULL
);

-- 持仓记录表索引
CREATE INDEX IF NOT EXISTS idx_position_fund ON fund_positions(fund_code);
CREATE INDEX IF NOT EXISTS idx_position_group ON fund_positions(group_id);
CREATE INDEX IF NOT EXISTS idx_position_active ON fund_positions(is_active);

-- ============================================================
-- 4. 交易流水表（记录所有买入卖出操作）
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    group_id INTEGER,                       -- 所属分组
    transaction_type VARCHAR(10) NOT NULL,  -- 交易类型: BUY/SELL/DIVIDEND
    transaction_date DATE NOT NULL,         -- 交易日期
    shares DECIMAL(15,4) NOT NULL,          -- 交易份额
    price DECIMAL(10,4) NOT NULL,           -- 成交单价（净值）
    amount DECIMAL(15,4) NOT NULL,          -- 成交金额
    fee DECIMAL(10,4) DEFAULT 0,            -- 手续费
    tax DECIMAL(10,4) DEFAULT 0,            -- 税费
    total_amount DECIMAL(15,4) NOT NULL,    -- 总支付/收到金额
    notes TEXT,                             -- 备注
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES fund_groups(id) ON DELETE SET NULL
);

-- 交易流水表索引
CREATE INDEX IF NOT EXISTS idx_trans_fund ON fund_transactions(fund_code);
CREATE INDEX IF NOT EXISTS idx_trans_group ON fund_transactions(group_id);
CREATE INDEX IF NOT EXISTS idx_trans_date ON fund_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_trans_type ON fund_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_trans_fund_date ON fund_transactions(fund_code, transaction_date);

-- ============================================================
-- 5. 持仓收益记录表（每日快照，用于计算历史收益）
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_position_profit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    record_date DATE NOT NULL,              -- 记录日期
    nav DECIMAL(10,4),                      -- 当日净值
    market_value DECIMAL(15,4),             -- 市值
    daily_profit DECIMAL(15,4),             -- 当日收益
    total_profit DECIMAL(15,4),             -- 累计收益
    total_profit_rate DECIMAL(8,4),         -- 累计收益率(%)
    holding_days INTEGER,                   -- 持有天数
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(position_id, record_date),
    FOREIGN KEY (position_id) REFERENCES fund_positions(id) ON DELETE CASCADE
);

-- 持仓收益记录表索引
CREATE INDEX IF NOT EXISTS idx_profit_position ON fund_position_profit(position_id);
CREATE INDEX IF NOT EXISTS idx_profit_date ON fund_position_profit(record_date);

-- ============================================================
-- 初始化默认分组
-- ============================================================
INSERT OR IGNORE INTO fund_groups (name, description, color, sort_order) VALUES
('自选基金', '默认自选基金分组', '#3b82f6', 1),
('持有基金', '当前持有的基金', '#10b981', 2),
('关注基金', '正在关注的基金', '#f59e0b', 3);
