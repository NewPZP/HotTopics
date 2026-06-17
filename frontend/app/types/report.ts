// 研报相关类型

export interface Report {
  id: string
  title: string
  subtitle: string
  summary: string
  generatedAt: string
  sourceCount: number
  importance: number
  timeSpan: string
  tags: string[]
  isFeatured: boolean
  status: 'published' | 'reviewing' | 'draft'
  sections: ReportSection[]
  sources: SourceCitation[]
}

export interface ReportSection {
  id: string
  title: string
  content: string[]
  highlights?: KeyDataPoint[]
  keyParticipants?: string[]
  shortTerm?: string
  longTerm?: string
  keyDrivers?: string[]
  risks?: RiskItem[]
}

export interface KeyDataPoint {
  label: string
  value: string
  color: string
}

export interface RiskItem {
  category: string
  categoryColor: string
  title: string
  description: string
}

export interface SourceCitation {
  index: number
  source: string
  title: string
  date: string
  url?: string
}
