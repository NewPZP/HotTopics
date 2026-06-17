# 主题管理 API 路由 — 真实数据驱动
from fastapi import APIRouter, HTTPException
from app.repositories.topic_repo import TopicRepo
from app.schemas.common import TopicItem, TopicUpdate

router = APIRouter()


@router.get("/topics")
async def list_topics():
    """获取监控主题列表 — DB 查询"""
    return TopicRepo.list_all()


@router.post("/topics")
async def create_topic(topic: TopicItem):
    """创建监控主题 — DB 持久化"""
    return TopicRepo.create(topic.model_dump(by_alias=True))


@router.put("/topics/{topic_id}")
async def update_topic(topic_id: str, topic: TopicUpdate):
    """更新监控主题 — DB 持久化"""
    updated = TopicRepo.update(topic_id, topic.model_dump(by_alias=True, exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"主题 {topic_id} 不存在")
    return updated


@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: str):
    """删除监控主题 — DB 操作"""
    ok = TopicRepo.delete(topic_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"主题 {topic_id} 不存在")
    return {"success": True}
