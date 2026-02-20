"""
AKShare官方数据同步模块
使用AKShare提供的计算好的风险指标和业绩数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import akshare as ak
import pandas as pd
from typing import List, Dict, Any, Optional
from funddb import get_db_connection, update_sync_meta


class AkshareDataSyncer:
    """
    AKShare官方数据同步器
    同步AKShare已经计算好的风险指标和业绩数据
    """
    
    def sync_fund_risk_metrics(self, fund_code: str) -> Dict[str, Any]:
        """
        同步单只基金的风险指标（从AKShare获取）
        
        数据来源：fund_individual_analysis_xq
        包含：最大回撤、夏普比率、年化波动率等
        """
        try:
            df = ak.fund_individual_analysis_xq(symbol=fund_code)
            
            if df is None or len(df) == 0:
                return {'success': False, 'error': '无数据'}
            
            # 保存到数据库
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                for _, row in df.iterrows():
                    period = str(row.get('周期', '')).strip()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO fund_risk_metrics
                        (fund_code, period, risk_return_ratio, risk_resistance,
                         annual_volatility, sharpe_ratio, max_drawdown, update_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    ''', (
                        fund_code,
                        period,
                        int(row.get('较同类风险收益比', 0)) if pd.notna(row.get('较同类风险收益比')) else None,
                        int(row.get('较同类抗风险波动', 0)) if pd.notna(row.get('较同类抗风险波动')) else None,
                        float(row.get('年化波动率', 0)) if pd.notna(row.get('年化波动率')) else None,
                        float(row.get('年化夏普比率', 0)) if pd.notna(row.get('年化夏普比率')) else None,
                        float(row.get('最大回撤', 0)) if pd.notna(row.get('最大回撤')) else None
                    ))
                
                conn.commit()
            
            return {
                'success': True,
                'record_count': len(df),
                'periods': df['周期'].tolist()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_fund_performance(self, fund_code: str) -> Dict[str, Any]:
        """
        同步单只基金的业绩表现（从AKShare获取）
        
        数据来源：fund_individual_achievement_xq
        包含：各周期收益率、年度业绩、同类排名等
        """
        try:
            df = ak.fund_individual_achievement_xq(symbol=fund_code)
            
            if df is None or len(df) == 0:
                return {'success': False, 'error': '无数据'}
            
            # 保存到数据库
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                for _, row in df.iterrows():
                    perf_type = str(row.get('业绩类型', '')).strip()
                    period = str(row.get('周期', '')).strip()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO fund_performance
                        (fund_code, performance_type, period, period_return, max_drawdown,
                         rank_in_category, update_time)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    ''', (
                        fund_code,
                        perf_type,
                        period,
                        float(row.get('本产品区间收益', 0)) if pd.notna(row.get('本产品区间收益')) else None,
                        float(row.get('本产品最大回撤', 0)) if pd.notna(row.get('本产品最大回撤')) else None,
                        str(row.get('周期收益同类排名', '')).strip()
                    ))
                
                conn.commit()
            
            return {
                'success': True,
                'record_count': len(df)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_batch_risk_and_performance(self, fund_codes: List[str]) -> Dict[str, Any]:
        """
        批量同步风险指标和业绩数据
        """
        results = {
            'risk': {'success': 0, 'failed': 0},
            'performance': {'success': 0, 'failed': 0}
        }
        
        for i, code in enumerate(fund_codes, 1):
            print(f"[{i}/{len(fund_codes)}] 同步 {code} 的风险指标和业绩数据...")
            
            # 同步风险指标
            risk_result = self.sync_fund_risk_metrics(code)
            if risk_result['success']:
                results['risk']['success'] += 1
            else:
                results['risk']['failed'] += 1
                print(f"  风险指标同步失败: {risk_result.get('error')}")
            
            # 同步业绩数据
            perf_result = self.sync_fund_performance(code)
            if perf_result['success']:
                results['performance']['success'] += 1
            else:
                results['performance']['failed'] += 1
                print(f"  业绩数据同步失败: {perf_result.get('error')}")
        
        return results


# 便捷函数
def sync_fund_risk_and_performance(fund_code: str = None, fund_codes: List[str] = None):
    """
    便捷函数：同步基金风险指标和业绩数据
    
    示例：
        # 单只基金
        sync_fund_risk_and_performance('000001')
        
        # 批量同步
        sync_fund_risk_and_performance(fund_codes=['000001', '000002'])
    """
    syncer = AkshareDataSyncer()
    
    if fund_code:
        syncer.sync_fund_risk_metrics(fund_code)
        syncer.sync_fund_performance(fund_code)
    elif fund_codes:
        syncer.sync_batch_risk_and_performance(fund_codes)


if __name__ == '__main__':
    # 测试
    syncer = AkshareDataSyncer()
    
    print("=" * 80)
    print("测试AKShare官方数据同步")
    print("=" * 80)
    
    # 测试单只基金
    print("\n1. 同步000001的风险指标:")
    result = syncer.sync_fund_risk_metrics('000001')
    print(f"   结果: {result}")
    
    print("\n2. 同步000001的业绩数据:")
    result = syncer.sync_fund_performance('000001')
    print(f"   结果: {result}")
