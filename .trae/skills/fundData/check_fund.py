from database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # 检查018956是否在fund_info表中
    cursor.execute('SELECT * FROM fund_info WHERE fund_code = ?', ('018956',))
    row = cursor.fetchone()
    if row:
        print('基金018956存在于fund_info表中')
        name = row['fund_name']
        print(f'基金名称: {name}')
    else:
        print('基金018956不存在于fund_info表中')
        print('这是持仓数据无法保存的原因！sync_group_holdings会验证基金代码')
