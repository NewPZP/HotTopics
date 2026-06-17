// API Composable — 纯粹的后端 API 调用封装，无 Mock 降级
import { ref } from 'vue'
import { apiClient, WS_BASE } from '~/utils/api/client'
import type { StatItem, TopicItem, CrawlerSite } from '~/types/common'
import type { Brief } from '~/types/brief'
import type { Report } from '~/types/report'
import type { NewsCluster, ClusterNode, ClusterLink } from '~/types/cluster'
import type { WorkflowState, LogEntry, SystemMetrics, PipelineStep } from '~/types/workflow'

// ==================== Dashboard ====================
export function useDashboardApi() {
  const stats = ref<StatItem[]>([])
  const loading = ref(false)

  const fetchStats = async (range = 'today') => {
    loading.value = true
    stats.value = await apiClient.get<StatItem[]>('/dashboard/stats', { date_range: range })
    loading.value = false
  }

  const fetchTopNews = async (range = 'today') => {
    return await apiClient.get('/dashboard/top-news', { date_range: range })
  }

  const fetchTrends = async (range = 'today') => {
    return await apiClient.get('/dashboard/trends', { date_range: range })
  }

  return { stats, loading, fetchStats, fetchTopNews, fetchTrends }
}

// ==================== Briefs ====================
export function useBriefsApi() {
  const fetchList = async (page = 1, pageSize = 10) => {
    return await apiClient.getPaginated('/briefs', { page, pageSize })
  }

  const fetchByDate = async (date: string): Promise<Brief> => {
    return await apiClient.get<Brief>(`/briefs/${date}`)
  }

  const downloadPdf = (date: string) => {
    window.open(`/api/v1/briefs/${date}/pdf`, '_blank')
  }

  return { fetchList, fetchByDate, downloadPdf }
}

// ==================== Reports ====================
export function useReportsApi() {
  const fetchList = async (params?: { page?: number; pageSize?: number; search?: string; topic?: string; sort?: string }) => {
    return await apiClient.getPaginated('/reports', params)
  }

  const fetchById = async (id: string): Promise<Report> => {
    return await apiClient.get<Report>(`/reports/${id}`)
  }

  return { fetchList, fetchById }
}

// ==================== Clusters ====================
export function useClustersApi() {
  const fetchList = async (params?: { page?: number; pageSize?: number; topic?: string; sort?: string }) => {
    return await apiClient.getPaginated<NewsCluster[]>('/clusters', params)
  }

  const fetchById = async (id: string): Promise<NewsCluster> => {
    return await apiClient.get<NewsCluster>(`/clusters/${id}`)
  }

  const fetchGraph = async (): Promise<{ nodes: ClusterNode[]; links: ClusterLink[] }> => {
    return await apiClient.get('/clusters/graph')
  }

  return { fetchList, fetchById, fetchGraph }
}

// ==================== Monitor ====================
export function useMonitorApi() {
  const fetchStatus = async (): Promise<WorkflowState> => {
    return await apiClient.get<WorkflowState>('/monitor/status')
  }

  const fetchMetrics = async (): Promise<SystemMetrics> => {
    return await apiClient.get<SystemMetrics>('/monitor/metrics')
  }

  const fetchLogs = async (limit = 20): Promise<LogEntry[]> => {
    return await apiClient.get<LogEntry[]>('/monitor/logs', { limit })
  }

  /** 触发采集 */
  const triggerCollect = async (topics?: string[]) => {
    return await apiClient.post('/collect', { topics })
  }

  /** 重置工作流（停止后端 + 清状态） */
  const resetWorkflow = async () => {
    return await apiClient.post('/monitor/reset')
  }

  return { fetchStatus, fetchMetrics, fetchLogs, triggerCollect, resetWorkflow }
}

// ==================== Topics ====================
export function useTopicsApi() {
  const fetchList = async (): Promise<TopicItem[]> => {
    return await apiClient.get<TopicItem[]>('/topics')
  }

  const create = async (topic: Partial<TopicItem>): Promise<TopicItem> => {
    return await apiClient.post<TopicItem>('/topics', topic)
  }

  const update = async (id: string, topic: Partial<TopicItem>): Promise<TopicItem> => {
    return await apiClient.put<TopicItem>(`/topics/${id}`, topic)
  }

  const remove = async (id: string) => {
    return await apiClient.delete(`/topics/${id}`)
  }

  return { fetchList, create, update, remove }
}

// ==================== Config ====================
export function useConfigApi() {
  const fetchConfig = async () => {
    return await apiClient.get('/config')
  }

  const updateConfig = async (config: Record<string, any>) => {
    return await apiClient.put('/config', config)
  }

  return { fetchConfig, updateConfig }
}

// ==================== Crawler Sites ====================
export function useCrawlerSitesApi() {
  const fetchSites = async (): Promise<CrawlerSite[]> => {
    return await apiClient.get<CrawlerSite[]>('/config/crawler-sites')
  }

  const createSite = async (site: Partial<CrawlerSite>): Promise<CrawlerSite> => {
    return await apiClient.post<CrawlerSite>('/config/crawler-sites', site)
  }

  const updateSite = async (id: string, site: Partial<CrawlerSite>): Promise<CrawlerSite> => {
    return await apiClient.put<CrawlerSite>(`/config/crawler-sites/${id}`, site)
  }

  const deleteSite = async (id: string) => {
    return await apiClient.delete(`/config/crawler-sites/${id}`)
  }

  return { fetchSites, createSite, updateSite, deleteSite }
}

// ==================== WebSocket ====================
export function useMonitorWebSocket() {
  const connected = ref(false)
  const lastMessage = ref<any>(null)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const connect = (onMessage?: (data: any) => void) => {
    if (ws && ws.readyState === WebSocket.OPEN) return

    ws = new WebSocket(`${WS_BASE}/ws/monitor`)

    ws.onopen = () => {
      connected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        lastMessage.value = data
        onMessage?.(data)
      } catch { /* ignore */ }
    }

    ws.onclose = () => {
      connected.value = false
      reconnectTimer = setTimeout(() => connect(onMessage), 5000)
    }

    ws.onerror = () => {
      connected.value = false
    }
  }

  const disconnect = () => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (ws) {
      ws.onclose = null
      ws.close()
      ws = null
      connected.value = false
    }
  }

  return { connected, lastMessage, connect, disconnect }
}
