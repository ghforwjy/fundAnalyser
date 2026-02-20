"""
测试导入接口
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_manager import import_profit_data, import_profit_data_from_table, list_portfolios

def test_import_api():
    """测试导入接口"""
    print("=" * 80)
    print("测试导入接口")
    print("=" * 80)
    
    # 获取持仓组合ID
    portfolios = list_portfolios()
    portfolio_id = None
    
    for portfolio in portfolios:
        if portfolio['name'] == '持仓组合':
            portfolio_id = portfolio['id']
            print(f"✅ 找到持仓组合: ID = {portfolio_id}")
            break
    
    if not portfolio_id:
        print("❌ 未找到持仓组合")
        return
    
    # 测试数据
    test_data = [
        {
            'fund_code': '000001',
            'fund_name': '华夏成长混合',
            'current_value': 10000.00,
            'profit_loss': 1000.00
        },
        {
            'fund_code': '000002',
            'fund_name': '华夏成长混合A',
            'current_value': 5000.00,
            'profit_loss': 500.00
        }
    ]
    
    print("\n📤 测试 import_profit_data 接口...")
    result = import_profit_data(
        portfolio_id=portfolio_id,
        profit_data=test_data,
        import_mode='overwrite',
        source_type='test'
    )
    
    print(f"✅ 导入结果: {result}")
    
    # 测试表格导入
    print("\n📤 测试 import_profit_data_from_table 接口...")
    table_data = [
        {'code': '000003', 'name': '华夏成长混合C', 'amount': 8000, 'profit': 800},
        {'code': '000004', 'name': '华夏成长混合D', 'amount': 6000, 'profit': 600}
    ]
    
    result_table = import_profit_data_from_table(
        table_data=table_data,
        portfolio_id=portfolio_id,
        import_mode='overwrite'
    )
    
    print(f"✅ 表格导入结果: {result_table}")
    
    print("\n=" * 80)
    print("测试完成!")
    print("=" * 80)

if __name__ == '__main__':
    test_import_api()
