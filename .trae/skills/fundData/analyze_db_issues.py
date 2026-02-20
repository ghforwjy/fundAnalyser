import sqlite3
import json
from datetime import datetime

# 连接fundData skill的数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== 分析数据库问题 ===")

print("\n1. 检查portfolio_fund表中的记录数")
try:
    c.execute("SELECT COUNT(*) as count FROM portfolio_fund")
    total_count = c.fetchone()['count']
    print(f"总记录数: {total_count}")
except Exception as e:
    print(f"获取记录数失败: {e}")

print("\n2. 检查重复的基金代码")
try:
    c.execute("""
        SELECT fund_code, COUNT(*) as count 
        FROM portfolio_fund 
        GROUP BY fund_code 
        HAVING COUNT(*) > 1
    """)
    duplicates = c.fetchall()
    if duplicates:
        print(f"找到 {len(duplicates)} 个重复的基金代码:")
        for dup in duplicates:
            print(f"  {dup['fund_code']}: {dup['count']} 条记录")
    else:
        print("没有找到重复的基金代码")
except Exception as e:
    print(f"检查重复记录失败: {e}")

print("\n3. 分析净值为0的基金")
try:
    c.execute("""
        SELECT pf.fund_code, pf.fund_name, fn.unit_nav, fn.nav_date
        FROM portfolio_fund pf
        LEFT JOIN (
            SELECT fund_code, unit_nav, nav_date
            FROM fund_nav
            WHERE (fund_code, nav_date) IN (
                SELECT fund_code, MAX(nav_date)
                FROM fund_nav
                GROUP BY fund_code
            )
        ) fn ON pf.fund_code = fn.fund_code
        WHERE fn.unit_nav = 0 OR fn.unit_nav IS NULL
    """)
    zero_nav_funds = c.fetchall()
    print(f"找到 {len(zero_nav_funds)} 只基金净值为0或为空:")
    for fund in zero_nav_funds:
        print(f"  {fund['fund_code']} - {fund['fund_name']}: 净值={fund['unit_nav']}, 日期={fund['nav_date']}")
except Exception as e:
    print(f"分析净值失败: {e}")

print("\n4. 检查fund_nav表中是否存在这些基金的数据")
try:
    # 获取净值为0的基金代码
    c.execute("""
        SELECT DISTINCT pf.fund_code
        FROM portfolio_fund pf
        LEFT JOIN (
            SELECT fund_code, unit_nav
            FROM fund_nav
            WHERE (fund_code, nav_date) IN (
                SELECT fund_code, MAX(nav_date)
                FROM fund_nav
                GROUP BY fund_code
            )
        ) fn ON pf.fund_code = fn.fund_code
        WHERE fn.unit_nav = 0 OR fn.unit_nav IS NULL
    """)
    zero_nav_codes = [row['fund_code'] for row in c.fetchall()]
    
    print(f"\n检查 {len(zero_nav_codes)} 只基金的nav数据:")
    for fund_code in zero_nav_codes:
        c.execute("SELECT COUNT(*) as count FROM fund_nav WHERE fund_code = ?", (fund_code,))
        count = c.fetchone()['count']
        print(f"  {fund_code}: {count} 条净值记录")
        
        # 查看最新的几条记录
        if count > 0:
            c.execute("""
                SELECT nav_date, unit_nav 
                FROM fund_nav 
                WHERE fund_code = ? 
                ORDER BY nav_date DESC 
                LIMIT 3
            """, (fund_code,))
            latest_navs = c.fetchall()
            for nav in latest_navs:
                print(f"    {nav['nav_date']}: {nav['unit_nav']}")
except Exception as e:
    print(f"检查nav数据失败: {e}")

print("\n5. 分析成本数据与前端显示的差异")
try:
    # 计算当前持仓的总成本（排除净值为0的基金）
    c.execute("""
        SELECT 
            SUM(CASE WHEN amount > 0 THEN amount ELSE shares * buy_nav END) as total_cost,
            COUNT(*) as fund_count
        FROM portfolio_fund pf
        LEFT JOIN (
            SELECT fund_code, unit_nav
            FROM fund_nav
            WHERE (fund_code, nav_date) IN (
                SELECT fund_code, MAX(nav_date)
                FROM fund_nav
                GROUP BY fund_code
            )
        ) fn ON pf.fund_code = fn.fund_code
        WHERE fn.unit_nav > 0
    """)
    result = c.fetchone()
    if result:
        valid_fund_cost = result['total_cost'] or 0
        valid_fund_count = result['fund_count'] or 0
        print(f"\n有效基金（净值>0）的成本: {valid_fund_cost}")
        print(f"有效基金数量: {valid_fund_count}")
        
        # 与前端显示的总成本对比
        frontend_cost = 1146110.68
        print(f"前端显示的总成本: {frontend_cost}")
        print(f"差异: {valid_fund_cost - frontend_cost}")
    
    # 计算所有基金的成本
    c.execute("""
        SELECT 
            SUM(CASE WHEN amount > 0 THEN amount ELSE shares * buy_nav END) as total_cost,
            COUNT(*) as fund_count
        FROM portfolio_fund
    """)
    all_result = c.fetchone()
    if all_result:
        all_fund_cost = all_result['total_cost'] or 0
        all_fund_count = all_result['fund_count'] or 0
        print(f"\n所有基金的总成本: {all_fund_cost}")
        print(f"所有基金数量: {all_fund_count}")
except Exception as e:
    print(f"分析成本数据失败: {e}")

print("\n6. 检查是否有交易记录或卖出记录")
try:
    # 检查是否有交易记录表
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%transaction%';")
    transaction_tables = c.fetchall()
    if transaction_tables:
        print(f"\n找到交易相关表: {[t[0] for t in transaction_tables]}")
        for table in transaction_tables:
            c.execute(f"SELECT COUNT(*) as count FROM {table[0]}")
            count = c.fetchone()['count']
            print(f"  {table[0]}: {count} 条记录")
    else:
        print("\n没有找到交易相关表")
    
    # 检查portfolio表
    c.execute("SELECT COUNT(*) as count FROM portfolio")
    portfolio_count = c.fetchone()['count']
    print(f"\nportfolio表记录数: {portfolio_count}")
    
    if portfolio_count > 0:
        c.execute("SELECT * FROM portfolio")
        portfolios = c.fetchall()
        print("portfolio列表:")
        for portfolio in portfolios:
            print(f"  ID: {portfolio['id']}, 名称: {portfolio['name']}")
            
            # 检查每个组合的基金数量
            c.execute("SELECT COUNT(*) as count FROM portfolio_fund WHERE portfolio_id = ?", (portfolio['id'],))
            fund_count = c.fetchone()['count']
            print(f"    基金数量: {fund_count}")
except Exception as e:
    print(f"检查交易记录失败: {e}")

print("\n7. 计算每个组合的盈亏")
try:
    c.execute("SELECT DISTINCT portfolio_id FROM portfolio_fund")
    portfolio_ids = [row['portfolio_id'] for row in c.fetchall()]
    
    print(f"\n分析 {len(portfolio_ids)} 个组合的盈亏:")
    for portfolio_id in portfolio_ids:
