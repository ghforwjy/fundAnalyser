"""
Tushare连接测试程序
用于测试tushare连接和数据获取的全过程
"""

import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = "../fund.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def test_tushare_connection():
    """测试tushare连接"""
    print("=" * 70)
    print("步骤1: 获取tushare配置")
    print("=" * 70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM data_source_config WHERE source_name = 'tushare'")
    row = cursor.fetchone()
    
    if not row:
        print("❌ 错误: 数据库中没有tushare配置")
        conn.close()
        return False
    
    print(f"✓ 找到tushare配置")
    print(f"  - ID: {row['id']}")
    print(f"  - 名称: {row['source_name']}")
    print(f"  - 类型: {row['source_type']}")
    print(f"  - 是否启用: {row['is_active']}")
    print(f"  - API Key: {'已配置' if row['api_key'] else '未配置'}")
    print(f"  - 是否连接: {row['is_connected']}")
    print(f"  - 最后测试时间: {row['last_test_time']}")
    print(f"  - 最后测试结果: {row['last_test_result']}")
    
    if not row['api_key']:
        print("\n❌ 错误: 未配置API Token")
        conn.close()
        return False
    
    if not row['is_active']:
        print("\n❌ 错误: 数据源未启用")
        conn.close()
        return False
    
    api_key = row['api_key']
    conn.close()
    
    print("\n" + "=" * 70)
    print("步骤2: 测试tushare连接")
    print("=" * 70)
    
    try:
        print("正在导入tushare...")
        import tushare as ts
        print(f"✓ tushare版本: {ts.__version__}")
        
        print("\n正在设置token...")
        ts.set_token(api_key)
        print("✓ Token设置成功")
        
        print("\n正在初始化pro_api...")
        pro = ts.pro_api()
        print("✓ Pro API初始化成功")
        
        print("\n正在测试trade_cal接口...")
        df = pro.trade_cal(exchange='SSE', start_date='20260101', end_date='20260110')
        
        if df is not None and len(df) > 0:
            print(f"✓ 连接成功，获取到{len(df)}条交易日历数据")
            print(f"\n数据预览:")
            print(df.head())
        else:
            print("❌ 连接成功但返回数据为空")
            return False
            
    except Exception as e:
        print(f"\n❌ 连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("步骤3: 测试获取基金列表")
    print("=" * 70)
    
    try:
        print("正在调用fund_basic接口...")
        df = pro.fund_basic(market='E')
        
        if df is not None and len(df) > 0:
            print(f"✓ 成功获取{len(df)}只基金信息")
            print(f"\n数据预览:")
            print(df.head())
            print(f"\n数据列: {list(df.columns)}")
        else:
            print("❌ 获取基金列表失败，返回数据为空")
            return False
            
    except Exception as e:
        print(f"\n❌ 获取基金列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("步骤4: 测试获取基金净值")
    print("=" * 70)
    
    try:
        # 获取第一只基金的代码
        fund_code = df.iloc[0]['ts_code']
        print(f"正在获取基金{fund_code}的净值...")
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        nav_df = pro.fund_nav(ts_code=fund_code, start_date=start_date, end_date=end_date)
        
        if nav_df is not None and len(nav_df) > 0:
            print(f"✓ 成功获取{len(nav_df)}条净值记录")
            print(f"\n数据预览:")
            print(nav_df.head())
            print(f"\n数据列: {list(nav_df.columns)}")
        else:
            print("⚠ 获取净值数据为空（可能是该基金没有净值数据）")
            
    except Exception as e:
        print(f"\n❌ 获取基金净值失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("步骤5: 测试数据插入数据库")
    print("=" * 70)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 测试插入基金信息
        test_fund = df.head(1).iloc[0]
        fund_code = test_fund['ts_code'].split('.')[0] if '.' in str(test_fund['ts_code']) else test_fund['ts_code']
        
        print(f"正在插入基金{fund_code}...")
        cursor.execute('''
            INSERT OR REPLACE INTO fund_info 
            (fund_code, fund_name, fund_type, manager_company, establish_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            fund_code,
            test_fund.get('name', ''),
            test_fund.get('type', '未知'),
            test_fund.get('management', ''),
            test_fund.get('setup_date', ''),
            '正常' if test_fund.get('status') == 'L' else '暂停'
        ))
        
        conn.commit()
        print(f"✓ 基金信息插入成功")
        
        # 验证插入
        cursor.execute("SELECT * FROM fund_info WHERE fund_code = ?", (fund_code,))
        row = cursor.fetchone()
        if row:
            print(f"✓ 验证成功，数据库中存在该基金")
            print(f"  - 基金代码: {row['fund_code']}")
            print(f"  - 基金名称: {row['fund_name']}")
            print(f"  - 基金类型: {row['fund_type']}")
        else:
            print("❌ 验证失败，数据库中不存在该基金")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 数据插入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✓ 所有测试通过！")
    print("=" * 70)
    return True

def test_sync_api():
    """测试同步API"""
    print("\n" + "=" * 70)
    print("测试同步API")
    print("=" * 70)
    
    import requests
    
    base_url = "http://localhost:8000/api"
    
    # 测试获取数据源
    print("\n1. 测试获取数据源列表...")
    try:
        response = requests.get(f"{base_url}/datasource")
        data = response.json()
        if data.get('success'):
            print(f"✓ 获取数据源成功，共{len(data['data'])}个数据源")
            for source in data['data']:
                print(f"  - {source['source_name']}: {'启用' if source['is_active'] else '禁用'}")
        else:
            print(f"❌ 获取数据源失败: {data.get('message')}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 测试连接
    print("\n2. 测试tushare连接...")
    try:
        response = requests.post(f"{base_url}/datasource/tushare/test")
        data = response.json()
        print(f"结果: {data}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 测试同步基金基本信息
    print("\n3. 测试同步基金基本信息...")
    try:
        response = requests.post(f"{base_url}/sync/fund-basic?limit=10")
        data = response.json()
        print(f"结果: {data}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    print("Tushare连接测试程序")
    print("=" * 70)
    
    # 测试直接连接
    success = test_tushare_connection()
    
    if success:
        # 测试API
        test_sync_api()
    else:
        print("\n❌ 直接连接测试失败，跳过API测试")
        sys.exit(1)
