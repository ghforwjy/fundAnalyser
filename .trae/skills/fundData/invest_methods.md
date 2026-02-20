# 投资算法索引

本文件用于索引所有投资算法的设计文档。

---

## 算法列表

| 算法名称 | 文档路径 | 说明 |
|---------|---------|------|
| 市值定投法 | [docs/value_averaging_design.md](./docs/value_averaging_design.md) | 基于目标市值增长的定投策略，支持任意日期回溯计算 |
| 20%阶梯止盈法 | [docs/Take_Profit_design.md](./docs/Take_Profit_design.md) | 基于收益率的阶梯式止盈策略，支持成本控制自动停止 |

---

## 快速导航

### 市值定投法 (Value Averaging)

**核心思想**：设定目标市值增长路径，根据实际市值与目标市值的偏差决定买入或卖出。

**适用场景**：
- 长期定投
- 市场波动较大时平滑成本
- 需要纪律性投资策略

**文档位置**：[docs/value_averaging_design.md](./docs/value_averaging_design.md)

**实现文件**：[value_averaging.py](./value_averaging.py)

---

### 20%阶梯止盈法 (Take Profit)

**核心思想**：基于收益率触发阶梯式止盈，初次止盈后按净值涨幅阶梯卖出，支持成本控制自动停止。

**适用场景**：
- 基金定投止盈
- 分批锁定收益
- 本金回收后自动停止

**文档位置**：[docs/Take_Profit_design.md](./docs/Take_Profit_design.md)

---

> 后续新增投资算法时，请在此文件中添加索引条目，并在 docs/ 目录下创建对应的详细设计文档。
