"""
FundData Skill - 主入口模块
AKShare基金数据管理工具

使用方法:
    from fund_data_skill import FundDataSkill
    
    skill = FundDataSkill()
    
    # 全局数据同步
    skill.sync_fund_info()
    skill.sync_all_global_data()
    
    # 分组数据同步
    skill.sync_group_nav(["000001", "000002"])
    skill.sync_group_all_data(["000001", "000002"])
    
    # 数据查询
    results = skill.search_funds("白酒")
    nav_data = skill.query_fund_nav("000001")
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any, Optional
from syncers import (
    sync_fund_info,
    sync_fund_rating,
    sync_fund_manager,
    sync_fund_company,
    sync_fund_dividend,
    sync_fund_split,
    sync_all_global_data,
    sync_group_nav,
    sync_group_holdings,
    sync_group_risk_metrics,
    sync_group_performance,
    sync_group_all_data
)
from queries import (
    search_funds,
    query_fund_nav,
    query_fund_rating,
    query_fund_manager,
    query_sync_status,
    get_fund_detail,
    get_fund_stats,
    query_fund_holdings,
    query_fund_risk,
    query_fund_performance
)


class FundDataSkill:
    """
    FundData Skill 主类
    
    提供基金数据管理和查询的统一接口
    """
    
    def __init__(self):
        """初始化Skill"""
        print("[FundData] Skill初始化完成")
    
    # ==================== 全局数据同步接口 ====================
    
    def sync_fund_info(self) -> Dict[str, Any]:
        """
        同步基金基本信息（批量）
        
        Returns:
            同步结果
        """
        result = sync_fund_info()
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_fund_rating(self) -> Dict[str, Any]:
        """同步基金评级数据"""
        result = sync_fund_rating()
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_fund_manager(self) -> Dict[str, Any]:
        """同步基金经理数据"""
        result = sync_fund_manager()
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_fund_company(self) -> Dict[str, Any]:
        """同步基金公司数据"""
        result = sync_fund_company()
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_fund_dividend(self, year: str = None) -> Dict[str, Any]:
        """
        同步基金分红数据
        
        Args:
            year: 年份，如 "2025"
        """
        result = sync_fund_dividend(year)
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_fund_split(self, year: str = None) -> Dict[str, Any]:
        """
        同步基金拆分数据
        
        Args:
            year: 年份，如 "2025"
        """
        result = sync_fund_split(year)
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_all_global_data(self) -> Dict[str, Any]:
        """
        同步所有全局数据
        
        Returns:
            各数据类型的同步结果
        """
        results = sync_all_global_data()
        return {
            name: {
                'success': r.success,
                'message': r.message,
                'record_count': r.record_count
            }
            for name, r in results.items()
        }
    
    # ==================== 分组数据同步接口 ====================
    
    def sync_group_nav(self, fund_codes: List[str]) -> Dict[str, Any]:
        """
        同步分组基金的历史净值
        
        Args:
            fund_codes: 基金代码列表
        
        Returns:
            同步结果
        """
        result = sync_group_nav(fund_codes)
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_group_holdings(self, fund_codes: List[str], year: str = None) -> Dict[str, Any]:
        """
        同步分组基金的持仓数据
        
        Args:
            fund_codes: 基金代码列表
            year: 年份
        """
        result = sync_group_holdings(fund_codes, year)
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_group_risk_metrics(self, fund_codes: List[str]) -> Dict[str, Any]:
        """同步分组基金的风险指标"""
        result = sync_group_risk_metrics(fund_codes)
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_group_performance(self, fund_codes: List[str]) -> Dict[str, Any]:
        """同步分组基金的业绩表现"""
        result = sync_group_performance(fund_codes)
        return {
            'success': result.success,
            'message': result.message,
            'record_count': result.record_count,
            'errors': result.errors
        }
    
    def sync_group_all_data(self, fund_codes: List[str], year: str = None) -> Dict[str, Any]:
        """
        同步分组的所有数据
        
        Args:
            fund_codes: 基金代码列表
            year: 持仓数据年份
        """
        results = sync_group_all_data(fund_codes, year)
        return {
            name: {
                'success': r.success,
                'message': r.message,
                'record_count': r.record_count
            }
            for name, r in results.items()
        }
    
    # ==================== 数据查询接口 ====================
    
    def search_funds(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索基金
        
        Args:
            keyword: 搜索关键词（代码、名称、拼音）
            limit: 返回数量限制
        
        Returns:
            基金列表
        """
        return search_funds(keyword, limit)
    
    def get_fund_detail(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金详细信息
        
        Args:
            fund_code: 基金代码
        
        Returns:
            基金详细信息
        """
        return get_fund_detail(fund_code)
    
    def query_fund_nav(self, fund_code: str, start_date: str = None, 
                       end_date: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询基金净值历史
        
        Args:
            fund_code: 基金代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回记录数限制
        
        Returns:
            净值历史列表
        """
        return query_fund_nav(fund_code, start_date, end_date, limit)
    
    def query_fund_rating(self, fund_code: str = None) -> List[Dict[str, Any]]:
        """
        查询基金评级
        
        Args:
            fund_code: 基金代码，不传则返回所有
        """
        return query_fund_rating(fund_code)
    
    def query_fund_manager(self, fund_code: str = None, 
                          manager_name: str = None) -> List[Dict[str, Any]]:
        """
        查询基金经理信息
        
        Args:
            fund_code: 基金代码
            manager_name: 基金经理姓名
        """
        return query_fund_manager(fund_code, manager_name)
    
    def query_fund_holdings(self, fund_code: str, year: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询基金持仓数据
        
        Args:
            fund_code: 基金代码
            year: 年份
        """
        return query_fund_holdings(fund_code, year)
    
    def query_fund_risk(self, fund_code: str) -> List[Dict[str, Any]]:
        """查询基金风险指标"""
        return query_fund_risk(fund_code)
    
    def query_fund_performance(self, fund_code: str) -> List[Dict[str, Any]]:
        """查询基金业绩表现"""
        return query_fund_performance(fund_code)
    
    def query_sync_status(self) -> Dict[str, Any]:
        """
        查询数据同步状态
        
        Returns:
            各数据表的同步状态
        """
        return query_sync_status()
    
    def get_fund_stats(self) -> Dict[str, Any]:
        """
        获取基金数据统计信息
        
        Returns:
            统计信息
        """
        return get_fund_stats()


# ==================== 命令行接口 ====================

def print_help():
    """打印帮助信息"""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    FundData Skill 使用指南                    ║
╚══════════════════════════════════════════════════════════════╝

【全局数据同步命令】
  同步基金基本信息          - 同步全市场基金列表
  同步基金评级             - 同步基金评级数据
  同步基金经理             - 同步基金经理信息
  同步基金公司             - 同步基金公司信息
  同步基金分红 [年份]       - 同步分红数据（默认当年）
  同步基金拆分 [年份]       - 同步拆分数据（默认当年）
  同步所有全局数据          - 批量同步所有全局数据

【分组数据同步命令】
  同步分组净值 [代码列表]    - 同步指定基金的历史净值
  同步分组持仓 [代码列表] [年份] - 同步持仓数据
  同步分组风险指标 [代码列表] - 同步风险指标
  同步分组业绩 [代码列表]    - 同步业绩表现
  同步分组所有数据 [代码列表] - 同步所有分组数据

【数据查询命令】
  查询基金 [关键词]          - 搜索基金
  查询基金净值 [代码]        - 查询净值历史
  查询基金评级 [代码]        - 查询评级
  查询基金经理 [代码]        - 查询基金经理
  查询数据同步状态           - 查看同步状态
  查询数据统计              - 查看数据统计

【示例】
  skill.sync_fund_info()
  skill.sync_group_nav(["000001", "000002"])
  results = skill.search_funds("白酒")
"""
    print(help_text)


def main():
    """命令行入口"""
    skill = FundDataSkill()
    
    import sys
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    # 全局数据同步
    if command == "sync_fund_info":
        result = skill.sync_fund_info()
        print(f"结果: {result['message']}")
    
    elif command == "sync_fund_rating":
        result = skill.sync_fund_rating()
        print(f"结果: {result['message']}")
    
    elif command == "sync_fund_manager":
        result = skill.sync_fund_manager()
        print(f"结果: {result['message']}")
    
    elif command == "sync_fund_company":
        result = skill.sync_fund_company()
        print(f"结果: {result['message']}")
    
    elif command == "sync_fund_dividend":
        year = sys.argv[2] if len(sys.argv) > 2 else None
        result = skill.sync_fund_dividend(year)
        print(f"结果: {result['message']}")
    
    elif command == "sync_fund_split":
        year = sys.argv[2] if len(sys.argv) > 2 else None
        result = skill.sync_fund_split(year)
        print(f"结果: {result['message']}")
    
    elif command == "sync_all_global":
        results = skill.sync_all_global_data()
        for name, r in results.items():
            status = "✓" if r['success'] else "✗"
            print(f"{status} {name}: {r['message']}")
    
    # 分组数据同步
    elif command == "sync_group_nav":
        if len(sys.argv) < 3:
            print("用法: sync_group_nav [基金代码1,基金代码2,...]")
            return
        fund_codes = sys.argv[2].split(',')
        result = skill.sync_group_nav(fund_codes)
        print(f"结果: {result['message']}")
    
    elif command == "sync_group_all":
        if len(sys.argv) < 3:
            print("用法: sync_group_all [基金代码1,基金代码2,...]")
            return
        fund_codes = sys.argv[2].split(',')
        year = sys.argv[3] if len(sys.argv) > 3 else None
        results = skill.sync_group_all_data(fund_codes, year)
        for name, r in results.items():
            status = "✓" if r['success'] else "✗"
            print(f"{status} {name}: {r['message']}")
    
    # 数据查询
    elif command == "search":
        if len(sys.argv) < 3:
            print("用法: search [关键词]")
            return
        keyword = sys.argv[2]
        results = skill.search_funds(keyword)
        print(f"找到 {len(results)} 只基金:")
        for fund in results[:10]:
            print(f"  {fund['fund_code']} - {fund['fund_name']} ({fund['fund_type']})")
    
    elif command == "query_nav":
        if len(sys.argv) < 3:
            print("用法: query_nav [基金代码]")
            return
        fund_code = sys.argv[2]
        results = skill.query_fund_nav(fund_code, limit=10)
        print(f"基金 {fund_code} 最新净值:")
        for nav in results:
            print(f"  {nav['nav_date']}: {nav['unit_nav']} ({nav['daily_return']}%)")
    
    elif command == "status":
        status = skill.query_sync_status()
        print("数据同步状态:")
        for table, info in status.items():
            if 'error' not in info:
                print(f"  {table}: {info['record_count']} 条记录, 最后同步: {info['last_sync_time'] or '从未'}")
    
    elif command == "stats":
        stats = skill.get_fund_stats()
        print("基金数据统计:")
        print(f"  总基金数: {stats['total_funds']}")
        print(f"  净值覆盖: {stats['nav_coverage']} ({stats['nav_coverage_rate']})")
        print("  类型分布:")
        for fund_type, count in list(stats['type_distribution'].items())[:5]:
            print(f"    {fund_type}: {count}")
    
    else:
        print(f"未知命令: {command}")
        print_help()


if __name__ == "__main__":
    main()
