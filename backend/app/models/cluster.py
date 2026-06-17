# 聚类相关 ORM 模型
import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from app.models.database import Base


class ClusterModel(Base):
    """新闻聚类"""
    __tablename__ = "clusters"

    id = Column(String(64), primary_key=True)
    topic_label = Column(String(256), comment="LLM生成的主题标签")
    icon = Column(String(16))
    article_count = Column(Integer, default=0)
    time_span = Column(String(64))
    importance = Column(Integer, default=3, comment="重要性 1-5")
    summary = Column(Text)
    tags = Column(JSON)
    timeline = Column(JSON, comment="事件时间线列表")
    representative_article_id = Column(String(64))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    cluster_date = Column(String(16), index=True, comment="聚类日期 YYYY-MM-DD")


class ClusterArticleModel(Base):
    """聚类中的文章关联"""
    __tablename__ = "cluster_articles"

    id = Column(String(64), primary_key=True)
    cluster_id = Column(String(64), index=True)
    title = Column(String(512))
    source = Column(String(128))
    date = Column(String(32))
    views = Column(String(32))
    url = Column(String(1024))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
