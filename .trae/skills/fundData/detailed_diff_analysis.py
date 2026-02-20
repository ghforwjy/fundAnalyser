import sqlite3

# 连接fundData skill的数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2  # 持仓组合

print("=== 详细分析差异原因 ===")

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
    
    db_funds = c.fetchall()
    print(f"数据库中找到 {len(db_funds)} 只基金")
    
    # 计算数据库中的总盈亏
    db_total_cost = 0
    db_total_market_value = 0
    db_total_profit = 0
    
    db_fund_details = []
    for fund in db_funds:
        shares = fund['shares'] or 0
        buy_nav = fund['buy_nav'] or 0
        amount = fund['amount'] or 0
        latest_nav = fund['latest_nav'] or 0
        
        # 计算成本
        if amount > 0:
            cost = amount
        elif shares > 0 and buy_nav > 0:
            cost = shares * buy_nav
        else:
            cost = 0
        
        # 计算市值和盈亏
        market_value = shares * latest_nav
        profit = market_value - cost
        
        db_total_cost += cost
        db_total_market_value += market_value
        db_total_profit += profit
        
        db_fund_details.append({
            'fund_code': fund['fund_code'],
            'fund_name': fund['fund_name'],
            'shares': shares,
            'buy_nav': buy_nav,
            'amount': amount,
            'latest_nav': latest_nav,
            'cost': cost,
            'market_value': market_value,
            'profit': profit
        })
    
    print(f"\n数据库计算结果:")
    print(f"总成本: {db_total_cost:.2f}")
    print(f"总市值: {db_total_market_value:.2f}")
    print(f"总盈亏: {db_total_profit:.2f}")
    
    # 原始图数据估算
    original_profit = 165174.56 + 175707.27  # 图1 + 图2
    print(f"\n原始图数据:")
    print(f"总盈亏: {original_profit:.2f}")
    print(f"差异: {db_total_profit - original_profit:.2f}")
    print(f"差异百分比: {(db_total_profit - original_profit)/original_profit*100:.2f}%")
    
    # 分析可能的差异原因
    print("\n=== 差异原因分析 ===")
    
    # 1. 检查基金数量差异
    print("\n1. 基金数量检查:")
    print(f"数据库中基金数量: {len(db_funds)}")
    print("原始图中基金数量: 约20只（图1+图2）")
    
    # 2. 检查每只基金的计算
    print("\n2. 每只基金计算检查:")
    print(f"{'基金代码':<10} {'基金名称':<20} {'份额':<10} {'买入净值':<10} {'最新净值':<10} {'成本':<10} {'市值':<10} {'盈亏':<10}")
    print("-" * 120)
    
    for fund in db_fund_details:
        print(f"{fund['fund_code']:<10} {fund['fund_name'][:20]:<20} "
              f"{fund['shares']:<10.2f} {fund['buy_nav']:<10.4f} "
              f"{fund['latest_nav']:<10.4f} {fund['cost']:<10.2f} "
              f"{fund['market_value']:<10.2f} {fund['profit']:<10.2f}")
    
    # 3. 检查是否有异常数据
    print("\n3. 异常数据检查:")
    for fund in db_fund_details:
        if fund['shares'] == 0:
            print(f"⚠️  {fund['fund_code']}: {fund['fund_name']} - 份额为0")
        if fund['latest_nav'] == 0:
            print(f"⚠️  {fund['fund_code']}: {fund['fund_name']} - 最新净值为0")
        if fund['cost'] == 0 and fund['shares'] > 0:
            print(f"⚠️  {fund['fund_code']}: {fund['fund_name']} - 成本为0但有份额")
    
    # 4. 检查净值日期一致性
    print("\n4. 净值日期检查:")
    c.execute("""
        SELECT DISTINCT nav_date
        FROM fund_nav
        WHERE fund_code IN (
            SELECT fund_code FROM portfolio_fund WHERE portfolio_id = ?
        )
        AND nav_date IN (
            SELECT MAX(nav_date) FROM fund_nav GROUP BY fund_code
        )
    """, (portfolio_id,))
    nav_dates = [row['nav_date'] for row in c.fetchall()]
    
    print(f"净值日期分布:")
    date_counts = {}
    for date in nav_dates:
        if date:
            date_counts[date] = date_counts.get(date, 0) + 1
    
    for date, count in date_counts.items():
        print(f"  {date}: {count}只基金")
    
    # 5. 检查成本计算方法
    print("\n5. 成本计算方法检查:")
    for fund in db_fund_details:
        if fund['amount'] > 0 and fund['shares'] > 0 and fund['buy_nav'] > 0:
            calc_cost = fund['shares'] * fund['buy_nav']
            diff = abs(fund['amount'] - calc_cost)
            if diff > 0.01:
                print(f"⚠️  {fund['fund_code']}: 记录成本({fund['amount']:.2f})与计算成本({calc_cost:.2f})不符")
    
    # 6. 分析大型基金的影响
    print("\n6. 大型基金影响分析:")
    large_funds = [fund for fund in db_fund_details if fund['cost'] > 50000]
    print(f"成本大于50,000的大型基金: {len(large_funds)}只")
    
    large_total_profit = sum(fund['profit'] for fund in large_funds)
    large_profit_percentage = (large_total_profit / db_total_profit * 100) if db_total_profit > 0 else 0
    print(f"大型基金盈亏总额: {large_total_profit:.2f} ({large_profit_percentage:.2f}%)")
    
    for fund in large_funds:
        profit_percentage = (fund['profit'] / db_total_profit * 100) if db_total_profit > 0 else 0
        print(f"  {fund['fund_code']}: {fund['fund_name'][:20]} - 盈亏: {fund['profit']:.2f} ({profit_percentage:.2f}%)")
    
    # 7. 检查是否有重复计算
    print("\n7. 重复计算检查:")
    fund_codes = [fund['fund_code'] for fund in db_fund_details]
    duplicate_codes = set([code for code in fund_codes if fund_codes.count(code) > 1])
    if duplicate_codes:
        print(f"⚠️  发现重复基金代码: {duplicate_codes}")
    else:
        print("无重复基金代码")
    
    # 8. 对比原始图的可能基金
    print("\n8. 与原始图基金对比:")
    
    # 从原始图中提取的基金信息（基于图中可见的基金）
    original_funds = [
        # 图1中的基金
        {'name': '中欧医疗健康混合C', 'code': '003096'},
        {'name': '中欧医疗创新股票C', 'code': '006229'},
        {'name': '工银全球股票(QDII)人民币', 'code': '486001'},
        {'name': '中银国有企业债C', 'code': '006331'},
        {'name': '华泰柏瑞消费成长混合C', 'code': '011490'},
        {'name': '华商鑫安灵活配置混合C', 'code': '004983'},
        {'name': '广发医疗保健股票A', 'code': '004593'},
        {'name': '华夏创新驱动混合A', 'code': '007049'},
        {'name': '华夏创新驱动混合C', 'code': '010356'},
        {'name': '华商嘉悦稳健一年持有期混合C', 'code': '010367'},
        # 图2中的基金
        {'name': '华安中证500指数增强A', 'code': '040008'},
        {'name': '银华鑫盛灵活配置混合LOF A', 'code': '161839'},
        {'name': '博时稳健回报债券C', 'code': '004477'},
        {'name': '招商瑞盈稳健配置混合C', 'code': '008264'},
        {'name': '华商新趋势优选灵活配置混合', 'code': '166301'},
        {'name': '华商嘉悦稳健一年持有期混合A', 'code': '010366'}
    ]
    
    print("\n原始图中可见的基金:")
    for fund in original_funds:
        # 检查是否在数据库中
        db_fund = next((f for f in db_fund_details if f['fund_code'] == fund['code']), None)
        if db_fund:
            print(f"✅ {fund['code']}: {fund['name']} - 在数据库中存在")
        else:
            print(f"❌ {fund['code']}: {fund['name']} - 不在数据库中")
    
    # 9. 计算仅包含原始图基金的盈亏
    print("\n9. 仅计算原始图基金的盈亏:")
    original_fund_codes = [fund['code'] for fund in original_funds]
    original_only_profit = sum(fund['profit'] for fund in db_fund_details if fund['fund_code'] in original_fund_codes)
    
    print(f"仅原始图基金的盈亏: {original_only_profit:.2f}")
    print(f"与原始图数据的差异: {original_only_profit - original_profit:.2f}")
    
    # 10. 检查数据库中但不在原始图中的基金
    print("\n10. 数据库中有但原始图中没有的基金:")
    for fund in db_fund_details:
        if fund['fund_code'] not in original_fund_codes:
            print(f"📊 {fund['fund_code']}: {fund['fund_name']} - 盈亏: {fund['profit']:.2f}")
    
    # 计算这些基金的总盈亏
    extra_funds_profit = sum(fund['profit'] for fund in db_fund_details if fund['fund_code'] not in original_fund_codes)
    print(f"\n数据库额外基金的总盈亏: {extra_funds_profit:.2f}")
    print(f"这部分贡献了差异的 {extra_funds_profit/(db_total_profit - original_profit)*100 if (db_total_profit - original_profit) != 0 else 0:.2f}%")
    
    # 11. 最终差异原因总结
    print("\n=== 差异原因总结 ===")
    print(f"1. 数据库计算总盈亏: {db_total_profit:.2f}")
    print(f"2. 原始图估算总盈亏: {original_profit:.2f}")
    print(f"3. 差异金额: {db_total_profit - original_profit:.2f}")
    print(f"4. 差异百分比: {(db_total_profit - original_profit)/original_profit*100:.2f}%")
    print()
    print("可能的差异原因:")
    print("1. 基金范围不同: 数据库包含更多基金")
    print("2. 净值日期不同: 可能使用了不同日期的净值")
    print("3. 成本计算方法不同: 可能包含了手续费等因素")
    print("4. 数据录入差异: 份额、成本等数据可能存在差异")
    print("5. 原始图数据估算误差: 手动计算可能存在误差")
    
    # 检查是否有基金在原始图中但数据库中净值为0
    print("\n=== 原始图基金净值检查 ===")
    for fund in original_funds:
        db_fund = next((f for f in db_fund_details if f['fund_code'] == fund['code']), None)
        if db_fund:
            if db_fund['latest_nav'] == 0:
                print(f"⚠️  {fund['code']}: {fund['name']} - 最新净值为0")
            else:
                print(f"✅ {fund['code']}: {fund['name']} - 最新净值: {db_fund['latest_nav']}")

    # 检查数据库中所有基金的净值
    print("\n=== 所有基金净值状态 ===")
    zero_nav_funds = [fund for fund in db_fund_details if fund['latest_nav'] == 0]
    non_zero_nav_funds = [fund for fund in db_fund_details if fund['latest_nav'] != 0]
    
    print(f"最新净值为0的基金: {len(zero_nav_funds)}只")
    for fund in zero_nav_funds:
        print(f"  {fund['fund_code']}: {fund['fund_name']}")
    
    print(f"\n最新净值不为0的基金: {len(non_zero_nav_funds)}只")
    for fund in non_zero_nav_funds:
        print(f"  {fund['fund_code']}: {fund['fund_name']} - {fund['latest_nav']}")
        
    # 计算净值不为0的基金的盈亏
    non_zero_profit = sum(fund['profit'] for fund in non_zero_nav_funds)
    print(f"\n净值不为0的基金总盈亏: {non_zero_profit:.2f}")
    print(f"与原始图数据的差异: {non_zero_profit - original_profit:.2f}")

except Exception as e:
    print(f"分析失败: {e}")
    import traceback
    traceback.print_exc()

# 关闭连接
conn.close()
