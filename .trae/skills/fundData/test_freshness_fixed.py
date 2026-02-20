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
    total_funds = len(funds)
    update_needed_count = 0
    
    for i, fund in enumerate(funds, 1):
        fund_code = fund['fund_code']
        fund_name = fund['fund_name']
        metrics_update_time = fund.get('metrics_update_time')
        
        if i <= 10:  # 只打印前10只基金的详细信息
            print(f'[{i}] {fund_code} - {fund_name}')
            print(f'  metrics_update_time: {metrics_update_time}')
        
        need_update = False
        if metrics_update_time:
            try:
                # 测试时间格式解析
                update_time = datetime.datetime.strptime(metrics_update_time, '%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.now()
                time_diff = now - update_time
                hours_diff = time_diff.total_seconds() / 3600
                
                if i <= 10:
                    print(f'  时间差: {hours_diff:.1f} 小时')
                    print(f'  是否需要更新: {hours_diff > 12}')
                
                if hours_diff > 12:
                    need_update = True
                    update_needed_count += 1
            except Exception as e:
                if i <= 10:
                    print(f'  格式错误: {e}')
                    print(f'  会触发更新: 是')
                need_update = True
                update_needed_count += 1
        else:
            if i <= 10:
                print(f'  字段缺失: 是')
                print(f'  会触发更新: 是')
            need_update = True
            update_needed_count += 1
        
        if i <= 10:
            print()
    
    print(f'\n风险指标更新统计:')
    print(f'总基金数: {total_funds}')
    print(f'需要更新的基金数: {update_needed_count}')
    print(f'更新率: {update_needed_count/total_funds*100:.1f}%')
else:
    print('没有找到组合')

# 测试持仓数据的fund_data_meta表
print('\n=== 测试持仓数据新鲜度机制 ===')
from database import get_db_connection

if portfolios and funds:
    test_funds = funds[:3]  # 只测试前3只基金
    total_holding_checks = 0
    holding_update_needed = 0
    
    for fund in test_funds:
        fund_code = fund['fund_code']
        fund_name = fund['fund_name']
        meta_key = f'holdings_{fund_code}'
        
        print(f'\n测试基金: {fund_code} - {fund_name}')
        print(f'Meta键: {meta_key}')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查该基金的持仓记录
            cursor.execute('''
                SELECT * FROM fund_data_meta 
                WHERE table_name = ?
            ''', (meta_key,))
            meta = cursor.fetchone()
            
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            need_update = True
            
            if meta:
                # 使用索引访问sqlite3.Row对象
                last_sync_time = meta[1]  # last_sync_time是第二个字段
                print(f'  找到记录，最后同步时间: {last_sync_time}')
                
                if last_sync_time:
                    try:
                        sync_date = last_sync_time.split(' ')[0]  # 提取日期部分
                        print(f'  同步日期: {sync_date}')
                        print(f'  今天日期: {today_str}')
                        if sync_date == today_str:
                            print(f'  今天已同步，不需要更新')
                            need_update = False
                        else:
                            print(f'  今天未同步，需要更新')
                            need_update = True
                    except Exception as e:
                        print(f'  时间格式错误: {e}')
                        need_update = True
            else:
                print('  未找到记录，需要更新')
                need_update = True
            
            # 检查fund_stock_holding表是否存在该基金的持仓数据
            cursor.execute('''
                SELECT COUNT(*) as count, MAX(quarter) as latest_quarter 
                FROM fund_stock_holding 
                WHERE fund_code = ?
            ''', (fund_code,))
            holding_data = cursor.fetchone()
            if holding_data:
                count = holding_data[0]  # 使用索引访问
                latest_quarter = holding_data[1]
                print(f'  持仓记录数量: {count}')
                print(f'  最新季度: {latest_quarter}')
            else:
                print('  无持仓数据')
            
            total_holding_checks += 1
            if need_update:
                holding_update_needed += 1
    
    print(f'\n持仓数据更新统计:')
    print(f'测试基金数: {total_holding_checks}')
    print(f'需要更新的基金数: {holding_update_needed}')
    print(f'更新率: {holding_update_needed/total_holding_checks*100:.1f}%')

# 测试净值数据的新鲜度检查
print('\n=== 测试净值数据新鲜度机制 ===')
from smart_fund_data import SmartFundData

if portfolios and funds:
    test_funds = funds[:3]  # 只测试前3只基金
    total_nav_checks = 0
    nav_update_needed = 0
    
    for fund in test_funds:
        fund_code = fund['fund_code']
        fund_name = fund['fund_name']
        
        print(f'\n测试基金: {fund_code} - {fund_name}')
        
        smart = SmartFundData()
        
        # 测试_is_nav_stale方法
        is_stale = smart._is_nav_stale(fund_code)
        print(f'  是否需要更新: {is_stale}')
        
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
                latest_date = nav_data[0]  # 使用索引访问
                update_time = nav_data[1]
                print(f'  最新净值日期: {latest_date}')
                print(f'  最新更新时间: {update_time}')
            else:
                print(f'  无净值数据')
        
        total_nav_checks += 1
        if is_stale:
            nav_update_needed += 1
    
    print(f'\n净值数据更新统计:')
    print(f'测试基金数: {total_nav_checks}')
    print(f'需要更新的基金数: {nav_update_needed}')
    print(f'更新率: {nav_update_needed/total_nav_checks*100:.1f}%')
