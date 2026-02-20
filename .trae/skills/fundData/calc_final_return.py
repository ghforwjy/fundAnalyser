from smart_fund_data import get_fund_nav
from portfolio_manager import list_portfolios, list_portfolio_funds
from database import get_db_connection
from datetime import datetime, timedelta

def get_nav_on_date(fund_code, target_date):
    """获取指定日期的净值"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT unit_nav FROM fund_nav 
            WHERE fund_code = ? AND nav_date <= ?
            ORDER BY nav_date DESC LIMIT 1
        ''', (fund_code, target_date))
        row = cursor.fetchone()
        return float(row['unit_nav']) if row else None

portfolios = list_portfolios()
for p in portfolios:
    print('组合:', p['name'], '(ID:', p['id'], ')')
    funds = list_portfolio_funds(p['id'])
    
    today = datetime.now().strftime('%Y-%m-%d')
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"\n计算日期: {one_month_ago} -> {today}")
    print("-" * 120)
    
    total_market_value_before = 0
    total_market_value_now = 0
    
    print(f"{'基金代码':<10} {'基金名称':<30} {'份额':>12} {'一个月前净值':>10} {'当前净值':>10} {'一个月前市值':>14} {'当前市值':>14}")
    print("-" * 120)
    
    for f in funds:
        fund_code = f['fund_code']
        fund_name = f.get('fund_name', '')[:25]
        shares = f.get('shares') or 0
        
        if shares == 0:
            continue
        
        nav_before = get_nav_on_date(fund_code, one_month_ago)
        nav_now = get_nav_on_date(fund_code, today)
        
        if nav_before and nav_now:
            mv_before = shares * nav_before
            mv_now = shares * nav_now
            print(f"{fund_code:<10} {fund_name:<30} {shares:>12.2f} {nav_before:>10.4f} {nav_now:>10.4f} {mv_before:>14.2f} {mv_now:>14.2f}")
            total_market_value_before += mv_before
            total_market_value_now += mv_now
    
    print("-" * 120)
    print(f"{'合计':<10} {'':<30} {'':>12} {'':>10} {'':>10} {total_market_value_before:>14.2f} {total_market_value_now:>14.2f}")
    
    if total_market_value_before > 0:
        portfolio_return = (total_market_value_now - total_market_value_before) / total_market_value_before * 100
        profit = total_market_value_now - total_market_value_before
        print(f"\n组合近1月收益率: {portfolio_return:.2f}%")
        print(f"组合近1月盈亏: {profit:,.2f} 元")
