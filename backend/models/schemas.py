"""
Pydantic数据模型
"""
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class FundInfo(BaseModel):
    """基金基本信息模型"""
    fund_code: str
    fund_name: str
    fund_full_name: Optional[str] = None
    fund_type: str
    pinyin_abbr: Optional[str] = None
    pinyin_full: Optional[str] = None
    establish_date: Optional[str] = None
    company_name: Optional[str] = None
    custodian: Optional[str] = None
    benchmark: Optional[str] = None
    manage_fee_rate: Optional[float] = None
    custodian_fee_rate: Optional[float] = None
    issue_date: Optional[str] = None
    establish_scale: Optional[float] = None
    status: Optional[str] = "正常"
    invest_scope: Optional[str] = None
    track_target: Optional[str] = None

class FundNav(BaseModel):
    """基金净值模型"""
    fund_code: str
    nav_date: str
    unit_nav: float
    accum_nav: Optional[float] = None
    daily_return: Optional[float] = None
    subscribe_status: Optional[str] = None
    redeem_status: Optional[str] = None
    dividend: Optional[float] = 0

class DataSource(BaseModel):
    """数据源模型"""
    id: int
    source_name: str
    source_type: str
    base_url: Optional[str] = ""
    api_key: Optional[str] = ""
    is_active: bool = False
    is_connected: bool = False
    last_test_time: Optional[str] = ""
    last_test_result: Optional[str] = ""
    last_error: Optional[str] = ""
    description: Optional[str] = ""
    rate_limit: Optional[int] = 60

class DataSourceConfig(BaseModel):
    """数据源配置更新模型"""
    api_key: Optional[str] = None
    is_active: Optional[bool] = None

class SyncProgress(BaseModel):
    """同步进度模型"""
    stage: str
    current: int
    total: int
    message: str

class SyncResult(BaseModel):
    """同步结果模型"""
    success: bool
    message: str
    record_count: Optional[int] = 0
    inserted: Optional[int] = 0
    updated: Optional[int] = 0
    total: Optional[int] = 0
    errors: Optional[List[str]] = []
    progress: Optional[SyncProgress] = None

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None