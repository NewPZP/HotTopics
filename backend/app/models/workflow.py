# 工作流运行记录 ORM 模型
import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Float
from app.models.database import Base


class WorkflowRunModel(Base):
    """工作流运行记录"""
    __tablename__ = "workflow_runs"

    id = Column(String(64), primary_key=True)
    status = Column(String(32), default="running", comment="running / completed / failed")
    step = Column(String(64), comment="当前执行步骤")
    progress = Column(Float, default=0.0)
    error_message = Column(Text)

    input_state = Column(JSON)
    output_state = Column(JSON)
    checkpoints = Column(JSON)

    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
