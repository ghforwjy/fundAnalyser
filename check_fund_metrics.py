"""
检查基金风险指标数据
"""
import sqlite3
import os

# 检查主数据库
db_path = os.path.join(os.path.dirname(__file__), 'fund_data.db')
if not os.path.exists(db_path):
    db_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData', 'fund_data.db')

print(f"数据库路径: {db_path}")
print(f"数据库存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    fund_code = '159566'

    print(f"\n=== 检查基金 {fund_code} 的数据 ===")

    # 检查 fund_info
    cursor.execute("SELECT fund_name, fund_type FROM fund_info WHERE fund_code = ?", (fund_code,))
    row = cursor.fetchone()
    if row:
        print(f"基金名称: {row['fund_name']}")
        print(f"基金类型: {row['fund_type']}")
    else:
        print("基金基本信息不存在")

    # 检查 fund_performance
    print("\n--- 阶段业绩 (fund_performance) ---")
    cursor.execute("""
        SELECT period, period_return, rank_in_category, update_time
        FROM fund_performance
        WHERE fund_code = ? AND performance_type = '阶段业绩'
    """, (fund_code,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  {row['period']}: 收益={row['period_return']}%, 排名={row['rank_in_category']}, 更新时间={row['update_time']}")
    else:
        print("  无数据")

    # 检查 fund_risk_metrics
    print("\n--- 风险指标 (fund_risk_metrics) ---")
    cursor.execute("""
        SELECT period, max_drawdown, sharpe_ratio, annual_volatility, update_time
        FROM fund_risk_metrics
        WHERE fund_code = ?
    """, (fund_code,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  {row['period']}: 最大回撤={row['max_drawdown']}%, 夏普={row['sharpe_ratio']}, 波动率={row['annual_volatility']}%, 更新时间={row['update_time']}")
    else:
        print("  无数据")

    # 检查 portfolio_fund
    print("\n--- 组合持仓 (portfolio_fund) ---")
    cursor.execute("""
        SELECT pf.*, p.name as portfolio_name
        FROM portfolio_fund pf
        JOIN portfolio p ON pf.portfolio_id = p.id
        WHERE pf.fund_code = ?
    """, (fund_code,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  组合: {row['portfolio_name']}")
            print(f"  份额: {row['shares']}")
            print(f"  买入净值: {row['buy_nav']}")
            print(f"  近1年收益: {row['return_1y']}")
            print(f"  最大回撤: {row['max_drawdown_1y']}")
            print(f"  夏普比率: {row['sharpe_ratio_1y']}")
            print(f"  指标更新时间: {row['metrics_update_time']}")
    else:
        print("  无组合持仓数据")

    conn.close()
else:
    print("数据库文件不存在")
