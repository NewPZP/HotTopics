# 聚类分析相关 Pydantic Schema — 严格匹配前端 TypeScript 类型
from pydantic import BaseModel, Field
from typing import Optional


class EventTimelineItem(BaseModel):
    date: str
    title: str
    description: str
    done: bool = False


class ClusterArticle(BaseModel):
    title: str
    source: str
    date: str
    views: str
    url: str = ""


class NewsCluster(BaseModel):
    id: str
    label: str
    icon: str
    articleCount: int = Field(alias="articleCount")
    timeSpan: str = Field(alias="timeSpan")
    importance: int
    summary: str
    tags: list[str] = []
    timeline: list[EventTimelineItem] = []
    articles: list[ClusterArticle] = []

    class Config:
        populate_by_name = True


class ClusterNode(BaseModel):
    name: str
    symbolSize: int = Field(alias="symbolSize")
    category: int
    itemStyle: Optional[dict] = Field(default=None, alias="itemStyle")

    class Config:
        populate_by_name = True


class ClusterLink(BaseModel):
    source: str
    target: str


class ClusterGraph(BaseModel):
    nodes: list[ClusterNode]
    links: list[ClusterLink]
