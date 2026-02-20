import sqlite3

# 连接fundData skill的数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== 检查portfolio表 ===")

# 检查portfolio表数据
try:
    c.execute("SELECT * FROM portfolio")
    portfolios = c.fetchall()
    print(f"\n找到 {len(portfolios)} 个组合:")
    for i, portfolio in enumerate(portfolios):
        print(f"\n组合 {i+1}:")
        for key in portfolio.keys():
            print(f"  {key}: {portfolio[key]}")
except Exception as e:
    print(f"获取组合数据失败: {e}")

print("\n=== 检查每个组合的持仓 ===")

# 检查每个组合的持仓
try:
    c.execute("SELECT DISTINCT portfolio_id FROM portfolio_fund")
    portfolio_ids = [row['portfolio_id'] for row in c.fetchall()]
    
    for portfolio_id in portfolio_ids:
        print(f"\n=== 检查组合 {portfolio_id} 的持仓 ===")
        
        # 获取组合名称
        c.execute("SELECT name FROM portfolio WHERE id = ?", (portfolio_id,))
        portfolio_row = c.fetchone()
        portfolio_name = portfolio_row['name'] if portfolio_row else f"组合 {portfolio_id}"
        print(f"组合名称: {portfolio_name}")
        
        # 获取组合持仓
        c.execute("""
            SELECT 
                pf.fund_code,
                pf.fund_name,
                pf.shares,
                pf.buy_nav,
                pf.amount,
                fn.unit_nav as latest_nav,
                fn.nav_date
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
            WHERE pf.portfolio_id = ?
        """, (portfolio_id,))
        
        rows = c.fetchall()
        print(f"找到 {len(rows)} 条持仓记录:")
        
        total_cost = 0
        total_market_value = 0
        total_profit = 0
        
        for row in rows:
            fund_code = row['fund_code']
            fund_name = row['fund_name']
            shares = row['shares'] or 0
            buy_nav = row['buy_nav'] or 0
            amount = row['amount'] or 0
            latest_nav = row['latest_nav'] or 0
            nav_date = row['nav_date'] or '无数据'
            
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
            print(f"  最新净值: {latest_nav} (日期: {nav_date})")
            print(f"  成本: {cost}")
            print(f"  市值: {market_value}")
            print(f"  盈亏: {profit}")
        
        print(f"\n=== 组合 {portfolio_id} 汇总 ===")
        print(f"总成本: {total_cost}")
        print(f"总市值: {total_market_value}")
        print(f"总盈亏: {total_profit}")
        print(f"收益率: {total_profit/total_cost*100 if total_cost>0 else 0}%")
        
        # 对比原始盈亏图数据
        print(f"\n=== 对比原始数据 ===")
        print(f"原始图1+图2盈亏估算: 约 165,174.56 + 175,707.27 = 340,881.83")
        print(f"当前组合盈亏: {total_profit}")
        print(f"差异: {total_profit - 340881.83}")
        
except Exception as e:
    print(f"获取组合持仓数据失败: {e}")

# 关闭连接
conn.close()
