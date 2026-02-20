"""
WebSocket API - 同步进度实时推送
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
from utils.progress import progress_manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/sync-progress")
async def sync_progress_websocket(websocket: WebSocket):
    """
    WebSocket 端点：同步进度实时推送
    
    连接后，所有同步器的进度更新都会通过此 WebSocket 推送
    
    消息格式：
    {
        "type": "fetch_start|fetch_progress|fetch_complete|save_start|save_progress|save_complete|error|info",
        "message": "进度描述",
        "current": 当前进度,
        "total": 总进度,
        "timestamp": "ISO格式时间戳",
        "sync_id": "同步任务ID",
        ...其他字段
    }
    """
    await websocket.accept()
    client_info = f"{websocket.client.host}:{websocket.client.port}"
    print(f"[WebSocket] 客户端连接: {client_info}")
    
    # 注册 WebSocket 连接
    progress_manager.register_websocket(websocket)
    
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "已连接到同步进度推送服务",
            "timestamp": ""
        })
        
        # 保持连接，等待客户端消息（可选，用于心跳检测等）
        while True:
            try:
                # 接收客户端消息（非阻塞，超时 30 秒）
                data = await websocket.receive_text()
                # 可以处理客户端发送的命令，如 ping/pong
                if data == "ping":
                    await websocket.send_json({"type": "pong", "message": "ok"})
            except Exception:
                # 接收超时或出错，继续循环
                pass
                
    except WebSocketDisconnect:
        print(f"[WebSocket] 客户端断开连接: {client_info}")
    except Exception as e:
        print(f"[WebSocket] 连接异常: {client_info}, 错误: {e}")
    finally:
        # 注销 WebSocket 连接
        progress_manager.unregister_websocket(websocket)
        print(f"[WebSocket] 客户端已清理: {client_info}")
