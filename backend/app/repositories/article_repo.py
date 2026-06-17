# Article Repository — 文章 CRUD
import datetime
from sqlalchemy import func, and_
from app.models.database import get_session
from app.models.article import RawArticle, ProcessedArticle


class ArticleRepo:

    @staticmethod
    def upsert_raw_articles(articles: list[dict]) -> int:
        """批量 upsert 原始文章（按 url_hash 去重）"""
        with get_session() as db:
            count = 0
            for art in articles:
                existing = db.query(RawArticle).filter(
                    RawArticle.url_hash == art.get("url_hash", "")
                ).first()
                if existing:
                    continue
                db.add(RawArticle(
                    id=art["id"],
                    source=art.get("source", ""),
                    title=art.get("title", ""),
                    content=art.get("content", ""),
                    url=art.get("url", ""),
                    published_at=art.get("published_at"),
                    author=art.get("author", ""),
                    language=art.get("language", "zh"),
                    topic_tags=art.get("topic_tags", []),
                    raw_data=art.get("raw_data", {}),
                    url_hash=art.get("url_hash", ""),
                    status="raw",
                ))
                count += 1
            db.commit()
            return count

    @staticmethod
    def upsert_processed_articles(articles: list[dict]) -> int:
        """批量 upsert 清洗后文章"""
        with get_session() as db:
            count = 0
            for art in articles:
                existing = db.query(ProcessedArticle).filter(
                    ProcessedArticle.id == art["id"]
                ).first()
                if existing:
                    for k, v in art.items():
                        if hasattr(existing, k) and k != "id":
                            setattr(existing, k, v)
                else:
                    db.add(ProcessedArticle(
                        id=art["id"],
                        raw_article_id=art.get("raw_article_id", ""),
                        source=art.get("source", ""),
                        title=art.get("title", ""),
                        content=art.get("content", ""),
                        url=art.get("url", ""),
                        published_at=art.get("published_at"),
                        author=art.get("author", ""),
                        language=art.get("language", "zh"),
                        topic_tags=art.get("topic_tags", []),
                        cluster_id=art.get("cluster_id", ""),
                        simhash_value=art.get("simhash_value", ""),
                        is_duplicate=art.get("is_duplicate", False),
                        duplicate_of=art.get("duplicate_of", ""),
                        embedding=art.get("embedding"),
                    ))
                    count += 1
            db.commit()
            return count

    @staticmethod
    def update_cluster_ids(article_cluster_map: dict[str, str]):
        """更新文章的 cluster_id"""
        with get_session() as db:
            for article_id, cluster_id in article_cluster_map.items():
                db.query(ProcessedArticle).filter(
                    ProcessedArticle.id == article_id
                ).update({"cluster_id": cluster_id})
            db.commit()

    @staticmethod
    def count_today() -> int:
        """今日采集数量"""
        with get_session() as db:
            today = datetime.date.today()
            return db.query(RawArticle).filter(
                func.date(RawArticle.created_at) == today
            ).count()

    @staticmethod
    def count_on_date(target: datetime.date) -> int:
        """指定日期的原始文章采集量"""
        with get_session() as db:
            return db.query(RawArticle).filter(
                func.date(RawArticle.created_at) == target
            ).count()

    @staticmethod
    def count_all() -> int:
        """全部原始文章数量"""
        with get_session() as db:
            return db.query(RawArticle).count()

    @staticmethod
    def count_unique_today() -> int:
        """今日去重后数量"""
        with get_session() as db:
            today = datetime.date.today()
            return db.query(ProcessedArticle).filter(
                and_(
                    func.date(ProcessedArticle.created_at) == today,
                    ProcessedArticle.is_duplicate == False,
                )
            ).count()

    @staticmethod
    def count_unique_all() -> int:
        """全部去重后文章数量"""
        with get_session() as db:
            return db.query(ProcessedArticle).filter(
                ProcessedArticle.is_duplicate == False
            ).count()

    @staticmethod
    def latest_article_time() -> datetime.datetime | None:
        """最新一篇文章的入库时间（兜底用）"""
        with get_session() as db:
            article = db.query(RawArticle).order_by(
                RawArticle.created_at.desc()
            ).first()
            return article.created_at if article else None

    @staticmethod
    def get_daily_counts(days: int = 7) -> list[dict]:
        """近 N 天每日文章数量"""
        with get_session() as db:
            results = []
            for i in range(days - 1, -1, -1):
                d = datetime.date.today() - datetime.timedelta(days=i)
                raw_count = db.query(RawArticle).filter(
                    func.date(RawArticle.created_at) == d
                ).count()
                unique_count = db.query(ProcessedArticle).filter(
                    and_(
                        func.date(ProcessedArticle.created_at) == d,
                        ProcessedArticle.is_duplicate == False,
                    )
                ).count()
                results.append({
                    "date": d.strftime("%m-%d"),
                    "raw": raw_count,
                    "unique": unique_count,
                })
            return results

    @staticmethod
    def get_top_articles(limit: int = 5) -> list[dict]:
        """获取今日热度最高文章（去重后）"""
        with get_session() as db:
            today = datetime.date.today()
            articles = db.query(ProcessedArticle).filter(
                and_(
                    func.date(ProcessedArticle.created_at) == today,
                    ProcessedArticle.is_duplicate == False,
                )
            ).order_by(ProcessedArticle.created_at.desc()).limit(limit).all()

            result = []
            for idx, a in enumerate(articles):
                tags = a.topic_tags if a.topic_tags else []
                result.append({
                    "id": a.id,
                    "rank": idx + 1,
                    "title": a.title,
                    "summary": (a.content or "")[:80],
                    "source": a.source or a.author or "",
                    "publishedAt": str(a.published_at) if a.published_at else "",
                    "hotIndex": 90 - idx * 5,
                    "tags": tags if isinstance(tags, list) else [tags],
                })
            return result
