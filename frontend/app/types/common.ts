// 通用类型

export interface StatItem {
  label: string
  value: string
  icon: string
  iconBg: string
  iconColor: string
  trend: string
  trendType: 'up' | 'down' | 'neutral'
  subLabel?: string
}

export interface DateRange {
  start: string
  end: string
}

export interface PaginationInfo {
  current: number
  total: number
  pageSize: number
}

export interface TopicItem {
  id: string
  name: string
  keywords: string[]
  enabled: boolean
}

export interface DataSourceItem {
  id: string
  name: string
  icon: string
  iconColor: string
  subLabel: string
  enabled: boolean
}

/** 爬虫站点配置 */
export interface CrawlerSite {
  id: string
  name: string
  url: string
  selector: string
  linkAttr: string
  category: string
  enabled: boolean
}
