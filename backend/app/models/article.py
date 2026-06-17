# 文章相关 ORM 模型
import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from app.models.database import Base


class RawArticle(Base):
    """原始采集文章"""
    __tablename__ = "raw_articles"

    id = Column(String(64), primary_key=True)
    source = Column(String(64), nullable=False, comment="来源: newsapi / crawler / rss")
    title = Column(String(512), nullable=False)
    content = Column(Text)
    url = Column(String(1024))
    published_at = Column(DateTime)
    author = Column(String(128))
    language = Column(String(16))
    topic_tags = Column(JSON)
    raw_data = Column(JSON)
    url_hash = Column(String(64), unique=True, index=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(32), default="raw", comment="raw / processed / discarded")


class ProcessedArticle(Base):
    """清洗后的文章"""
    __tablename__ = "processed_articles"

    id = Column(String(64), primary_key=True)
    raw_article_id = Column(String(64), index=True)
    source = Column(String(64))
    title = Column(String(512), nullable=False)
    content = Column(Text)
    url = Column(String(1024))
    published_at = Column(DateTime)
    author = Column(String(128))
    language = Column(String(16))
    topic_tags = Column(JSON)
    cluster_id = Column(String(64), index=True)

    simhash_value = Column(String(64))
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(String(64))

    embedding = Column(JSON)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
