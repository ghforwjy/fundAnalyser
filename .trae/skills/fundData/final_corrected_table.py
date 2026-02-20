"""
生成修正后的最终表格
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

# 最终修正的基金数据
final_funds = [
    {'code': '018957', 'name': '中航机遇领航混合发起C', 'amount': '25,956.71', 'profit': '+16,456.71', 'rate': '+173.23%'},
    {'code': '022853', 'name': '中航优选领航混合发起C', 'amount': '12,803.50', 'profit': '+4,103.50', 'rate': '+47.16%'},
    {'code': '021489', 'name': '中航趋势领航混合发起A', 'amount': '7,104.70', 'profit': '+2,684.70', 'rate': '+60.76%'},
    {'code': '021492', 'name': '中航远见领航混合发起C', 'amount': '11,506.50', 'profit': '+2,613.24', 'rate': '+29.39%'},
    {'code': '024389', 'name': '中航智选领航混合发起C', 'amount': '10,688.38', 'profit': '+4,688.38', 'rate': '+78.08%'},
    {'code': '024291', 'name': '中航月月鑫30天持有期债券C', 'amount': '10.03', 'profit': '+0.03', 'rate': '+0.26%'},
    {'code': '024290', 'name': '中航月月鑫30天持有期债券A', 'amount': '10.01', 'profit': '+0.01', 'rate': '+0.12%'},
    {'code': '001052', 'name': '华夏中证500ETF联接A', 'amount': '16,297.49', 'profit': '+7,797.49', 'rate': '+91.76%'},
    {'code': '486001', 'name': '工银全球股票(QDII)人民币', 'amount': '32,979.62', 'profit': '+18,577.96', 'rate': '+128.81%'},
    {'code': '001595', 'name': '天弘中证银行ETF联接C', 'amount': '63,536.79', 'profit': '+30,036.79', 'rate': '+89.66%'},
    {'code': '000143', 'name': '鹏华双债加利债券A', 'amount': '388,704.74', 'profit': '+90,596.94', 'rate': '+30.42%'},
    {'code': '006331', 'name': '中银国有企业债C', 'amount': '31,449.00', 'profit': '+1,449.00', 'rate': '~4.6%'},
    {'code': '007994', 'name': '华夏中证500指数增强A', 'amount': '259,469.63', 'profit': '94,469.69', 'rate': '+57.25%'},
    {'code': '501022', 'name': '银华鑫盛灵活配置混合(LOF)A', 'amount': '202,204.78', 'profit': '29,704.78', 'rate': '+17.22%'},
    {'code': '160514', 'name': '博时稳健回报债券(LOF)C', 'amount': '114,807.42', 'profit': '14,807.42', 'rate': '+14.81%'},
    {'code': '009424', 'name': '招商瑞信稳健配置混合C', 'amount': '111,674.48', 'profit': '11,674.48', 'rate': '+11.67%'},
    {'code': '013431', 'name': '华泰柏瑞景气汇选三年持有期混合A', 'amount': '67,730.12', 'profit': '17,730.12', 'rate': '+35.46%'},
    {'code': '004011', 'name': '华泰柏瑞鼎利灵活配置混合C', 'amount': '52,567.55', 'profit': '7,521.17', 'rate': '+16.69%'},
]

def print_final_table():
    """打印最终修正的表格"""
    print("=" * 120)
    print("最终修正版 - 基金盈亏数据汇总表")
    print("=" * 120)
    
    # 表头
    print(f"{'序号':<5} {'基金代码':<10} {'基金名称':<30} {'持有金额':<12} {'持仓收益':<12} {'收益率':<10}")
    print("-" * 120)
    
    # 数据行
    for i, fund in enumerate(final_funds, 1):
        print(f"{i:<5} {fund['code']:<10} {fund['name']:<30} {fund['amount']:<12} {fund['profit']:<12} {fund['rate']:<10}")
    
    print("=" * 120)
    
    # 统计
    print(f"\n统计: 共 {len(final_funds)} 只基金")
    print("-" * 40)
    
    # 计算总金额和总收益
    total_amount = 0
    total_profit = 0
    
    for fund in final_funds:
        # 提取金额数字
        amount_str = fund['amount'].replace(',', '')
        if amount_str.replace('.', '').isdigit():
            total_amount += float(amount_str)
        
        # 提取收益数字
        profit_str = fund['profit'].replace('+', '').replace(',', '')
        if profit_str.replace('.', '').isdigit():
            total_profit += float(profit_str)
    
    print(f"总持有金额: ¥{total_amount:,.2f}")
    print(f"总持仓收益: ¥{total_profit:,.2f}")
    if total_amount > 0:
        overall_rate = (total_profit / (total_amount - total_profit)) * 100
        print(f"总收益率: {overall_rate:.2f}%")
    
    print("=" * 120)

if __name__ == '__main__':
    print_final_table()
