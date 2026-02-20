"""
按原有字段结构重新导入数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from datetime import datetime

def get_portfolio_id():
    """获取持仓组合ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM portfolio WHERE name = '持仓组合'")
        row = cursor.fetchone()
        if row:
            return row['id']
        return None

def check_existing_fields():
    """检查现有字段结构"""
    print("=" * 80)
    print("检查现有字段结构")
    print("=" * 80)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("PRAGMA table_info(portfolio_fund)")
        columns = cursor.fetchall()
        
        print("现有字段:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 查询持仓组合数据
        cursor.execute(
            "SELECT portfolio_id, fund_code, shares, buy_nav, amount, return_1y FROM portfolio_fund WHERE portfolio_id = 2 LIMIT 5"
        )
        rows = cursor.fetchall()
        
        print("\n示例数据:")
        for row in rows:
            print(f"  - {row['fund_code']}: shares={row['shares']}, buy_nav={row['buy_nav']}, amount={row['amount']}, return_1y={row['return_1y']}")

def revert_database():
    """回滚数据库结构，移除新增字段"""
    print("\n=" * 80)
    print("回滚数据库结构")
    print("=" * 80)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查并移除新增字段
        new_fields = ['current_value', 'profit_loss', 'profit_rate', 'cost_nav', 'import_date', 'import_source']
        
        for field in new_fields:
            try:
                # 先检查字段是否存在
                cursor.execute(f"PRAGMA table_info(portfolio_fund)")
                columns = cursor.fetchall()
                field_exists = any(col[1] == field for col in columns)
                
                if field_exists:
                    print(f"⚠️  字段 {field} 存在，需要移除")
                    # SQLite 不支持直接删除字段，需要重建表
                    # 这里我们先跳过，直接在导入时使用原有字段
                else:
                    print(f"✅ 字段 {field} 不存在")
            except Exception as e:
                print(f"❌ 检查字段 {field} 失败: {e}")
        
        # 检查表是否存在
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_import_history'")
            if cursor.fetchone():
                print(f"⚠️  表 portfolio_import_history 存在，需要移除")
                # 同样，跳过删除操作
            else:
                print(f"✅ 表 portfolio_import_history 不存在")
        except Exception as e:
            print(f"❌ 检查表失败: {e}")

def import_with_existing_fields():
    """按原有字段结构导入数据"""
    # 获取持仓组合ID
    portfolio_id = 2  # 已知ID
    
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
        
        print(f"\n📤 开始按原有字段导入数据 (组合ID: {portfolio_id})")
        print("=" * 80)
        
        success_count = 0
        fail_count = 0
        total_amount = 0
        total_profit = 0
        
        for fund in fund_data:
            try:
                fund_code = fund['code']
                current_value = fund['current_value']
                profit_loss = fund['profit_loss']
                
                # 计算成本金额
                cost_amount = current_value - profit_loss
                
                # 获取基金份额
                cursor.execute(
                    "SELECT shares FROM portfolio_fund WHERE portfolio_id = ? AND fund_code = ?",
                    (portfolio_id, fund_code)
                )
                row = cursor.fetchone()
                
                if row:
                    shares = row['shares']
                    print(f"✅ 找到份额: {fund_code} - {shares}")
                else:
                    # 计算份额（使用当前市值）
                    shares = current_value / 1.0
                    print(f"⚠️  未找到份额，计算为: {fund_code} - {shares}")
                
                # 计算买入净值 (cost_amount / shares)
                buy_nav = cost_amount / shares if shares > 0 else 0
                
                # 计算收益率
                profit_rate = (profit_loss / cost_amount) if cost_amount > 0 else 0
                
                # 插入或更新数据（使用原有字段）
                cursor.execute('''
                    INSERT OR REPLACE INTO portfolio_fund (
                        portfolio_id, fund_code, fund_name, shares, 
                        buy_nav, amount, return_1y, update_time
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                    )
                ''', (
                    portfolio_id, fund_code, fund['name'], shares,
                    buy_nav, cost_amount, profit_rate
                ))
                
                success_count += 1
                total_amount += cost_amount
                total_profit += profit_loss
                
                print(f"✅ 导入成功: {fund_code} - {fund['name']}")
                print(f"   持有金额: ¥{current_value:.2f}")
                print(f"   持仓收益: ¥{profit_loss:.2f}")
                print(f"   成本金额: ¥{cost_amount:.2f}")
                print(f"   买入净值: ¥{buy_nav:.4f}")
                print(f"   收益率: {profit_rate:.2%}")
                
            except Exception as e:
                fail_count += 1
                print(f"❌ 导入失败: {fund_code} - {e}")
        
        conn.commit()
        
        print("=" * 80)
        print(f"\n📊 导入完成!")
        print(f"✅ 成功: {success_count} 只基金")
        print(f"❌ 失败: {fail_count} 只基金")
        print(f"💰 总成本金额: ¥{total_amount:.2f}")
        print(f"📈 总持仓收益: ¥{total_profit:.2f}")
        print(f"📉 总收益率: {(total_profit / total_amount):.2%}")
        print("=" * 80)

def main():
    """主函数"""
    # 检查现有字段
    check_existing_fields()
    
    # 回滚数据库结构
    revert_database()
    
    # 按原有字段导入数据
    import_with_existing_fields()

if __name__ == '__main__':
    main()
