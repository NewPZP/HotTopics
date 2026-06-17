<template>
  <div class="fade-in">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">实时监控</h1>
        <p class="text-sm text-slate-500 mt-0.5">Agent 工作流管道视图 · 实时日志 · 系统资源指标</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200 text-slate-500 bg-white hover:bg-slate-50 hover:border-red-200 hover:text-red-500 transition-colors"
          @click="handleReset"
        >
          <RotateCcw class="w-3 h-3" />
          重置
        </button>
        <button
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-brand-500 text-white hover:bg-brand-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="triggering"
          @click="handleTrigger"
        >
          <Loader v-if="triggering" class="w-3 h-3 animate-spin" />
          <Play v-else class="w-3 h-3" />
          {{ triggering ? '触发中...' : '手动采集' }}
        </button>
      </div>
    </div>

    <template v-if="wf">
    <!-- Pipeline -->
    <div class="bg-white rounded-xl border border-slate-200/80 p-5 mb-4">
      <h3 class="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><GitBranch class="w-4 h-4 text-brand-600" /> 工作流管道视图</h3>
      <div class="flex flex-wrap items-center gap-3 justify-center">
        <template v-for="(step, idx) in wf.pipelineSteps" :key="step.name">
          <div class="text-center">
            <div class="w-16 h-16 rounded-2xl border-2 flex items-center justify-center mb-1.5" :class="pipeBoxClass(step.status)">
              <CheckCircle v-if="step.status === 'done'" class="w-6 h-6 text-green-500" />
              <Loader v-else-if="step.status === 'running'" class="w-6 h-6 text-blue-500 animate-spin" />
              <Clock v-else class="w-5 h-5 text-slate-300" />
            </div>
            <span class="text-[11px] font-medium" :class="step.status === 'running' ? 'text-blue-600' : step.status === 'pending' ? 'text-slate-400' : 'text-slate-600'">{{ step.label }}</span>
          </div>
          <ArrowRight v-if="idx < wf.pipelineSteps.length - 1" class="w-4 h-4 text-slate-300" />
        </template>
      </div>
      <div class="mt-4 w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div class="bg-gradient-to-r from-brand-500 to-accent-500 h-2 rounded-full" :style="`width:${wf.totalProgress}%`"></div>
      </div>
      <p class="text-xs text-slate-400 text-center mt-2">总进度 {{ wf.totalProgress }}% </p>
    </div>

    <!-- Agent Status + Logs -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-3">Agent 运行状态</h3>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="agent in wf.agents" :key="agent.name" class="p-3 rounded-xl border" :class="agentBoxClass(agent.status)">
            <div class="flex items-center gap-1.5 mb-1">
              <span class="w-1.5 h-1.5 rounded-full" :class="agent.status === 'running' ? 'bg-blue-500 pulse-dot' : agent.status === 'pending' ? 'bg-slate-300' : 'bg-green-500'"></span>
              <span class="text-xs font-semibold" :class="agent.status === 'running' ? 'text-blue-700' : agent.status === 'pending' ? 'text-slate-500' : 'text-green-700'">{{ agent.label }}</span>
            </div>
            <span class="text-[10px]" :class="agent.status === 'running' ? 'text-blue-600' : agent.status === 'pending' ? 'text-slate-400' : 'text-green-600'">{{ agent.status === 'idle' ? '✅ Idle' : agent.status === 'running' ? '🔄 Running' : '⏳ Pending' }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-3 flex items-center justify-between">
          <span class="flex items-center gap-2"><Terminal class="w-4 h-4 text-slate-500" /> 实时日志</span>
          <span class="text-[10px] text-slate-400">自动刷新 · 5s前</span>
        </h3>
        <div class="bg-slate-900 rounded-xl p-4 font-mono text-xs space-y-2 max-h-[320px] overflow-y-auto scrollbar-thin">
          <div v-for="(log, idx) in wf.logs" :key="idx" class="flex gap-2">
            <span class="text-slate-500 whitespace-nowrap">{{ log.timestamp }}</span>
            <span :class="log.level === 'WARN' ? 'text-amber-400' : log.level === 'ERROR' ? 'text-red-400' : 'text-blue-400'">[{{ log.level }}]</span>
            <span class="text-slate-300">{{ log.agent }}: {{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- System Metrics -->
    <div class="bg-white rounded-xl border border-slate-200/80 p-5">
      <h3 class="text-sm font-semibold text-slate-700 mb-3">系统资源指标</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="p-3 rounded-xl bg-slate-50 text-center">
          <div class="text-xs text-slate-500 mb-1">CPU 使用率</div>
          <div class="text-xl font-extrabold text-slate-800">{{ wf.metrics.cpu }}%</div>
          <div class="w-full bg-slate-200 rounded-full h-1.5 mt-1.5"><div class="bg-blue-500 h-1.5 rounded-full" :style="`width:${wf.metrics.cpu}%`"></div></div>
        </div>
        <div class="p-3 rounded-xl bg-slate-50 text-center">
          <div class="text-xs text-slate-500 mb-1">内存使用</div>
          <div class="text-xl font-extrabold text-slate-800">{{ wf.metrics.memory.used }}<span class="text-sm text-slate-500">/{{ wf.metrics.memory.total }} GB</span></div>
          <div class="w-full bg-slate-200 rounded-full h-1.5 mt-1.5"><div class="bg-green-500 h-1.5 rounded-full" :style="`width:${(wf.metrics.memory.used / wf.metrics.memory.total) * 100}%`"></div></div>
        </div>
        <div class="p-3 rounded-xl bg-slate-50 text-center">
          <div class="text-xs text-slate-500 mb-1">Redis 缓存</div>
          <div class="text-xl font-extrabold text-slate-800">{{ wf.metrics.redis }}<span class="text-sm text-slate-500"> MB</span></div>
          <div class="w-full bg-slate-200 rounded-full h-1.5 mt-1.5"><div class="bg-amber-500 h-1.5 rounded-full" style="width:31%"></div></div>
        </div>
        <div class="p-3 rounded-xl bg-slate-50 text-center">
          <div class="text-xs text-slate-500 mb-1">数据库连接</div>
          <div class="text-xl font-extrabold text-slate-800">{{ wf.metrics.dbConnections }}<span class="text-sm text-slate-500"> GB</span></div>
          <div class="w-full bg-slate-200 rounded-full h-1.5 mt-1.5"><div class="bg-purple-500 h-1.5 rounded-full" style="width:15%"></div></div>
        </div>
      </div>
    </div>
    </template>

    <!-- Loading -->
    <div v-else class="flex items-center justify-center py-20">
      <Loader class="w-6 h-6 text-brand-500 animate-spin" />
      <span class="ml-2 text-sm text-slate-400">加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { GitBranch, CheckCircle, Clock, Loader, ArrowRight, Terminal, Play, RefreshCw, RotateCcw } from 'lucide-vue-next'
import { useMonitorApi } from '~/composables/useApi'
import { useMonitorStore } from '~/stores/monitor'
import type { WorkflowState } from '~/types/workflow'

const { fetchStatus, triggerCollect, resetWorkflow } = useMonitorApi()
const store = useMonitorStore()

const wf = ref<WorkflowState | null>(null)
const loading = ref(true)
const triggering = ref(false)
const refreshing = ref(false)

// 全灰色初始状态
const EMPTY_STATE: WorkflowState = {
  isRunning: false,
  lastCollectTime: '--',
  nextCollectTime: '--',
  totalProgress: 0,
  estimatedRemaining: '--',
  pipelineSteps: [
    { name: 'collect', label: '采集', status: 'pending', count: '0篇' },
    { name: 'preprocess', label: '预处理', status: 'pending', count: '0篇' },
    { name: 'dedup', label: '去重', status: 'pending', count: '0篇' },
    { name: 'cluster', label: '聚类', status: 'pending', count: '0簇' },
    { name: 'research', label: '摘要', status: 'pending', count: '0%' },
    { name: 'review', label: '审核', status: 'pending', count: '等待' },
    { name: 'compose', label: '组装', status: 'pending', count: '等待' },
    { name: 'dispatch', label: '推送', status: 'pending', count: '等待' },
  ],
  agents: [
    { name: 'CollectorAgent', label: 'CollectorAgent', status: 'pending', detail: '等待采集' },
    { name: 'DedupAgent', label: 'DedupAgent', status: 'pending', detail: '等待采集' },
    { name: 'ClusterAgent', label: 'ClusterAgent', status: 'pending', detail: '等待采集' },
    { name: 'ResearchAgent', label: 'ResearchAgent', status: 'pending', detail: '等待采集' },
    { name: 'ReviewAgent', label: 'ReviewAgent', status: 'pending', detail: '等待采集' },
    { name: 'DispatchAgent', label: 'DispatchAgent', status: 'pending', detail: '等待采集' },
  ],
  logs: [],
  metrics: { cpu: 0, memory: { used: 0, total: 0 }, redis: 0, dbConnections: 0 },
}

const loadData = async () => {
  wf.value = await fetchStatus()
}

const handleReset = async () => {
  try {
    await resetWorkflow()
  } catch { /* 忽略网络错误 */ }
  wf.value = { ...EMPTY_STATE, pipelineSteps: EMPTY_STATE.pipelineSteps.map(s => ({ ...s })), agents: EMPTY_STATE.agents.map(a => ({ ...a })) }
}

const handleRefresh = async () => {
  refreshing.value = true
  try {
    await loadData()
  } finally {
    refreshing.value = false
  }
}

const handleTrigger = async () => {
  triggering.value = true
  try {
    await triggerCollect()
    // 触发后延迟刷新状态
    setTimeout(() => loadData(), 2000)
  } catch { /* ignore */ }
  finally {
    triggering.value = false
  }
}

// WebSocket 消息回调
const onWsMessage = (data: any) => {
  if (data.type === 'workflow:progress' || data.type === 'agent:status' || data.type === 'log:new') {
    loadData()
  }
}

onMounted(() => {
  loadData()
  // 使用 Store 全局单例 WebSocket，页面切换不会断开
  store.connectWs(onWsMessage)
  // 每 10 秒轮询一次作为兜底
  const interval = setInterval(loadData, 10000)
  onBeforeUnmount(() => clearInterval(interval))
})

onBeforeUnmount(() => {
  // 移除回调但不关闭 WebSocket，保持全局连接
  store.removeWsHandler(onWsMessage)
})

const pipeBoxClass = (status: string) => {
  if (status === 'done') return 'bg-green-50 border-green-200'
  if (status === 'running') return 'bg-blue-50 border-blue-200'
  return 'bg-slate-50 border-slate-100'
}

const agentBoxClass = (status: string) => {
  if (status === 'idle') return 'bg-green-50 border-green-100'
  if (status === 'running') return 'bg-blue-50 border-blue-100'
  return 'bg-slate-50 border-slate-100'
}
</script>
