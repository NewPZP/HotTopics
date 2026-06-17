# 研报相关 Pydantic Schema — 严格匹配前端 TypeScript 类型
from pydantic import BaseModel, Field
from typing import Optional


class KeyDataPoint(BaseModel):
    label: str
    value: str
    color: str


class RiskItem(BaseModel):
    category: str
    categoryColor: str = Field(alias="categoryColor")
    title: str
    description: str

    class Config:
        populate_by_name = True


class ReportSection(BaseModel):
    id: str
    title: str
    content: list[str] = []
    highlights: Optional[list[KeyDataPoint]] = None
    keyParticipants: Optional[list[str]] = Field(default=None, alias="keyParticipants")
    shortTerm: Optional[str] = Field(default=None, alias="shortTerm")
    longTerm: Optional[str] = Field(default=None, alias="longTerm")
    keyDrivers: Optional[list[str]] = Field(default=None, alias="keyDrivers")
    risks: Optional[list[RiskItem]] = None

    class Config:
        populate_by_name = True


class SourceCitation(BaseModel):
    index: int
    source: str
    title: str
    date: str
    url: Optional[str] = None


class Report(BaseModel):
    id: str
    title: str
    subtitle: str = ""
    summary: str = ""
    generatedAt: str = Field(alias="generatedAt")
    sourceCount: int = Field(alias="sourceCount")
    importance: int = 3
    timeSpan: str = Field(alias="timeSpan")
    tags: list[str] = []
    isFeatured: bool = Field(default=False, alias="isFeatured")
    status: str = "published"  # published / reviewing / draft
    sections: list[ReportSection] = []
    sources: list[SourceCitation] = []

    class Config:
        populate_by_name = True
