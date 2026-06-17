# 主题与配置相关 ORM 模型
import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from app.models.database import Base


class TopicModel(Base):
    """监控主题"""
    __tablename__ = "topics"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    keywords = Column(JSON)
    enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class DataSourceModel(Base):
    """数据源配置"""
    __tablename__ = "data_sources"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    icon = Column(String(32))
    icon_color = Column(String(32))
    sub_label = Column(String(256))
    enabled = Column(Boolean, default=True)
    config_json = Column(JSON)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class CrawlerSiteModel(Base):
    """爬虫站点配置"""
    __tablename__ = "crawler_sites"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False, comment="站点名称")
    url = Column(String(1024), nullable=False, comment="站点首页URL")
    selector = Column(String(512), nullable=False, comment="CSS选择器")
    link_attr = Column(String(32), default="href", comment="链接属性名")
    category = Column(String(64), default="综合", comment="分类标签")
    enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class SystemConfigModel(Base):
    """系统配置键值对"""
    __tablename__ = "system_configs"

    key = Column(String(128), primary_key=True)
    value = Column(Text)
    value_type = Column(String(32), default="string")
    description = Column(String(256))

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
