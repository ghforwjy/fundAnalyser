-- ============================================================
-- 基金分析系统数据库初始化脚本 (AKShare 版本)
-- 基于 AKShare 数据源设计
-- ============================================================

-- 开启外键约束
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. 基金基本信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_info (
    fund_code VARCHAR(10) PRIMARY KEY,
    fund_name VARCHAR(100) NOT NULL,        -- 基金简称
    fund_full_name VARCHAR(200),            -- 基金全称
    fund_type VARCHAR(50),                  -- 基金类型
    pinyin_abbr VARCHAR(20),                -- 拼音缩写
    pinyin_full VARCHAR(100),               -- 拼音全称
    
    -- 公司和托管信息
    company_name VARCHAR(100),              -- 基金公司
    custodian VARCHAR(100),                 -- 托管银行
    
    -- 日期和规模
    issue_date DATE,                        -- 发行日期
    establish_date DATE,                    -- 成立日期
    establish_scale DECIMAL(20,4),          -- 成立规模
    
    -- 费率信息
    manage_fee_rate DECIMAL(5,4),           -- 管理费率
    custodian_fee_rate DECIMAL(5,4),        -- 托管费率
    
    -- 投资信息
    benchmark VARCHAR(500),                 -- 业绩比较基准
    invest_scope TEXT,                      -- 投资范围
    track_target VARCHAR(100),              -- 跟踪标的（指数基金）
    
    -- 状态
    status VARCHAR(20) DEFAULT '正常',      -- 基金状态
    
    -- 数据来源
    data_source VARCHAR(50) DEFAULT 'akshare',
    
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金基本信息表索引
CREATE INDEX IF NOT EXISTS idx_fund_type ON fund_info(fund_type);
CREATE INDEX IF NOT EXISTS idx_fund_company ON fund_info(company_name);
CREATE INDEX IF NOT EXISTS idx_fund_status ON fund_info(status);
CREATE INDEX IF NOT EXISTS idx_fund_establish ON fund_info(establish_date);
CREATE INDEX IF NOT EXISTS idx_fund_pinyin ON fund_info(pinyin_abbr);
CREATE INDEX IF NOT EXISTS idx_fund_source ON fund_info(data_source);

-- ============================================================
-- 2. 基金公司信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(100) UNIQUE NOT NULL,
    establish_date DATE,
    total_assets DECIMAL(20,4),             -- 管理规模（亿元）
    fund_count INTEGER,                     -- 基金数量
    manager_count INTEGER,                  -- 经理人数
    rating INTEGER,                         -- 天相评级
    description TEXT,                       -- 公司简介
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金公司信息表索引
CREATE INDEX IF NOT EXISTS idx_company_name ON fund_company(company_name);
CREATE INDEX IF NOT EXISTS idx_company_assets ON fund_company(total_assets);
CREATE INDEX IF NOT EXISTS idx_company_source ON fund_company(data_source);

-- ============================================================
-- 3. 基金经理信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_manager (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_name VARCHAR(50) NOT NULL,
    company_name VARCHAR(100),              -- 所属公司
    tenure_days INTEGER,                    -- 累计从业时间（天）
    total_scale DECIMAL(20,4),              -- 管理资产总规模（亿元）
    best_return DECIMAL(10,4),              -- 最佳回报（%）
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金经理信息表索引
CREATE INDEX IF NOT EXISTS idx_manager_name ON fund_manager(manager_name);
CREATE INDEX IF NOT EXISTS idx_manager_company ON fund_manager(company_name);
CREATE INDEX IF NOT EXISTS idx_manager_source ON fund_manager(data_source);

-- ============================================================
-- 4. 基金净值数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    nav_date DATE NOT NULL,
    unit_nav DECIMAL(10,4),                 -- 单位净值
    accum_nav DECIMAL(10,4),                -- 累计净值
    daily_return DECIMAL(8,4),              -- 日增长率
    subscribe_status VARCHAR(20),           -- 申购状态
    redeem_status VARCHAR(20),              -- 赎回状态
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, nav_date, data_source),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金净值数据表索引
CREATE INDEX IF NOT EXISTS idx_nav_fund_code ON fund_nav(fund_code);
CREATE INDEX IF NOT EXISTS idx_nav_date ON fund_nav(nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_fund_date ON fund_nav(fund_code, nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_return ON fund_nav(daily_return);
CREATE INDEX IF NOT EXISTS idx_nav_source ON fund_nav(data_source);

-- ============================================================
-- 5. 基金规模数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_scale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,              -- 规模报告日期
    unit_nav DECIMAL(10,4),                 -- 单位净值
    total_issue_scale DECIMAL(20,4),        -- 总募集规模（万份）
    total_share DECIMAL(20,4),              -- 最近总份额（份）
    fund_manager VARCHAR(50),               -- 基金经理
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, report_date, data_source),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金规模数据表索引
CREATE INDEX IF NOT EXISTS idx_scale_fund_code ON fund_scale(fund_code);
CREATE INDEX IF NOT EXISTS idx_scale_date ON fund_scale(report_date);
CREATE INDEX IF NOT EXISTS idx_scale_fund_date ON fund_scale(fund_code, report_date);
CREATE INDEX IF NOT EXISTS idx_scale_source ON fund_scale(data_source);

-- ============================================================
-- 6. 基金股票持仓表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_stock_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,              -- 报告期（季度末）
    stock_code VARCHAR(10) NOT NULL,        -- 股票代码
    stock_name VARCHAR(50),                 -- 股票名称
    nav_ratio DECIMAL(6,2),                 -- 占净值比例（%）
    share_count DECIMAL(15,2),              -- 持股数（万股）
    market_value DECIMAL(15,2),             -- 持仓市值（万元）
    quarter VARCHAR(10),                    -- 季度（如：2024Q1）
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, report_date, stock_code, data_source),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金股票持仓表索引
CREATE INDEX IF NOT EXISTS idx_stock_fund_code ON fund_stock_holding(fund_code);
CREATE INDEX IF NOT EXISTS idx_stock_date ON fund_stock_holding(report_date);
CREATE INDEX IF NOT EXISTS idx_stock_code ON fund_stock_holding(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_fund_date ON fund_stock_holding(fund_code, report_date);
CREATE INDEX IF NOT EXISTS idx_stock_source ON fund_stock_holding(data_source);

-- ============================================================
-- 7. 基金债券持仓表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_bond_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    bond_code VARCHAR(20) NOT NULL,         -- 债券代码
    bond_name VARCHAR(100),                 -- 债券名称
    nav_ratio DECIMAL(6,2),                 -- 占净值比例（%）
    market_value DECIMAL(15,2),             -- 持仓市值（万元）
    quarter VARCHAR(10),
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, report_date, bond_code, data_source),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金债券持仓表索引
CREATE INDEX IF NOT EXISTS idx_bond_fund_code ON fund_bond_holding(fund_code);
CREATE INDEX IF NOT EXISTS idx_bond_date ON fund_bond_holding(report_date);
CREATE INDEX IF NOT EXISTS idx_bond_code ON fund_bond_holding(bond_code);
CREATE INDEX IF NOT EXISTS idx_bond_source ON fund_bond_holding(data_source);

-- ============================================================
-- 8. 基金行业配置表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_industry_allocation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    industry_name VARCHAR(50) NOT NULL,     -- 行业类别
    nav_ratio DECIMAL(6,2),                 -- 占净值比例（%）
    market_value DECIMAL(15,2),             -- 市值（万元）
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, report_date, industry_name, data_source),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金行业配置表索引
CREATE INDEX IF NOT EXISTS idx_industry_fund_code ON fund_industry_allocation(fund_code);
CREATE INDEX IF NOT EXISTS idx_industry_date ON fund_industry_allocation(report_date);
CREATE INDEX IF NOT EXISTS idx_industry_name ON fund_industry_allocation(industry_name);
CREATE INDEX IF NOT EXISTS idx_industry_source ON fund_industry_allocation(data_source);

-- ============================================================
-- 9. 基金评级表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_rating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    rating_date DATE NOT NULL,              -- 评级日期
    rating_agency VARCHAR(20),              -- 评级机构（上海证券/招商/济安金信/晨星）
    rating_3y INTEGER,                      -- 3年期评级
    rating_5y INTEGER,                      -- 5年期评级
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, rating_date, rating_agency, data_source),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金评级表索引
CREATE INDEX IF NOT EXISTS idx_rating_fund_code ON fund_rating(fund_code);
CREATE INDEX IF NOT EXISTS idx_rating_date ON fund_rating(rating_date);
CREATE INDEX IF NOT EXISTS idx_rating_agency ON fund_rating(rating_agency);
CREATE INDEX IF NOT EXISTS idx_rating_source ON fund_rating(data_source);

-- ============================================================
-- 10. 数据源配置表
-- ============================================================
CREATE TABLE IF NOT EXISTS data_source_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name VARCHAR(50) UNIQUE NOT NULL,
    source_type VARCHAR(20) NOT NULL,       -- free/paid
    base_url VARCHAR(200),
    api_key TEXT,
    is_active BOOLEAN DEFAULT 0,
    is_connected BOOLEAN DEFAULT 0,
    last_test_time DATETIME,
    last_test_result VARCHAR(20),
    last_error TEXT,
    description VARCHAR(200),
    rate_limit INTEGER DEFAULT 60,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 11. 数据更新日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS data_update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    update_type VARCHAR(20) NOT NULL,       -- full/incremental
    status VARCHAR(20) NOT NULL,            -- success/failed/running
    start_time DATETIME,
    end_time DATETIME,
    record_count INTEGER DEFAULT 0,
    message TEXT,
    error_message TEXT,
    data_source VARCHAR(50) DEFAULT 'akshare',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 数据更新日志表索引
CREATE INDEX IF NOT EXISTS idx_log_table ON data_update_log(table_name);
CREATE INDEX IF NOT EXISTS idx_log_status ON data_update_log(status);
CREATE INDEX IF NOT EXISTS idx_log_time ON data_update_log(create_time);
CREATE INDEX IF NOT EXISTS idx_log_source ON data_update_log(data_source);

-- ============================================================
-- 初始化数据源配置
-- ============================================================
INSERT OR IGNORE INTO data_source_config (source_name, source_type, is_active, is_connected, description, rate_limit)
VALUES 
    ('akshare', 'free', 1, 1, 'AKShare免费开源数据源-天天基金', 1000),
    ('tushare', 'paid', 0, 0, 'Tushare专业数据源', 60);

-- 更新统计信息
ANALYZE;

-- 验证表创建
SELECT 'fund_info' as table_name, COUNT(*) as record_count FROM fund_info
UNION ALL
SELECT 'fund_company', COUNT(*) FROM fund_company
UNION ALL
SELECT 'fund_manager', COUNT(*) FROM fund_manager
UNION ALL
SELECT 'fund_nav', COUNT(*) FROM fund_nav
UNION ALL
SELECT 'fund_scale', COUNT(*) FROM fund_scale
UNION ALL
SELECT 'fund_stock_holding', COUNT(*) FROM fund_stock_holding
UNION ALL
SELECT 'fund_bond_holding', COUNT(*) FROM fund_bond_holding
UNION ALL
SELECT 'fund_industry_allocation', COUNT(*) FROM fund_industry_allocation
UNION ALL
SELECT 'fund_rating', COUNT(*) FROM fund_rating
UNION ALL
SELECT 'data_source_config', COUNT(*) FROM data_source_config
UNION ALL
SELECT 'data_update_log', COUNT(*) FROM data_update_log;
