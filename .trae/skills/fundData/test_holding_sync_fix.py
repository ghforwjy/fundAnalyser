#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试持仓同步修复功能
1. 验证错误日志记录到log目录
2. 验证当天不重复查询（即使失败）
"""

import os
import sys
import time
from datetime import date

sys.path.append('d:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')

from syncers.group_syncers import sync_group_holdings
from smart_fund_data import get_fund_holdings
from funddb import get_db_connection

def test_error_logging():
    """测试错误日志记录"""
    print("=== 测试1: 错误日志记录 ===")
    
    # 清空当天的错误日志（如果存在）
    log_file = f"log/holdings_sync_error_{date.today().strftime('%Y%m%d')}.log"
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"已清空旧日志文件: {log_file}")
    
    # 使用一个可能会失败的基金代码（比如太短的代码）
    test_fund_code = "123"
    print(f"\n测试同步基金: {test_fund_code}（预期会失败）")
    
    # 执行同步
    result = sync_group_holdings([test_fund_code])
    print(f"同步结果: {'成功' if result.success else '失败'}")
    print(f"消息: {result.message}")
    
    # 检查日志文件是否生成
    if os.path.exists(log_file):
        print(f"✓ 错误日志文件已生成: {log_file}")
        # 读取日志内容
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        print(f"日志内容:\n{log_content}")
    else:
        print(f"✗ 错误日志文件未生成: {log_file}")

def test_no_repeat_query():
    """测试当天不重复查询"""
    print("\n=== 测试2: 当天不重复查询 ===")
    
    # 使用一个真实的基金代码
    test_fund_code = "501022"  # 之前出现过错误的基金
    
    # 强制第一次同步（即使会失败）
    print(f"\n第一次同步基金: {test_fund_code}（可能会失败）")
    result1 = get_fund_holdings(test_fund_code, force_update=True)
    print(f"第一次同步结果: {result1}")
    
    # 等待1秒，确保时间戳不同
    time.sleep(1)
    
    # 第二次查询，应该使用缓存（即使第一次失败）
    print(f"\n第二次查询基金: {test_fund_code}（应该使用缓存）")
    result2 = get_fund_holdings(test_fund_code, force_update=False)
    print(f"第二次查询结果: {result2}")
    
    # 检查是否使用了缓存
    if result2.get('from_cache', False):
        print("✓ 第二次查询成功使用缓存")
    else:
        print("✗ 第二次查询未使用缓存，可能重复查询了")

def test_meta_table_update():
    """测试fund_data_meta表更新"""
    print("\n=== 测试3: fund_data_meta表更新 ===")
    
    test_fund_code = "501022"
    meta_key = f'holdings_{test_fund_code}'
    
    # 检查fund_data_meta表中的记录
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT table_name, last_sync_time, last_sync_status
            FROM fund_data_meta
            WHERE table_name = ?
        ''', (meta_key,))
        row = cursor.fetchone()
        
        if row:
            print(f"✓ fund_data_meta表中有记录:")
            print(f"  表名: {row[0]}")
            print(f"  最后同步时间: {row[1]}")
            print(f"  同步状态: {row[2]}")
            
            # 检查是否是今天的日期
            sync_date = row[1].split(' ')[0] if row[1] else ''
            today_str = date.today().strftime('%Y-%m-%d')
            if sync_date == today_str:
                print(f"✓ 同步时间是今天: {sync_date}")
            else:
                print(f"✗ 同步时间不是今天: {sync_date}（今天是: {today_str}")
        else:
            print(f"✗ fund_data_meta表中无记录: {meta_key}")

if __name__ == "__main__":
    print("开始测试持仓同步修复功能...")
    print(f"当前日期: {date.today()}")
    print(f"当前时间: {time.strftime('%H:%M:%S')}")
    print()
    
    try:
        test_error_logging()
        print("\n" + "="*60)
        test_no_repeat_query()
        print("\n" + "="*60)
        test_meta_table_update()
        print("\n" + "="*60)
        print("测试完成！")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
