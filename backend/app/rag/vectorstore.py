# 向量存储 — Elasticsearch 封装（必需）
import logging
from elasticsearch import AsyncElasticsearch
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_es_client() -> AsyncElasticsearch:
    """创建带认证的 ES 客户端"""
    kwargs = {"hosts": [settings.ES_HOST]}
    if settings.ES_USER and settings.ES_PASSWORD:
        kwargs["basic_auth"] = (settings.ES_USER, settings.ES_PASSWORD)
    return AsyncElasticsearch(**kwargs)


async def index_articles(articles: list[dict]):
    """将文章索引到 ES"""
    es = _get_es_client()
    try:
        index_name = f"{settings.ES_INDEX_PREFIX}_articles"
        for article in articles:
            doc = {
                "title": article.get("title", ""),
                "content": article.get("content", "")[:1000],
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "published_at": article.get("published_at", ""),
                "topic_tags": article.get("topic_tags", []),
            }
            await es.index(index=index_name, id=article.get("id"), document=doc)
        logger.info(f"ES索引完成: {len(articles)} 篇")
    finally:
        await es.close()
