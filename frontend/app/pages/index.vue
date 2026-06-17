<template>
  <div class="fade-in">
    <!-- Welcome + Action Bar -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">Dashboard 工作台</h1>
        <p class="text-sm text-slate-500 mt-0.5">欢迎回来，今日数据总览</p>
      </div>
      <div class="flex items-center gap-2.5">
        <span class="text-xs text-slate-400">数据范围</span>
        <select v-model="dateRange" @change="loadData" class="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 cursor-pointer focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 outline-none">
          <option value="today">今日</option><option value="week">本周</option><option value="month">本月</option>
        </select>
        <button @click="loadData" class="flex items-center gap-1.5 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors">
          <RefreshCw class="w-3.5 h-3.5" /> 刷新数据
        </button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="stat in stats" :key="stat.label" class="stat-card bg-white rounded-xl border border-slate-200/80 p-5 cursor-pointer">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wide">{{ stat.label }}</span>
          <div :class="`w-8 h-8 rounded-lg ${stat.iconBg} flex items-center justify-center`">
            <component :is="iconMap[stat.icon]" :class="`w-4 h-4 ${stat.iconColor}`" />
          </div>
        </div>
        <div class="text-3xl font-extrabold text-slate-800 tracking-tight">{{ stat.value }}</div>
        <div class="flex items-center gap-1 mt-1.5 text-xs font-medium"
          :class="stat.trendType === 'up' ? 'text-green-600' : stat.trendType === 'down' ? 'text-red-600' : 'text-slate-400'">
          <TrendingUp v-if="stat.trendType === 'up'" class="w-3 h-3" />
          {{ stat.trend }}
          <span v-if="stat.subLabel" class="text-slate-400 font-normal ml-1">{{ stat.subLabel }}</span>
        </div>
      </div>
    </div>

    <!-- Charts + News Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Today's TOP5 News -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><Star class="w-4 h-4 text-amber-500" /> 今日要闻 TOP5</h3>
        <div class="space-y-3">
          <div v-for="(news, idx) in topNews" :key="news.id"
            class="flex items-start gap-3 pb-3 border-b border-slate-100 cursor-pointer hover:bg-slate-50 rounded-lg p-1.5 -m-1 transition-colors"
            :class="{ 'border-b-0': idx === topNews.length - 1 }"
            @click="navigateTo(`/briefs/${news.id}`)">
            <span class="flex-shrink-0 w-5 h-5 rounded-full text-xs font-bold flex items-center justify-center"
              :class="rankColors[idx]">{{ idx + 1 }}</span>
            <div class="min-w-0">
              <p class="text-sm font-medium text-slate-800 leading-snug">{{ news.title }}</p>
              <p class="text-xs text-slate-400 mt-0.5">{{ news.publishedAt }} · 来源: {{ news.source }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Trend Chart (span 2) -->
      <div class="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2"><TrendingUp class="w-4 h-4 text-blue-600" /> 采集与产出趋势（近7日）</h3>
        <div ref="trendChartRef" style="height: 280px;"></div>
      </div>
    </div>

    <!-- Latest Reports -->
    <div class="bg-white rounded-xl border border-slate-200/80 p-5 mb-6">
      <h3 class="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><FileText class="w-4 h-4 text-purple-600" /> 最新研报</h3>
      <div class="space-y-3">
        <div v-for="report in latestReports" :key="report.id"
          class="flex items-center justify-between p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer"
          @click="navigateTo(`/reports/${report.id}`)">
          <div class="min-w-0">
            <p class="text-sm font-medium text-slate-800">{{ report.title }}</p>
            <p class="text-xs text-slate-400 mt-0.5">生成于 {{ report.generatedAt }} · 引用{{ report.sourceCount }}篇 · {{ '⭐'.repeat(report.importance) }}</p>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-medium"
            :class="report.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
            {{ report.status === 'published' ? '已发布' : '审核中' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { TrendingUp, RefreshCw, Star, FileText, Rss, Filter, Send } from 'lucide-vue-next'
import * as echarts from 'echarts'
import { useDashboardApi, useReportsApi } from '~/composables/useApi'
import type { TopNews } from '~/types/brief'
import type { Report } from '~/types/report'

const { stats, fetchStats, fetchTopNews, fetchTrends } = useDashboardApi()

const topNews = ref<TopNews[]>([])
const trendData = ref<{ dates: string[]; collect: number[]; dedup: number[]; reports: number[] }>({ dates: [], collect: [], dedup: [], reports: [] })
const latestReports = ref<Report[]>([])
const loading = ref(true)
const dateRange = ref<'today' | 'week' | 'month'>('today')

const rankColors = [
  'bg-red-100 text-red-600',
  'bg-orange-100 text-orange-600',
  'bg-amber-100 text-amber-600',
  'bg-blue-100 text-blue-600',
  'bg-slate-100 text-slate-500',
]

const iconMap: Record<string, any> = { rss: Rss, filter: Filter, 'file-text': FileText, send: Send }

const trendChartRef = ref<HTMLDivElement | null>(null)
let trendChart: echarts.ECharts | null = null

const initChart = () => {
  if (trendChartRef.value) {
    trendChart?.dispose()
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['采集量', '去重量', '研报产出'], bottom: 0, textStyle: { fontSize: 11 } },
      grid: { left: 40, right: 20, top: 10, bottom: 30 },
      xAxis: { type: 'category', data: trendData.value.dates, axisLabel: { fontSize: 10 } },
      yAxis: { type: 'value', axisLabel: { fontSize: 10 } },
      series: [
        { name: '采集量', type: 'line', data: trendData.value.collect, smooth: true, lineStyle: { width: 2, color: '#2d8eff' }, itemStyle: { color: '#2d8eff' }, symbol: 'circle', symbolSize: 4 },
        { name: '去重量', type: 'line', data: trendData.value.dedup, smooth: true, lineStyle: { width: 2, color: '#10b981' }, itemStyle: { color: '#10b981' }, symbol: 'circle', symbolSize: 4 },
        { name: '研报产出', type: 'bar', data: trendData.value.reports, barWidth: 12, itemStyle: { color: '#8b5cf6', borderRadius: [3, 3, 0, 0] } },
      ],
    })
  }
}

const loadData = async () => {
  loading.value = true
  await fetchStats(dateRange.value)
  topNews.value = await fetchTopNews(dateRange.value)
  trendData.value = await fetchTrends(dateRange.value)

  const reportsApi = useReportsApi()
  const result = await reportsApi.fetchList({ page: 1, pageSize: 3 })
  latestReports.value = Array.isArray(result.data) ? result.data : []

  loading.value = false
  nextTick(() => initChart())
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => trendChart?.resize())
})

onBeforeUnmount(() => {
  trendChart?.dispose()
})
</script>
