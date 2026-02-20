"""
验证新图片的累计持仓收益
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def extract_new_images_data():
    """从新图片提取数据"""
    print("=" * 100)
    print("从新图片提取数据")
    print("=" * 100)
    
    # 图片1数据（蓝色界面）
    print("\n图片1数据（蓝色界面）:")
    print("-" * 100)
    
    image1_data = [
        {'name': '中航机遇领航混合C', 'amount': 25956.71, 'profit': 16456.71},
        {'name': '中航优选领航混合C', 'amount': 12803.50, 'profit': 4103.50},
        {'name': '中航趋势领航混合A', 'amount': 7104.70, 'profit': 2684.70},
        {'name': '中航远见领航混合C', 'amount': 11506.50, 'profit': 2613.24},
        {'name': '中航智选领航混合C', 'amount': 10688.38, 'profit': 4688.38},
        {'name': '中航月月鑫30天持有期债券C', 'amount': 10.03, 'profit': 0.03},
        {'name': '中航月月鑫30天持有期债券A', 'amount': 10.01, 'profit': 0.01},
        {'name': '华夏中证500ETF联接A', 'amount': 16297.49, 'profit': 7797.49},
        {'name': '工银全球股票(QDII)人民币', 'amount': 32979.62, 'profit': 14899.97},
        {'name': '天弘中证银行ETF联接C', 'amount': 63536.79, 'profit': 28808.98},
        {'name': '鹏华双债加利债券A', 'amount': 388704.74, 'profit': 79296.84},
        {'name': '中银国有企业债券C', 'amount': 31449.00, 'profit': 1449.00},
    ]
    
    # 图片2数据（红色界面）
    print("\n图片2数据（红色界面）:")
    print("-" * 100)
    
    image2_data = [
        {'name': '华夏中证500指数增强A', 'amount': 259469.63, 'profit': 94469.69},
        {'name': '银华鑫盛灵活配置混合(LOF)A', 'amount': 202204.78, 'profit': 29704.78},
        {'name': '博时稳健回报债券(LOF)C', 'amount': 114807.42, 'profit': 14807.42},
        {'name': '招商瑞信稳健配置C', 'amount': 111674.48, 'profit': 11674.48},
        {'name': '华泰柏瑞景气汇选三年持有期混合A', 'amount': 67730.12, 'profit': 17730.12},
        {'name': '华泰柏瑞鼎利混合C', 'amount': 52567.55, 'profit': 7521.17},
    ]
    
    return image1_data, image2_data

def verify_total_profit_new():
    """验证新图片的累计持仓收益"""
    # 提取数据
    image1_data, image2_data = extract_new_images_data()
    
    # 计算图片1总和
    total1_amount = 0
    total1_profit = 0
    for item in image1_data:
        total1_amount += item['amount']
        total1_profit += item['profit']
    
    # 计算图片2总和
    total2_amount = 0
    total2_profit = 0
    for item in image2_data:
        total2_amount += item['amount']
        total2_profit += item['profit']
    
    # 计算总计
    grand_total_amount = total1_amount + total2_amount
    grand_total_profit = total1_profit + total2_profit
    
    print("\n=" * 100)
    print("新图片数据汇总")
    print("=" * 100)
    
    print(f"图片1 持有金额: ¥{total1_amount:,.2f}")
    print(f"图片1 持仓收益: ¥{total1_profit:,.2f}")
    print(f"图片1 收益率: {(total1_profit / (total1_amount - total1_profit)):.2%}")
    print()
    print(f"图片2 持有金额: ¥{total2_amount:,.2f}")
    print(f"图片2 持仓收益: ¥{total2_profit:,.2f}")
    print(f"图片2 收益率: {(total2_profit / (total2_amount - total2_profit)):.2%}")
    print()
    print(f"总计 持有金额: ¥{grand_total_amount:,.2f}")
    print(f"总计 持仓收益: ¥{grand_total_profit:,.2f}")
    print(f"总计 收益率: {(grand_total_profit / (grand_total_amount - grand_total_profit)):.2%}")
    
    # 对比官方数据
    print("\n=" * 100)
    print("与官方数据对比")
    print("=" * 100)
    
    official_profit_image1 = 165174.75  # 图片1顶部显示
    official_profit_image2 = 175907.20  # 图片2顶部显示
    official_total = official_profit_image1 + official_profit_image2
    
    print(f"官方图片1持仓收益: ¥{official_profit_image1:,.2f}")
    print(f"官方图片2持仓收益: ¥{official_profit_image2:,.2f}")
    print(f"官方总计持仓收益: ¥{official_total:,.2f}")
    print()
    print(f"提取总计持仓收益: ¥{grand_total_profit:,.2f}")
    print(f"差异: ¥{abs(official_total - grand_total_profit):,.2f}")
    print(f"差异率: {abs((official_total - grand_total_profit) / official_total):.2%}")
    
    # 详细对比
    print("\n=" * 100)
    print("详细对比")
    print("=" * 100)
    
    print("图片1详细数据:")
    print("-" * 80)
    for item in image1_data:
        print(f"{item['name']:<30} | ¥{item['amount']:>10.2f} | ¥{item['profit']:>10.2f}")
    
    print("\n图片2详细数据:")
    print("-" * 80)
    for item in image2_data:
        print(f"{item['name']:<30} | ¥{item['amount']:>10.2f} | ¥{item['profit']:>10.2f}")

def main():
    """主函数"""
    verify_total_profit_new()

if __name__ == '__main__':
    main()
