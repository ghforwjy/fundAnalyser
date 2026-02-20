"""
基金数据平台后端服务
FastAPI + SQLite (使用fundData skill的数据库)
入口文件，只负责启动和路由注册
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_CONFIG, CORS_CONFIG
from database import init_datasource_table, init_portfolio_tables
from api import funds_router, datasource_router, db_manage_router, filters_router, portfolio_router
from api.websocket import router as websocket_router

# 加载环境变量
load_dotenv()
print(f"[main] 环境变量加载完成")
print(f"[main] ARK_API_KEY: {os.getenv('ARK_API_KEY', '未设置')[:20]}...")
print(f"[main] ARK_VISION_MODEL: {os.getenv('ARK_VISION_MODEL', '未设置')}")

# 初始化数据源表
init_datasource_table()
init_portfolio_tables()

# 启动时检查基金基本信息新鲜度
def check_fund_info_freshness():
    """检查基金基本信息是否过期（超过7天未更新），过期则更新"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.trae', 'skills', 'fundData'))
    from database import get_db_connection
    from datetime import datetime, timedelta
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查fund_info表最新更新时间
            cursor.execute('''
                SELECT MAX(update_time) as latest_update, COUNT(*) as count
                FROM fund_info
            ''')
            row = cursor.fetchone()
            
            if not row or not row['latest_update']:
                print("[启动检查] fund_info表无数据，需要同步")
                need_update = True
            else:
                latest_update = datetime.strptime(row['latest_update'], '%Y-%m-%d %H:%M:%S')
                days_since_update = (datetime.now() - latest_update).days
                print(f"[启动检查] fund_info表记录数: {row['count']}, 最后更新: {days_since_update}天前")
                
                # 超过7天视为过期
                need_update = days_since_update > 7
            
            if need_update:
                print("[启动检查] 基金基本信息过期，正在后台同步...")
                try:
                    from fund_data_skill import FundDataSkill
                    skill = FundDataSkill()
                    skill.sync_fund_info()
                    print("[启动检查] 基金基本信息同步完成")
                except Exception as e:
                    print(f"[启动检查] 基金基本信息同步失败: {e}")
            else:
                print("[启动检查] 基金基本信息新鲜度正常，跳过同步")
                
    except Exception as e:
        print(f"[启动检查] 检查基金基本信息失败: {e}")

# 启动时执行检查（非阻塞，在后台运行）
import threading
threading.Thread(target=check_fund_info_freshness, daemon=True).start()

# 创建FastAPI应用
app = FastAPI(
    title=APP_CONFIG["title"],
    version=APP_CONFIG["version"]
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["allow_origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
)

# 注册路由
app.include_router(funds_router)
app.include_router(datasource_router)
app.include_router(db_manage_router)
app.include_router(filters_router)
app.include_router(websocket_router)
app.include_router(portfolio_router)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": APP_CONFIG["title"],
        "version": APP_CONFIG["version"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=APP_CONFIG["host"],
        port=APP_CONFIG["port"]
    )
