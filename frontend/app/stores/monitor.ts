// 监控状态管理 — WebSocket 全局单例，页面切换不断开
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WorkflowState, LogEntry } from '~/types/workflow'

/** WebSocket 连接地址 */
const WS_URL = `ws://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000/ws/monitor`

export const useMonitorStore = defineStore('monitor', () => {
  const workflowState = ref<WorkflowState | null>(null)

  // ---- WebSocket 全局单例 ----
  const wsConnected = ref(false)
  const wsLastMessage = ref<any>(null)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let messageHandlers: Array<(data: any) => void> = []

  const connectWs = (onMessage?: (data: any) => void) => {
    // 注册回调
    if (onMessage && !messageHandlers.includes(onMessage)) {
      messageHandlers.push(onMessage)
    }

    // 已连接则跳过
    if (ws && ws.readyState === WebSocket.OPEN) return
    // 正在连接中也跳过
    if (ws && ws.readyState === WebSocket.CONNECTING) return
    ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      wsConnected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        wsLastMessage.value = data
        messageHandlers.forEach((h) => h(data))
      } catch { /* ignore */ }
    }

    ws.onclose = () => {
      wsConnected.value = false
      // 自动重连（5 秒后），页面切换不中断
      if (reconnectTimer) clearTimeout(reconnectTimer)
      reconnectTimer = setTimeout(() => connectWs(), 5000)
    }

    ws.onerror = () => {
      wsConnected.value = false
    }
  }

  const disconnectWs = () => {
    // 仅在应用彻底关闭时调用（如登出），页面切换不调用
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.onclose = null // 阻止自动重连
      ws.onerror = null
      ws.onmessage = null
      ws.close()
      ws = null
      wsConnected.value = false
    }
  }

  const removeWsHandler = (handler: (data: any) => void) => {
    messageHandlers = messageHandlers.filter((h) => h !== handler)
  }

  // ---- 数据操作 ----

  const addLog = (log: LogEntry) => {
    if (!workflowState.value) return
    workflowState.value.logs.unshift(log)
    if (workflowState.value.logs.length > 50) {
      workflowState.value.logs.pop()
    }
  }

  /** 从 API 响应刷新完整状态 */
  const refreshFromApi = (state: WorkflowState) => {
    workflowState.value = state
  }

  const refresh = () => {
    // no-op: no mock fallback
  }

  return {
    workflowState,
    wsConnected,
    wsLastMessage,
    connectWs,
    disconnectWs,
    removeWsHandler,
    addLog,
    refreshFromApi,
    refresh,
  }
})
