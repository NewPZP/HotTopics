# 配置管理 API 路由 — 真实数据驱动
from fastapi import APIRouter, Body
from app.repositories.config_repo import ConfigRepo
from app.scheduler.jobs import reload_scheduler_config

router = APIRouter()


@router.get("/config")
async def get_config():
    """获取系统配置 — DB 查询"""
    config = ConfigRepo.get_all()
    return {"data": config}


@router.put("/config")
async def update_config(config: dict = Body(...)):
    """更新系统配置 — DB 持久化"""
    for key, value in config.items():
        ConfigRepo.set(key, str(value))
    # 配置更新后重载调度器
    reload_scheduler_config()
    return {"data": ConfigRepo.get_all(), "message": "配置已保存"}
