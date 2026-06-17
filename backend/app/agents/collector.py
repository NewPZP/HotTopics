# CollectorAgent — 多源信息采集（纯爬虫驱动）
import logging
from app.agents.state import PlatformState
from app.collectors.web_scraper import fetch_from_crawler

logger = logging.getLogger(__name__)


async def collector_node(state: PlatformState) -> PlatformState:
    """采集节点：爬虫多源采集，结果持久化到数据库"""
    topics = state.get("topics", ["AI", "金融", "新能源"])
    state["current_step"] = "collect"
    state["progress"] = 5.0
    logger.info(f"[CollectorAgent] 启动采集，主题: {topics}")

    all_articles = []
    errors = []

    # 爬虫采集
    try:
        articles = await fetch_from_crawler(topics)
        all_articles.extend(articles)
    except Exception as e:
        errors.append(f"crawler: {str(e)}")
        logger.error(f"[CollectorAgent] 爬虫采集异常: {e}")

    # 持久化原始文章到数据库
    if all_articles:
        try:
            from app.repositories.article_repo import ArticleRepo
            saved = ArticleRepo.upsert_raw_articles(all_articles)
            logger.info(f"[CollectorAgent] 持久化到 DB: {saved} 篇新文章")
        except Exception as e:
            logger.warning(f"[CollectorAgent] DB 持久化失败: {e}")

    state["raw_articles"] = all_articles
    state["collect_count"] = len(all_articles)
    state["collection_errors"] = errors
    state["progress"] = 10.0

    logger.info(f"[CollectorAgent] 采集完成: 共 {len(all_articles)} 篇, 错误 {len(errors)} 个")
    return state
