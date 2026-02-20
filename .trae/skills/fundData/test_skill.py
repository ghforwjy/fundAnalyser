"""
FundData Skill 测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_data_skill import FundDataSkill

def test_skill():
    """测试Skill基本功能"""
    print("=" * 60)
    print("FundData Skill 测试")
    print("=" * 60)
    
    # 初始化Skill
    print("\n1. 初始化Skill...")
    skill = FundDataSkill()
    print("   ✓ Skill初始化成功")
    
    # 获取统计数据
    print("\n2. 获取数据统计...")
    stats = skill.get_fund_stats()
    print(f"   总基金数: {stats['total_funds']}")
    print(f"   净值覆盖: {stats['nav_coverage']} ({stats['nav_coverage_rate']})")
    print("   ✓ 统计数据获取成功")
    
    # 搜索基金
    print("\n3. 搜索基金...")
    results = skill.search_funds("白酒", limit=5)
    print(f"   找到 {len(results)} 只基金:")
    for fund in results:
        print(f"     {fund['fund_code']} - {fund['fund_name']}")
    print("   ✓ 搜索功能正常")
    
    # 查询同步状态
    print("\n4. 查询同步状态...")
    status = skill.query_sync_status()
    print(f"   数据表数量: {len(status)}")
    for table, info in list(status.items())[:3]:
        if 'error' not in info:
            print(f"     {table}: {info['record_count']} 条记录")
    print("   ✓ 同步状态查询正常")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

def test_sync_fund_info():
    """测试同步基金基本信息"""
    print("\n" + "=" * 60)
    print("测试: 同步基金基本信息")
    print("=" * 60)
    
    skill = FundDataSkill()
    result = skill.sync_fund_info()
    
    print(f"结果: {result['message']}")
    print(f"成功: {result['success']}")
    print(f"记录数: {result['record_count']}")
    
    if result['errors']:
        print(f"错误: {result['errors'][:3]}")

def test_search_and_query():
    """测试搜索和查询功能"""
    print("\n" + "=" * 60)
    print("测试: 搜索和查询")
    print("=" * 60)
    
    skill = FundDataSkill()
    
    # 搜索
    print("\n搜索 '000001':")
    results = skill.search_funds("000001")
    for fund in results[:3]:
        print(f"  {fund['fund_code']} - {fund['fund_name']}")
    
    # 获取详情
    if results:
        fund_code = results[0]['fund_code']
        print(f"\n获取基金 {fund_code} 详情:")
        detail = skill.get_fund_detail(fund_code)
        if detail:
            print(f"  名称: {detail['fund_name']}")
            print(f"  类型: {detail['fund_type']}")
            print(f"  公司: {detail['company_name']}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FundData Skill 测试')
    parser.add_argument('--test', choices=['all', 'basic', 'sync', 'query'], 
                       default='basic', help='测试类型')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        test_skill()
        test_sync_fund_info()
        test_search_and_query()
    elif args.test == 'basic':
        test_skill()
    elif args.test == 'sync':
        test_sync_fund_info()
    elif args.test == 'query':
        test_search_and_query()
