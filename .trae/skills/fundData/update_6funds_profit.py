import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_manager import import_profit_data

# 组合ID
portfolio_id = 2

# 6只基金的盈亏数据（用户指定）
profit_data = [
    {
        'fund_code': '001052',
        'fund_name': '华夏中证500ETF联接A',
        'current_value': 16297.49,  # 成本8500 + 盈亏7797.49
        'profit_loss': 7797.49
    },
    {
        'fund_code': '001595',
        'fund_name': '天弘中证银行ETF联接C',
        'current_value': 53524.79,  # 成本33500 + 盈亏20024.79
        'profit_loss': 20024.79
    },
    {
        'fund_code': '007994',
        'fund_name': '华夏中证500指数增强A',
        'current_value': 259469.57,  # 成本164999.94 + 盈亏94469.63
        'profit_loss': 94469.63
    },
    {
        'fund_code': '024290',
        'fund_name': '中航月月鑫30天持有期债券A',
        'current_value': 10.01,  # 成本10 + 盈亏0.01
        'profit_loss': 0.01
    },
    {
        'fund_code': '486001',
        'fund_name': '工银全球股票(QDII)人民币',
        'current_value': 32999.62,  # 成本14401.66 + 盈亏18597.96
        'profit_loss': 18597.96
    }
]

print("=== 更新6只基金的盈亏数据 ===")
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
