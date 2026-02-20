#!/usr/bin/env python3
"""
调试工银全球股票(QDII)人民币(486001)的数据问题
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from database import get_db_connection

def debug_fund_data(fund_code='486001', portfolio_id=1):
    """调试指定基金的数据"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        print(f"=== 基金 {fund_code} 数据调试 ===\n")
        
        # 1. 查询portfolio_fund表
        print("1. portfolio_fund 表数据:")
        cursor.execute('''
            SELECT * FROM portfolio_fund 
            WHERE fund_code = ? AND portfolio_id = ?
        ''', (fund_code, portfolio_id))
        row = cursor.fetchone()
        if row:
            for key in row.keys():
                print(f"   {key}: {row[key]}")
        else:
            print("   未找到记录")
        
        # 2. 查询最新净值
        print("\n2. fund_nav 表最新净值:")
        cursor.execute('''
            SELECT nav_date, unit_nav, accumulate_nav 
            FROM fund_nav 
            WHERE fund_code = ? 
            ORDER BY nav_date DESC LIMIT 1
        ''', (fund_code,))
        nav_row = cursor.fetchone()
        if nav_row:
            print(f"   日期: {nav_row['nav_date']}")
            print(f"   单位净值: {nav_row['unit_nav']}")
            print(f"   累计净值: {nav_row['accumulate_nav']}")
        else:
            print("   未找到净值记录")
        
        # 3. 手动计算验证
        print("\n3. 手动计算验证:")
        if row and nav_row:
            shares = row['shares'] or 0
            buy_nav = row['buy_nav'] or 0
            cost_nav = row['cost_nav'] or 0
            latest_nav = nav_row['unit_nav'] or 0
            
            print(f"   份额(shares): {shares}")
            print(f"   买入净值(buy_nav): {buy_nav}")
            print(f"   成本净值(cost_nav): {cost_nav}")
            print(f"   最新净值(latest_nav): {latest_nav}")
            
            market_value = shares * latest_nav
            print(f"\n   市值 = {shares} × {latest_nav} = {market_value:.2f}")
            
            if buy_nav > 0:
                cost_by_buy_nav = shares * buy_nav
                profit_by_buy_nav = market_value - cost_by_buy_nav
                profit_rate_by_buy_nav = (latest_nav - buy_nav) / buy_nav * 100
                print(f"\n   使用 buy_nav 计算:")
                print(f"   成本 = {shares} × {buy_nav} = {cost_by_buy_nav:.2f}")
                print(f"   盈亏 = {market_value:.2f} - {cost_by_buy_nav:.2f} = {profit_by_buy_nav:.2f}")
                print(f"   收益率 = ({latest_nav} - {buy_nav}) / {buy_nav} × 100 = {profit_rate_by_buy_nav:.2f}%")
            
            if cost_nav > 0 and cost_nav != buy_nav:
                cost_by_cost_nav = shares * cost_nav
                profit_by_cost_nav = market_value - cost_by_cost_nav
                profit_rate_by_cost_nav = (latest_nav - cost_nav) / cost_nav * 100
                print(f"\n   使用 cost_nav 计算:")
                print(f"   成本 = {shares} × {cost_nav} = {cost_by_cost_nav:.2f}")
                print(f"   盈亏 = {market_value:.2f} - {cost_by_cost_nav:.2f} = {profit_by_cost_nav:.2f}")
                print(f"   收益率 = ({latest_nav} - {cost_nav}) / {cost_nav} × 100 = {profit_rate_by_cost_nav:.2f}%")
        
        # 4. 查询盈亏导入历史
        print("\n4. profit_import 历史记录:")
        cursor.execute('''
            SELECT * FROM profit_import 
            WHERE fund_code = ? AND portfolio_id = ?
            ORDER BY import_date DESC LIMIT 5
        ''', (fund_code, portfolio_id))
        import_rows = cursor.fetchall()
        if import_rows:
            for i, import_row in enumerate(import_rows, 1):
                print(f"   记录{i}: {dict(import_row)}")
        else:
            print("   无导入记录")

if __name__ == '__main__':
    # 调试工银全球股票
    debug_fund_data('486001', 1)
