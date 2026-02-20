import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('fund.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== 检查数据库结构 ===")

# 检查portfolio_fund表结构
try:
    c.execute("PRAGMA table_info(portfolio_fund)")
    columns = c.fetchall()
    print("\nportfolio_fund表结构:")
    for col in columns:
        print(f"{col['name']} ({col['type']})")
except Exception as e:
    print(f"获取表结构失败: {e}")

print("\n=== 检查组合持仓数据 ===")

# 检查portfolio_fund表数据
try:
    c.execute("SELECT * FROM portfolio_fund LIMIT 20")
    rows = c.fetchall()
    print(f"\n找到 {len(rows)} 条持仓记录:")
    for i, row in enumerate(rows):
        print(f"\n记录 {i+1}:")
        for key in row.keys():
            print(f"  {key}: {row[key]}")
except Exception as e:
    print(f"获取持仓数据失败: {e}")

print("\n=== 检查基金净值数据 ===")

# 检查fund_nav表最新数据
try:
    # 获取所有持仓的基金代码
    c.execute("SELECT DISTINCT fund_code FROM portfolio_fund")
    fund_codes = [row['fund_code'] for row in c.fetchall()]
    
    print(f"\n检查 {len(fund_codes)} 只基金的最新净值:")
    for fund_code in fund_codes:
        c.execute("""
            SELECT fund_code, nav_date, unit_nav, accum_nav
            FROM fund_nav 
            WHERE fund_code = ?
            ORDER BY nav_date DESC
            LIMIT 1
        """, (fund_code,))
        nav_row = c.fetchone()
        if nav_row:
            print(f"{fund_code}: 日期={nav_row['nav_date']}, 单位净值={nav_row['unit_nav']}")
        else:
            print(f"{fund_code}: 无净值数据")
except Exception as e:
    print(f"获取净值数据失败: {e}")

print("\n=== 计算实际盈亏 ===")

# 计算实际盈亏
try:
    c.execute("""
        SELECT 
            pf.fund_code,
            pf.fund_name,
            pf.shares,
            pf.buy_nav,
            pf.amount,
            fn.unit_nav as latest_nav
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
    """)
    
    rows = c.fetchall()
    total_cost = 0
    total_market_value = 0
    total_profit = 0
    
    print("\n每只基金的计算:")
    for row in rows:
        fund_code = row['fund_code']
        fund_name = row['fund_name']
        shares = row['shares'] or 0
        buy_nav = row['buy_nav'] or 0
        amount = row['amount'] or 0
        latest_nav = row['latest_nav'] or 0
        
        # 计算成本
        if amount > 0:
            cost = amount
        elif shares > 0 and buy_nav > 0:
            cost = shares * buy_nav
        else:
            cost = 0
        
        # 计算市值
        market_value = shares * latest_nav
        
        # 计算盈亏
        profit = market_value - cost
        
        total_cost += cost
        total_market_value += market_value
        total_profit += profit
        
        print(f"\n{fund_code} - {fund_name}:")
        print(f"  份额: {shares}")
        print(f"  买入净值: {buy_nav}")
        print(f"  买入金额: {amount}")
        print(f"  最新净值: {latest_nav}")
        print(f"  成本: {cost}")
        print(f"  市值: {market_value}")
        print(f"  盈亏: {profit}")
    
    print(f"\n=== 汇总计算 ===")
    print(f"总成本: {total_cost}")
    print(f"总市值: {total_market_value}")
    print(f"总盈亏: {total_profit}")
    print(f"收益率: {total_profit/total_cost*100 if total_cost>0 else 0}%")
    
    # 对比原始盈亏图数据
    print(f"\n=== 对比原始数据 ===")
    print(f"原始图1+图2盈亏估算: 约 165,174.56 + 175,707.27 = 340,881.83")
    print(f"项目计算盈亏: {total_profit}")
    print(f"差异: {total_profit - 340881.83}")
    
except Exception as e:
    print(f"计算盈亏失败: {e}")

# 关闭连接
conn.close()
