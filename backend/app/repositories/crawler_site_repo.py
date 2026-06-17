# CrawlerSite Repository — 爬虫站点配置 CRUD
import uuid
import logging
from app.models.database import get_session
from app.models.topic import CrawlerSiteModel

logger = logging.getLogger(__name__)

# 默认站点（与 web_scraper.NEWS_SOURCES 保持一致）
_DEFAULT_SITES = [
    {
        "id": "cs-sina-finance",
        "name": "新浪财经",
        "url": "https://finance.sina.com.cn/",
        "selector": ".m-poster a, .m-list li a, .feed-card-item h2 a, .bd_i_txt_c a",
        "link_attr": "href",
        "category": "金融",
        "enabled": True,
    },
    {
        "id": "cs-eastmoney",
        "name": "东方财富-要闻",
        "url": "https://finance.eastmoney.com/a/czqyw.html",
        "selector": ".title a, .list h2 a, .news-item h3 a",
        "link_attr": "href",
        "category": "金融",
        "enabled": True,
    },
    {
        "id": "cs-163-money",
        "name": "网易财经",
        "url": "https://money.163.com/",
        "selector": ".news-default a, .news-list li a, .headline a, h3 a",
        "link_attr": "href",
        "category": "金融",
        "enabled": True,
    },
    {
        "id": "cs-sina-tech",
        "name": "新浪科技",
        "url": "https://tech.sina.com.cn/",
        "selector": ".tech-news a, .news-item h2 a, .feed-card-item h2 a",
        "link_attr": "href",
        "category": "AI",
        "enabled": True,
    },
    {
        "id": "cs-36kr",
        "name": "36氪-资讯",
        "url": "https://36kr.com/information/web_news",
        "selector": ".article-item-title, .information-title",
        "link_attr": "href",
        "category": "AI",
        "enabled": True,
    },
    {
        "id": "cs-thepaper",
        "name": "澎湃新闻",
        "url": "https://www.thepaper.cn/",
        "selector": ".news_li h2 a, .card-container h3 a, .idx-news-title a",
        "link_attr": "href",
        "category": "综合",
        "enabled": True,
    },
]


class CrawlerSiteRepo:

    @staticmethod
    def get_all() -> list[dict]:
        """获取所有站点"""
        with get_session() as db:
            sites = db.query(CrawlerSiteModel).order_by(CrawlerSiteModel.created_at).all()
            return [_site_to_dict(s) for s in sites]

    @staticmethod
    def get_enabled() -> list[dict]:
        """获取所有已启用站点（供爬虫调用）"""
        with get_session() as db:
            sites = (
                db.query(CrawlerSiteModel)
                .filter(CrawlerSiteModel.enabled == True)
                .order_by(CrawlerSiteModel.created_at)
                .all()
            )
            result = [_site_to_dict(s) for s in sites]
            if not result:
                # 降级：返回默认站点（不持久化）
                logger.warning("DB 无启用爬虫站点，使用硬编码默认站点")
                return [dict(d) for d in _DEFAULT_SITES]
            return result

    @staticmethod
    def create(data: dict) -> dict:
        """新增站点"""
        with get_session() as db:
            site_id = data.get("id") or f"cs-{uuid.uuid4().hex[:8]}"
            site = CrawlerSiteModel(
                id=site_id,
                name=data["name"],
                url=data["url"],
                selector=data["selector"],
                link_attr=data.get("link_attr", "href"),
                category=data.get("category", "综合"),
                enabled=data.get("enabled", True),
            )
            db.add(site)
            db.commit()
            db.refresh(site)
            return _site_to_dict(site)

    @staticmethod
    def update(site_id: str, data: dict) -> dict | None:
        """更新站点"""
        with get_session() as db:
            site = db.query(CrawlerSiteModel).filter(CrawlerSiteModel.id == site_id).first()
            if not site:
                return None
            for field in ("name", "url", "selector", "link_attr", "category"):
                if field in data:
                    setattr(site, field, data[field])
            if "enabled" in data:
                site.enabled = data["enabled"]
            db.commit()
            db.refresh(site)
            return _site_to_dict(site)

    @staticmethod
    def delete(site_id: str) -> bool:
        """删除站点"""
        with get_session() as db:
            site = db.query(CrawlerSiteModel).filter(CrawlerSiteModel.id == site_id).first()
            if not site:
                return False
            db.delete(site)
            db.commit()
            return True

    @staticmethod
    def seed_default():
        """插入默认站点（仅在表为空时生效）"""
        with get_session() as db:
            if db.query(CrawlerSiteModel).count() == 0:
                for ds in _DEFAULT_SITES:
                    db.add(CrawlerSiteModel(**ds))
                db.commit()
                logger.info(f"已插入 {len(_DEFAULT_SITES)} 个默认爬虫站点")


def _site_to_dict(s: CrawlerSiteModel) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "url": s.url,
        "selector": s.selector,
        "linkAttr": s.link_attr,
        "category": s.category,
        "enabled": s.enabled,
    }
