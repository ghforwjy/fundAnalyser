# 基金标签管理功能设计文档

## 概述

基金标签管理功能允许用户为基金打上自定义标签，用于标识基金的投资方向、主题概念等。标签与基金直接关联，不依赖于组合，但在组合持仓管理界面提供便捷的操作入口。

## 设计原则

1. **独立性**：标签只与基金绑定，与组合无关
2. **灵活性**：支持多标签、分类管理、自定义颜色
3. **易用性**：支持下拉选择 + 模糊搜索 + 快速创建
4. **可扩展**：Skill层提供完整API，支持多种使用场景

## 数据模型

### 1. 标签表 (fund_tags)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INTEGER PRIMARY KEY | 标签ID |
| name | VARCHAR(50) UNIQUE | 标签名称（唯一） |
| category | VARCHAR(50) | 标签分类（如"行业主题"、"投资风格"） |
| color | VARCHAR(20) | 标签颜色（HEX格式，如#3b82f6） |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

### 2. 基金标签关联表 (fund_tag_relations)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INTEGER PRIMARY KEY | 关联ID |
| fund_code | VARCHAR(10) | 基金代码 |
| tag_id | INTEGER | 标签ID（外键） |
| create_time | DATETIME | 关联创建时间 |

**约束**：
- UNIQUE(fund_code, tag_id) - 一个基金不能有重复标签
- FOREIGN KEY (tag_id) REFERENCES fund_tags(id) ON DELETE CASCADE

## 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ TagSelector  │  │  持仓列表    │  │ 标签管理弹窗 │      │
│  │  组件        │  │  标签列      │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API层                          │
│  GET    /api/funds/tags/all                                 │
│  GET    /api/funds/tags/search?keyword=xxx                  │
│  GET    /api/funds/tags/categories                          │
│  POST   /api/funds/tags                                     │
│  PUT    /api/funds/tags/{tag_id}                            │
│  DELETE /api/funds/tags/{tag_id}                            │
│  GET    /api/funds/{fund_code}/tags                         │
│  PUT    /api/funds/{fund_code}/tags                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Skill层                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              tag_manager.py                         │   │
│  │  ┌──────────────┐  ┌──────────────────────────────┐ │   │
│  │  │  标签管理    │  │      基金标签关联管理        │ │   │
│  │  │  - 创建      │  │  - 获取基金标签              │ │   │
│  │  │  - 更新      │  │  - 设置基金标签（覆盖）      │ │   │
│  │  │  - 删除      │  │  - 添加/移除单个标签         │ │   │
│  │  │  - 查询      │  │  - 按标签查询基金            │ │   │
│  │  │  - 搜索      │  │  - 获取所有基金标签映射      │ │   │
│  │  └──────────────┘  └──────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据层 (SQLite)                          │
│  fund_tags  +  fund_tag_relations                           │
└─────────────────────────────────────────────────────────────┘
```

## Skill层接口详解

### 标签管理接口

#### create_tag(name, category=None, color=None)
创建新标签

**参数**：
- `name`: 标签名称（必填，唯一）
- `category`: 标签分类（可选）
- `color`: 标签颜色（可选，默认#3b82f6）

**返回**：
```python
{
    'success': True/False,
    'data': {'id': 1, 'name': '新能源', 'category': '行业主题', 'color': '#10b981'},
    'error': '错误信息'  # 失败时
}
```

#### update_tag(tag_id, **fields)
更新标签信息

**参数**：
- `tag_id`: 标签ID
- `fields`: 可更新字段（name, category, color）

**返回**：
```python
{'success': True/False, 'message': '更新成功'/'错误信息'}
```

#### delete_tag(tag_id)
删除标签（会自动删除所有关联）

**返回**：
```python
{'success': True/False, 'message': '删除成功'/'错误信息'}
```

#### get_all_tags(category=None)
获取所有标签

**参数**：
- `category`: 按分类筛选（可选）

**返回**：
```python
[
    {'id': 1, 'name': '新能源', 'category': '行业主题', 'color': '#10b981', ...},
    ...
]
```

#### search_tags(keyword)
模糊搜索标签

**参数**：
- `keyword`: 搜索关键词

**返回**：匹配的标签列表

#### get_tag_categories()
获取所有标签分类

**返回**：`['行业主题', '投资风格', ...]`

### 基金标签关联接口

#### get_fund_tags(fund_code)
获取基金的标签列表

**返回**：
```python
[
    {'id': 1, 'name': '新能源', 'category': '行业主题', 'color': '#10b82f6', 'tagged_time': '2026-02-17 14:43:27'},
    ...
]
```

#### set_fund_tags(fund_code, tag_ids)
批量设置基金标签（覆盖式）

**参数**：
- `fund_code`: 基金代码
- `tag_ids`: 标签ID列表

**说明**：会先删除该基金的所有标签，再添加新的标签

**返回**：
```python
{'success': True/False, 'message': '设置成功'/'错误信息'}
```

#### add_fund_tag(fund_code, tag_id)
给基金添加单个标签

**返回**：
```python
{'success': True/False, 'message': '添加成功'/'错误信息'}
```

#### remove_fund_tag(fund_code, tag_id)
移除基金的单个标签

**返回**：
```python
{'success': True/False, 'message': '移除成功'/'错误信息'}
```

#### get_funds_by_tag(tag_id)
获取拥有指定标签的所有基金代码

**返回**：`['000001', '000002', ...]`

#### get_all_fund_tags()
获取所有基金的标签映射

**返回**：
```python
{
    '000001': [{'id': 1, 'name': '新能源', ...}, {'id': 2, 'name': '半导体', ...}],
    '000002': [{'id': 1, 'name': '新能源', ...}],
    ...
}
```

## 前端组件设计

### TagSelector 组件

**功能**：
- 下拉选择标签
- 输入模糊搜索
- 创建新标签（输入不存在时）
- 多选展示
- 按分类分组显示

**Props**：
```typescript
interface TagSelectorProps {
  fundCode: string;           // 基金代码
  selectedTags: Tag[];        // 已选标签
  onTagsChange: (tags: Tag[]) => void;  // 标签变化回调
  placeholder?: string;       // 占位文字
}
```

**交互流程**：
1. 点击触发按钮，弹出下拉框
2. 显示已选标签（可点击移除）
3. 输入关键词搜索现有标签
4. 未找到时显示"创建新标签"选项
5. 点击标签切换选中状态
6. 按分类分组展示所有标签

### 持仓列表集成

**新增列**：
- 列名：标签
- 显示：标签徽章列表（带颜色）
- 操作菜单：新增"标签管理"选项

**标签管理弹窗**：
- 标题：标签管理 - {基金名称}
- 内容：TagSelector 组件
- 按钮：取消 / 保存

## 使用场景示例

### 场景1：给基金打标签

```python
from tag_manager import create_tag, add_fund_tag

# 创建行业主题标签
tag_new_energy = create_tag('新能源', '行业主题', '#10b981')
tag_semiconductor = create_tag('半导体', '行业主题', '#f59e0b')
tag_medicine = create_tag('医药', '行业主题', '#ef4444')

# 给基金添加标签
add_fund_tag('000001', tag_new_energy['data']['id'])
add_fund_tag('000001', tag_semiconductor['data']['id'])
```

### 场景2：查询某主题的所有基金

```python
from tag_manager import get_funds_by_tag, get_fund_tags

# 获取新能源主题的所有基金
new_energy_funds = get_funds_by_tag(1)

# 查看每只基金的完整标签
for fund_code in new_energy_funds:
    tags = get_fund_tags(fund_code)
    print(f"{fund_code}: {[t['name'] for t in tags]}")
```

### 场景3：批量更新基金标签

```python
from tag_manager import set_fund_tags

# 重新设置基金的标签（覆盖原有）
set_fund_tags('000001', [1, 3, 5])  # 只保留这3个标签
```

### 场景4：前端交互

```typescript
// 打开标签管理弹窗
const openTagDialog = (fund: Position) => {
  setSelectedFundForTag(fund);
  setFundTags(fund.tags || []);
  setTagDialogOpen(true);
};

// 保存标签
const saveFundTags = async () => {
  const tagIds = fundTags.map(t => t.id);
  await tagApi.setFundTags(fundCode, tagIds);
};
```

## 数据库初始化

```python
from tag_manager import init_tag_tables

# 初始化标签相关表
init_tag_tables()
```

会自动创建：
1. `fund_tags` 表
2. `fund_tag_relations` 表
3. 相关索引

## 注意事项

1. **标签名称唯一**：创建时会检查名称是否已存在
2. **级联删除**：删除标签会自动移除所有基金关联
3. **覆盖式设置**：`set_fund_tags` 会替换原有标签，不是追加
4. **颜色格式**：建议使用 HEX 颜色码（如 #3b82f6）
5. **分类管理**：分类是字符串，没有单独的分类表，通过 `get_tag_categories()` 动态获取

## 扩展建议

1. **标签推荐**：根据基金持仓自动推荐标签
2. **标签统计**：统计每个标签下的基金数量、收益情况
3. **标签筛选**：在基金列表支持按标签筛选
4. **热门标签**：展示使用频率最高的标签
5. **标签云**：可视化展示标签分布
