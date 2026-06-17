<template>
  <div class="fade-in">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">每日简报</h1>
        <p class="text-sm text-slate-500 mt-0.5">智能聚合每日资讯，一键导出 PDF / Markdown</p>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex items-center bg-white border border-slate-200 rounded-lg overflow-hidden">
          <button class="px-3 py-2 hover:bg-slate-50 transition-colors" @click="prevDay"><ChevronLeft class="w-4 h-4 text-slate-500" /></button>
          <span class="px-4 py-2 text-sm font-semibold text-slate-700 border-x border-slate-200">{{ currentDate }}</span>
          <button class="px-3 py-2 hover:bg-slate-50 transition-colors" @click="nextDay"><ChevronRight class="w-4 h-4 text-slate-500" /></button>
        </div>
        <button class="flex items-center gap-1.5 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50 transition-colors" @click="downloadPdf(currentDate)"><FileText class="w-3.5 h-3.5" /> PDF</button>
        <button class="flex items-center gap-1.5 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50 transition-colors" @click="downloadMd(currentDate)"><span class="font-mono text-xs font-semibold">MD</span> Markdown</button>
      </div>
    </div>

    <template v-if="brief">
    <!-- TOP5 Section -->
    <div class="bg-white rounded-xl border border-slate-200/80 p-5 mb-4">
      <h2 class="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2"><span class="w-1 h-5 bg-red-500 rounded-full"></span> 今日要闻 TOP5</h2>
      <div class="space-y-2">
        <div v-for="(news, idx) in brief.topNews" :key="news.id"
          class="flex items-center gap-4 p-3 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer border border-transparent hover:border-slate-200"
          @click="navigateTo(`/briefs/${news.id}?date=${currentDate}`)">
          <span class="font-mono text-lg font-bold w-8 text-center" :class="topColors[idx]">{{ String(idx + 1).padStart(2, '0') }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-slate-800">{{ news.title }}</p>
            <p class="text-xs text-slate-500 mt-0.5">{{ news.summary }}</p>
          </div>
          <span class="text-xs text-brand-600 hover:underline whitespace-nowrap">展开详情 &rarr;</span>
        </div>
      </div>
    </div>

    <!-- 深度研报 Section -->
    <div class="mb-4">
      <h2 class="text-base font-semibold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1 h-5 bg-purple-500 rounded-full"></span> 深度研报（{{ brief.reports.length }}篇）</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="report in brief.reports" :key="report.id"
          class="bg-white rounded-xl border border-slate-200/80 p-5 hover:shadow-md transition-shadow cursor-pointer">
          <div class="flex items-center gap-2 mb-3"><span class="text-xl">📊</span><span class="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">深度研报</span></div>
          <h3 class="text-sm font-semibold text-slate-800 mb-2">{{ report.title }}</h3>
          <p class="text-xs text-slate-500 leading-relaxed mb-3">{{ report.summary }}</p>
          <div class="flex items-center gap-3 text-[10px] text-slate-400">
            <span>📖 {{ report.sourceCount }}篇引用</span><span>🕐 生成于 {{ report.generatedAt }}</span><span>⭐ 重要性 {{ report.importance }}/5</span>
          </div>
          <div class="mt-3 flex gap-1.5">
            <span v-for="section in report.sections" :key="section"
              class="px-2 py-0.5 rounded-full text-[10px]" :class="sectionColors[section]">{{ section }}</span>
          </div>
          <button class="mt-3 w-full py-2 text-sm font-medium text-brand-600 border border-brand-200 rounded-lg hover:bg-brand-50 transition-colors" @click="navigateTo(`/reports/${report.id}`)">阅读全文</button>
        </div>
      </div>
    </div>

    <!-- 行业动态 + 数据看板 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h2 class="text-base font-semibold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1 h-5 bg-green-500 rounded-full"></span> 行业动态速览</h2>
        <div class="space-y-3">
          <div v-for="group in brief.industryNews" :key="group.industry">
            <span class="text-xs font-semibold text-slate-500">{{ group.icon }} {{ group.industry }}</span>
            <div class="flex flex-wrap gap-1.5 mt-1">
              <span v-for="item in group.items" :key="item" class="text-xs bg-slate-50 border border-slate-200 rounded px-2 py-1 cursor-pointer hover:border-blue-300 transition-colors">{{ item }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h2 class="text-base font-semibold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1 h-5 bg-amber-500 rounded-full"></span> 市场情绪数据看板</h2>
        <div class="grid grid-cols-3 gap-3">
          <div class="text-center p-4 bg-slate-50 rounded-xl">
            <div class="text-2xl font-extrabold text-green-600">{{ brief.sentimentData.sentiment }}</div>
            <div class="text-xs text-slate-500 mt-1">情绪指数</div>
            <div class="text-[10px] text-green-500 mt-0.5">{{ brief.sentimentData.sentimentTrend === 'up' ? '▲' : '▼' }} {{ brief.sentimentData.sentimentLabel }}</div>
          </div>
          <div class="text-center p-4 bg-slate-50 rounded-xl">
            <div class="text-2xl font-extrabold text-blue-600">{{ brief.sentimentData.hotIndex }}</div>
            <div class="text-xs text-slate-500 mt-1">热度指数</div>
            <div class="text-[10px] text-blue-500 mt-0.5">{{ brief.sentimentData.hotTrend === 'up' ? '▲' : '▼' }} {{ brief.sentimentData.hotLabel }}</div>
          </div>
          <div class="text-center p-4 bg-slate-50 rounded-xl">
            <div class="text-2xl font-extrabold text-amber-600">{{ brief.sentimentData.volatility }}</div>
            <div class="text-xs text-slate-500 mt-1">波动指数</div>
            <div class="text-[10px] text-amber-500 mt-0.5">{{ brief.sentimentData.volatilityTrend === 'up' ? '▲' : '▼' }} {{ brief.sentimentData.volatilityLabel }}</div>
          </div>
        </div>
        <div class="mt-4 p-4 bg-slate-50 rounded-xl">
          <p class="text-xs text-slate-500 mb-2">明日关注</p>
          <div class="space-y-1.5">
            <div v-for="item in brief.tomorrowFocus" :key="item" class="text-xs text-slate-700">📅 {{ item }}</div>
          </div>
        </div>
      </div>
    </div>
    </template>

    <!-- Loading -->
    <div v-else-if="loading" class="flex items-center justify-center py-20">
      <Loader class="w-6 h-6 text-brand-500 animate-spin" />
      <span class="ml-2 text-sm text-slate-400">加载中...</span>
    </div>

    <!-- 空状态：当日简报未生成 -->
    <div v-else class="flex flex-col items-center justify-center py-20">
      <div class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
        <FileText class="w-8 h-8 text-slate-300" />
      </div>
      <p class="text-sm font-medium text-slate-500 mb-1">今日简报尚未生成</p>
      <p class="text-xs text-slate-400">请等待系统自动采集生成，或前往<a href="/monitor" class="text-brand-600 hover:underline">监控页面</a>手动触发采集</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, FileText, Loader } from 'lucide-vue-next'
import { useBriefsApi } from '~/composables/useApi'
import type { Brief } from '~/types/brief'

const { fetchByDate, downloadPdf } = useBriefsApi()

const downloadMd = (date: string) => {
  window.open(`/api/v1/briefs/${date}/md`, '_blank')
}

const brief = ref<Brief | null>(null)
const currentDate = ref(new Date().toISOString().substring(0, 10))
const loading = ref(true)

const topColors = ['text-red-500', 'text-orange-500', 'text-amber-500', 'text-blue-500', 'text-slate-400']

const sectionColors: Record<string, string> = {
  '事件背景': 'bg-blue-50 text-blue-600 border border-blue-200',
  '现状分析': 'bg-green-50 text-green-600 border border-green-200',
  '趋势研判': 'bg-amber-50 text-amber-600 border border-amber-200',
  '风险提示': 'bg-red-50 text-red-600 border border-red-200',
}

const loadData = async (date: string) => {
  loading.value = true
  try {
    brief.value = await fetchByDate(date)
    currentDate.value = date
  } catch (e: any) {
    // 404 表示该日期简报未生成，正常显示空状态
    brief.value = null
    currentDate.value = date
  } finally {
    loading.value = false
  }
}

const prevDay = () => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() - 1)
  const dateStr = d.toISOString().substring(0, 10)
  loadData(dateStr)
}
const nextDay = () => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + 1)
  const next = d.toISOString().substring(0, 10)
  if (next <= new Date().toISOString().substring(0, 10)) {
    loadData(next)
  }
}

onMounted(() => loadData(currentDate.value))
</script>
