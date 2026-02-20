1、python命令用py;
2、项目的目录结构：
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
3、tushare的表结构描述在以下文档中：
docs\tushare_fund_api.md
4、tushare的公募基金相关api文档在以下链接中：
https://tushare.pro/document/2?doc_id=18
5、akshare的表结构描述文档：
docs\akshare_fund_api.md

6、akshare的公募基金相关api文档在以下链接中：
https://akshare.akfamily.xyz/data/fund/fund_public.html
7、git操作见：docs\GIT_GUIDE.md