# 种子数据 — 首次启动时插入默认主题和配置
import logging

logger = logging.getLogger(__name__)


def seed_all():
    """插入所有默认种子数据（仅在表为空时生效）"""
    from app.repositories.topic_repo import TopicRepo
    from app.repositories.config_repo import ConfigRepo
    from app.repositories.crawler_site_repo import CrawlerSiteRepo

    logger.info("检查种子数据...")
    TopicRepo.seed_default()
    ConfigRepo.seed_default()
    CrawlerSiteRepo.seed_default()
    logger.info("种子数据检查完成")
