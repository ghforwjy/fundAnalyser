import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_manager import import_profit_data

# 组合ID
portfolio_id = 2

# 4只基金的盈亏数据（从图片识别修正）
profit_data = [
    {
        'fund_code': '022853',
        'fund_name': '中航优选领航混合发起C',
        'current_value': 13503.50,  # 成本8700 + 盈亏4803.5
        'profit_loss': 4803.5
    },
    {
        'fund_code': '021489',
        'fund_name': '中航趋势领航混合发起A',
        'current_value': 7104.70,  # 成本4420 + 盈亏2684.7
        'profit_loss': 2684.7
    },
    {
        'fund_code': '021492',
        'fund_name': '中航远见领航混合发起C',
        'current_value': 10906.50,  # 成本8893.26 + 盈亏2013.24
        'profit_loss': 2013.24
    },
    {
        'fund_code': '024389',
        'fund_name': '中航智选领航混合发起C',
        'current_value': 6688.38,  # 成本6000 + 盈亏688.38
        'profit_loss': 688.38
    }
]

print("=== 更新4只基金的盈亏数据 ===")
print(f"组合ID: {portfolio_id}")
print(f"导入模式: 覆盖模式 (overwrite)")
print()

for fund in profit_data:
    print(f"基金代码: {fund['fund_code']}")
    print(f"基金名称: {fund['fund_name']}")
    print(f"当前市值: {fund['current_value']}")
    print(f"盈亏金额: {fund['profit_loss']}")
    print()

# 调用导入函数
result = import_profit_data(
    portfolio_id=portfolio_id,
    profit_data=profit_data,
    import_mode='overwrite',  # 覆盖模式
    source_type='manual_correction'  # 来源：手动修正
)

print("=== 导入结果 ===")
print(f"成功: {result.get('success', False)}")
print(f"消息: {result.get('message', '')}")
print(f"更新记录数: {result.get('updated_count', 0)}")

if result.get('success'):
    print("\n✅ 盈亏数据更新成功！")
else:
    print("\n❌ 盈亏数据更新失败！")
    if 'errors' in result:
        print("错误详情:")
        for error in result['errors']:
            print(f"  - {error}")
