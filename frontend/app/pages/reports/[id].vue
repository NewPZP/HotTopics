<template>
  <div class="fade-in">
    <!-- Back Bar -->
    <div class="flex items-center gap-3 mb-6">
      <button @click="goBack" class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-500 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors cursor-pointer">
        <ArrowLeft class="w-4 h-4" /> 返回
      </button>
      <span class="text-xs text-slate-300">|</span>
      <span class="text-xs text-slate-400">研报中心</span>
    </div>

    <template v-if="report">
      <!-- Report Header -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-6 mb-4">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-purple-100 text-purple-600">深度研报</span>
              <span class="text-xs text-slate-400">生成于 {{ report.generatedAt }} · 引用{{ report.sourceCount }}篇 · {{ '⭐'.repeat(report.importance) }}</span>
            </div>
            <h1 class="text-xl font-bold text-slate-800 mb-1">{{ report.title }}</h1>
            <p class="text-sm text-slate-500">{{ report.subtitle }}</p>
          </div>
        </div>
      </div>

      <!-- Report Sections -->
      <template v-for="section in report.sections" :key="section.id">
        <!-- Section 1: 事件背景 -->
        <div v-if="section.id === 'background'" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
          <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-blue-500 rounded-full"></span> {{ section.title }}</h2>
          <p v-for="(p, i) in section.content" :key="i" class="text-sm text-slate-600 leading-relaxed mb-3">{{ p }}</p>
          <div v-if="section.keyParticipants" class="mt-3 p-3 bg-blue-50 rounded-lg">
            <p class="text-xs text-blue-700 font-medium mb-1">📌 关键参与方</p>
            <div class="flex flex-wrap gap-1.5">
              <span v-for="p in section.keyParticipants" :key="p" class="text-[10px] bg-white text-slate-600 px-2 py-0.5 rounded border border-blue-100">{{ p }}</span>
            </div>
          </div>
        </div>

        <!-- Section 2: 现状分析 -->
        <div v-else-if="section.id === 'analysis'" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
          <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-green-500 rounded-full"></span> {{ section.title }}</h2>
          <p v-for="(p, i) in section.content" :key="i" class="text-sm text-slate-600 leading-relaxed mb-3">{{ p }}</p>
          <div v-if="section.highlights" class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
            <div v-for="h in section.highlights" :key="h.label" class="p-3 rounded-lg text-center" :class="`bg-${h.color}-50`">
              <div class="text-lg font-extrabold" :class="`text-${h.color}-600`">{{ h.value }}</div>
              <div class="text-[10px] mt-0.5" :class="`text-${h.color}-700`">{{ h.label }}</div>
            </div>
          </div>
        </div>

        <!-- Section 3: 趋势研判 -->
        <div v-else-if="section.id === 'trend'" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
          <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-amber-500 rounded-full"></span> {{ section.title }}</h2>
          <div class="space-y-3">
            <div class="p-3 bg-slate-50 rounded-lg">
              <p class="text-xs font-semibold text-slate-700 mb-1">短期（1-3个月）</p>
              <p class="text-xs text-slate-500 leading-relaxed">{{ section.shortTerm }}</p>
            </div>
            <div class="p-3 bg-slate-50 rounded-lg">
              <p class="text-xs font-semibold text-slate-700 mb-1">中长期（6-12个月）</p>
              <p class="text-xs text-slate-500 leading-relaxed">{{ section.longTerm }}</p>
            </div>
            <div v-if="section.keyDrivers" class="p-3 bg-blue-50 rounded-lg">
              <p class="text-xs font-semibold text-blue-700 mb-1">🔑 关键驱动因素</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span v-for="d in section.keyDrivers" :key="d" class="text-[10px] bg-white text-slate-600 px-2 py-0.5 rounded border border-blue-100">{{ d }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: 风险提示 -->
        <div v-else-if="section.id === 'risks'" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
          <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-red-500 rounded-full"></span> {{ section.title }}</h2>
          <div class="space-y-2.5">
            <div v-for="risk in section.risks" :key="risk.category" class="flex items-start gap-2.5 p-3 rounded-lg" :class="`bg-${risk.categoryColor}-50`">
              <span class="mt-0.5" :class="`text-${risk.categoryColor}-500`">⚠️</span>
              <div>
                <p class="text-xs font-semibold" :class="`text-${risk.categoryColor}-700`">{{ risk.title }}</p>
                <p class="text-[11px] leading-relaxed" :class="`text-${risk.categoryColor}-600`">{{ risk.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Sources -->
      <div v-if="report.sources.length > 0" class="bg-white rounded-xl border border-slate-200/80 p-6">
        <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-slate-400 rounded-full"></span> 信息来源（共{{ report.sourceCount }}篇）</h2>
        <div class="space-y-2">
          <div v-for="src in report.sources" :key="src.index"
            class="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg text-xs hover:bg-slate-100 transition-colors cursor-pointer"
            @click="openSource(src.url)">
            <div class="min-w-0">
              <span class="font-medium text-slate-700">[{{ src.index }}]</span>
              <span class="text-slate-600">{{ src.title }}</span>
              <span class="text-slate-400 ml-2">— {{ src.source }} · {{ src.date }}</span>
            </div>
            <span class="text-brand-600 hover:underline whitespace-nowrap ml-2">查看原文 ↗</span>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-12 text-slate-400">
      <template v-if="loading">
        <Loader class="w-6 h-6 text-brand-500 animate-spin mx-auto mb-2" />
        <p>加载中...</p>
      </template>
      <p v-else>研报未找到</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, Download, Share2, Loader } from 'lucide-vue-next'
import { useReportsApi } from '~/composables/useApi'
import type { Report } from '~/types/report'

const { fetchById } = useReportsApi()

const router = useRouter()
const route = useRoute()

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/reports')
  }
}
const report = ref<Report | null>(null)
const loading = ref(true)

const loadData = async () => {
  const id = route.params.id as string
  report.value = await fetchById(id)
  loading.value = false
}

const openSource = (url?: string) => {
  if (url) window.open(url, '_blank', 'noopener')
}

onMounted(() => loadData())
</script>
