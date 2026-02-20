"""
测试 Pydantic exclude_unset 行为
"""
from pydantic import BaseModel
from typing import Optional

class TestUpdate(BaseModel):
    name: Optional[str] = None
    enable_buy_back: Optional[bool] = None
    buy_back_threshold: Optional[float] = None

# 测试1: 只设置 enable_buy_back = True
print("测试1: 设置 enable_buy_back = True")
data1 = TestUpdate(enable_buy_back=True)
print(f"  dict(): {data1.dict()}")
print(f"  dict(exclude_unset=True): {data1.dict(exclude_unset=True)}")

# 测试2: 只设置 enable_buy_back = False
print("\n测试2: 设置 enable_buy_back = False")
data2 = TestUpdate(enable_buy_back=False)
print(f"  dict(): {data2.dict()}")
print(f"  dict(exclude_unset=True): {data2.dict(exclude_unset=True)}")

# 测试3: 设置所有字段
print("\n测试3: 设置所有字段")
data3 = TestUpdate(name="测试", enable_buy_back=True, buy_back_threshold=0.2)
print(f"  dict(): {data3.dict()}")
print(f"  dict(exclude_unset=True): {data3.dict(exclude_unset=True)}")

# 测试4: 设置所有字段，enable_buy_back = False
print("\n测试4: 设置所有字段，enable_buy_back = False")
data4 = TestUpdate(name="测试", enable_buy_back=False, buy_back_threshold=0.2)
print(f"  dict(): {data4.dict()}")
print(f"  dict(exclude_unset=True): {data4.dict(exclude_unset=True)}")
