"""
测试图片识别服务并比对数据库
"""
import os
import sys
import base64
import sqlite3

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_recognition_service import get_image_recognition_service


def check_fund_in_db(fund_code: str) -> dict:
    """检查基金是否在数据库中"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'fund.db')
    db_path = os.path.abspath(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询基金基本信息
        cursor.execute("SELECT * FROM fund_info WHERE fund_code = ?", (fund_code,))
        row = cursor.fetchone()
        
        if row:
            result = {
                'exists': True,
                'fund_code': row['fund_code'],
                'fund_name': row['fund_name'],
                'fund_type': row['fund_type'],
                'company_name': row['company_name']
            }
        else:
            result = {'exists': False}
        
        conn.close()
        return result
    except Exception as e:
        return {'exists': False, 'error': str(e)}


def test_image_recognition():
    """测试图片识别功能并比对数据库"""
    # 测试图片路径
    image_path = os.path.join(os.path.dirname(__file__), 'testpic.jpg')
    
    if not os.path.exists(image_path):
        print(f"错误: 测试图片不存在: {image_path}")
        return
    
    print(f"正在读取测试图片: {image_path}")
    
    # 读取图片并转换为base64
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    print(f"图片大小: {len(image_bytes)} bytes")
    print(f"Base64长度: {len(image_base64)} characters")
    
    # 获取服务实例
    service = get_image_recognition_service()
    
    # 检查服务是否可用
    if not service.is_available():
        print("\n错误: 图片识别服务不可用")
        print(f"API Key: {service.api_key[:10]}..." if service.api_key else "未设置")
        print(f"Vision Model: {service.vision_model}")
        print(f"Base URL: {service.base_url}")
        return
    
    print("\n服务状态: 可用")
    print(f"Vision Model: {service.vision_model}")
    print("\n开始识别图片...")
    
    # 调用识别服务
    result = service.recognize_fund_image(image_base64)
    
    print("\n" + "="*80)
    print("识别结果:")
    print("="*80)
    
    if result['success']:
        print(f"✓ 识别成功: {result['message']}")
        print(f"\n共识别到 {len(result['data'])} 只基金:\n")
        
        # 统计
        exists_count = 0
        not_exists_count = 0
        
        for i, fund in enumerate(result['data'], 1):
            fund_code = fund['fundCode']
            db_info = check_fund_in_db(fund_code)
            
            print(f"{i}. 基金代码: {fund_code}")
            print(f"   基金名称(识别): {fund['fundName']}")
            print(f"   持有份额: {fund['shares']}")
            print(f"   参考净值: {fund['nav']}")
            print(f"   市值: {fund['amount']}")
            print(f"   盈利: {fund.get('profit', 'N/A')}")
            
            if db_info['exists']:
                print(f"   数据库状态: ✓ 存在")
                print(f"   数据库名称: {db_info['fund_name']}")
                print(f"   基金类型: {db_info['fund_type']}")
                print(f"   基金公司: {db_info['company_name']}")
                exists_count += 1
            else:
                print(f"   数据库状态: ✗ 不存在")
                not_exists_count += 1
            print()
        
        print("="*80)
        print(f"统计: 数据库中存在 {exists_count} 只, 不存在 {not_exists_count} 只")
        print("="*80)
    else:
        print(f"✗ 识别失败: {result['message']}")
        print(f"返回数据: {result['data']}")


if __name__ == '__main__':
    test_image_recognition()
