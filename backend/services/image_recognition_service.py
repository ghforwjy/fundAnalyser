"""
图片识别服务 - 使用火山方舟多模态模型识别基金持仓截图
"""
import os
import json
import base64
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 尝试导入火山方舟SDK
try:
    from volcenginesdkarkruntime import Ark
    ARK_SDK_AVAILABLE = True
except ImportError:
    ARK_SDK_AVAILABLE = False
    print("警告: volcengine-python-sdk 未安装，图片识别功能将不可用")


class ImageRecognitionService:
    """图片识别服务"""
    
    def __init__(self):
        self.api_key = os.getenv('ARK_API_KEY')
        self.base_url = os.getenv('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        self.vision_model = os.getenv('ARK_VISION_MODEL', 'doubao-vision-xxx')
        self.client = None
        
        if ARK_SDK_AVAILABLE and self.api_key and self.api_key != 'your_api_key_here':
            try:
                self.client = Ark(
                    base_url=self.base_url,
                    api_key=self.api_key,
                )
            except Exception as e:
                print(f"初始化火山方舟客户端失败: {e}")
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return ARK_SDK_AVAILABLE and self.client is not None
    
    def recognize_fund_image(self, image_base64: str) -> Dict[str, Any]:
        """
        识别基金持仓截图
        
        Args:
            image_base64: Base64编码的图片数据
            
        Returns:
            {
                "success": bool,
                "data": [
                    {
                        "fundCode": str,
                        "fundName": str,
                        "shares": float,
                        "nav": float,
                        "amount": float
                    }
                ],
                "message": str
            }
        """
        if not self.is_available():
            return {
                "success": False,
                "data": [],
                "message": "图片识别服务未配置，请检查ARK_API_KEY和ARK_VISION_MODEL环境变量"
            }
        
        try:
            # 构建提示词
            prompt = """请识别这张基金持仓截图，提取以下信息：
1. 基金代码（6位数字）
2. 基金名称
3. 持有份额
4. 参考净值
5. 资产情况/市值
6. 持有收益/盈亏金额（如果有）

请严格按照以下JSON格式返回，不要包含任何其他内容：
{
  "funds": [
    {
      "fundCode": "000330",
      "fundName": "汇添富现金宝货币A",
      "shares": 19098.83,
      "nav": 1.0000,
      "amount": 19098.83,
      "profit": 1234.56
    }
  ]
}

注意：
- 基金代码必须是6位数字
- 份额、净值、金额、收益必须是数字
- 如果某个字段无法识别，使用null
- 只返回JSON，不要包含markdown代码块标记
- 持有收益/盈亏金额：正数表示盈利，负数表示亏损，如果没有显示则使用null
"""

            # 调用多模态模型
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # 低温度以获得更确定的结果
                max_tokens=4096
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 清理响应内容（去除可能的markdown代码块）
            content = self._clean_json_response(content)
            
            # 解析JSON
            result = json.loads(content)
            
            if "funds" not in result:
                return {
                    "success": False,
                    "data": [],
                    "message": "识别结果格式不正确"
                }
            
            # 验证和清理数据
            funds = self._validate_fund_data(result["funds"])
            
            return {
                "success": True,
                "data": funds,
                "message": f"成功识别 {len(funds)} 条基金记录"
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "data": [],
                "message": f"JSON解析失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"识别失败: {str(e)}"
            }
    
    def _clean_json_response(self, content: str) -> str:
        """清理模型返回的JSON响应"""
        # 去除markdown代码块标记
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    
    def _validate_fund_data(self, funds: List[Dict]) -> List[Dict[str, Any]]:
        """验证和清理基金数据"""
        validated = []
        
        for fund in funds:
            try:
                # 验证基金代码（6位数字）
                fund_code = str(fund.get("fundCode", "")).strip()
                if not fund_code or len(fund_code) != 6 or not fund_code.isdigit():
                    continue
                
                # 获取其他字段
                fund_name = str(fund.get("fundName", "")).strip()
                
                # 解析数字字段
                shares = self._parse_number(fund.get("shares"))
                nav = self._parse_number(fund.get("nav"))
                amount = self._parse_number(fund.get("amount"))
                
                # 如果金额为空但份额和净值有值，计算金额
                if amount is None and shares is not None and nav is not None:
                    amount = round(shares * nav, 2)
                
                validated.append({
                    "fundCode": fund_code,
                    "fundName": fund_name or f"基金 {fund_code}",
                    "shares": shares or 0,
                    "nav": nav or 0,
                    "amount": amount or 0
                })
                
            except Exception:
                continue
        
        return validated
    
    def _parse_number(self, value: Any) -> Optional[float]:
        """解析数字字段"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # 去除千分位分隔符和其他非数字字符
            cleaned = value.replace(",", "").replace("，", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return None
        
        return None


# 全局服务实例
_image_recognition_service: Optional[ImageRecognitionService] = None


def get_image_recognition_service() -> ImageRecognitionService:
    """获取图片识别服务实例（单例模式）"""
    global _image_recognition_service
    if _image_recognition_service is None:
        _image_recognition_service = ImageRecognitionService()
    return _image_recognition_service
