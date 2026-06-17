# 爬虫站点配置 API 路由
from fastapi import APIRouter, Body, HTTPException
from app.repositories.crawler_site_repo import CrawlerSiteRepo

router = APIRouter()


@router.get("/config/crawler-sites")
async def get_crawler_sites():
    """获取所有爬虫站点配置"""
    sites = CrawlerSiteRepo.get_all()
    return {"data": sites}


@router.post("/config/crawler-sites")
async def create_crawler_site(site: dict = Body(...)):
    """新增爬虫站点"""
    try:
        result = CrawlerSiteRepo.create(site)
        return {"data": result, "message": "站点已添加"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/config/crawler-sites/{site_id}")
async def update_crawler_site(site_id: str, site: dict = Body(...)):
    """更新爬虫站点"""
    result = CrawlerSiteRepo.update(site_id, site)
    if result is None:
        raise HTTPException(status_code=404, detail="站点不存在")
    return {"data": result, "message": "站点已更新"}


@router.delete("/config/crawler-sites/{site_id}")
async def delete_crawler_site(site_id: str):
    """删除爬虫站点"""
    ok = CrawlerSiteRepo.delete(site_id)
    if not ok:
        raise HTTPException(status_code=404, detail="站点不存在")
    return {"message": "站点已删除"}
