# Cluster Repository — 聚类 CRUD
from sqlalchemy import func
from app.models.database import get_session
from app.models.cluster import ClusterModel, ClusterArticleModel


class ClusterRepo:

    @staticmethod
    def list_all(topic: str = "", sort: str = "importance", limit: int = None, offset: int = 0) -> list[dict]:
        """列出聚类（支持分页）"""
        with get_session() as db:
            q = db.query(ClusterModel)
            if topic:
                q = q.filter(ClusterModel.topic_label.contains(topic))
            if sort == "importance":
                q = q.order_by(ClusterModel.importance.desc())
            else:
                q = q.order_by(ClusterModel.created_at.desc())
            if limit is not None:
                q = q.limit(limit).offset(offset)
            return [_cluster_to_dict(c, db) for c in q.all()]

    @staticmethod
    def count_all(topic: str = "") -> int:
        """聚类总数"""
        with get_session() as db:
            q = db.query(ClusterModel)
            if topic:
                q = q.filter(ClusterModel.topic_label.contains(topic))
            return q.count()

    @staticmethod
    def get_by_id(cluster_id: str) -> dict | None:
        """按 ID 获取聚类（含关联文章）"""
        with get_session() as db:
            c = db.query(ClusterModel).filter(ClusterModel.id == cluster_id).first()
            return _cluster_to_dict(c, db) if c else None

    @staticmethod
    def count_today() -> int:
        """今日聚类数量"""
        import datetime
        with get_session() as db:
            today = datetime.date.today()
            return db.query(ClusterModel).filter(
                func.date(ClusterModel.created_at) == today
            ).count()

    @staticmethod
    def upsert(cluster: dict, articles: list[dict] = None):
        """创建或更新聚类及其关联文章"""
        with get_session() as db:
            c = db.query(ClusterModel).filter(ClusterModel.id == cluster["id"]).first()
            if c:
                c.topic_label = cluster.get("topic_label", c.topic_label)
                c.icon = cluster.get("icon", c.icon)
                c.article_count = cluster.get("article_count", c.article_count)
                c.time_span = cluster.get("time_span", c.time_span)
                c.importance = cluster.get("importance", c.importance)
                c.summary = cluster.get("summary", c.summary)
                c.tags = cluster.get("tags", c.tags)
                c.timeline = cluster.get("timeline", c.timeline)
            else:
                c = ClusterModel(
                    id=cluster["id"],
                    topic_label=cluster.get("topic_label", ""),
                    icon=cluster.get("icon", ""),
                    article_count=cluster.get("article_count", 0),
                    time_span=cluster.get("time_span", ""),
                    importance=cluster.get("importance", 3),
                    summary=cluster.get("summary", ""),
                    tags=cluster.get("tags", []),
                    timeline=cluster.get("timeline", []),
                    cluster_date=cluster.get("cluster_date", ""),
                )
                db.add(c)

            # 关联文章
            if articles:
                for art in articles:
                    existing = db.query(ClusterArticleModel).filter(
                        ClusterArticleModel.id == art["id"]
                    ).first()
                    if existing:
                        continue
                    db.add(ClusterArticleModel(
                        id=art["id"],
                        cluster_id=cluster["id"],
                        title=art.get("title", ""),
                        source=art.get("source", ""),
                        date=art.get("date", ""),
                        views=art.get("views", ""),
                        url=art.get("url", ""),
                    ))

            db.commit()
            return _cluster_to_dict(c, db)

    @staticmethod
    def build_graph(max_nodes: int = 25) -> dict:
        """从聚类数据构建关系图，节点数不超过 max_nodes"""
        with get_session() as db:
            clusters = db.query(ClusterModel).order_by(
                ClusterModel.importance.desc()
            ).all()
            nodes = []
            links = []
            name_set = set()
            colors = ["#ef4444", "#f97316", "#2d8eff", "#8b5cf6", "#10b981", "#ec4899"]

            for idx, c in enumerate(clusters):
                if len(nodes) >= max_nodes:
                    break
                tags = c.tags if isinstance(c.tags, list) else []
                # 过滤含乱码的标签（含 ? 或纯非中英文符号）
                tags = [t for t in tags if _valid_tag(t)]
                if c.topic_label and c.topic_label not in name_set:
                    name_set.add(c.topic_label)
                    nodes.append({
                        "name": c.topic_label,
                        "symbolSize": max(20, min(50, c.article_count or 10)),
                        "category": idx % len(colors),
                        "itemStyle": {"color": colors[idx % len(colors)]},
                    })
                for tag in tags:
                    if len(nodes) >= max_nodes:
                        break
                    if tag not in name_set:
                        name_set.add(tag)
                        nodes.append({
                            "name": tag,
                            "symbolSize": 18,
                            "category": idx % len(colors),
                        })
                    if c.topic_label and c.topic_label != tag:
                        links.append({"source": c.topic_label, "target": tag})

            # 过滤 links，确保只包含存在节点间的连线
            links = [l for l in links if l["source"] in name_set and l["target"] in name_set]

            return {"nodes": nodes, "links": links}


def _valid_tag(tag: str) -> bool:
    """过滤乱码标签：排除含 ? 或全部由非中英文符号组成的标签"""
    if not tag or not isinstance(tag, str):
        return False
    if "?" in tag:
        return False
    # 至少包含一个中文字符或英文字母
    import re
    return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]|[a-zA-Z]', tag))


def _cluster_to_dict(c: ClusterModel, db) -> dict:
    articles = db.query(ClusterArticleModel).filter(
        ClusterArticleModel.cluster_id == c.id
    ).order_by(ClusterArticleModel.created_at.desc()).limit(10).all()

    return {
        "id": c.id,
        "label": c.topic_label or "",
        "icon": c.icon or "📌",
        "articleCount": c.article_count or 0,
        "timeSpan": c.time_span or "",
        "importance": c.importance or 3,
        "summary": c.summary or "",
        "tags": [t for t in (c.tags if isinstance(c.tags, list) else []) if _valid_tag(t)],
        "timeline": c.timeline if isinstance(c.timeline, list) else (c.timeline or []),
        "articles": [
            {
                "title": a.title,
                "source": a.source,
                "date": a.date,
                "views": a.views,
                "url": a.url or "",
            }
            for a in articles
        ],
    }
