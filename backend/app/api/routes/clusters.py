# 聚类分析 API 路由 — 真实数据驱动
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.repositories.cluster_repo import ClusterRepo
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/clusters")
async def list_clusters(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    topic: Optional[str] = Query(None),
    sort: str = Query("importance", pattern="^(importance|time)$"),
):
    """获取聚类列表 — 分页查询"""
    total = ClusterRepo.count_all(topic=topic or "")
    offset = (page - 1) * page_size
    clusters = ClusterRepo.list_all(
        topic=topic or "", sort=sort, limit=page_size, offset=offset,
    )
    return PaginatedResponse(
        data=clusters,
        pagination={"current": page, "total": total, "pageSize": page_size},
    )


@router.get("/clusters/graph")
async def get_cluster_graph():
    """获取聚类关系图数据 — 从 DB 实时构建"""
    return ClusterRepo.build_graph()


@router.get("/clusters/{cluster_id}")
async def get_cluster_detail(cluster_id: str):
    """获取聚类详情 — DB 查询"""
    cluster = ClusterRepo.get_by_id(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail=f"聚类 {cluster_id} 不存在")
    return cluster
