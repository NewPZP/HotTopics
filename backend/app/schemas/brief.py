# 简报相关 Pydantic Schema — 严格匹配前端 TypeScript 类型
from pydantic import BaseModel, Field
from typing import Optional


class SourceArticle(BaseModel):
    name: str
    time: str
    title: str
    excerpt: str
    url: str = ""


class KeyDataItem(BaseModel):
    label: str
    value: str
    unit: str = ""
    color: str = "blue"


class TopNews(BaseModel):
    id: str
    rank: int
    title: str
    summary: str
    source: str
    publishedAt: str = Field(alias="publishedAt")
    hotIndex: int = Field(alias="hotIndex")
    tags: list[str] = []
    sources: list[SourceArticle] = []
    keyData: list[KeyDataItem] = Field(default_factory=list, alias="keyData")

    class Config:
        populate_by_name = True


class BriefReport(BaseModel):
    id: str
    title: str
    summary: str
    sourceCount: int = Field(alias="sourceCount")
    generatedAt: str = Field(alias="generatedAt")
    importance: int
    sections: list[str] = []

    class Config:
        populate_by_name = True


class IndustryNewsGroup(BaseModel):
    industry: str
    icon: str
    items: list[str] = []


class SentimentData(BaseModel):
    sentiment: int
    sentimentLabel: str = Field(alias="sentimentLabel")
    sentimentTrend: str = Field(alias="sentimentTrend")
    hotIndex: int = Field(alias="hotIndex")
    hotLabel: str = Field(alias="hotLabel")
    hotTrend: str = Field(alias="hotTrend")
    volatility: int
    volatilityLabel: str = Field(alias="volatilityLabel")
    volatilityTrend: str = Field(alias="volatilityTrend")

    class Config:
        populate_by_name = True


class Brief(BaseModel):
    date: str
    topNews: list[TopNews] = Field(default_factory=list, alias="topNews")
    reports: list[BriefReport] = Field(default_factory=list)
    industryNews: list[IndustryNewsGroup] = Field(default_factory=list, alias="industryNews")
    sentimentData: SentimentData = Field(alias="sentimentData")
    tomorrowFocus: list[str] = Field(default_factory=list, alias="tomorrowFocus")

    class Config:
        populate_by_name = True
