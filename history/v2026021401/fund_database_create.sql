-- ============================================================
-- 基金数据库创建脚本 (SQLite)
-- 版本: 1.0
-- 说明: 完整的基金数据库DDL脚本，包含表、索引、视图、触发器
-- ============================================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 设置数据库优化参数
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
PRAGMA temp_store = MEMORY;

-- ============================================================
-- 1. 基金基本信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_info (
    fund_code VARCHAR(10) PRIMARY KEY,
    fund_name VARCHAR(100) NOT NULL,
    fund_abbr VARCHAR(50),
    fund_type VARCHAR(20) NOT NULL,
    sub_type VARCHAR(30),
    establish_date DATE,
    manager_company VARCHAR(100),
    custodian VARCHAR(100),
    benchmark VARCHAR(200),
    manage_fee_rate DECIMAL(5,4),
    custodian_fee_rate DECIMAL(5,4),
    risk_level TINYINT CHECK(risk_level BETWEEN 1 AND 5),
    min_purchase_amount DECIMAL(12,2),
    status VARCHAR(10) DEFAULT '正常',
    invest_style VARCHAR(50),
    invest_scope TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金基本信息表索引
CREATE INDEX IF NOT EXISTS idx_fund_type ON fund_info(fund_type);
CREATE INDEX IF NOT EXISTS idx_fund_company ON fund_info(manager_company);
CREATE INDEX IF NOT EXISTS idx_risk_level ON fund_info(risk_level);
CREATE INDEX IF NOT EXISTS idx_fund_status ON fund_info(status);
CREATE INDEX IF NOT EXISTS idx_fund_establish ON fund_info(establish_date);

-- ============================================================
-- 2. 基金净值数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    nav_date DATE NOT NULL,
    unit_nav DECIMAL(10,4) NOT NULL,
    accum_nav DECIMAL(10,4),
    daily_return DECIMAL(8,4),
    subscribe_status VARCHAR(10),
    redeem_status VARCHAR(10),
    dividend DECIMAL(10,4) DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, nav_date),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 基金净值数据表索引
CREATE INDEX IF NOT EXISTS idx_nav_fund_code ON fund_nav(fund_code);
CREATE INDEX IF NOT EXISTS idx_nav_date ON fund_nav(nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_fund_date ON fund_nav(fund_code, nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_return ON fund_nav(daily_return);

-- ============================================================
-- 3. 基金股票持仓表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_stock_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50),
    nav_ratio DECIMAL(6,2),
    share_count BIGINT,
    market_value DECIMAL(15,2),
    rank_num SMALLINT,
    sector VARCHAR(30),
    change_type VARCHAR(10),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, report_date, stock_code),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
);

-- 基金股票持仓表索引
CREATE INDEX IF NOT EXISTS idx_stock_fund_code ON fund_stock_holding(fund_code);
CREATE INDEX IF NOT EXISTS idx_stock_report_date ON fund_stock_holding(report_date);
CREATE INDEX IF NOT EXISTS idx_stock_code ON fund_stock_holding(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_fund_report ON fund_stock_holding(fund_code, report_date);
CREATE INDEX IF NOT EXISTS idx_stock_sector ON fund_stock_holding(sector);
CREATE INDEX IF NOT EXISTS idx_stock_rank ON fund_stock_holding(rank_num);

-- ============================================================
-- 4. 基金债券持仓表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_bond_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    bond_code VARCHAR(20) NOT NULL,
    bond_name VARCHAR(100),
    bond_type VARCHAR(30),
    nav_ratio DECIMAL(6,2),
    market_value DECIMAL(15,2),
    rank_num SMALLINT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, report_date, bond_code),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
);

-- 基金债券持仓表索引
CREATE INDEX IF NOT EXISTS idx_bond_fund_code ON fund_bond_holding(fund_code);
CREATE INDEX IF NOT EXISTS idx_bond_report_date ON fund_bond_holding(report_date);
CREATE INDEX IF NOT EXISTS idx_bond_fund_report ON fund_bond_holding(fund_code, report_date);
CREATE INDEX IF NOT EXISTS idx_bond_type ON fund_bond_holding(bond_type);

-- ============================================================
-- 5. 基金经理信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_manager (
    manager_id VARCHAR(20) PRIMARY KEY,
    manager_name VARCHAR(50) NOT NULL,
    gender CHAR(1),
    education VARCHAR(20),
    entry_date DATE,
    company VARCHAR(100),
    introduction TEXT,
    invest_style VARCHAR(50),
    total_scale DECIMAL(15,2),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基金经理信息表索引
CREATE INDEX IF NOT EXISTS idx_manager_name ON fund_manager(manager_name);
CREATE INDEX IF NOT EXISTS idx_manager_company ON fund_manager(company);

-- ============================================================
-- 6. 基金经理任职历史表
-- ============================================================
CREATE TABLE IF NOT EXISTS manager_fund_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id VARCHAR(20) NOT NULL,
    fund_code VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    tenure_return DECIMAL(8,2),
    is_current BOOLEAN DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(manager_id, fund_code, start_date),
    FOREIGN KEY (manager_id) REFERENCES fund_manager(manager_id) ON DELETE CASCADE,
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

-- 基金经理任职历史表索引
CREATE INDEX IF NOT EXISTS idx_mfh_manager ON manager_fund_history(manager_id);
CREATE INDEX IF NOT EXISTS idx_mfh_fund ON manager_fund_history(fund_code);
CREATE INDEX IF NOT EXISTS idx_mfh_current ON manager_fund_history(is_current);
CREATE INDEX IF NOT EXISTS idx_mfh_dates ON manager_fund_history(start_date, end_date);

-- ============================================================
-- 7. 基金分类字典表
-- ============================================================
CREATE TABLE IF NOT EXISTS category_dict (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_name VARCHAR(50) NOT NULL,
    parent_id INTEGER,
    category_level TINYINT NOT NULL CHECK(category_level IN (1, 2, 3)),
    description VARCHAR(200),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES category_dict(category_id)
);

-- 基金分类字典表索引
CREATE INDEX IF NOT EXISTS idx_cat_parent ON category_dict(parent_id);
CREATE INDEX IF NOT EXISTS idx_cat_level ON category_dict(category_level);
CREATE INDEX IF NOT EXISTS idx_cat_code ON category_dict(category_code);

-- ============================================================
-- 8. 基金分类关联表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    category_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    assign_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, category_id),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category_dict(category_id) ON DELETE CASCADE
);

-- 基金分类关联表索引
CREATE INDEX IF NOT EXISTS idx_fc_fund ON fund_category(fund_code);
CREATE INDEX IF NOT EXISTS idx_fc_category ON fund_category(category_id);
CREATE INDEX IF NOT EXISTS idx_fc_primary ON fund_category(is_primary);

-- ============================================================
-- 9. 基金主题标签表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    tag_name VARCHAR(30) NOT NULL,
    tag_type VARCHAR(20),
    confidence DECIMAL(3,2) DEFAULT 1.00 CHECK(confidence BETWEEN 0 AND 1),
    source VARCHAR(20),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, tag_name),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
);

-- 基金主题标签表索引
CREATE INDEX IF NOT EXISTS idx_tag_fund ON fund_tags(fund_code);
CREATE INDEX IF NOT EXISTS idx_tag_name ON fund_tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_tag_type ON fund_tags(tag_type);

-- ============================================================
-- 10. 基金统计指标表
-- ============================================================
CREATE TABLE IF NOT EXISTS fund_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    calc_date DATE NOT NULL,
    period_type VARCHAR(10) NOT NULL,
    
    -- 收益率指标
    return_rate DECIMAL(8,2),
    annualized_return DECIMAL(8,2),
    excess_return DECIMAL(8,2),
    
    -- 风险指标
    max_drawdown DECIMAL(8,2),
    volatility DECIMAL(6,2),
    downside_volatility DECIMAL(6,2),
    var_95 DECIMAL(8,2),
    
    -- 风险调整收益指标
    sharpe_ratio DECIMAL(6,2),
    sortino_ratio DECIMAL(6,2),
    calmar_ratio DECIMAL(6,2),
    treynor_ratio DECIMAL(6,2),
    information_ratio DECIMAL(6,2),
    
    -- 其他指标
    alpha DECIMAL(8,4),
    beta DECIMAL(6,4),
    win_rate DECIMAL(5,2),
    profit_loss_ratio DECIMAL(6,2),
    
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, calc_date, period_type),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
);

-- 基金统计指标表索引
CREATE INDEX IF NOT EXISTS idx_stat_fund ON fund_statistics(fund_code);
CREATE INDEX IF NOT EXISTS idx_stat_date ON fund_statistics(calc_date);
CREATE INDEX IF NOT EXISTS idx_stat_period ON fund_statistics(period_type);
CREATE INDEX IF NOT EXISTS idx_stat_fund_period ON fund_statistics(fund_code, period_type);
CREATE INDEX IF NOT EXISTS idx_stat_sharpe ON fund_statistics(sharpe_ratio);
CREATE INDEX IF NOT EXISTS idx_stat_return ON fund_statistics(return_rate);
CREATE INDEX IF NOT EXISTS idx_stat_drawdown ON fund_statistics(max_drawdown);

-- ============================================================
-- 11. 数据更新日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS data_update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    update_type VARCHAR(20) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    record_count INTEGER,
    status VARCHAR(20),
    message TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 数据更新日志表索引
CREATE INDEX IF NOT EXISTS idx_log_table ON data_update_log(table_name);
CREATE INDEX IF NOT EXISTS idx_log_time ON data_update_log(start_time);
CREATE INDEX IF NOT EXISTS idx_log_status ON data_update_log(status);

-- ============================================================
-- 创建视图
-- ============================================================

-- 视图1: 基金基本信息综合视图
CREATE VIEW IF NOT EXISTS v_fund_basic AS
SELECT 
    f.fund_code,
    f.fund_name,
    f.fund_abbr,
    f.fund_type,
    f.sub_type,
    f.risk_level,
    f.manager_company,
    f.custodian,
    f.benchmark,
    f.manage_fee_rate,
    f.custodian_fee_rate,
    f.establish_date,
    f.status,
    m.manager_name,
    m.total_scale AS manager_total_scale,
    m.invest_style AS manager_style
FROM fund_info f
LEFT JOIN manager_fund_history mf ON f.fund_code = mf.fund_code AND mf.is_current = 1
LEFT JOIN fund_manager m ON mf.manager_id = m.manager_id;

-- 视图2: 最新净值视图
CREATE VIEW IF NOT EXISTS v_latest_nav AS
SELECT 
    n.fund_code,
    n.unit_nav,
    n.accum_nav,
    n.daily_return,
    n.nav_date,
    n.subscribe_status,
    n.redeem_status
FROM fund_nav n
INNER JOIN (
    SELECT fund_code, MAX(nav_date) AS max_date 
    FROM fund_nav 
    GROUP BY fund_code
) latest ON n.fund_code = latest.fund_code AND n.nav_date = latest.max_date;

-- 视图3: 基金收益率排名视图（近1年）
CREATE VIEW IF NOT EXISTS v_fund_rank_1y AS
SELECT 
    s.fund_code,
    f.fund_name,
    f.fund_type,
    s.return_rate,
    s.sharpe_ratio,
    s.max_drawdown,
    s.calc_date,
    RANK() OVER (ORDER BY s.return_rate DESC) AS rank_by_return,
    RANK() OVER (ORDER BY s.sharpe_ratio DESC) AS rank_by_sharpe
FROM fund_statistics s
JOIN fund_info f ON s.fund_code = f.fund_code
WHERE s.period_type = '1Y'
AND s.calc_date = (SELECT MAX(calc_date) FROM fund_statistics WHERE period_type = '1Y');

-- 视图4: 基金经理当前管理基金视图
CREATE VIEW IF NOT EXISTS v_manager_current_funds AS
SELECT 
    m.manager_id,
    m.manager_name,
    m.company,
    m.total_scale,
    mf.fund_code,
    f.fund_name,
    f.fund_type,
    mf.start_date,
    mf.tenure_return,
    JULIANDAY('now') - JULIANDAY(mf.start_date) AS tenure_days
FROM fund_manager m
JOIN manager_fund_history mf ON m.manager_id = mf.manager_id
JOIN fund_info f ON mf.fund_code = f.fund_code
WHERE mf.is_current = 1;

-- 视图5: 基金持仓集中度视图
CREATE VIEW IF NOT EXISTS v_holding_concentration AS
SELECT 
    fund_code,
    report_date,
    SUM(nav_ratio) AS top10_ratio,
    COUNT(*) AS holding_count,
    AVG(nav_ratio) AS avg_ratio,
    MAX(nav_ratio) AS max_ratio
FROM fund_stock_holding
WHERE rank_num <= 10
GROUP BY fund_code, report_date;

-- ============================================================
-- 初始化数据：基金分类字典
-- ============================================================

-- 一级分类
INSERT OR IGNORE INTO category_dict (category_code, category_name, category_level, description) VALUES
('EQUITY', '股票型', 1, '主要投资于股票的基金'),
('BOND', '债券型', 1, '主要投资于债券的基金'),
('HYBRID', '混合型', 1, '股票和债券混合投资的基金'),
('MONEY', '货币型', 1, '投资于货币市场工具的基金'),
('INDEX', '指数型', 1, '跟踪特定指数的基金'),
('QDII', 'QDII', 1, '投资于境外市场的基金'),
('FOF', 'FOF', 1, '投资于其他基金的基金'),
('ETF', 'ETF', 1, '交易所交易基金');

-- 二级分类（股票型）
INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'EQUITY_GROWTH', '股票型-成长', category_id, 2, '成长型股票基金' 
FROM category_dict WHERE category_code = 'EQUITY';

INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'EQUITY_VALUE', '股票型-价值', category_id, 2, '价值型股票基金' 
FROM category_dict WHERE category_code = 'EQUITY';

INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'EQUITY_BLEND', '股票型-平衡', category_id, 2, '平衡型股票基金' 
FROM category_dict WHERE category_code = 'EQUITY';

-- 二级分类（混合型）
INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'HYBRID_STOCK', '混合型-偏股', category_id, 2, '偏股混合型基金' 
FROM category_dict WHERE category_code = 'HYBRID';

INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'HYBRID_BOND', '混合型-偏债', category_id, 2, '偏债混合型基金' 
FROM category_dict WHERE category_code = 'HYBRID';

INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'HYBRID_BALANCED', '混合型-平衡', category_id, 2, '平衡混合型基金' 
FROM category_dict WHERE category_code = 'HYBRID';

-- 二级分类（债券型）
INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'BOND_GOVERNMENT', '债券型-国债', category_id, 2, '国债基金' 
FROM category_dict WHERE category_code = 'BOND';

INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'BOND_CREDIT', '债券型-信用债', category_id, 2, '信用债基金' 
FROM category_dict WHERE category_code = 'BOND';

INSERT OR IGNORE INTO category_dict (category_code, category_name, parent_id, category_level, description) 
SELECT 'BOND_CONVERTIBLE', '债券型-可转债', category_id, 2, '可转债基金' 
FROM category_dict WHERE category_code = 'BOND';

-- ============================================================
-- 触发器：自动更新 update_time
-- ============================================================

-- fund_info 表更新触发器
CREATE TRIGGER IF NOT EXISTS trg_fund_info_update 
AFTER UPDATE ON fund_info
BEGIN
    UPDATE fund_info SET update_time = CURRENT_TIMESTAMP 
    WHERE fund_code = NEW.fund_code;
END;

-- fund_manager 表更新触发器
CREATE TRIGGER IF NOT EXISTS trg_fund_manager_update 
AFTER UPDATE ON fund_manager
BEGIN
    UPDATE fund_manager SET update_time = CURRENT_TIMESTAMP 
    WHERE manager_id = NEW.manager_id;
END;

-- ============================================================
-- 数据库创建完成
-- ============================================================

-- 更新统计信息
ANALYZE;

-- 验证表创建
SELECT 'fund_info' as table_name, COUNT(*) as record_count FROM fund_info
UNION ALL
SELECT 'fund_nav', COUNT(*) FROM fund_nav
UNION ALL
SELECT 'fund_stock_holding', COUNT(*) FROM fund_stock_holding
UNION ALL
SELECT 'fund_bond_holding', COUNT(*) FROM fund_bond_holding
UNION ALL
SELECT 'fund_manager', COUNT(*) FROM fund_manager
UNION ALL
SELECT 'manager_fund_history', COUNT(*) FROM manager_fund_history
UNION ALL
SELECT 'category_dict', COUNT(*) FROM category_dict
UNION ALL
SELECT 'fund_category', COUNT(*) FROM fund_category
UNION ALL
SELECT 'fund_tags', COUNT(*) FROM fund_tags
UNION ALL
SELECT 'fund_statistics', COUNT(*) FROM fund_statistics
UNION ALL
SELECT 'data_update_log', COUNT(*) FROM data_update_log;
