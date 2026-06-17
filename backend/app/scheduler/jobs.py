# 任务调度 — APScheduler 定时任务
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler()


def start_scheduler():
    """启动调度器：优先从 DB 读取配置，回退到 .env 默认值"""
    if not scheduler.running:
        from app.repositories.config_repo import ConfigRepo
        db_config = ConfigRepo.get_all()
        collect_cron = db_config.get("collectCron") or settings.COLLECT_CRON
        brief_gen_time = db_config.get("briefGenTime") or settings.BRIEF_GEN_TIME

        # 采集任务
        scheduler.add_job(
            _scheduled_collect,
            CronTrigger.from_crontab(collect_cron),
            id="collect_job",
            name="定时采集",
            replace_existing=True,
        )

        # 日报生成任务
        hour, minute = brief_gen_time.split(":")
        scheduler.add_job(
            _scheduled_brief_generation,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id="brief_job",
            name="日报生成",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(f"调度器已启动: 采集={collect_cron}, 日报={brief_gen_time}")


def shutdown_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("调度器已停止")


def reload_scheduler_config():
    """配置更新后重载调度任务：从 DB 读取最新配置并重新调度"""
    from app.repositories.config_repo import ConfigRepo
    db_config = ConfigRepo.get_all()
    new_cron = db_config.get("collectCron", settings.COLLECT_CRON)
    new_brief_time = db_config.get("briefGenTime", settings.BRIEF_GEN_TIME)

    if not scheduler.running:
        logger.info("调度器未运行，跳过重载")
        return

    # 重新调度采集任务
    try:
        scheduler.reschedule_job(
            "collect_job",
            trigger=CronTrigger.from_crontab(new_cron),
        )
        logger.info(f"采集任务已更新: {new_cron}")
    except Exception as e:
        logger.warning(f"更新采集任务失败: {e}")

    # 重新调度日报生成任务
    try:
        hour, minute = new_brief_time.split(":")
        scheduler.reschedule_job(
            "brief_job",
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        )
        logger.info(f"日报任务已更新: {new_brief_time}")
    except Exception as e:
        logger.warning(f"更新日报任务失败: {e}")


async def _scheduled_collect():
    """定时采集任务"""
    logger.info(f"[Scheduler] 定时采集触发 {datetime.now().isoformat()}")
    try:
        from app.agents.graph import run_workflow
        await run_workflow()
    except Exception as e:
        logger.error(f"[Scheduler] 定时采集失败: {e}")


async def _scheduled_brief_generation():
    """定时日报生成"""
    logger.info(f"[Scheduler] 日报生成触发 {datetime.now().isoformat()}")
    try:
        from app.agents.graph import run_workflow
        await run_workflow()
    except Exception as e:
        logger.error(f"[Scheduler] 日报生成失败: {e}")
