import sys
sys.path.append('d:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')
from portfolio_manager import list_portfolios, list_portfolio_funds
import datetime

# 测试风险指标的metrics_update_time字段
print('=== 测试风险指标新鲜度机制 ===')
portfolios = list_portfolios()
if portfolios:
    portfolio_id = portfolios[0]['id']
    print(f'测试组合: ID={portfolio_id}, 名称={portfolios[0]["name"]}')
    
    funds = list_portfolio_funds(portfolio_id)
    print(f'基金数量: {len(funds)}')
    
    # 检查metrics_update_time字段
    print('\n检查metrics_update_time字段:')
    for i, fund in enumerate(funds[:10], 1):  # 只检查前10只基金
        fund_code = fund['fund_code']
        fund_name = fund['fund_name']
        metrics_update_time = fund.get('metrics_update_time')
        
        print(f'[{i}] {fund_code} - {fund_name}')
        print(f'  metrics_update_time: {metrics_update_time}')
        
        if metrics_update_time:
            try:
                # 测试时间格式解析
                update_time = datetime.datetime.strptime(metrics_update_time, '%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.now()
                time_diff = now - update_time
                hours_diff = time_diff.total_seconds() / 3600
                print(f'  时间差: {hours_diff:.1f} 小时')
                print(f'  是否需要更新: {hours_diff > 12}')
            except Exception as e:
                print(f'  格式错误: {e}')
                print(f'  会触发更新: 是')
        else:
            print(f'  字段缺失: 是')
            print(f'  会触发更新: 是')
        print()
else:
    print('没有找到组合')

# 测试持仓数据的fund_data_meta表
print('=== 测试持仓数据新鲜度机制 ===')
from database import get_db_connection

if portfolios:
    fund_code = funds[0]['fund_code'] if funds else '000001'
    meta_key = f'holdings_{fund_code}'
    
    print(f'测试基金: {fund_code}')
    print(f'Meta键: {meta_key}')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查fund_data_meta表结构
        print('\n检查fund_data_meta表结构:')
        cursor.execute('PRAGMA table_info(fund_data_meta)')
        columns = cursor.fetchall()
        for col in columns:
            print(f'  {col["name"]} ({col["type"]})')
        
        # 检查该基金的持仓记录
        print('\n检查fund_data_meta表记录:')
        cursor.execute('''
            SELECT * FROM fund_data_meta 
            WHERE table_name = ?
        ''', (meta_key,))
        meta = cursor.fetchone()
        if meta:
            print(f'  找到记录: {dict(meta)}')
            last_sync_time = meta.get('last_sync_time')
            if last_sync_time:
                try:
                    sync_time = datetime.datetime.strptime(last_sync_time, '%Y-%m-%d %H:%M:%S')
                    today = datetime.date.today()
                    sync_date = sync_time.date()
                    print(f'  同步日期: {sync_date}')
                    print(f'  今天日期: {today}')
                    print(f'  是否今天同步: {sync_date == today}')
                except Exception as e:
                    print(f'  时间格式错误: {e}')
        else:
            print('  未找到记录，会触发更新')
        
        # 检查fund_stock_holding表是否存在该基金的持仓数据
        print('\n检查fund_stock_holding表数据:')
        cursor.execute('''
            SELECT COUNT(*) as count, MAX(quarter) as latest_quarter 
            FROM fund_stock_holding 
            WHERE fund_code = ?
        ''', (fund_code,))
        holding_data = cursor.fetchone()
        if holding_data:
            print(f'  持仓记录数量: {holding_data["count"]}')
            print(f'  最新季度: {holding_data["latest_quarter"]}')
        else:
            print('  无持仓数据，会触发更新')

# 测试净值数据的新鲜度检查
print('\n=== 测试净值数据新鲜度机制 ===')
from smart_fund_data import SmartFundData

if funds:
    test_fund = funds[0]
    fund_code = test_fund['fund_code']
    fund_name = test_fund['fund_name']
    
    print(f'测试基金: {fund_code} - {fund_name}')
    
    smart = SmartFundData()
    
    # 测试_is_nav_stale方法
    print('\n测试_is_nav_stale方法:')
    is_stale = smart._is_nav_stale(fund_code)
    print(f'基金 {fund_code} 是否需要更新: {is_stale}')
    
    # 检查净值数据
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(nav_date) as latest_date, MAX(update_time) as update_time
            FROM fund_nav
            WHERE fund_code = ?
        ''', (fund_code,))
        nav_data = cursor.fetchone()
        if nav_data:
            print(f'\n净值数据:')
            print(f'  最新净值日期: {nav_data["latest_date"]}')
            print(f'  最新更新时间: {nav_data["update_time"]}')
        else:
            print('\n无净值数据')
