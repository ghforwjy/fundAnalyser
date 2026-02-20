## 当前问题
所有代码都在main.py中，难以维护。

## 建议的项目结构
```
backend/
├── main.py                    # 入口文件，只负责启动和路由注册
├── requirements.txt
├── init_db.py
├── config.py                  # 配置文件
├── database.py                # 数据库连接管理
├── tests/
│   └── test_tushare.py
├── api/                       # API路由
│   ├── __init__.py
│   ├── funds.py              # 基金相关API
│   ├── sync.py               # 数据同步API
│   ├── datasource.py         # 数据源配置API
│   ├── db_manage.py          # 数据库管理API
│   └── dashboard.py          # 仪表盘API
├── services/                  # 业务逻辑层
│   ├── __init__.py
│   ├── fund_service.py       # 基金服务
│   ├── sync_service.py       # 同步服务
│   └── datasource_service.py # 数据源服务
├── syncers/                   # 数据同步器（每个表一个）
│   ├── __init__.py
│   ├── base_syncer.py        # 基础同步器类
│   ├── fund_info_syncer.py   # 基金基本信息同步
│   ├── fund_nav_syncer.py    # 基金净值同步
│   ├── fund_holding_syncer.py # 持仓同步
│   └── fund_manager_syncer.py # 基金经理同步
└── models/                    # 数据模型
    ├── __init__.py
    └── schemas.py            # Pydantic模型
```

## 实施步骤
1. 创建目录结构
2. 提取数据库配置到database.py
3. 创建基础同步器类
4. 为每个表创建独立的同步器
5. 重构main.py，只保留路由注册
6. 更新测试程序

请确认这个方案后，我将开始实施重构。