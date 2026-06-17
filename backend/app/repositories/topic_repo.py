# Topic Repository — 监控主题 CRUD
from app.models.database import get_session
from app.models.topic import TopicModel


class TopicRepo:

    @staticmethod
    def list_all() -> list[dict]:
        """列出所有主题"""
        with get_session() as db:
            topics = db.query(TopicModel).order_by(TopicModel.created_at.desc()).all()
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "keywords": t.keywords or [],
                    "enabled": t.enabled,
                }
                for t in topics
            ]

    @staticmethod
    def create(topic: dict) -> dict:
        """创建主题"""
        with get_session() as db:
            t = TopicModel(
                id=topic["id"],
                name=topic["name"],
                keywords=topic.get("keywords", []),
                enabled=topic.get("enabled", True),
            )
            db.add(t)
            db.commit()
            return {
                "id": t.id,
                "name": t.name,
                "keywords": t.keywords or [],
                "enabled": t.enabled,
            }

    @staticmethod
    def update(topic_id: str, topic: dict) -> dict | None:
        """更新主题"""
        with get_session() as db:
            t = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
            if not t:
                return None
            if "name" in topic:
                t.name = topic["name"]
            if "keywords" in topic:
                t.keywords = topic["keywords"]
            if "enabled" in topic:
                t.enabled = topic["enabled"]
            db.commit()
            db.refresh(t)
            return {
                "id": t.id,
                "name": t.name,
                "keywords": t.keywords or [],
                "enabled": t.enabled,
            }

    @staticmethod
    def delete(topic_id: str) -> bool:
        """删除主题"""
        with get_session() as db:
            t = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
            if t:
                db.delete(t)
                db.commit()
                return True
            return False

    @staticmethod
    def get_enabled_keywords() -> list[str]:
        """获取所有已启用主题的关键词列表"""
        with get_session() as db:
            topics = db.query(TopicModel).filter(TopicModel.enabled == True).all()
            keywords = []
            for t in topics:
                if t.keywords:
                    keywords.extend([kw for kw in t.keywords if kw])
            return keywords

    @staticmethod
    def seed_default():
        """插入默认主题（如果表为空）"""
        with get_session() as db:
            if db.query(TopicModel).count() > 0:
                return
            defaults = [
                ("topic-ai", "AI监管与政策", ["AI", "监管", "政策", "芯片管制"]),
                ("topic-semi", "半导体供应链", ["半导体", "芯片", "供应链", "台积电"]),
                ("topic-ev", "新能源汽车", ["新能源", "电动汽车", "出海", "电池"]),
                ("topic-macro", "宏观经济", ["GDP", "CPI", "PMI", "央行", "利率"]),
            ]
            for tid, name, keywords in defaults:
                db.add(TopicModel(id=tid, name=name, keywords=keywords, enabled=True))
            db.commit()
