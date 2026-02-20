"""
FundData Skill - 数据库管理模块
管理SQLite数据库连接和表结构
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fund_data.db")


@contextmanager
def get_db_connection():
    """
    获取数据库连接的上下文管理器
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """初始化数据库表结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. 全局数据表 - 基金基本信息
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_info (
                fund_code VARCHAR(10) PRIMARY KEY,
                fund_name VARCHAR(100) NOT NULL,
                fund_full_name VARCHAR(200),
                fund_type VARCHAR(50),
                pinyin_abbr VARCHAR(50),
                pinyin_full VARCHAR(100),
                company_name VARCHAR(100),
                custodian VARCHAR(100),
                establish_date DATE,
                issue_date DATE,
                establish_scale DECIMAL(15,4),
                manage_fee_rate DECIMAL(8,4),
                custodian_fee_rate DECIMAL(8,4),
                benchmark VARCHAR(200),
                invest_scope TEXT,
                track_target VARCHAR(100),
                status VARCHAR(20) DEFAULT '正常',
                data_source VARCHAR(20),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 全局数据表 - 基金申购状态
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_purchase_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                fund_name VARCHAR(100),
                fund_type VARCHAR(50),
                unit_nav DECIMAL(10,4),
                nav_date DATE,
                subscribe_status VARCHAR(20),
                redeem_status VARCHAR(20),
                next_open_date DATE,
                min_purchase DECIMAL(15,4),
                daily_limit DECIMAL(15,4),
                fee_rate DECIMAL(8,4),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code)
            )
        ''')
        
        # 3. 全局数据表 - 基金评级
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_rating (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                fund_name VARCHAR(100),
                manager_name VARCHAR(50),
                company_name VARCHAR(100),
                rating_5star_count INTEGER,
                rating_sh DECIMAL(3,2),
                rating_zs DECIMAL(3,2),
                rating_ja DECIMAL(3,2),
                rating_morningstar DECIMAL(3,2),
                fee_rate DECIMAL(8,4),
                fund_type VARCHAR(50),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code)
            )
        ''')
        
        # 4. 全局数据表 - 基金经理
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_manager (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manager_name VARCHAR(50) NOT NULL,
                company_name VARCHAR(100),
                fund_code VARCHAR(10),
                fund_name VARCHAR(100),
                tenure_days INTEGER,
                total_scale DECIMAL(15,4),
                best_return DECIMAL(8,4),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(manager_name, fund_code)
            )
        ''')
        
        # 5. 全局数据表 - 基金公司
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(100) NOT NULL UNIQUE,
                establish_date DATE,
                manage_scale DECIMAL(15,4),
                fund_count INTEGER,
                manager_count INTEGER,
                rating_tx INTEGER,
                description TEXT,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 6. 全局数据表 - 基金分红
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_dividend (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                fund_name VARCHAR(100),
                record_date DATE,
                ex_dividend_date DATE,
                dividend_per_share DECIMAL(10,4),
                payment_date DATE,
                year VARCHAR(4),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, record_date)
            )
        ''')
        
        # 7. 全局数据表 - 基金拆分
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_split (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                fund_name VARCHAR(100),
                split_date DATE,
                split_type VARCHAR(50),
                split_ratio DECIMAL(10,4),
                year VARCHAR(4),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, split_date)
            )
        ''')
        
        # 8. 全局数据表 - 基金排行
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_rank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                fund_name VARCHAR(100),
                rank_date DATE,
                unit_nav DECIMAL(10,4),
                accum_nav DECIMAL(10,4),
                daily_return DECIMAL(8,4),
                return_1w DECIMAL(8,4),
                return_1m DECIMAL(8,4),
                return_3m DECIMAL(8,4),
                return_6m DECIMAL(8,4),
                return_1y DECIMAL(8,4),
                return_2y DECIMAL(8,4),
                return_3y DECIMAL(8,4),
                return_this_year DECIMAL(8,4),
                return_since_inception DECIMAL(8,4),
                fee_rate DECIMAL(8,4),
                fund_category VARCHAR(50),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, rank_date, fund_category)
            )
        ''')
        
        # 9. 分组数据表 - 历史净值
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_nav (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                nav_date DATE NOT NULL,
                unit_nav DECIMAL(10,4),
                accum_nav DECIMAL(10,4),
                daily_return DECIMAL(8,4),
                subscribe_status VARCHAR(20),
                redeem_status VARCHAR(20),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, nav_date)
            )
        ''')
        
        # 10. 分组数据表 - 股票持仓
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_stock_holding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                report_date DATE NOT NULL,
                stock_code VARCHAR(10),
                stock_name VARCHAR(50),
                hold_ratio DECIMAL(8,4),
                hold_shares DECIMAL(15,4),
                hold_value DECIMAL(15,4),
                quarter VARCHAR(10),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, report_date, stock_code)
            )
        ''')
        
        # 11. 分组数据表 - 债券持仓
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_bond_holding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                report_date DATE NOT NULL,
                bond_code VARCHAR(10),
                bond_name VARCHAR(50),
                hold_ratio DECIMAL(8,4),
                hold_value DECIMAL(15,4),
                quarter VARCHAR(10),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, report_date, bond_code)
            )
        ''')
        
        # 12. 分组数据表 - 行业配置
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_industry_allocation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                report_date DATE NOT NULL,
                industry_name VARCHAR(50),
                allocation_ratio DECIMAL(8,4),
                market_value DECIMAL(15,4),
                quarter VARCHAR(10),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, report_date, industry_name)
            )
        ''')
        
        # 13. 分组数据表 - 风险指标
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_risk_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                period VARCHAR(20) NOT NULL,
                risk_return_ratio INTEGER,
                risk_resistance INTEGER,
                annual_volatility DECIMAL(8,4),
                sharpe_ratio DECIMAL(8,4),
                max_drawdown DECIMAL(8,4),
                data_source VARCHAR(20) DEFAULT 'xueqiu',
                calc_start_date DATE,
                calc_end_date DATE,
                trading_days INTEGER,
                period_return DECIMAL(8,4),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, period)
            )
        ''')
        
        # 兼容旧表：添加新字段
        try:
            cursor.execute("ALTER TABLE fund_risk_metrics ADD COLUMN data_source VARCHAR(20) DEFAULT 'xueqiu'")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE fund_risk_metrics ADD COLUMN calc_start_date DATE")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE fund_risk_metrics ADD COLUMN calc_end_date DATE")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE fund_risk_metrics ADD COLUMN trading_days INTEGER")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE fund_risk_metrics ADD COLUMN period_return DECIMAL(8,4)")
        except:
            pass
        
        # 14. 分组数据表 - 业绩表现
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                performance_type VARCHAR(50),
                period VARCHAR(20),
                period_return DECIMAL(8,4),
                max_drawdown DECIMAL(8,4),
                rank_in_category VARCHAR(20),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, performance_type, period)
            )
        ''')
        
        # 15. 分组数据表 - 资产配置
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_asset_allocation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                report_date DATE NOT NULL,
                asset_type VARCHAR(50),
                allocation_ratio DECIMAL(8,4),
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, report_date, asset_type)
            )
        ''')
        
        # 16. 元数据表 - 同步状态
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_data_meta (
                table_name VARCHAR(50) PRIMARY KEY,
                last_sync_time DATETIME,
                record_count INTEGER DEFAULT 0,
                last_sync_status VARCHAR(20),
                last_error TEXT
            )
        ''')
        
        # 17. 交易日历表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_calendar (
                trade_date DATE PRIMARY KEY,
                is_trade_day INTEGER DEFAULT 1,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 18. 指数参考基准表 - 市值定投用
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_benchmark (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_code VARCHAR(10) NOT NULL,
                index_name VARCHAR(50),
                market_phase VARCHAR(20) NOT NULL,
                avg_monthly_return DECIMAL(8,4),
                monthly_return_std DECIMAL(8,4),
                sample_months INTEGER,
                data_start_date DATE,
                data_end_date DATE,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(index_code, market_phase)
            )
        ''')
        
        # 18. 市场阶段记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_phase_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_name VARCHAR(20) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                is_current INTEGER DEFAULT 0,
                confirmed_date DATE,
                data_source TEXT,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(phase_name, start_date)
            )
        ''')
        
        # 19. 组合表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                cash DECIMAL(15,2) DEFAULT 0,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 兼容旧表：添加cash字段
        try:
            cursor.execute("ALTER TABLE portfolio ADD COLUMN cash DECIMAL(15,2) DEFAULT 0")
        except:
            pass

        # 兼容旧表：为portfolio_fund添加缺失字段
        portfolio_fund_new_columns = [
            ("current_value", "DECIMAL(15,2)"),
            ("cost_nav", "DECIMAL(10,4)"),
            ("import_date", "DATE"),
            ("import_source", "VARCHAR(20)"),
            ("profit_loss", "DECIMAL(15,2)"),
        ]
        for col_name, col_type in portfolio_fund_new_columns:
            try:
                cursor.execute(f"ALTER TABLE portfolio_fund ADD COLUMN {col_name} {col_type}")
            except:
                pass

        # 20. 成分基金表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_fund (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                fund_code VARCHAR(10) NOT NULL,
                fund_name VARCHAR(100),
                buy_date DATE,
                buy_nav DECIMAL(10,4),
                cost_nav DECIMAL(10,4),
                shares DECIMAL(15,4),
                amount DECIMAL(15,2),
                current_value DECIMAL(15,2),
                profit_loss DECIMAL(15,2),
                notes TEXT,
                return_1m DECIMAL(8,4),
                return_6m DECIMAL(8,4),
                return_1y DECIMAL(8,4),
                max_drawdown_1y DECIMAL(8,4),
                sharpe_ratio_1y DECIMAL(8,4),
                annual_volatility_1y DECIMAL(8,4),
                rank_in_category VARCHAR(20),
                rank_category VARCHAR(50),
                import_date DATE,
                import_source VARCHAR(20),
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                metrics_update_time DATETIME,
                UNIQUE(portfolio_id, fund_code),
                FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
            )
        ''')
        
        # 21. 持仓历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holding_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                fund_code VARCHAR(10) NOT NULL,
                record_date DATE NOT NULL,
                shares DECIMAL(15,4) NOT NULL,
                nav DECIMAL(10,4),
                shares_change DECIMAL(15,4),
                notes TEXT,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(portfolio_id, fund_code, record_date),
                FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
            )
        ''')

        # 22. 交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_transaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                fund_code VARCHAR(10) NOT NULL,
                transaction_type VARCHAR(10) NOT NULL,  -- BUY/SELL
                transaction_date DATE NOT NULL,
                shares DECIMAL(15,4) NOT NULL,          -- 交易份额
                amount DECIMAL(15,2) NOT NULL,          -- 交易金额（买入为投入金额，卖出为获得金额）
                nav DECIMAL(10,4),                      -- 交易时净值
                fee DECIMAL(10,2) DEFAULT 0,            -- 手续费
                is_recovered INTEGER DEFAULT 0,         -- 卖出记录是否已被捡回 (0:未回收, 1:已回收)
                confirmed_nav DECIMAL(10,4),            -- 卖出时的确认净值，用于计算跌幅
                notes TEXT,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
            )
        ''')

        # 兼容旧表：添加交易记录表的波段捡回字段
        try:
            cursor.execute("ALTER TABLE portfolio_transaction ADD COLUMN is_recovered INTEGER DEFAULT 0")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE portfolio_transaction ADD COLUMN confirmed_nav DECIMAL(10,4)")
        except:
            pass
        
        # 23. 止盈参数模板表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS take_profit_template (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                first_threshold DECIMAL(5,4) DEFAULT 0.20,
                first_sell_ratio DECIMAL(5,4) DEFAULT 0.30,
                step_size DECIMAL(5,4) DEFAULT 0.05,
                follow_up_sell_ratio DECIMAL(5,4) DEFAULT 0.20,
                enable_cost_control INTEGER DEFAULT 1,
                target_diluted_cost DECIMAL(10,4) DEFAULT 0,
                enable_buy_back INTEGER DEFAULT 0,
                buy_back_threshold DECIMAL(5,4) DEFAULT 0.20,
                is_default INTEGER DEFAULT 0,
                is_system INTEGER DEFAULT 0,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 兼容旧表：添加波段捡回相关字段
        try:
            cursor.execute("ALTER TABLE take_profit_template ADD COLUMN enable_buy_back INTEGER DEFAULT 0")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE take_profit_template ADD COLUMN buy_back_threshold DECIMAL(5,4) DEFAULT 0.20")
        except:
            pass
        
        # 24. 基金止盈配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_take_profit_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                fund_code VARCHAR(10) NOT NULL,
                template_id INTEGER,
                custom_first_threshold DECIMAL(5,4),
                custom_first_sell_ratio DECIMAL(5,4),
                custom_step_size DECIMAL(5,4),
                custom_follow_up_sell_ratio DECIMAL(5,4),
                custom_enable_cost_control INTEGER,
                custom_target_diluted_cost DECIMAL(10,4),
                custom_enable_buy_back INTEGER,
                custom_buy_back_threshold DECIMAL(5,4),
                enabled INTEGER DEFAULT 1,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES take_profit_template(id) ON DELETE SET NULL,
                UNIQUE(portfolio_id, fund_code)
            )
        ''')

        # 兼容旧表：添加基金止盈配置表的波段捡回字段
        try:
            cursor.execute("ALTER TABLE fund_take_profit_config ADD COLUMN custom_enable_buy_back INTEGER")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE fund_take_profit_config ADD COLUMN custom_buy_back_threshold DECIMAL(5,4)")
        except:
            pass
        
        # 初始化系统预设止盈模板
        cursor.execute("SELECT COUNT(*) as count FROM take_profit_template WHERE is_system = 1")
        if cursor.fetchone()['count'] == 0:
            cursor.execute('''
                INSERT INTO take_profit_template (name, description, first_threshold, first_sell_ratio, step_size, follow_up_sell_ratio, enable_cost_control, target_diluted_cost, is_default, is_system) VALUES
                ('标准型', '首次盈利20%卖出30%，后续每涨5%卖出20%', 0.20, 0.30, 0.05, 0.20, 1, 0, 1, 1),
                ('激进型', '首次盈利30%卖出20%，后续每涨8%卖出15%', 0.30, 0.20, 0.08, 0.15, 0, 0, 0, 1),
                ('稳健型', '首次盈利15%卖出40%，后续每涨3%卖出25%', 0.15, 0.40, 0.03, 0.25, 1, 0, 0, 1),
                ('保守型', '首次盈利10%卖出50%，后续每涨2%卖出30%', 0.10, 0.50, 0.02, 0.30, 1, 0, 0, 1)
            ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_info_type ON fund_info(fund_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_info_company ON fund_info(company_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_nav_code ON fund_nav(fund_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_nav_date ON fund_nav(nav_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_holding_code ON fund_stock_holding(fund_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_rating_code ON fund_rating(fund_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_manager_code ON fund_manager(fund_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_holding_history_portfolio_fund ON holding_history(portfolio_id, fund_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_holding_history_date ON holding_history(record_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_fund_portfolio ON portfolio_fund(portfolio_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_take_profit_config_portfolio ON fund_take_profit_config(portfolio_id)')
        
        conn.commit()
        print(f"[FundData] 数据库初始化完成: {DB_PATH}")


def get_table_stats() -> Dict[str, Any]:
    """获取各数据表的统计信息"""
    tables = [
        'fund_info', 'fund_purchase_status', 'fund_rating', 'fund_manager',
        'fund_company', 'fund_dividend', 'fund_split', 'fund_rank',
        'fund_nav', 'fund_stock_holding', 'fund_bond_holding',
        'fund_industry_allocation', 'fund_risk_metrics', 'fund_performance',
        'fund_asset_allocation'
    ]
    
    stats = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                
                cursor.execute(
                    "SELECT last_sync_time, last_sync_status FROM fund_data_meta WHERE table_name = ?",
                    (table,)
                )
                meta = cursor.fetchone()
                
                stats[table] = {
                    'record_count': count,
                    'last_sync_time': meta['last_sync_time'] if meta else None,
                    'last_sync_status': meta['last_sync_status'] if meta else None
                }
            except Exception as e:
                stats[table] = {
                    'record_count': 0,
                    'error': str(e)
                }
    
    return stats


def update_sync_meta(table_name: str, status: str, error: str = None):
    """更新同步元数据"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO fund_data_meta 
               (table_name, last_sync_time, record_count, last_sync_status, last_error)
               VALUES (?, datetime('now'), 
               (SELECT COUNT(*) FROM {}), ?, ?)""".format(table_name),
            (table_name, status, error)
        )
        conn.commit()


def update_holdings_meta(fund_code: str, status: str):
    """更新持仓查询元数据（不查询记录数）"""
    from datetime import datetime
    meta_key = f'holdings_{fund_code}'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO fund_data_meta 
               (table_name, last_sync_time, last_sync_status)
               VALUES (?, ?, ?)""",
            (meta_key, current_time, status)
        )
        conn.commit()


def sync_trade_calendar(force: bool = False) -> Dict[str, Any]:
    """
    同步交易日历数据
    
    Args:
        force: 是否强制刷新
    
    Returns:
        同步结果
    """
    from datetime import date
    import akshare as ak
    
    today = date.today()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查是否需要更新
        cursor.execute("SELECT MAX(trade_date) as max_date FROM trade_calendar")
        row = cursor.fetchone()
        max_date = row['max_date'] if row else None
        
        # 如果数据存在且覆盖到今天之后，且不强制刷新，则跳过
        if not force and max_date:
            max_date_obj = datetime.strptime(max_date, '%Y-%m-%d').date() if isinstance(max_date, str) else max_date
            if max_date_obj >= today:
                return {'success': True, 'message': '交易日历数据已是最新', 'skipped': True}
        
        # 从AKShare获取交易日历
        try:
            df = ak.tool_trade_date_hist_sina()
            trade_dates = df['trade_date'].tolist()
            
            # 清空旧数据并插入新数据
            cursor.execute("DELETE FROM trade_calendar")
            
            for trade_date in trade_dates:
                date_str = trade_date.strftime('%Y-%m-%d') if hasattr(trade_date, 'strftime') else str(trade_date)
                cursor.execute(
                    "INSERT OR REPLACE INTO trade_calendar (trade_date, is_trade_day) VALUES (?, 1)",
                    (date_str,)
                )
            
            conn.commit()
            
            return {
                'success': True,
                'message': f'成功同步 {len(trade_dates)} 个交易日',
                'count': len(trade_dates),
                'max_date': trade_dates[-1].strftime('%Y-%m-%d') if hasattr(trade_dates[-1], 'strftime') else str(trade_dates[-1])
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


def is_trade_day(check_date: Any = None) -> bool:
    """
    判断是否为交易日
    
    Args:
        check_date: 要检查的日期，默认为今天
    
    Returns:
        是否为交易日
    """
    from datetime import date, datetime
    
    if check_date is None:
        check_date = date.today()
    elif isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    elif isinstance(check_date, datetime):
        check_date = check_date.date()
    
    date_str = check_date.strftime('%Y-%m-%d')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 先检查数据是否覆盖到该日期
        cursor.execute("SELECT MAX(trade_date) as max_date FROM trade_calendar")
        row = cursor.fetchone()
        max_date = row['max_date'] if row else None
        
        if max_date:
            max_date_obj = datetime.strptime(max_date, '%Y-%m-%d').date() if isinstance(max_date, str) else max_date
            # 如果查询日期在数据范围内
            if check_date <= max_date_obj:
                cursor.execute(
                    "SELECT is_trade_day FROM trade_calendar WHERE trade_date = ?",
                    (date_str,)
                )
                result = cursor.fetchone()
                return result is not None and result['is_trade_day'] == 1
        
        # 数据不在范围内，尝试同步
        sync_result = sync_trade_calendar()
        if sync_result['success'] and not sync_result.get('skipped'):
            # 重新查询
            cursor.execute(
                "SELECT is_trade_day FROM trade_calendar WHERE trade_date = ?",
                (date_str,)
            )
            result = cursor.fetchone()
            return result is not None and result['is_trade_day'] == 1
        
        # 同步失败，使用简单判断（排除周末）
        return check_date.weekday() < 5


def get_latest_trade_day(before_date: Any = None) -> str:
    """
    获取指定日期之前（含）的最近一个交易日
    
    Args:
        before_date: 截止日期，默认为今天
    
    Returns:
        最近交易日的日期字符串
    """
    from datetime import date, datetime, timedelta
    
    if before_date is None:
        before_date = date.today()
    elif isinstance(before_date, str):
        before_date = datetime.strptime(before_date, '%Y-%m-%d').date()
    elif isinstance(before_date, datetime):
        before_date = before_date.date()
    
    date_str = before_date.strftime('%Y-%m-%d')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查数据是否覆盖
        cursor.execute("SELECT MAX(trade_date) as max_date FROM trade_calendar")
        row = cursor.fetchone()
        max_date = row['max_date'] if row else None
        
        if max_date:
            max_date_obj = datetime.strptime(max_date, '%Y-%m-%d').date() if isinstance(max_date, str) else max_date
            if before_date <= max_date_obj:
                cursor.execute(
                    "SELECT trade_date FROM trade_calendar WHERE trade_date <= ? ORDER BY trade_date DESC LIMIT 1",
                    (date_str,)
                )
                result = cursor.fetchone()
                if result:
                    return result['trade_date']
        
        # 数据不足，尝试同步
        sync_result = sync_trade_calendar()
        if sync_result['success']:
            cursor.execute(
                "SELECT trade_date FROM trade_calendar WHERE trade_date <= ? ORDER BY trade_date DESC LIMIT 1",
                (date_str,)
            )
            result = cursor.fetchone()
            if result:
                return result['trade_date']
        
        # 同步失败，使用简单判断
        check_date = before_date
        for _ in range(7):
            if check_date.weekday() < 5:
                return check_date.strftime('%Y-%m-%d')
            check_date -= timedelta(days=1)
        
        return check_date.strftime('%Y-%m-%d')


# 初始化数据库
init_database()
