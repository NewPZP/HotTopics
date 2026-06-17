# RSS 订阅器
import hashlib
import logging
from datetime import datetime, timezone

import httpx
import feedparser

logger = logging.getLogger(__name__)

# 预配置的 RSS 源
RSS_FEEDS = [
    {"name": "36氪", "url": "https://36kr.com/feed"},
    {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss"},
]


async def fetch_from_rss(topics: list[str]) -> list[dict]:
    """从 RSS 源获取新闻"""
    articles = []

    async with httpx.AsyncClient(timeout=20) as client:
        for feed_info in RSS_FEEDS:
            try:
                resp = await client.get(feed_info["url"], headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    logger.warning(f"RSS请求失败 {feed_info['name']}: HTTP {resp.status_code}")
                    continue

                feed = feedparser.parse(resp.text)
                entries = feed.entries[:15]

                for entry in entries:
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    summary = entry.get("summary", "") or entry.get("description", "")
                    url_hash = hashlib.md5((link or title).encode()).hexdigest()

                    published = entry.get("published_parsed") or entry.get("updated_parsed")
                    if published:
                        try:
                            pub_date = datetime(*published[:6], tzinfo=timezone.utc).isoformat()
                        except Exception:
                            pub_date = datetime.utcnow().isoformat()
                    else:
                        pub_date = datetime.utcnow().isoformat()

                    articles.append({
                        "id": f"rss-{url_hash[:12]}",
                        "source": "rss",
                        "title": title,
                        "content": summary,
                        "url": link,
                        "published_at": pub_date,
                        "author": feed_info["name"],
                        "language": "zh",
                        "topic_tags": topics,
                        "url_hash": url_hash,
                        "raw_data": {"feed_name": feed_info["name"]},
                    })

                logger.info(f"RSS {feed_info['name']}: 获取 {len(entries)} 篇")

            except Exception as e:
                logger.error(f"RSS异常 {feed_info['name']}: {e}")

    return articles
