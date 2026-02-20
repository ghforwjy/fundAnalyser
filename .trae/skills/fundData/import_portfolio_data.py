"""
导入持仓组合数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from portfolio_manager import create_portfolio, list_portfolios
from datetime import datetime

def get_or_create_portfolio():
    """获取或创建持仓组合"""
    # 先查询现有组合
    portfolios = list_portfolios()
    
    # 查找名为"持仓组合"的组合
    for portfolio in portfolios:
        if portfolio['name'] == '持仓组合':
            print(f"✅ 找到现有组合: 持仓组合 (ID: {portfolio['id']})")
            return portfolio['id']
    
    # 如果不存在，创建新组合
    print("❌ 未找到持仓组合，创建新组合...")
    result = create_portfolio('持仓组合', '导入的持仓组合数据')
    
    if result['success']:
        portfolio_id = result['portfolio_id']
        print(f"✅ 创建成功: 持仓组合 (ID: {portfolio_id})")
        return portfolio_id
    else:
        print(f"❌ 创建失败: {result['error']}")
        return None

def upgrade_database():
    """升级数据库结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 添加新字段到 portfolio_fund 表
        fields_to_add = [
            ('current_value', 'DECIMAL(15,2)'),
            ('profit_loss', 'DECIMAL(15,2)'),
            ('profit_rate', 'DECIMAL(8,4)'),
            ('cost_nav', 'DECIMAL(10,4)'),
            ('import_date', 'DATE'),
            ('import_source', 'VARCHAR(20)'),
        ]
        
        for field_name, field_type in fields_to_add:
            try:
                cursor.execute(f"ALTER TABLE portfolio_fund ADD COLUMN {field_name} {field_type}")
                print(f"✅ 添加字段: {field_name}")
            except Exception as e:
                # 字段已存在
                print(f"⚠️  字段 {field_name} 可能已存在")
        
        # 创建导入记录表
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_import_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER NOT NULL,
                    import_date DATE NOT NULL,
                    import_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fund_count INTEGER,
                    total_current_value DECIMAL(15,2),
                    total_profit_loss DECIMAL(15,2),
                    import_mode VARCHAR(10),
                    source_type VARCHAR(20),
                    notes TEXT,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
                )
            ''')
            print("✅ 创建表: portfolio_import_history")
        except Exception as e:
            print(f"⚠️  创建表失败: {e}")
        
        conn.commit()

def import_profit_data(portfolio_id):
    """导入盈亏数据"""
    # 最终修正版数据
    fund_data = [
        {'code': '018957', 'name': '中航机遇领航混合发起C', 'current_value': 25956.71, 'profit_loss': 16456.71},
        {'code': '022853', 'name': '中航优选领航混合发起C', 'current_value': 12803.50, 'profit_loss': 4103.50},
        {'code': '021489', 'name': '中航趋势领航混合发起A', 'current_value': 7104.70, 'profit_loss': 2684.70},
        {'code': '021492', 'name': '中航远见领航混合发起C', 'current_value': 11506.50, 'profit_loss': 2613.24},
        {'code': '024389', 'name': '中航智选领航混合发起C', 'current_value': 10688.38, 'profit_loss': 4688.38},
        {'code': '024291', 'name': '中航月月鑫30天持有期债券C', 'current_value': 10.03, 'profit_loss': 0.03},
        {'code': '024290', 'name': '中航月月鑫30天持有期债券A', 'current_value': 10.01, 'profit_loss': 0.01},
        {'code': '001052', 'name': '华夏中证500ETF联接A', 'current_value': 16297.49, 'profit_loss': 7797.49},
        {'code': '486001', 'name': '工银全球股票(QDII)人民币', 'current_value': 32979.62, 'profit_loss': 18577.96},
        {'code': '001595', 'name': '天弘中证银行ETF联接C', 'current_value': 63536.79, 'profit_loss': 30036.79},
        {'code': '000143', 'name': '鹏华双债加利债券A', 'current_value': 388704.74, 'profit_loss': 90596.94},
        {'code': '006331', 'name': '中银国有企业债C', 'current_value': 31449.00, 'profit_loss': 1449.00},
        {'code': '007994', 'name': '华夏中证500指数增强A', 'current_value': 259469.63, 'profit_loss': 94469.69},
        {'code': '501022', 'name': '银华鑫盛灵活配置混合(LOF)A', 'current_value': 202204.78, 'profit_loss': 29704.78},
        {'code': '160514', 'name': '博时稳健回报债券(LOF)C', 'current_value': 114807.42, 'profit_loss': 14807.42},
        {'code': '009424', 'name': '招商瑞信稳健配置混合C', 'current_value': 111674.48, 'profit_loss': 11674.48},
        {'code': '013431', 'name': '华泰柏瑞景气汇选三年持有期混合A', 'current_value': 67730.12, 'profit_loss': 17730.12},
        {'code': '004011', 'name': '华泰柏瑞鼎利灵活配置混合C', 'current_value': 52567.55, 'profit_loss': 7521.17},
    ]
    
    import_date = datetime.now().strftime('%Y-%m-%d')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 开始导入
        print(f"\n📤 开始导入数据到组合 ID: {portfolio_id} (日期: {import_date})")
        print("=" * 80)
        
        success_count = 0
        fail_count = 0
        total_current_value = 0
        total_profit_loss = 0
        
        for fund in fund_data:
            try:
                # 获取基金份额（从现有记录或计算）
                cursor.execute(
                    "SELECT shares FROM portfolio_fund WHERE portfolio_id = ? AND fund_code = ?",
                    (portfolio_id, fund['code'])
                )
                row = cursor.fetchone()
                
                if row:
                    shares = row['shares']
                    print(f"✅ 找到份额: {fund['code']} - {shares}")
                else:
                    # 计算份额（假设当前净值 = current_value / shares）
                    # 这里使用简单方法，实际应该从 fund_nav 表获取最新净值
                    # 暂时使用 1.0 作为默认值
                    shares = fund['current_value'] / 1.0
                    print(f"⚠️  未找到份额，计算为: {fund['code']} - {shares}")
                
                # 计算成本净值
                cost_nav = (fund['current_value'] - fund['profit_loss']) / shares if shares > 0 else 0
                profit_rate = (fund['profit_loss'] / (fund['current_value'] - fund['profit_loss'])) if (fund['current_value'] - fund['profit_loss']) > 0 else 0
                
                # 插入或更新数据
                cursor.execute('''
                    INSERT OR REPLACE INTO portfolio_fund (
                        portfolio_id, fund_code, fund_name, shares, 
                        current_value, profit_loss, profit_rate, cost_nav, 
                        import_date, import_source, update_time
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                    )
                ''', (
                    portfolio_id, fund['code'], fund['name'], shares,
                    fund['current_value'], fund['profit_loss'], profit_rate, cost_nav,
                    import_date, 'final_corrected'
                ))
                
                success_count += 1
                total_current_value += fund['current_value']
                total_profit_loss += fund['profit_loss']
                
                print(f"✅ 导入成功: {fund['code']} - {fund['name']}")
                print(f"   持有金额: ¥{fund['current_value']:.2f}")
                print(f"   持仓收益: ¥{fund['profit_loss']:.2f}")
                print(f"   成本净值: ¥{cost_nav:.4f}")
                print(f"   收益率: {profit_rate:.2%}")
                
            except Exception as e:
                fail_count += 1
                print(f"❌ 导入失败: {fund['code']} - {e}")
        
        # 记录导入历史
        cursor.execute('''
            INSERT INTO portfolio_import_history (
                portfolio_id, import_date, fund_count, 
                total_current_value, total_profit_loss, 
                import_mode, source_type, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            portfolio_id, import_date, success_count,
            total_current_value, total_profit_loss,
            'overwrite', 'final_corrected', '最终修正版数据导入'
        ))
        
        conn.commit()
        
        print("=" * 80)
        print(f"\n📊 导入完成!")
        print(f"✅ 成功: {success_count} 只基金")
        print(f"❌ 失败: {fail_count} 只基金")
        print(f"💰 总持有金额: ¥{total_current_value:.2f}")
        print(f"📈 总持仓收益: ¥{total_profit_loss:.2f}")
        print(f"📉 总收益率: {(total_profit_loss / (total_current_value - total_profit_loss)):.2%}")
        print("=" * 80)

def main():
    """主函数"""
    print("=" * 80)
    print("导入持仓组合数据")
    print("=" * 80)
    
    # 获取或创建组合
    portfolio_id = get_or_create_portfolio()
    
    if portfolio_id:
        # 升级数据库
        print("\n🔧 升级数据库结构...")
        upgrade_database()
        
        # 导入数据
        import_profit_data(portfolio_id)
    else:
        print("❌ 无法获取组合ID，导入失败")

if __name__ == '__main__':
    main()
