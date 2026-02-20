## 问题
当前同步进度只显示大步骤（如"正在同步基金信息"），用户看不到具体进展（如已获取多少条、已保存多少条），导致长时间等待时不知道发生了什么。

## 解决方案

### 方案：WebSocket 实时推送进度日志

#### 后端修改
1. **创建 WebSocket 连接** `/ws/sync-progress`
2. **同步器发送进度事件**：
   - `fetch_start` - 开始获取数据
   - `fetch_progress` - 获取进度（已获取 X 条）
   - `fetch_complete` - 获取完成（共 X 条）
   - `save_start` - 开始保存
   - `save_progress` - 保存进度（已保存 X/Y 条）
   - `save_complete` - 保存完成
   - `error` - 错误信息

3. **修改同步器**：在关键节点调用进度回调函数

#### 前端修改
1. **连接 WebSocket** 接收实时进度
2. **显示详细日志**：在进度条下方显示实时日志流
3. **保留大步骤进度**：同时显示整体进度和详细日志

### 实现示例

**后端 WebSocket：**
```python
@router.websocket("/ws/sync-progress")
async def sync_progress_websocket(websocket: WebSocket):
    await websocket.accept()
    # 将 websocket 存入全局，供同步器使用
    active_websockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_websockets.remove(websocket)

# 同步器中发送进度
def send_progress(event_type, message, progress=None):
    for ws in active_websockets:
        await ws.send_json({
            "type": event_type,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        })
```

**前端显示：**
```
[==========>          ] 50% 同步基金信息

详细日志：
[14:32:01] 开始获取基金列表...
[14:32:03] 已获取 5000 条...
[14:32:05] 已获取 10000 条...
[14:32:07] 获取完成，共 26154 条
[14:32:08] 开始保存到数据库...
[14:32:10] 已保存 5000/26154 条...
```

### 替代方案：轮询进度 API
如果不使用 WebSocket，也可以：
1. 同步开始时返回任务 ID
2. 前端轮询 `/api/sync/progress/{task_id}` 获取进度
3. 后端将进度存入内存或 Redis

## 建议
推荐使用 **WebSocket 方案**，因为：
- 实时性更好
- 服务器推送，减少轮询开销
- 用户体验更流畅

请确认采用哪种方案，我将开始实施。