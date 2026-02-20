import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_manager import import_profit_data

# 组合ID
portfolio_id = 2

# 所有基金的盈亏数据（从原始图片提取）
profit_data = [
    {'fund_code': '024389', 'fund_name': '中航智选领航混合C', 'current_value': 10688.38, 'profit_loss': 4688.38},
    {'fund_code': '022853', 'fund_name': '中航优选领航混合C', 'current_value': 12803.50, 'profit_loss': 4103.50},
    {'fund_code': '021489', 'fund_name': '中航趋势领航混合A', 'current_value': 7184.70, 'profit_loss': 2764.70},
    {'fund_code': '021492', 'fund_name': '中航远见领航混合C', 'current_value': 11508.50, 'profit_loss': 2615.24},
    {'fund_code': '024291', 'fund_name': '中航月月鑫30天持有期债券C', 'current_value': 10.03, 'profit_loss': 0.03},
    {'fund_code': '024290', 'fund_name': '中航月月鑫30天持有期债券A', 'current_value': 10.04, 'profit_loss': 0.04},
    {'fund_code': '001052', 'fund_name': '华夏中证500ETF联接A', 'current_value': 18297.49, 'profit_loss': 9797.49},
    {'fund_code': '486001', 'fund_name': '工银全球股票(QDII)人民币', 'current_value': 32979.62, 'profit_loss': 18577.96},
    {'fund_code': '001595', 'fund_name': '天弘中证银行ETF联接C', 'current_value': 63524.79, 'profit_loss': 30024.79},
    {'fund_code': '000143', 'fund_name': '鹏华双债加利债券A', 'current_value': 388704.74, 'profit_loss': 90596.94},
    {'fund_code': '006331', 'fund_name': '中银国有企业债C', 'current_value': 31449.00, 'profit_loss': 1449.00},
    {'fund_code': '018957', 'fund_name': '中航机遇领航混合发起C', 'current_value': 25956.71, 'profit_loss': 16456.71},
    {'fund_code': '007