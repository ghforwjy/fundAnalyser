"""
验证累计持仓收益
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

def extract_data_from_images():
    """从图片提取数据"""
    # 图片1数据
    image1_data = [
        {'name': '中航机遇领航混合C', 'amount': 25956.71, 'profit': 16456.71},
        {'name': '中航优选领航混合C', 'amount': 12803.50, 'profit': 4103.50},
        {'name': '中航趋势领航混合A', 'amount': 7104.70, 'profit': 2684.70},
        {'name': '中航远见领航混合C', 'amount': 11506.50, 'profit': 2613.24},
        {'name': '中航智选领航混合C', 'amount': 10688.38, 'profit': 4688.38},
        {'name': '中航月月鑫30天持有期债券C', 'amount': 10.03, 'profit': 0.03},
        {'name': '中航月月鑫30天持有期债券A', 'amount': 10.01, 'profit': 0.01},
        {'name': '华夏中证500ETF联接A', 'amount': 16297.49, 'profit': 7797.49},
        {'name': '工银全球股票(QDII)人民币', 'amount': 32979.62, 'profit': 18577.96},
        {'name': '天弘中证银行ETF联接C', 'amount': 63536.79, 'profit': 30036.79},
        {'name': '鹏华双债加利债券A', 'amount': 388704.74, 'profit': 90596.94},
        {'name': '中银国有企业债C', 'amount': 31449.00, 'profit': 1449.00},
    ]
    
    # 图片2数据
    image2_data = [
        {'name': '华夏中证500指数增强A', 'amount': 259469.63, 'profit': 94469.69},
        {'name': '银华鑫盛灵活配置混合(LOF)A', 'amount': 202204.78, 'profit': 29704.78},
        {'name': '博时稳健回报债券(LOF)C', 'amount': 114807.42, 'profit': 14807.42},
        {'name': '招商瑞信稳健配置C', 'amount': 111674.48, 'profit': 11674.48},
        {'name': '华泰柏瑞景气汇选三年持有期混合A', 'amount': 67730.12, 'profit': 17730.12},
        {'name': '华泰柏瑞鼎利混合C', 'amount': 52567.55, 'profit': 7521.17},
    ]
    
    return image1_data + image2_data

def verify_total_profit():
    """验证累计持仓收益"""
    print("=" * 100)
    print("验证累计持仓收益")
    print("=" * 100)
    
    # 从图片提取数据
    data = extract_data_from_images()
    
    print("图片数据汇总:")
    print("-" * 100)
    
    total_amount = 0
    total_profit = 0
    
    for i, item in enumerate(data, 1):
        total_amount += item['amount']
        total_profit += item['profit']
        print(f"{i:2d} | {item['name']:<30} | 持有金额: ¥{item['amount']:>10.2f} | 持仓收益: ¥{item['profit']:>10.2f}")
    
    print("-" * 100)
    print(f"合 计 | {'':<30} | 持有金额: ¥{total_amount:>10.2f} | 持仓收益: ¥{total_profit:>10.2f}")
    print(f"收益率: {(total_profit / (total_amount - total_profit)):.2%}")
    
    # 与导入结果对比
    print("\n=" * 100)
    print("与导入结果对比")
    print("=" * 100)
    
    # 查询数据库导入结果
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT SUM(amount) as total_amount, SUM(return_1y * amount) as total_profit FROM portfolio_fund WHERE portfolio_id = 2"
        )
        row = cursor.fetchone()
        
        if row:
            db_amount = row['total_amount']
            db_profit = row['total_profit']
            
            print(f"数据库成本金额: ¥{db_amount:,.2f}")
            print(f"数据库计算收益: ¥{db_profit:,.2f}")
            print(f"数据库收益率: {(db_profit / db_amount):.2%}")
        else:
            print("数据库中无数据")
    
    print("\n=" * 100)
    print("验证结论")
    print("=" * 100)
    
    # 计算差异
    expected_profit = 354912.41  # 之前计算的总收益
    actual_profit = total_profit
    
    print(f"预期总收益: ¥{expected_profit:.2f}")
    print(f"实际总收益: ¥{actual_profit:.2f}")
    print(f"差异: ¥{abs(expected_profit - actual_profit):.2f}")
    
    if abs(expected_profit - actual_profit) < 0.01:
        print("✅ 累计持仓收益正确")
    else:
        print("❌ 累计持仓收益有误")

def main():
    """主函数"""
    verify_total_profit()

if __name__ == '__main__':
    main()
