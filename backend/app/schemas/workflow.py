# 工作流与监控相关 Pydantic Schema — 严格匹配前端 TypeScript 类型
from pydantic import BaseModel, Field
from typing import Optional


class PipelineStep(BaseModel):
    name: str
    label: str
    status: str  # done / running / pending
    count: str
    progress: Optional[int] = None


class AgentStatus(BaseModel):
    name: str
    label: str
    status: str  # idle / running / pending
    detail: str


class LogEntry(BaseModel):
    timestamp: str
    level: str  # INFO / WARN / ERROR
    agent: str
    message: str


class MemoryMetrics(BaseModel):
    used: float
    total: float


class SystemMetrics(BaseModel):
    cpu: float
    memory: MemoryMetrics
    redis: float
    dbConnections: float = Field(alias="dbConnections")

    class Config:
        populate_by_name = True


class WorkflowState(BaseModel):
    isRunning: bool = Field(alias="isRunning")
    lastCollectTime: str = Field(alias="lastCollectTime")
    nextCollectTime: str = Field(alias="nextCollectTime")
    totalProgress: float = Field(alias="totalProgress")
    estimatedRemaining: str = Field(alias="estimatedRemaining")
    pipelineSteps: list[PipelineStep] = Field(default_factory=list, alias="pipelineSteps")
    agents: list[AgentStatus] = []
    logs: list[LogEntry] = []
    metrics: SystemMetrics

    class Config:
        populate_by_name = True
