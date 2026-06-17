# WebSocket 端点 — 工作流状态实时推送
import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

ws_router = APIRouter()

# 连接池
_active_connections: list[WebSocket] = []


@ws_router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """监控WebSocket：实时推送工作流状态、Agent状态、日志"""
    await websocket.accept()
    _active_connections.append(websocket)
    logger.info(f"WebSocket连接建立，当前连接数: {len(_active_connections)}")

    try:
        # 发送初始状态
        await websocket.send_json({
            "type": "connection:established",
            "data": {"message": "已连接到智览平台监控服务", "timestamp": ""},
        })

        # 心跳循环
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                msg = json.loads(data)
                logger.debug(f"WS收到消息: {msg}")

                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                # 发送心跳
                await websocket.send_json({"type": "heartbeat"})

    except WebSocketDisconnect:
        logger.info("WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
    finally:
        if websocket in _active_connections:
            _active_connections.remove(websocket)
        logger.info(f"WebSocket连接关闭，当前连接数: {len(_active_connections)}")


async def broadcast_workflow_progress(data: dict):
    """向所有连接的客户端广播工作流进度（非阻塞，超时保护）"""
    disconnected = []
    # 拷贝列表避免遍历时并发修改
    for ws in list(_active_connections):
        try:
            await asyncio.wait_for(ws.send_json(data), timeout=3.0)
        except (Exception, asyncio.TimeoutError):
            disconnected.append(ws)

    for ws in disconnected:
        if ws in _active_connections:
            _active_connections.remove(ws)
