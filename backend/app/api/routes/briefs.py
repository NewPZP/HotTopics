# 简报 API 路由 — 真实数据驱动
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from app.repositories.brief_repo import BriefRepo
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/briefs")
async def list_briefs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50, alias="pageSize"),
):
    """获取历史日报列表 — DB 查询"""
    briefs = BriefRepo.list_all()
    total = len(briefs)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(
        data=briefs[start:end],
        pagination={"current": page, "total": total, "pageSize": page_size},
    )


@router.get("/briefs/{date}")
async def get_brief_by_date(date: str):
    """获取指定日期日报 — DB 查询"""
    brief = BriefRepo.get_by_date(date)
    if not brief:
        raise HTTPException(status_code=404, detail=f"简报 {date} 不存在")
    return brief


@router.get("/briefs/{date}/pdf")
async def download_brief_pdf(date: str):
    """下载 PDF 版日报"""
    import os
    from app.config import get_settings
    settings = get_settings()
    pdf_path = os.path.join(settings.EXPORT_DIR, f"brief_{date}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"brief_{date}.pdf")
    raise HTTPException(status_code=404, detail="PDF 尚未生成")


@router.get("/briefs/{date}/md")
async def download_brief_md(date: str):
    """下载 Markdown 版日报"""
    import os
    from app.config import get_settings
    settings = get_settings()
    md_path = os.path.join(settings.EXPORT_DIR, f"brief_{date}.md")
    if os.path.exists(md_path):
        return FileResponse(md_path, media_type="text/markdown", filename=f"brief_{date}.md")
    raise HTTPException(status_code=404, detail="Markdown 尚未生成")
