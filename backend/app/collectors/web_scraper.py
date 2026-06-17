# 通用网页爬虫 — 多源财经/科技/综合新闻采集
import hashlib
import logging
import asyncio
import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 多源新闻站点配置
NEWS_SOURCES = [
    # ── 财经类 ──
    {
        "name": "新浪财经",
        "url": "https://finance.sina.com.cn/",
        "selector": ".m-poster a, .m-list li a, .feed-card-item h2 a, .bd_i_txt_c a",
        "link_attr": "href",
        "category": "金融",
    },
    {
        "name": "东方财富-要闻",
        "url": "https://finance.eastmoney.com/a/czqyw.html",
        "selector": ".title a, .list h2 a, .news-item h3 a",
        "link_attr": "href",
        "category": "金融",
    },
    {
        "name": "网易财经",
        "url": "https://money.163.com/",
        "selector": ".news-default a, .news-list li a, .headline a, h3 a",
        "link_attr": "href",
        "category": "金融",
    },
    # ── 科技类 ──
    {
        "name": "新浪科技",
        "url": "https://tech.sina.com.cn/",
        "selector": ".tech-news a, .news-item h2 a, .feed-card-item h2 a",
        "link_attr": "href",
        "category": "AI",
    },
    {
        "name": "36氪-资讯",
        "url": "https://36kr.com/information/web_news",
        "selector": ".article-item-title, .information-title",
        "link_attr": "href",
        "category": "AI",
    },
    # ── 综合类 ──
    {
        "name": "澎湃新闻",
        "url": "https://www.thepaper.cn/",
        "selector": ".news_li h2 a, .card-container h3 a, .idx-news-title a",
        "link_attr": "href",
        "category": "综合",
    },
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

# 停用词，避免采集到无意义的链接
SKIP_TITLES = {"首页", "登录", "注册", "更多", "下一页", "上一页", "查看全文", "详情", "阅读原文"}
SKIP_HOSTS = {"login", "reg", "passport", "account"}


def _is_valid_title(title: str) -> bool:
    """过滤无效标题"""
    t = title.strip()
    if not t or len(t) < 4 or t in SKIP_TITLES:
        return False
    return True


def _match_topics(title: str, topics: list[str]) -> bool:
    """简单的关键词匹配，判断文章是否相关"""
    title_lower = title.lower()
    for topic in topics:
        if topic.lower() in title_lower:
            return True
    # 始终保留：至少匹配一个通用关键词
    general = ["经济", "科技", "市场", "产业", "企业", "政策", "数据", "芯片", "AI",
               "人工智能", "新能源", "光伏", "电池", "汽车", "金融", "银行", "证券",
               "基金", "股票", "投资", "融资", "上市", "降准", "利率", "央行", "美元"]
    for kw in general:
        if kw in title_lower:
            return True
    return False


def _clean_url(url: str, base_url: str) -> str:
    """补全相对 URL"""
    if not url or url.startswith("#") or url.startswith("javascript"):
        return ""
    if url.startswith("//"):
        return "https:" + url
    if not url.startswith("http"):
        url = base_url.rstrip("/") + "/" + url.lstrip("/")
    # 过滤非新闻域名
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or ""
        if any(s in host for s in SKIP_HOSTS):
            return ""
    except Exception:
        return ""
    return url


async def _extract_content(client: httpx.AsyncClient, url: str) -> str:
    """尝试提取文章正文"""
    try:
        resp = await client.get(url, headers={
            "User-Agent": USER_AGENTS[0],
            "Accept": "text/html,application/xhtml+xml",
        })
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        # 移除脚本和样式
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        # 常见正文容器
        for sel in ["article", ".article", ".article-content", ".post-content",
                     ".news-content", "#article", ".content", "main"]:
            body = soup.select_one(sel)
            if body:
                text = body.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return text[:2000]
        # 回退：取 body 内最长文本块
        body = soup.find("body")
        if body:
            text = body.get_text(separator="\n", strip=True)
            return text[:2000]
    except Exception:
        pass
    return ""


async def fetch_from_crawler(topics: list[str]) -> list[dict]:
    """从多个新闻站点爬取新闻（优先从 DB 读取站点配置）"""
    # 优先从数据库读取启用的站点
    sources = _load_sources_from_db()
    if not sources:
        sources = NEWS_SOURCES

    articles = []
    ua_idx = 0

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for source in sources:
            ua = USER_AGENTS[ua_idx % len(USER_AGENTS)]
            ua_idx += 1

            try:
                resp = await client.get(
                    source["url"],
                    headers={"User-Agent": ua, "Accept": "text/html,application/xhtml+xml"},
                )
                if resp.status_code != 200:
                    logger.warning(f"爬虫 {source['name']}: HTTP {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                items = soup.select(source["selector"])

                count = 0
                for item in items:
                    title = item.get_text(strip=True)
                    if not _is_valid_title(title):
                        continue
                    if not _match_topics(title, topics):
                        continue

                    link_attr = source.get("link_attr", "href")
                    url = _clean_url(item.get(link_attr, ""), source["url"])
                    if not url:
                        continue

                    url_hash = hashlib.md5((url or title).encode()).hexdigest()

                    # 可选：抓取正文
                    content = title
                    if count < 3:  # 仅前3篇抓正文，避免太慢
                        body = await _extract_content(client, url)
                        if body:
                            content = body

                    articles.append({
                        "id": f"crawler-{url_hash[:12]}",
                        "source": "crawler",
                        "title": title,
                        "content": content,
                        "url": url,
                        "published_at": datetime.now().isoformat(),
                        "author": source["name"],
                        "language": "zh",
                        "topic_tags": [source["category"]] + topics,
                        "url_hash": url_hash,
                        "raw_data": {"source_name": source["name"], "category": source["category"]},
                    })
                    count += 1

                logger.info(f"爬虫 {source['name']}: 匹配 {count} 篇相关新闻")

            except Exception as e:
                logger.error(f"爬虫异常 {source['name']}: {e}")

            # 请求间隔，避免被封
            await asyncio.sleep(2)

    return articles


def _load_sources_from_db() -> list[dict]:
    """从数据库加载已启用的爬虫站点，转换为爬虫所需格式"""
    try:
        from app.repositories.crawler_site_repo import CrawlerSiteRepo
        db_sites = CrawlerSiteRepo.get_enabled()
        return [
            {
                "name": s["name"],
                "url": s["url"],
                "selector": s["selector"],
                "link_attr": s.get("linkAttr", "href"),
                "category": s.get("category", "综合"),
            }
            for s in db_sites
        ]
    except Exception as e:
        logger.warning(f"从 DB 加载爬虫站点失败，使用硬编码默认: {e}")
        return []
