import sqlite3

# 连接fundData skill的数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2  # 持仓组合

print("=== 详细分析持仓组合 (ID: 2) 的盈亏差异 ===")

# 获取组合名称
try:
    c.execute("SELECT name FROM portfolio WHERE id = ?", (portfolio_id,))
    portfolio_row = c.fetchone()
    portfolio_name = portfolio_row['name'] if portfolio_row else f"组合 {portfolio_id}"
    print(f"组合名称: {portfolio_name}")
except Exception as e:
    print(f"获取组合名称失败: {e}")

# 获取组合持仓详情
try:
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
    
    print("\n=== 每只基金详细计算 ===")
    print(f"{'基金代码':<10} {'基金名称':<30} {'成本':<12} {'市值':<12} {'盈亏':<12} {'盈亏占比':<10}")
    print("-" * 100)
    
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
        
        # 计算盈亏占比
        profit_ratio = (profit / total_profit * 100) if total_profit != 0 else 0
        
        print(f"{fund_code:<10} {fund_name:<30} {cost:<12.2f} {market_value:<12.2f} {profit:<12.2f} {profit_ratio:<10.2f}%")
    
    print("-" * 100)
    print(f"{'总计':<40} {total_cost:<12.2f} {total_market_value:<12.2f} {total_profit:<12.2f}")
    
    print(f"\n=== 汇总计算 ===")
    print(f"总成本: {total_cost:.2f}")
    print(f"总市值: {total_market_value:.2f}")
    print(f"总盈亏: {total_profit:.2f}")
    print(f"收益率: {total_profit/total_cost*100 if total_cost>0 else 0:.2f}%")
    
    # 对比原始盈亏图数据
    print(f"\n=== 对比原始数据 ===")
    original_profit = 165174.56 + 175707.27  # 图1 + 图2
    print(f"原始图1+图2盈亏估算: {original_profit:.2f}")
    print(f"项目计算盈亏: {total_profit:.2f}")
    print(f"差异: {total_profit - original_profit:.2f}")
    print(f"差异百分比: {(total_profit - original_profit)/original_profit*100:.2f}%")
    
    # 分析差异原因
    print(f"\n=== 差异原因分析 ===")
    print("1. 检查每只基金的计算是否正确")
    print("2. 对比数据库中的份额、成本与原始图数据")
    print("3. 检查净值数据的日期是否匹配")
    print("4. 分析哪些基金贡献了主要差异")
    
    # 计算每只基金的盈亏贡献
    print(f"\n=== 盈亏贡献分析 ===")
    print(f"{'基金代码':<10} {'基金名称':<30} {'盈亏':<12} {'贡献占比':<10} {'对差异的贡献':<15}")
    print("-" * 100)
    
    total_diff = total_profit - original_profit
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
        
        # 计算盈亏
        profit = shares * latest_nav - cost
        
        # 计算贡献占比
        profit_ratio = (profit / total_profit * 100) if total_profit != 0 else 0
        
        # 计算对差异的贡献
        diff_contribution = (profit / total_profit * total_diff) if total_profit != 0 else 0
        
        print(f"{fund_code:<10} {fund_name:<30} {profit:<12.2f} {profit_ratio:<10.2f}% {diff_contribution:<15.2f}")
    
    print("\n=== 净值数据检查 ===")
    print("检查每只基金的最新净值日期:")
    for row in rows:
        fund_code = row['fund_code']
        fund_name = row['fund_name']
        nav_date = row['nav_date'] or '无数据'
        latest_nav = row['latest_nav'] or 0
        print(f"{fund_code}: {fund_name} - 日期: {nav_date}, 净值: {latest_nav}")
        
    # 检查是否有重复的基金
    print(f"\n=== 重复基金检查 ===")
    fund_codes = [row['fund_code'] for row in rows]
    duplicate_codes = set([code for code in fund_codes if fund_codes.count(code) > 1])
    if duplicate_codes:
        print(f"发现重复基金代码: {duplicate_codes}")
    else:
        print("无重复基金代码")
        
    # 检查成本和份额的一致性
    print(f"\n=== 成本与份额一致性检查 ===")
    for row in rows:
        fund_code = row['fund_code']
        fund_name = row['fund_name']
        shares = row['shares'] or 0
        buy_nav = row['buy_nav'] or 0
        amount = row['amount'] or 0
        
        # 计算理论成本
        theoretical_cost = shares * buy_nav
        
        # 检查差异
        if amount > 0 and shares > 0 and buy_nav > 0:
            cost_diff = abs(amount - theoretical_cost)
            cost_diff_percent = (cost_diff / amount * 100) if amount > 0 else 0
            print(f"{fund_code}: {fund_name}")
            print(f"  记录成本: {amount:.2f}")
            print(f"  理论成本: {theoretical_cost:.2f}")
            print(f"  差异: {cost_diff:.2f} ({cost_diff_percent:.2f}%)")
            if cost_diff_percent > 1:
                print(f"  ⚠️  成本差异较大")
            print()

except Exception as e:
    print(f"分析失败: {e}")
    import traceback
    traceback.print_exc()

# 关闭连接
conn.close()
