# 研报相关 ORM 模型
import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean
from app.models.database import Base


class ReportModel(Base):
    """深度研报"""
    __tablename__ = "reports"

    id = Column(String(64), primary_key=True)
    title = Column(String(512), nullable=False)
    subtitle = Column(String(512))
    summary = Column(Text)
    generated_at = Column(String(128))
    source_count = Column(Integer, default=0)
    importance = Column(Integer, default=3)
    time_span = Column(String(64))
    tags = Column(JSON)
    is_featured = Column(Boolean, default=False)
    status = Column(String(32), default="draft", comment="published / reviewing / draft")
    cluster_id = Column(String(64), index=True)

    sections = Column(JSON, comment="ReportSection 列表")
    sources = Column(JSON, comment="SourceCitation 列表")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
