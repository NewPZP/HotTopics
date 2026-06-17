# Config Repository — 系统配置与数据源 CRUD
from app.models.database import get_session
from app.models.topic import SystemConfigModel, DataSourceModel


class ConfigRepo:

    @staticmethod
    def get_all() -> dict:
        """获取所有系统配置"""
        with get_session() as db:
            configs = db.query(SystemConfigModel).all()
            result = {}
            for c in configs:
                result[c.key] = c.value
            return result

    @staticmethod
    def get(key: str, default: str = "") -> str:
        """获取单个配置值"""
        with get_session() as db:
            c = db.query(SystemConfigModel).filter(SystemConfigModel.key == key).first()
            return c.value if c else default

    @staticmethod
    def set(key: str, value: str, description: str = ""):
        """设置配置值"""
        with get_session() as db:
            c = db.query(SystemConfigModel).filter(SystemConfigModel.key == key).first()
            if c:
                c.value = value
            else:
                c = SystemConfigModel(key=key, value=value, description=description)
                db.add(c)
            db.commit()

    @staticmethod
    def list_sources() -> list[dict]:
        """获取所有数据源"""
        with get_session() as db:
            sources = db.query(DataSourceModel).order_by(DataSourceModel.created_at).all()
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "icon": s.icon or "",
                    "iconColor": s.icon_color or "",
                    "subLabel": s.sub_label or "",
                    "enabled": s.enabled,
                }
                for s in sources
            ]

    @staticmethod
    def update_sources(sources: list[dict]):
        """批量更新数据源"""
        with get_session() as db:
            for src in sources:
                s = db.query(DataSourceModel).filter(DataSourceModel.id == src["id"]).first()
                if s:
                    s.name = src.get("name", s.name)
                    s.icon = src.get("icon", s.icon)
                    s.icon_color = src.get("iconColor", s.icon_color)
                    s.sub_label = src.get("subLabel", s.sub_label)
                    s.enabled = src.get("enabled", s.enabled)
            db.commit()

    @staticmethod
    def seed_default():
        """插入默认配置（如果表为空）"""
        from app.config import get_settings
        settings = get_settings()
        with get_session() as db:
            # 系统配置
            if db.query(SystemConfigModel).count() == 0:
                defaults = [
                    ("collectCron", settings.COLLECT_CRON, "采集 Cron 表达式"),
                    ("briefGenTime", settings.BRIEF_GEN_TIME, "日报生成时间"),
                    ("pushChannels", "api,file", "推送渠道"),
                ]
                for key, value, desc in defaults:
                    db.add(SystemConfigModel(key=key, value=value, description=desc))

            # 数据源（已迁移至 crawler_site_repo.py，此处保持兼容空集合）
            if db.query(DataSourceModel).count() == 0:
                pass

            db.commit()
