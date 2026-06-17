# 通用 Pydantic Schema
from pydantic import BaseModel, Field
from typing import Optional


class StatItem(BaseModel):
    label: str
    value: str
    icon: str
    iconBg: str = Field(alias="iconBg")
    iconColor: str = Field(alias="iconColor")
    trend: str
    trendType: str = Field(alias="trendType", description="up / down / neutral")
    subLabel: Optional[str] = Field(default=None, alias="subLabel")

    class Config:
        populate_by_name = True


class PaginationInfo(BaseModel):
    current: int
    total: int
    pageSize: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


class TopicItem(BaseModel):
    id: str
    name: str
    keywords: list[str] = []
    enabled: bool = True


class TopicUpdate(BaseModel):
    """主题更新 — 所有字段可选，只传需要改的"""
    name: Optional[str] = None
    keywords: Optional[list[str]] = None
    enabled: Optional[bool] = None


class DataSourceItem(BaseModel):
    id: str
    name: str
    icon: str
    iconColor: str = Field(alias="iconColor")
    subLabel: str = Field(alias="subLabel")
    enabled: bool = True

    class Config:
        populate_by_name = True


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Optional[object] = None


class PaginatedResponse(ApiResponse):
    pagination: Optional[PaginationInfo] = None
