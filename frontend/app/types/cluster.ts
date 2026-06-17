// 聚类分析相关类型

export interface NewsCluster {
  id: string
  label: string
  icon: string
  articleCount: number
  timeSpan: string
  importance: number
  summary: string
  tags: string[]
  timeline: EventTimelineItem[]
  articles: ClusterArticle[]
}

export interface EventTimelineItem {
  date: string
  title: string
  description: string
  done: boolean
}

export interface ClusterArticle {
  title: string
  source: string
  date: string
  views: string
  url: string
}

// ECharts 力导向图数据
export interface ClusterNode {
  name: string
  symbolSize: number
  category: number
  itemStyle?: { color?: string }
}

export interface ClusterLink {
  source: string
  target: string
}
