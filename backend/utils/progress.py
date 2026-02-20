"""
同步进度管理模块
用于 WebSocket 实时推送同步进度到前端
"""
from typing import Set, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio
from fastapi import WebSocket


class SyncProgressManager:
    """同步进度管理器 - 单例模式"""
    _instance = None
    _websockets: Set[WebSocket] = set()
    _progress_callbacks: Dict[str, Callable] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_websocket(self, websocket: WebSocket):
        """注册 WebSocket 连接"""
        self._websockets.add(websocket)
    
    def unregister_websocket(self, websocket: WebSocket):
        """注销 WebSocket 连接"""
        self._websockets.discard(websocket)
    
    def register_callback(self, sync_id: str, callback: Callable):
        """注册进度回调函数"""
        self._progress_callbacks[sync_id] = callback
    
    def unregister_callback(self, sync_id: str):
        """注销进度回调函数"""
        self._progress_callbacks.pop(sync_id, None)
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有连接的 WebSocket"""
        if not self._websockets:
            return
        
        # 添加时间戳
        message['timestamp'] = datetime.now().isoformat()
        
        # 发送给所有连接的客户端
        disconnected = set()
        for ws in self._websockets:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        
        # 清理断开的连接
        for ws in disconnected:
            self._websockets.discard(ws)
    
    def send_progress(self, sync_id: str, event_type: str, message: str, 
                      current: Optional[int] = None, total: Optional[int] = None,
                      extra: Optional[Dict] = None):
        """
        发送进度更新
        
        Args:
            sync_id: 同步任务ID
            event_type: 事件类型 (fetch_start, fetch_progress, fetch_complete, save_start, save_progress, save_complete, error)
            message: 进度消息
            current: 当前进度
            total: 总进度
            extra: 额外数据
        """
        data = {
            'sync_id': sync_id,
            'type': event_type,
            'message': message,
            'current': current,
            'total': total,
        }
        
        if extra:
            data.update(extra)
        
        # 异步广播
        asyncio.create_task(self.broadcast(data))
        
        # 调用注册的回调函数
        if sync_id in self._progress_callbacks:
            try:
                self._progress_callbacks[sync_id](data)
            except Exception:
                pass


# 全局进度管理器实例
progress_manager = SyncProgressManager()


class SyncProgressTracker:
    """同步进度追踪器 - 用于在同步器中追踪和报告进度"""
    
    def __init__(self, sync_id: str, sync_name: str):
        self.sync_id = sync_id
        self.sync_name = sync_name
        self.start_time = datetime.now()
        
    def log(self, event_type: str, message: str, 
            current: Optional[int] = None, total: Optional[int] = None,
            extra: Optional[Dict] = None):
        """记录进度日志"""
        progress_manager.send_progress(
            self.sync_id, event_type, message, current, total, extra
        )
    
    def fetch_start(self, message: str = "开始获取数据"):
        """开始获取数据"""
        self.log('fetch_start', message)
    
    def fetch_progress(self, current: int, total: Optional[int] = None, message: Optional[str] = None):
        """获取数据进度"""
        if message is None:
            if total:
                message = f"已获取 {current}/{total} 条"
            else:
                message = f"已获取 {current} 条"
        self.log('fetch_progress', message, current, total)
    
    def fetch_complete(self, total: int, message: Optional[str] = None):
        """获取数据完成"""
        if message is None:
            message = f"获取完成，共 {total} 条"
        self.log('fetch_complete', message, total, total)
    
    def save_start(self, message: str = "开始保存数据"):
        """开始保存数据"""
        self.log('save_start', message)
    
    def save_progress(self, current: int, total: int, message: Optional[str] = None):
        """保存数据进度"""
        if message is None:
            message = f"已保存 {current}/{total} 条"
        self.log('save_progress', message, current, total)
    
    def save_complete(self, total: int, inserted: int = 0, updated: int = 0):
        """保存数据完成"""
        message = f"保存完成，共 {total} 条（新增 {inserted}，更新 {updated}）"
        self.log('save_complete', message, total, total, {
            'inserted': inserted,
            'updated': updated
        })
    
    def error(self, message: str):
        """错误信息"""
        self.log('error', message)
    
    def info(self, message: str):
        """普通信息"""
        self.log('info', message)
    
    def get_elapsed_time(self) -> float:
        """获取已耗时（秒）"""
        return (datetime.now() - self.start_time).total_seconds()
