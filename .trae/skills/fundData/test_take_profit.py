import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit_manager import TakeProfitTemplateManager
from take_profit import TakeProfitCalculator, TakeProfitParams

print("=== 止盈模板列表 ===")
m = TakeProfitTemplateManager()
templates = m.list_templates()
for t in templates:
    print(f"  {t['id']}: {t['name']} (默认={t['is_default']}, 系统={t['is_system']})")

print("\n=== 测试止盈算法 ===")
calc = TakeProfitCalculator()

params = TakeProfitParams(
    first_threshold=0.20,
    first_sell_ratio=0.30,
    step_size=0.05,
    follow_up_sell_ratio=0.20,
    enable_cost_control=True,
    target_diluted_cost=0.0
)

print(f"参数: 首次阈值={params.first_threshold*100}%, 首次卖出={params.first_sell_ratio*100}%")
print(f"       阶梯步长={params.step_size*100}%, 后续卖出={params.follow_up_sell_ratio*100}%")

print("\n注意: 需要有组合数据才能测试完整功能")

print("\n=== 测试完成 ===")
