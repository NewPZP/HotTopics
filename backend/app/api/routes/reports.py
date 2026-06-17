# 研报 API 路由 — 真实数据驱动
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.repositories.report_repo import ReportRepo
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/reports")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50, alias="pageSize"),
    search: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    sort: str = Query("time", pattern="^(time|importance)$"),
):
    """获取研报列表 — DB 查询"""
    reports = ReportRepo.list_all(search=search or "", topic=topic or "", sort=sort)
    total = len(reports)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(
        data=reports[start:end],
        pagination={"current": page, "total": total, "pageSize": page_size},
    )


@router.get("/reports/{report_id}")
async def get_report_detail(report_id: str):
    """获取研报详情 — DB 查询"""
    report = ReportRepo.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"研报 {report_id} 不存在")
    return report
