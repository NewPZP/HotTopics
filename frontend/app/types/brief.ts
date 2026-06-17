// 简报相关类型

export interface KeyDataItem {
  label: string
  value: string
  unit: string
  color: string
}

export interface TopNews {
  id: string
  rank: number
  title: string
  summary: string
  source: string
  publishedAt: string
  hotIndex: number
  tags: string[]
  sources: SourceArticle[]
  keyData: KeyDataItem[]
}

export interface SourceArticle {
  name: string
  time: string
  title: string
  excerpt: string
  url: string
}

export interface Brief {
  date: string
  topNews: TopNews[]
  reports: BriefReport[]
  industryNews: IndustryNewsGroup[]
  sentimentData: SentimentData
  tomorrowFocus: string[]
}

export interface BriefReport {
  id: string
  title: string
  summary: string
  sourceCount: number
  generatedAt: string
  importance: number
  sections: string[]
}

export interface IndustryNewsGroup {
  industry: string
  icon: string
  items: string[]
}

export interface SentimentData {
  sentiment: number
  sentimentLabel: string
  sentimentTrend: string
  hotIndex: number
  hotLabel: string
  hotTrend: string
  volatility: number
  volatilityLabel: string
  volatilityTrend: string
}
