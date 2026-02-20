"""
AKShare 同步器测试用例
测试基金信息、净值、基金公司同步功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from syncers.akshare_fund_info_syncer import AkshareFundInfoSyncer
from syncers.akshare_fund_nav_syncer import AkshareFundNavSyncer
from syncers.akshare_fund_company_syncer import AkshareFundCompanySyncer
from database import get_db_connection


def test_fund_info_syncer():
    """测试基金信息同步器"""
    print("\n" + "=" * 80)
    print("测试: AkshareFundInfoSyncer - 基金信息同步")
    print("=" * 80)

    syncer = AkshareFundInfoSyncer()

    # 测试获取数据
    print("\n1. 测试 fetch_data() - 获取基金列表...")
    try:
        data = syncer.fetch_data()
        print(f"   ✓ 成功获取 {len(data)} 只基金信息")
        if data:
            print(f"   ✓ 第一条数据示例: {data[0]}")
    except Exception as e:
        print(f"   ✗ 获取数据失败: {e}")
        return False

    # 测试同步功能
    print("\n2. 测试 sync() - 同步到数据库...")
    try:
        result = syncer.sync()
        print(f"   ✓ 同步结果: {result.success}")
        print(f"   ✓ 消息: {result.message}")
        print(f"   ✓ 记录数: {result.record_count}")
        print(f"   ✓ 新增: {result.inserted}")
        print(f"   ✓ 更新: {result.updated}")
    except Exception as e:
        print(f"   ✗ 同步失败: {e}")
        return False

    return True


def test_fund_nav_syncer():
    """测试基金净值同步器"""
    print("\n" + "=" * 80)
    print("测试: AkshareFundNavSyncer - 基金净值同步")
    print("=" * 80)

    syncer = AkshareFundNavSyncer()

    # 测试获取当日净值
    print("\n1. 测试 fetch_daily_nav() - 获取当日净值...")
    try:
        import pandas as pd
        df = syncer.fetch_daily_nav()
        if not df.empty:
            print(f"   ✓ 成功获取 {len(df)} 条净值记录")
            print(f"   ✓ 字段: {df.columns.tolist()[:5]}...")
        else:
            print("   ⚠ 未获取到净值数据（可能是非交易日）")
    except Exception as e:
        print(f"   ✗ 获取净值失败: {e}")
        return False

    # 测试获取历史净值
    print("\n2. 测试 fetch_fund_history_nav() - 获取单只基金历史净值...")
    try:
        df = syncer.fetch_fund_history_nav("000001")
        if not df.empty:
            print(f"   ✓ 成功获取基金 000001 的 {len(df)} 条历史记录")
        else:
            print("   ⚠ 未获取到历史净值数据")
    except Exception as e:
        print(f"   ✗ 获取历史净值失败: {e}")
        return False

    # 测试同步功能
    print("\n3. 测试 sync() - 同步当日净值到数据库...")
    try:
        result = syncer.sync(mode='daily')
        print(f"   ✓ 同步结果: {result.success}")
        print(f"   ✓ 消息: {result.message}")
        print(f"   ✓ 记录数: {result.record_count}")
    except Exception as e:
        print(f"   ✗ 同步失败: {e}")
        return False

    return True


def test_fund_company_syncer():
    """测试基金公司同步器"""
    print("\n" + "=" * 80)
    print("测试: AkshareFundCompanySyncer - 基金公司同步")
    print("=" * 80)

    syncer = AkshareFundCompanySyncer()

    # 测试获取数据
    print("\n1. 测试 fetch_data() - 获取基金公司列表...")
    try:
        data = syncer.fetch_data()
        print(f"   ✓ 成功获取 {len(data)} 家基金公司信息")
        if data:
            print(f"   ✓ 第一条数据示例: {data[0]}")
    except Exception as e:
        print(f"   ✗ 获取数据失败: {e}")
        return False

    # 测试同步功能
    print("\n2. 测试 sync() - 同步到数据库...")
    try:
        result = syncer.sync()
        print(f"   ✓ 同步结果: {result.success}")
        print(f"   ✓ 消息: {result.message}")
        print(f"   ✓ 记录数: {result.record_count}")
        print(f"   ✓ 新增: {result.inserted}")
        print(f"   ✓ 更新: {result.updated}")
    except Exception as e:
        print(f"   ✗ 同步失败: {e}")
        return False

    return True


def test_database_tables():
    """测试数据库表结构"""
    print("\n" + "=" * 80)
    print("测试: 数据库表结构")
    print("=" * 80)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查 fund_info 表字段
        print("\n1. 检查 fund_info 表字段...")
        try:
            cursor.execute("PRAGMA table_info(fund_info)")
            columns = {row['name'] for row in cursor.fetchall()}
            required = {'fund_code', 'fund_name', 'pinyin_abbr', 'data_source'}
            if required.issubset(columns):
                print(f"   ✓ fund_info 表包含所有必需字段")
                print(f"   ✓ 新增字段: pinyin_abbr, data_source")
            else:
                missing = required - columns
                print(f"   ✗ 缺少字段: {missing}")
                return False
        except Exception as e:
            print(f"   ✗ 检查失败: {e}")
            return False

        # 检查 fund_nav 表字段
        print("\n2. 检查 fund_nav 表字段...")
        try:
            cursor.execute("PRAGMA table_info(fund_nav)")
            columns = {row['name'] for row in cursor.fetchall()}
            if 'data_source' in columns:
                print(f"   ✓ fund_nav 表包含 data_source 字段")
            else:
                print(f"   ✗ fund_nav 表缺少 data_source 字段")
                return False
        except Exception as e:
            print(f"   ✗ 检查失败: {e}")
            return False

        # 检查 fund_company 表
        print("\n3. 检查 fund_company 表...")
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fund_company'")
            if cursor.fetchone():
                print(f"   ✓ fund_company 表已创建")

                cursor.execute("PRAGMA table_info(fund_company)")
                columns = {row['name'] for row in cursor.fetchall()}
                print(f"   ✓ 字段: {columns}")
            else:
                print(f"   ✗ fund_company 表不存在")
                return False
        except Exception as e:
            print(f"   ✗ 检查失败: {e}")
            return False

        # 检查 data_source_config 表
        print("\n4. 检查 data_source_config 表...")
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_source_config'")
            if cursor.fetchone():
                print(f"   ✓ data_source_config 表已创建")

                cursor.execute("SELECT source_name, is_active FROM data_source_config")
                sources = cursor.fetchall()
                for source in sources:
                    print(f"   ✓ 数据源: {source['source_name']}, 激活: {source['is_active']}")
            else:
                print(f"   ✗ data_source_config 表不存在")
                return False
        except Exception as e:
            print(f"   ✗ 检查失败: {e}")
            return False

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("AKShare 同步器测试套件")
    print("=" * 80)

    results = []

    # 测试数据库表结构
    results.append(("数据库表结构", test_database_tables()))

    # 测试基金信息同步器
    results.append(("基金信息同步器", test_fund_info_syncer()))

    # 测试基金净值同步器
    results.append(("基金净值同步器", test_fund_nav_syncer()))

    # 测试基金公司同步器
    results.append(("基金公司同步器", test_fund_company_syncer()))

    # 打印测试结果汇总
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")

    return all(r for _, r in results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
