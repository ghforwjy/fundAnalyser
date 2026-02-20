## AKShare 基金数据同步器设计方案

### 一、设计原则
1. **批量获取，减少调用**：AKShare 接口大部分返回全部数据，单次调用即可获取所有基金信息
2. **与现有架构兼容**：继承 BaseSyncer，保持与 tushare 同步器相同的接口
3. **数据互补**：AKShare 作为 tushare 的补充数据源，覆盖更全的基金数据

### 二、同步器架构

```
syncers/
├── base_syncer.py              # 基础同步器（已有）
├── fund_info_syncer.py         # tushare 基金信息同步器（已有）
├── fund_nav_syncer.py          # tushare 净值同步器（已有）
├── akshare_fund_info_syncer.py # AKShare 基金信息同步器（新增）
├── akshare_fund_nav_syncer.py  # AKShare 净值同步器（新增）
└── akshare_fund_company_syncer.py # AKShare 基金公司同步器（新增）
```

### 三、具体同步器设计

#### 1. AkshareFundInfoSyncer（基金基本信息同步器）

**使用接口**：`fund_name_em()` - 单次返回所有基金基本信息（26,000+只）

**字段映射**：
| AKShare 字段 | 数据库字段 | 说明 |
|-------------|-----------|------|
| 基金代码 | fund_code | 主键 |
| 基金简称 | fund_name | 基金名称 |
| 基金类型 | fund_type | 混合型/债券型等 |
| 拼音缩写 | pinyin_abbr | 新增字段 |

**批量策略**：
- 一次 API 调用获取全部 26,154 只基金
- 批量插入/更新数据库（使用事务）

#### 2. AkshareFundNavSyncer（基金净值同步器）

**使用接口**：`fund_open_fund_daily_em()` - 单次返回当日所有开放式基金净值

**批量策略**：
- 一次 API 调用获取当日全部基金净值
- 按日期批量保存
- 支持增量同步（对比数据库最新日期）

**历史净值获取**：
- 对于单只基金历史净值，使用 `fund_open_fund_info_em(symbol, indicator="单位净值走势")`
- 仅在需要补全某只基金历史数据时调用

#### 3. AkshareFundCompanySyncer（基金公司同步器）

**使用接口**：`fund_company_em()` - 单次返回所有基金公司

**字段映射**：
| AKShare 字段 | 数据库字段 |
|-------------|-----------|
| 基金公司 | company_name |
| 成立日期 | establish_date |
| 管理规模 | total_assets |
| 基金数量 | fund_count |
| 经理人数 | manager_count |

### 四、数据库表设计（新增/修改）

#### 1. 新增 fund_company 表
```sql
CREATE TABLE fund_company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(100) UNIQUE NOT NULL,
    establish_date DATE,
    total_assets DECIMAL(20,4),
    fund_count INTEGER,
    manager_count INTEGER,
    rating INTEGER,
    description TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 修改 fund_info 表（新增字段）
```sql
ALTER TABLE fund_info ADD COLUMN pinyin_abbr VARCHAR(20);
ALTER TABLE fund_info ADD COLUMN data_source VARCHAR(20) DEFAULT 'tushare'; -- tushare/akshare/both
```

### 五、批量数据处理优化

#### 1. 批量插入策略
```python
# 使用 executemany 批量插入
cursor.executemany('''
    INSERT OR REPLACE INTO fund_info 
    (fund_code, fund_name, fund_type, pinyin_abbr, data_source)
    VALUES (?, ?, ?, ?, ?)
''', data_list)
```

#### 2. 分页处理（如数据量过大）
```python
# 将大数据集分批处理
batch_size = 1000
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    save_batch(batch)
```

### 六、调用次数优化

| 同步器 | API 调用次数 | 数据量 |
|--------|-------------|--------|
| AkshareFundInfoSyncer | 1 次 | 26,154 只基金 |
| AkshareFundNavSyncer | 1 次/天 | 当日全部净值 |
| AkshareFundCompanySyncer | 1 次 | 全部基金公司 |

**对比 tushare**：
- tushare fund_basic: 1 次获取约 10,000+ 基金
- tushare fund_nav: 需按日期多次调用

### 七、数据源配置

修改 database.py 中的数据源配置：
```python
# 添加 AKShare 数据源配置
cursor.execute('''
    INSERT OR IGNORE INTO data_source_config 
    (source_name, source_type, is_active, is_connected, description, rate_limit)
    VALUES 
    ('akshare', 'free', 1, 1, 'AKShare免费开源数据源-天天基金', 1000)
''')
```

### 八、实施步骤

1. **创建 AKShare 同步器文件**（3个同步器）
2. **新增基金公司表**
3. **修改基金信息表**（增加拼音、数据源字段）
4. **添加数据源配置**
5. **创建同步服务接口**
6. **编写测试用例**

### 九、代码实现要点

1. 继承 BaseSyncer 基类
2. 实现 fetch_data() 和 save_data() 方法
3. 使用批量插入优化性能
4. 添加详细的日志记录
5. 错误处理和重试机制

请确认这个设计方案后，我将开始编写具体的同步器代码。