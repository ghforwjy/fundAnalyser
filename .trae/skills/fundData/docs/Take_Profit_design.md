# 阶梯止盈法完整设计文档

## 1. 算法概述

本文档定义了"阶梯止盈法"的完整设计方案，包括核心计算逻辑、参数模板管理、基金个性化配置、数据库设计、接口设计和前端UI设计。

---

## 2. 核心逻辑判定表

算法根据"是否存在卖出记录"和"波段捡回设置"分流进入不同的判定分支。

| 状态判定 | 算法入参 | 计算公式 | 触发条件 | 动作 |
| :--- | :--- | :--- | :--- | :--- |
| **初次止盈**<br>(卖出记录为空) | 1. **当前收益率**<br>2. **首次止盈阈值** (如20%)<br>3. **首次止盈卖出比例** (如30%) | (无需计算，直接判定) | **当前收益率** >= **首次止盈阈值** | 卖出 **首次止盈卖出比例** |
| **后续止盈**<br>(卖出记录不为空) | 1. **当前净值**<br>2. **最近卖出日净值**<br>3. **阶梯步长** (如5%)<br>4. **后续止盈卖出比例** (如20%)<br>5. **是否启用成本控制**<br>6. **当前摊薄成本**<br>7. **目标摊薄成本** | **涨幅** = (当前净值 - 最近卖出日净值) / 最近卖出日净值 | **前置拦截：**<br>若启用控制 且 当前摊薄成本 <= 目标摊薄成本<br>-> **停止止盈**<br><br>**正常判定：**<br>**涨幅** >= **阶梯步长** | 卖出 **后续止盈卖出比例** |
| **波段捡回**<br>(存在未回收卖出记录) | 1. **当前净值**<br>2. **目标卖出净值**<br>3. **捡回阈值** (如20%)<br>4. **可用现金**<br>5. **原卖出份额** | **跌幅** = (目标卖出净值 - 当前净值) / 目标卖出净值 | **前置条件：**<br>启用波段捡回 = True<br>存在未回收卖出记录<br><br>**触发条件：**<br>**跌幅** >= **捡回阈值**<br>且 **可用现金** >= **捡回金额** | 买回 **原卖出份额** |

---

## 3. 详细流程图解

1. **状态分流**：查询数据库 `卖出流水表`。
   - 若为空 -> 进入 **初次止盈逻辑**。
   - 若不为空 -> 进入 **后续止盈逻辑**。

2. **初次止盈逻辑**：
   - 计算/获取 `当前收益率`。
   - 判断 `当前收益率` >= `首次止盈阈值`？
     - 是 -> 返回 `SELL`，比例=`首次止盈卖出比例`。
     - 否 -> 返回 `HOLD`。

3. **后续止盈逻辑**：
   - **Step 1 波段捡回检查**：
     - 若 `enable_buy_back` == True 且存在未回收卖出记录。
     - 获取最早未回收卖出记录的 `target_sell_nav`。
     - 计算 `跌幅` = (`target_sell_nav` - `current_nav`) / `target_sell_nav`。
     - 若 `跌幅` >= `buy_back_threshold` 且 `available_cash` >= `buy_back_amount`。
     - -> 返回 `BUY`，份额=`原卖出份额`。
   - **Step 2 成本检查**：
     - 若 `enable_cost_control` == True 且 `current_diluted_cost` <= `target_diluted_cost`。
     - -> 返回 `STOP`。
   - **Step 3 涨幅计算**：
     - 调用接口获取 `last_sell_nav`。
     - 计算 `涨幅` = (`current_nav` - `last_sell_nav`) / `last_sell_nav`。
   - **Step 4 阶梯判定**：
     - 若 `涨幅` >= `step_size`。
     - -> 返回 `SELL`，比例=`后续止盈卖出比例`。
     - 否则 -> 返回 `HOLD`。

---

## 4. 参数模板管理设计

### 4.1 功能概述

1. **多模板管理**：用户可以创建、编辑、删除多套止盈参数模板
2. **默认模板**：设置某一套模板为全局默认
3. **基金个性化**：可以为特定基金指定不同的参数模板

### 4.2 参数优先级规则

```
参数获取优先级（从高到低）：

1. 基金个性化参数（fund_take_profit_config.custom_*）
   ↓ 如果没有设置
2. 基金指定模板（fund_take_profit_config.template_id）
   ↓ 如果没有设置
3. 默认模板（take_profit_template.is_default = 1）
   ↓ 如果没有
4. 系统内置默认值
```

---

## 5. 数据库设计

### 5.1 止盈参数模板表 `take_profit_template`

```sql
CREATE TABLE IF NOT EXISTS take_profit_template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 模板名称，如"激进型"、"稳健型"
    description TEXT,                      -- 模板描述
    
    -- 止盈参数
    first_threshold DECIMAL(5,4) DEFAULT 0.20,        -- 首次止盈阈值
    first_sell_ratio DECIMAL(5,4) DEFAULT 0.30,       -- 首次止盈卖出比例
    step_size DECIMAL(5,4) DEFAULT 0.05,              -- 阶梯步长
    follow_up_sell_ratio DECIMAL(5,4) DEFAULT 0.20,   -- 后续止盈卖出比例
    enable_cost_control INTEGER DEFAULT 1,            -- 是否启用成本控制
    target_diluted_cost DECIMAL(10,4) DEFAULT 0,      -- 目标摊薄成本
    
    -- 波段捡回参数（高抛低吸）
    enable_buy_back INTEGER DEFAULT 0,                -- 是否启用波段捡回
    buy_back_threshold DECIMAL(5,4) DEFAULT 0.20,     -- 捡回阈值（跌幅达到此比例触发捡回）
    
    -- 元数据
    is_default INTEGER DEFAULT 0,          -- 是否为默认模板
    is_system INTEGER DEFAULT 0,           -- 是否为系统预设模板（不可删除）
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 基金止盈配置表 `fund_take_profit_config`

```sql
CREATE TABLE IF NOT EXISTS fund_take_profit_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,         -- 组合ID
    fund_code TEXT NOT NULL,               -- 基金代码
    template_id INTEGER,                   -- 使用的模板ID（NULL表示使用默认模板）
    
    -- 个性化覆盖参数（可选，优先级高于模板）
    custom_first_threshold DECIMAL(5,4),   -- 自定义首次止盈阈值
    custom_first_sell_ratio DECIMAL(5,4),  -- 自定义首次止盈卖出比例
    custom_step_size DECIMAL(5,4),         -- 自定义阶梯步长
    custom_follow_up_sell_ratio DECIMAL(5,4), -- 自定义后续止盈卖出比例
    custom_enable_cost_control INTEGER,    -- 自定义是否启用成本控制
    custom_target_diluted_cost DECIMAL(10,4), -- 自定义目标摊薄成本
    custom_enable_buy_back INTEGER,        -- 自定义是否启用波段捡回
    custom_buy_back_threshold DECIMAL(5,4), -- 自定义捡回阈值
    
    -- 元数据
    enabled INTEGER DEFAULT 1,             -- 是否启用止盈
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
    FOREIGN KEY (template_id) REFERENCES take_profit_template(id),
    UNIQUE(portfolio_id, fund_code)
);
```

### 5.3 系统预设模板

```sql
-- 初始化系统预设模板
INSERT INTO take_profit_template (name, description, first_threshold, first_sell_ratio, step_size, follow_up_sell_ratio, enable_cost_control, target_diluted_cost, is_default, is_system) VALUES
('标准型', '首次盈利20%卖出30%，后续每涨5%卖出20%', 0.20, 0.30, 0.05, 0.20, 1, 0, 1, 1),
('激进型', '首次盈利30%卖出20%，后续每涨8%卖出15%', 0.30, 0.20, 0.08, 0.15, 0, 0, 0, 1),
('稳健型', '首次盈利15%卖出40%，后续每涨3%卖出25%', 0.15, 0.40, 0.03, 0.25, 1, 0, 0, 1),
('保守型', '首次盈利10%卖出50%，后续每涨2%卖出30%', 0.10, 0.50, 0.02, 0.30, 1, 0, 0, 1);
```

---

## 6. 数据来源说明

### 6.1 基金明细表格字段来源

| 列名 | 字段 | 数据来源接口 | 接口文件 | 说明 |
|-----|------|-------------|---------|------|
| 基金代码 | fund_code | `list_portfolio_funds(portfolio_id)` -> `fund_code` | portfolio_manager.py | 组合内基金代码 |
| 基金名称 | fund_name | `list_portfolio_funds(portfolio_id)` -> `fund_name` | portfolio_manager.py | 组合内基金名称 |
| 当前份额 | current_shares | `list_portfolio_funds(portfolio_id)` -> `shares` | portfolio_manager.py | 持仓份额 |
| 当前净值 | current_nav | `get_fund_nav(fund_code)` -> `unit_nav` | smart_fund_data.py | 最新净值，**自动检查新鲜度，过期自动从AKShare同步** |
| 买入净值 | buy_nav | `list_portfolio_funds(portfolio_id)` -> `buy_nav` | portfolio_manager.py | 买入成本净值 |
| 当前市值 | current_value | 计算：`current_shares * current_nav` | - | 份额 * 当前净值 |
| 当前收益率 | current_profit_rate | 计算：`(current_nav - buy_nav) / buy_nav` | - | (当前净值-买入净值)/买入净值 |
| 卖出记录 | last_sell_nav | `get_portfolio_transactions(portfolio_id, fund_code, transaction_type='SELL')` -> `nav` | portfolio_manager.py | 最近卖出净值，无则显示"无" |
| 摊薄成本 | diluted_cost | `list_portfolio_funds(portfolio_id)` -> `cost_nav` | portfolio_manager.py | 摊薄成本净值，**直接从接口获取** |
| 建议操作 | action + sell_ratio | 止盈算法计算结果 | take_profit.py | SELL显示卖出比例，HOLD显示持有，STOP显示停止 |

### 6.2 数据新鲜度机制

| 接口 | 新鲜度机制 | 说明 |
|-----|-----------|------|
| `get_fund_nav()` | 自动检查 | 净值数据过期会自动从AKShare同步 |
| `list_portfolio_funds()` | 无 | 持仓数据从本地数据库读取 |
| `get_portfolio_transactions()` | 无 | 交易记录从本地数据库读取 |

**重要**：`get_fund_nav()` 是唯一有新鲜度检查的接口，会自动判断是否需要从AKShare获取最新净值。

---

## 7. Skills层接口设计

### 7.1 止盈算法接口 - `take_profit.py`

```python
"""
止盈算法模块
"""

@dataclass
class TakeProfitParams:
    """止盈策略参数"""
    first_threshold: float = 0.20
    first_sell_ratio: float = 0.30
    step_size: float = 0.05
    follow_up_sell_ratio: float = 0.20
    enable_cost_control: bool = True
    target_diluted_cost: float = 0.0
    enable_buy_back: bool = False           # 是否启用波段捡回
    buy_back_threshold: float = 0.20        # 捡回阈值（默认20%）


@dataclass
class TakeProfitFundResult:
    """单只基金止盈结果"""
    fund_code: str
    fund_name: str
    current_shares: float
    current_nav: float
    current_value: float
    buy_nav: float
    current_profit_rate: float
    has_sell_record: bool
    last_sell_nav: Optional[float]
    last_sell_date: Optional[str]
    diluted_cost: Optional[float]
    available_cash: float          # 可用现金（用于波段捡回判断）
    action: str                    # HOLD / SELL / STOP / BUY
    sell_ratio: Optional[float]
    sell_shares: Optional[float]
    sell_amount: Optional[float]
    buy_back_shares: Optional[float]      # 波段捡回：建议买回份额
    buy_back_amount: Optional[float]      # 波段捡回：预计花费金额
    target_sell_nav: Optional[float]      # 波段捡回：目标卖出净值
    decline_rate: Optional[float]         # 波段捡回：当前跌幅
    unrecovered_sells_count: int          # 未回收卖出记录数
    reason: str
    param_source: str              # 参数来源：default/custom/template_name
    template_name: Optional[str]   # 模板名称
    algorithm_details: List[str]


class TakeProfitCalculator:
    """止盈计算器"""
    
    def calculate(self, fund_code: str, portfolio_id: int, params: TakeProfitParams = None) -> TakeProfitFundResult:
        """
        计算单只基金的止盈建议
        
        数据获取：
        - 当前净值：get_fund_nav(fund_code) - 自动检查新鲜度
        - 持仓信息：list_portfolio_funds(portfolio_id)
        - 卖出记录：get_portfolio_transactions(portfolio_id, fund_code, transaction_type='SELL')
        """
        pass
    
    def calculate_portfolio(self, portfolio_id: int) -> Dict[str, Any]:
        """计算组合内所有基金的止盈建议"""
        pass


# 便捷函数
def calculate_take_profit(fund_code: str, portfolio_id: int, params: TakeProfitParams = None) -> TakeProfitFundResult:
    """计算单只基金止盈建议"""
    pass

def calculate_portfolio_take_profit(portfolio_id: int) -> Dict[str, Any]:
    """计算组合止盈建议"""
    pass

def get_take_profit_report_text(portfolio_id: int) -> str:
    """获取格式化的止盈报告"""
    pass
```

### 7.2 模板管理接口 - `take_profit_manager.py`

```python
"""
止盈参数模板管理模块
"""

class TakeProfitTemplateManager:
    """止盈参数模板管理器"""
    
    # ==================== 模板管理 ====================
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """获取所有止盈参数模板"""
        pass
    
    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """获取单个模板详情"""
        pass
    
    def get_default_template(self) -> Dict[str, Any]:
        """获取默认模板"""
        pass
    
    def create_template(self, name: str, description: str = None, **params) -> Dict[str, Any]:
        """创建新模板"""
        pass
    
    def update_template(self, template_id: int, **kwargs) -> Dict[str, Any]:
        """更新模板"""
        pass
    
    def delete_template(self, template_id: int) -> Dict[str, Any]:
        """删除模板（系统预设模板不可删除）"""
        pass
    
    def set_default_template(self, template_id: int) -> Dict[str, Any]:
        """设置默认模板"""
        pass
    
    # ==================== 基金配置管理 ====================
    
    def get_fund_config(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        """
        获取基金的止盈配置（合并模板参数）
        
        按优先级获取参数：
        1. 基金个性化参数
        2. 基金指定模板
        3. 默认模板
        """
        pass
    
    def set_fund_template(self, portfolio_id: int, fund_code: str, template_id: int = None) -> Dict[str, Any]:
        """为基金设置使用的模板"""
        pass
    
    def set_fund_custom_params(self, portfolio_id: int, fund_code: str, **custom_params) -> Dict[str, Any]:
        """为基金设置个性化参数（覆盖模板）"""
        pass
    
    def clear_fund_custom_params(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        """清除基金个性化参数，恢复使用模板"""
        pass
    
    def get_portfolio_fund_configs(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """获取组合内所有基金的止盈配置"""
        pass


# 便捷函数
def list_take_profit_templates() -> List[Dict[str, Any]]:
    """获取所有止盈参数模板"""
    pass

def get_fund_take_profit_config(portfolio_id: int, fund_code: str) -> Dict[str, Any]:
    """获取基金的止盈配置"""
    pass
```

### 7.3 接口封装 - `smart_fund_data.py`

在 `smart_fund_data.py` 中添加：

```python
from take_profit import (
    TakeProfitParams,
    calculate_take_profit,
    calculate_portfolio_take_profit,
    get_take_profit_report_text
)
from take_profit_manager import (
    TakeProfitTemplateManager,
    list_take_profit_templates,
    get_fund_take_profit_config
)


def get_take_profit_advice(portfolio_id: int) -> Dict[str, Any]:
    """
    便捷函数：获取组合止盈建议
    
    自动获取各基金配置的参数
    """
    pass
```

---

## 8. 后端API设计

### 8.1 止盈模板API

```python
# backend/api/portfolio.py

# 获取所有止盈参数模板
@router.get("/take-profit-templates")
async def list_take_profit_templates():
    pass

# 获取单个模板详情
@router.get("/take-profit-templates/{template_id}")
async def get_take_profit_template(template_id: int):
    pass

# 创建新模板
@router.post("/take-profit-templates")
async def create_take_profit_template(data: TemplateCreate):
    pass

# 更新模板
@router.put("/take-profit-templates/{template_id}")
async def update_take_profit_template(template_id: int, data: TemplateUpdate):
    pass

# 删除模板
@router.delete("/take-profit-templates/{template_id}")
async def delete_take_profit_template(template_id: int):
    pass

# 设置默认模板
@router.post("/take-profit-templates/{template_id}/set-default")
async def set_default_template(template_id: int):
    pass
```

### 8.2 基金止盈配置API

```python
# 获取基金的止盈配置
@router.get("/groups/{group_id}/funds/{fund_code}/take-profit-config")
async def get_fund_take_profit_config(group_id: int, fund_code: str):
    pass

# 设置基金的止盈配置
@router.put("/groups/{group_id}/funds/{fund_code}/take-profit-config")
async def set_fund_take_profit_config(group_id: int, fund_code: str, data: FundConfigUpdate):
    pass

# 获取组合内所有基金的止盈配置
@router.get("/groups/{group_id}/take-profit-configs")
async def get_portfolio_take_profit_configs(group_id: int):
    pass
```

### 8.3 止盈建议API

```python
# 获取组合的止盈建议
@router.get("/groups/{group_id}/take-profit-advice")
async def get_take_profit_advice(group_id: int):
    """
    获取组合的止盈建议（使用各基金配置的参数，支持波段捡回）
    
    后端只调用 skills 接口，不做业务逻辑
    """
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import get_take_profit_advice as _get_take_profit_advice

        result = _get_take_profit_advice(portfolio_id=group_id)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": str(e)}
```

### 8.4 波段捡回交易API

```python
# 执行波段捡回交易
@router.post("/groups/{group_id}/funds/{fund_code}/buy-back")
async def execute_buy_back_transaction(
    group_id: int,
    fund_code: str,
    data: BuyBackTransactionRequest
):
    """
    执行波段捡回交易
    
    功能：
    1. 记录买入交易
    2. 标记对应的卖出记录为已回收 (is_recovered = 1)
    3. 扣除组合现金
    
    前置条件：
    - 目标卖出记录必须存在且未回收
    - 捡回份额必须与卖出份额一致
    - 组合现金必须充足
    """
    pass
```

---

## 9. 前端UI设计

### 9.1 止盈建议主界面 (TakeProfitTab)

止盈建议作为投资组合页面的一个Tab页签展示，不是弹窗模式。

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 当前默认模板: [标准型]                                    [模板管理]    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐   │
│ │  📊     │ │  📉     │ │  ℹ️     │ │  ✅     │ │  💰             │   │
│ │ 持仓基金│ │ 建议卖出│ │ 继续持有│ │ 停止止盈│ │ 预计卖出金额    │   │
│ │ 5 只    │ │ 2 只    │ │ 2 只    │ │ 1 只    │ │ ¥4,500.00       │   │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────────┘   │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 📉 止盈建议明细                                    5 只基金         │ │
│ ├──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┤ │
│ │ 基金     │ 当前份额 │ 当前净值 │ 持仓市值 │ 买入净值 │ 当前收益率   │ │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤ │
│ │ 华夏成长 │ 1000.00  │ 1.2500   │ ¥1250.00 │ 1.0000   │ +25.00%      │ │
│ │ 000001   │          │          │          │          │              │ │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤ │
│ │ 可用现金 │ 卖出记录 │ 摊薄成本 │ 建议操作 │ 使用模板 │              │ │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┤              │ │
│ │ ¥0.00    │ 无       │ 1.0000   │ [卖出]   │ 标准型 ▼ │              │ │
│ │          │          │          │ ¥375.00  │          │              │ │
│ └──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘ │
│                                                                         │
│ 说明：                                                                  │
│ • 建议操作列显示"卖出"时，下方显示预计卖出金额                           │
│ • 鼠标悬停在"卖出"标签上显示卖出数量计算算法Tooltip                      │
│ • 使用模板列支持下拉选择其他模板或重置为默认                             │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ ℹ️ 数据来源说明                                                         │
│ • 当前份额、买入净值、摊薄成本: list_portfolio_funds()                  │
│ • 当前净值: get_fund_nav()（自动检查新鲜度，过期自动同步）               │
│ • 卖出记录: get_portfolio_transactions()                                │
├─────────────────────────────────────────────────────────────────────────┤
│ ℹ️ 算法详情（第一只基金）                                               │
│ 【华夏成长 000001】                                                     │
│ 当前收益率: 25.00%                                                      │
│ 首次止盈阈值: 20.00%                                                    │
│ 触发条件: 25.00% >= 20.00% ✓                                            │
│ 建议操作: 卖出 30%                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

**界面元素说明：**

| 区域 | 说明 |
|------|------|
| 顶部模板栏 | 显示当前默认模板名称，右侧"模板管理"按钮打开模板管理对话框 |
| 统计卡片 | 5个卡片展示：持仓基金数、建议卖出数、继续持有数、停止止盈数、预计卖出金额 |
| 基金明细表格 | 11列：基金、当前份额、当前净值、持仓市值、买入净值、当前收益率、可用现金、卖出记录、摊薄成本、建议操作、使用模板 |
| 数据来源说明 | 底部卡片说明各字段数据来源 |
| 算法详情 | 展示第一只基金的算法计算详情（可选显示） |

### 9.2 模板管理对话框

点击"模板管理"按钮打开的对话框：

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ⚙️ 止盈参数模板管理                                          [新建模板] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 标准型                                    [默认]  [系统预设]        │ │
│ │ 首次盈利20%卖出30%，后续每涨5%卖出20%                               │ │
│ │ ─────────────────────────────────────────────────────────────────── │ │
│ │ 首次阈值: 20% │ 首次卖出: 30% │ 阶梯步长: 5% │ 后续卖出: 20%       │ │
│ │ 成本控制: 启用                                                      │ │
│ │                                          [⭐] [✏️]                  │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 激进型                                          [系统预设]          │ │
│ │ 首次盈利30%卖出20%，后续每涨8%卖出15%                               │ │
│ │ 首次阈值: 30% │ 首次卖出: 20% │ 阶梯步长: 8% │ 后续卖出: 15%       │ │
│ │ 成本控制: 禁用                                                      │ │
│ │                                          [⭐] [✏️]                  │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 我的自定义                                                          │ │
│ │ 首次盈利25%卖出25%，后续每涨6%卖出20%                               │ │
│ │ 首次阈值: 25% │ 首次卖出: 25% │ 阶梯步长: 6% │ 后续卖出: 20%       │ │
│ │ 成本控制: 启用                                                      │ │
│ │                                          [⭐] [✏️] [🗑️]             │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**操作按钮说明：**
- ⭐ 设为默认（仅非默认模板显示）
- ✏️ 编辑模板
- 🗑️ 删除模板（仅自定义模板显示，系统预设不可删除）

### 9.3 创建/编辑模板对话框

```
┌─────────────────────────────────────────────────────────┐
│ 新建止盈参数模板 / 编辑止盈参数模板                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 模板名称                                                │
│ [请输入模板名称                    ]                    │
│                                                         │
│ 模板描述                                                │
│ [请输入模板描述（可选）            ]                    │
│                                                         │
│ ┌─────────────────┐ ┌─────────────────┐                 │
│ │ 首次止盈阈值(%) │ │ 首次卖出比例(%) │                 │
│ │ [20           ] │ │ [30           ] │                 │
│ └─────────────────┘ └─────────────────┘                 │
│                                                         │
│ ┌─────────────────┐ ┌─────────────────┐                 │
│ │ 阶梯步长(%)     │ │ 后续卖出比例(%) │                 │
│ │ [5            ] │ │ [20           ] │                 │
│ └─────────────────┘ └─────────────────┘                 │
│                                                         │
│ 启用成本控制在                                  [开关]  │
│                                                         │
│ 目标摊薄成本                                            │
│ [0.00                            ]                      │
│                                                         │
│ ─────────────────────────────────────────────────────  │
│ 启用波段捡回（高抛低吸）                        [开关]  │
│                                                         │
│ 捡回阈值(%)                                             │
│ [20                              ]                      │
│                                                         │
│ ℹ️ 波段捡回说明：                                       │
│ 当基金净值从卖出价格下跌达到此阈值时，触发买回建议      │
│                                                         │
│                              [取消]  [创建]/[保存]      │
└─────────────────────────────────────────────────────────┘
```

### 9.4 基金模板选择下拉菜单

在基金明细表格的"使用模板"列点击下拉：

```
┌─────────────────┐
│ 标准型    [默认]│
│ 激进型          │
│ 稳健型          │
│ 保守型          │
│ 我的自定义      │
│ ─────────────── │
│ 重置为默认      │
└─────────────────┘
```

### 9.5 卖出操作 Tooltip

鼠标悬停在"卖出"标签上时显示：

```
┌─────────────────────────────────────┐
│ 卖出数量计算算法                    │
│                                     │
│ 卖出份额 = 当前份额 × 卖出比例      │
│ 卖出金额 = 卖出份额 × 当前净值      │
│                                     │
│ ─────────────────────────────────   │
│ 当前计算：                          │
│ 1000.00 × 30% = 300.00 份           │
│ 300.00 × 1.2500 = ¥375.00           │
└─────────────────────────────────────┘
```

### 9.6 波段捡回操作 Tooltip

鼠标悬停在"捡回"标签上时显示：

```
┌─────────────────────────────────────┐
│ 波段捡回计算算法                    │
│                                     │
│ 跌幅 = (卖出净值 - 当前净值) / 卖出净值 │
│ 捡回份额 = 原卖出份额               │
│ 捡回金额 = 捡回份额 × 当前净值      │
│                                     │
│ ─────────────────────────────────   │
│ 当前计算：                          │
│ 目标卖出净值: 2.0000                │
│ 当前跌幅: 25.36%                    │
│ 捡回 1000.00 份 = ¥1492.90          │
└─────────────────────────────────────┘
```

### 9.7 前端交互流程

```
用户进入投资组合页面 -> 点击"止盈建议"Tab
        ↓
显示当前默认模板名称 + "模板管理"按钮
        ↓
加载并显示统计卡片（持仓/卖出/持有/停止/捡回/预计金额）
        ↓
加载基金明细表格（包含11列详细信息）
        ↓
用户可以：
├─ 点击"模板管理" -> 打开模板管理对话框
│   ├─ 点击"新建模板" -> 打开创建模板对话框（可设置波段捡回参数）
│   ├─ 点击"编辑" -> 打开编辑模板对话框
│   ├─ 点击"删除" -> 确认后删除自定义模板
│   └─ 点击"设为默认" -> 设置默认模板
├─ 在表格中点击"使用模板"下拉
│   ├─ 选择其他模板 -> 为该基金应用选中模板
│   └─ 选择"重置为默认" -> 恢复使用默认模板
├─ 鼠标悬停"卖出"标签 -> 查看卖出计算详情
└─ 鼠标悬停"捡回"标签 -> 查看捡回计算详情
    └─ 点击"执行捡回"按钮 -> 确认对话框 -> 执行捡回交易
        └─ 交易成功后刷新基金列表现金数据
```

---

## 10. 实现文件清单

| 文件 | 位置 | 说明 |
|-----|------|------|
| take_profit.py | .trae/skills/fundData/ | 止盈算法实现（含波段捡回逻辑） |
| take_profit_manager.py | .trae/skills/fundData/ | 模板管理实现（含波段捡回参数） |
| portfolio_manager.py | .trae/skills/fundData/ | 组合管理（含执行捡回交易函数） |
| smart_fund_data.py | .trae/skills/fundData/ | 接口封装（添加止盈和捡回相关函数） |
| portfolio.py | backend/api/ | 后端API（添加止盈和捡回相关接口） |
| TakeProfitTab.tsx | app/src/pages/Portfolio/InvestmentAdvice/ | 止盈建议组件（含捡回操作） |
| index.tsx | app/src/pages/Portfolio/InvestmentAdvice/ | 主组件（下拉框模式） |

---

## 11. 相关文档

- 投资算法索引：[invest_methods.md](./invest_methods.md)
- 市值定投法设计：[value_averaging_design.md](./value_averaging_design.md)
- 组合管理设计：[portfolio_design.md](./portfolio_design.md)
