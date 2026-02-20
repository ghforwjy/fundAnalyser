"""
搜索图片中基金名称对应的基金代码
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

# 从图片中提取的基金名称列表
fund_names_from_images = [
    # 图片1
    "中航机遇领航混合C",
    "中航优选领航混合C",
    "中航趋势领航混合A",
    "中航远见领航混合C",
    "中航智造机遇混合C",
    "中航月月鑫30天持有期债券C",
    "中航月月鑫30天持有期债券A",
    "华夏中证500ETF联接A",
    "工银全球中国机会全球股票",
    "天弘中证银行ETF联接C",
    "鹏华双债加利债券A",
    "中银国有企业债券C",
    # 图片2
    "华夏中证500指数增强A",
    "银华鑫盛灵活配置混合",
    "博时稳健回报C类LOF",
    "招商瑞信稳健配置C",
    "华泰柏瑞景气汇选三年持有期混合A",
    "华泰柏瑞鼎利混合C",
]

def search_fund_by_name(fund_name):
    """根据基金名称模糊搜索基金代码"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 先尝试精确匹配
        cursor.execute(
            "SELECT fund_code, fund_name, fund_type FROM fund_info WHERE fund_name = ?",
            (fund_name,)
        )
        exact_match = cursor.fetchone()
        if exact_match:
            return {
                'fund_code': exact_match['fund_code'],
                'fund_name': exact_match['fund_name'],
                'fund_type': exact_match['fund_type'],
                'match_type': 'exact'
            }
        
        # 尝试模糊匹配 - 去掉末尾的A/C等后缀
        base_name = fund_name
        if fund_name.endswith(('A', 'C', 'E')):
            base_name = fund_name[:-1]
        
        # 去掉括号内容
        import re
        base_name_clean = re.sub(r'[\(（].*?[\)）]', '', base_name)
        
        cursor.execute(
            "SELECT fund_code, fund_name, fund_type FROM fund_info WHERE fund_name LIKE ? LIMIT 5",
            (f"%{base_name_clean}%",)
        )
        fuzzy_matches = cursor.fetchall()
        
        if fuzzy_matches:
            matches = []
            for row in fuzzy_matches:
                matches.append({
                    'fund_code': row['fund_code'],
                    'fund_name': row['fund_name'],
                    'fund_type': row['fund_type']
                })
            return {
                'match_type': 'fuzzy',
                'matches': matches
            }
        
        return None

def main():
    print("=" * 100)
    print("基金代码搜索结果")
    print("=" * 100)
    
    results = []
    
    for fund_name in fund_names_from_images:
        result = search_fund_by_name(fund_name)
        
        if result is None:
            results.append({
                'search_name': fund_name,
                'status': 'not_found',
                'fund_code': None,
                'fund_name': None,
                'fund_type': None
            })
        elif result['match_type'] == 'exact':
            results.append({
                'search_name': fund_name,
                'status': 'exact_match',
                'fund_code': result['fund_code'],
                'fund_name': result['fund_name'],
                'fund_type': result['fund_type']
            })
        else:
            # 模糊匹配，取第一个
            best_match = result['matches'][0]
            results.append({
                'search_name': fund_name,
                'status': 'fuzzy_match',
                'fund_code': best_match['fund_code'],
                'fund_name': best_match['fund_name'],
                'fund_type': best_match['fund_type'],
                'all_matches': result['matches']
            })
    
    # 打印结果表格
    print(f"\n{'搜索名称':<40} {'状态':<12} {'基金代码':<10} {'基金类型':<20} {'匹配名称':<40}")
    print("-" * 120)
    
    for r in results:
        status_str = {
            'exact_match': '✓ 精确匹配',
            'fuzzy_match': '~ 模糊匹配',
            'not_found': '✗ 未找到'
        }.get(r['status'], r['status'])
        
        print(f"{r['search_name']:<40} {status_str:<12} {r['fund_code'] or '-':<10} {r['fund_type'] or '-':<20} {r['fund_name'] or '-':<40}")
        
        # 如果是模糊匹配，显示其他候选
        if r['status'] == 'fuzzy_match' and 'all_matches' in r:
            for i, match in enumerate(r['all_matches'][1:], 2):
                print(f"  └─ 候选{i}: {match['fund_code']} | {match['fund_name']} | {match['fund_type']}")
    
    # 统计
    print("\n" + "=" * 100)
    exact_count = sum(1 for r in results if r['status'] == 'exact_match')
    fuzzy_count = sum(1 for r in results if r['status'] == 'fuzzy_match')
    not_found_count = sum(1 for r in results if r['status'] == 'not_found')
    
    print(f"统计: 精确匹配 {exact_count} 个, 模糊匹配 {fuzzy_count} 个, 未找到 {not_found_count} 个")
    print("=" * 100)
    
    # 列出需要人工复核的基金
    print("\n【需要人工复核的基金】")
    print("-" * 100)
    
    fuzzy_or_not_found = [r for r in results if r['status'] in ('fuzzy_match', 'not_found')]
    if fuzzy_or_not_found:
        for r in fuzzy_or_not_found:
            print(f"\n搜索: {r['search_name']}")
            if r['status'] == 'fuzzy_match':
                print(f"  → 最佳匹配: {r['fund_code']} | {r['fund_name']}")
                print(f"  → 请确认是否正确")
            else:
                print(f"  → 未找到匹配，请手动查找基金代码")
    else:
        print("所有基金都已精确匹配，无需复核")
    
    return results

if __name__ == '__main__':
    results = main()
