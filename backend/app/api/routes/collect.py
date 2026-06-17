# 采集控制 API 路由
from fastapi import APIRouter, BackgroundTasks, Body
from typing import Optional
from app.schemas.common import ApiResponse

router = APIRouter()


@router.post("/collect", response_model=ApiResponse)
async def trigger_collect(background_tasks: BackgroundTasks, body: Optional[dict] = Body(None)):
    """触发即时采集任务（后台异步执行）"""
    topics = body.get("topics", None) if body else None

    async def _run():
        from app.agents.graph import run_workflow
        await run_workflow(topics=topics or ["AI监管", "金融政策", "新能源"])

    background_tasks.add_task(_run)
    return ApiResponse(message="采集任务已触发，正在后台执行")
