# 去重引擎 — 三层去重策略
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 内存版 BloomFilter（无 Redis 时使用）
_seen_urls: set[str] = set()
_seen_simhashes: set[str] = set()


def exact_dedup(articles: list[dict]) -> tuple[list[dict], int]:
    """精确去重：URL哈希 + 标题哈希去重"""
    seen_urls = set()
    unique = []

    for article in articles:
        url_hash = article.get("url_hash", hashlib.md5(
            (article.get("url", "") or article.get("title", "")).encode()
        ).hexdigest())
        title_hash = hashlib.md5(article.get("title", "").encode()).hexdigest()

        if url_hash in seen_urls or url_hash in _seen_urls:
            continue
        if title_hash in seen_urls:
            continue

        seen_urls.add(url_hash)
        seen_urls.add(title_hash)
        _seen_urls.add(url_hash)
        unique.append(article)

    removed = len(articles) - len(unique)
    logger.info(f"精确去重: 移除 {removed} 篇, 保留 {len(unique)} 篇")
    return unique, removed


def simhash_dedup(articles: list[dict], threshold: int = 3) -> tuple[list[dict], int]:
    """近似去重：SimHash 文本指纹"""
    try:
        from simhash import Simhash
    except ImportError:
        logger.warning("simhash 未安装，跳过近似去重")
        return articles, 0

    unique = []
    seen_hashes = set()
    removed = 0

    for article in articles:
        text = article.get("title", "") + " " + (article.get("content", "") or "")[:500]
        if not text.strip():
            unique.append(article)
            continue

        simhash_value = Simhash(text).value

        is_dup = False
        for existing in list(seen_hashes)[-100:]:  # 只检查最近100条
            if Simhash(existing).distance(Simhash(simhash_value)) <= threshold:
                is_dup = True
                removed += 1
                break

        if not is_dup:
            seen_hashes.add(simhash_value)
            article["simhash_value"] = str(simhash_value)
            unique.append(article)
        else:
            article["is_duplicate"] = True
            unique.append(article)

    logger.info(f"近似去重: 移除 {removed} 篇, 保留 {len([a for a in unique if not a.get('is_duplicate')])} 篇")
    return unique, removed
