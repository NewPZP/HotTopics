# 简报相关 ORM 模型
import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.models.database import Base


class BriefModel(Base):
    """每日简报"""
    __tablename__ = "briefs"

    id = Column(String(64), primary_key=True)
    date = Column(String(16), unique=True, index=True, comment="简报日期 YYYY-MM-DD")
    top_news = Column(JSON)
    reports = Column(JSON)
    industry_news = Column(JSON)
    sentiment_data = Column(JSON)
    tomorrow_focus = Column(JSON)
    markdown_content = Column(Text)
    pdf_path = Column(String(512))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(32), default="draft", comment="draft / published")
