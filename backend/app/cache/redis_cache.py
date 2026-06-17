# Redis 缓存层（必需）
import logging
import json
from typing import Optional, Any
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_client = None


async def init_redis():
    """初始化 Redis 连接"""
    global _redis_client
    import redis.asyncio as aioredis
    _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await _redis_client.ping()
    logger.info("Redis 连接成功")


async def close_redis():
    """关闭 Redis 连接"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def cache_get(key: str) -> Optional[Any]:
    """获取缓存"""
    value = await _redis_client.get(key)
    return json.loads(value) if value else None


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600):
    """设置缓存"""
    await _redis_client.set(key, json.dumps(value, default=str), ex=ttl_seconds)


async def cache_delete(key: str):
    """删除缓存"""
    await _redis_client.delete(key)


# ── 业务缓存快捷方法 ──

async def get_cached_articles(topic: str) -> Optional[list[dict]]:
    """获取已缓存的文章"""
    return await cache_get(f"articles:{topic}")


async def set_cached_articles(topic: str, articles: list[dict], ttl_hours: int = 2):
    """缓存文章"""
    await cache_set(f"articles:{topic}", articles, ttl_hours * 3600)


async def is_url_seen(url_hash: str) -> bool:
    """检查 URL 是否已处理"""
    result = await cache_get(f"seen:{url_hash}")
    return result is not None


async def mark_url_seen(url_hash: str):
    """标记 URL 已处理"""
    await cache_set(f"seen:{url_hash}", True, 7 * 24 * 3600)  # 7天


async def get_cached_report(cluster_id: str) -> Optional[dict]:
    """获取已缓存的研报"""
    return await cache_get(f"report:{cluster_id}")


async def set_cached_report(cluster_id: str, report: dict):
    """缓存研报"""
    await cache_set(f"report:{cluster_id}", report, 7 * 24 * 3600)


async def get_cached_brief(date: str) -> Optional[dict]:
    """获取已缓存的日报"""
    return await cache_get(f"brief:{date}")


async def set_cached_brief(date: str, brief: dict):
    """缓存日报"""
    await cache_set(f"brief:{date}", brief, 30 * 24 * 3600)
