# 检索器 — ES 混合检索（kNN + BM25）
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


async def hybrid_search(
    query: str,
    articles: list[dict] = None,
    top_k: int = 10,
) -> list[dict]:
    """ES 混合检索：multi_match 标题^3 + 正文"""
    es = _get_es_client()
    try:
        index_name = f"{settings.ES_INDEX_PREFIX}_articles"
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content"],
                    "type": "best_fields",
                }
            },
            "size": top_k,
        }
        resp = await es.search(index=index_name, body=body)
        return [hit["_source"] for hit in resp["hits"]["hits"]]
    finally:
        await es.close()
