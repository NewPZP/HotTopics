<template>
  <div class="fade-in">
    <div class="flex items-center gap-3 mb-6">
      <button @click="goBack" class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-500 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors cursor-pointer">
        <ArrowLeft class="w-4 h-4" /> 返回
      </button>
      <span class="text-xs text-slate-300">|</span>
      <span class="text-xs text-slate-400">每日简报</span>
    </div>

    <template v-if="news">
      <div class="bg-white rounded-xl border border-slate-200/80 p-6 mb-4">
        <div class="flex items-center gap-2 mb-2"><span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 text-red-600 border border-red-200">今日要闻</span><span class="text-xs text-slate-400">生成于 {{ news.publishedAt }}</span></div>
        <h1 class="text-xl font-bold text-slate-800 mb-2">{{ news.title }}</h1>
        <div class="flex items-center gap-3 text-xs text-slate-400 mb-4">
          <span>📰 来源: {{ sourceSummary }}</span>
          <span>🕐 发布于 {{ news.publishedAt }}</span>
          <span>🔥 热度指数: {{ news.hotIndex }}/100</span>
        </div>
        <div class="flex gap-1.5 mb-4">
          <span v-for="tag in news.tags" :key="tag" class="text-[10px] px-2 py-0.5 rounded-full border" :class="getTagColor(tag)">{{ tag }}</span>
        </div>
      </div>

      <!-- AI Summary -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
        <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-brand-500 rounded-full"></span> AI 智能摘要</h2>
        <div class="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
          <p class="text-sm text-slate-700 leading-relaxed">{{ news.summary }}</p>
        </div>
      </div>

      <!-- Multi-source Coverage -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
        <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-green-500 rounded-full"></span> 多源报道聚合</h2>
        <div class="space-y-3">
          <div v-for="src in (news.sources || [])" :key="src.title + src.name" class="p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer" @click="openSourceUrl(src.url)">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded" :class="getSourceBadgeClass(src.name)">{{ src.name }}</span>
              <span class="text-xs text-slate-400">{{ src.time }}</span>
            </div>
            <p class="text-sm text-slate-700 font-medium">{{ src.title }}</p>
            <p class="text-xs text-slate-500 mt-1">{{ src.excerpt }}</p>
            <span class="text-xs text-brand-600 hover:underline mt-1 inline-block">阅读原文 →</span>
          </div>
        </div>
      </div>

      <!-- Key Data -->
      <div v-if="news.keyData && news.keyData.length" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-3">
        <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2"><span class="w-1.5 h-5 bg-amber-500 rounded-full"></span> 关键数据</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="item in news.keyData" :key="item.label" class="text-center p-3 bg-slate-50 rounded-xl">
            <div :class="getKeyDataColor(item.color)">{{ item.value }}<span v-if="item.unit" class="text-xs text-slate-400">{{ item.unit }}</span></div>
            <div class="text-[10px] text-slate-500 mt-1">{{ item.label }}</div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-12 text-slate-400">
      <template v-if="loading">
        <Loader class="w-6 h-6 text-brand-500 animate-spin mx-auto mb-2" />
        <p>加载中...</p>
      </template>
      <p v-else>新闻未找到</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, Loader } from 'lucide-vue-next'
import { useBriefsApi } from '~/composables/useApi'
import type { TopNews } from '~/types/brief'

const { fetchByDate } = useBriefsApi()

const router = useRouter()
const route = useRoute()

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/briefs')
  }
}
const news = ref<TopNews | undefined>(undefined)
const loading = ref(true)

const sourceSummary = computed(() => {
  const sources = news.value?.sources || []
  if (sources.length === 0) return news.value?.source || '综合媒体'
  const names = [...new Set(sources.map(s => s.name))]
  return names.slice(0, 3).join(' · ') + (names.length > 3 ? ` 等${names.length}家媒体` : '')
})

const sourceBadgePool = ['bg-blue-100 text-blue-600', 'bg-orange-100 text-orange-600', 'bg-red-100 text-red-600', 'bg-green-100 text-green-600', 'bg-purple-100 text-purple-600']
const getSourceBadgeClass = (name: string) => sourceBadgePool[name.length % sourceBadgePool.length]

onMounted(async () => {
  const date = (route.query.date as string) || new Date().toISOString().substring(0, 10)
  const brief = await fetchByDate(date)
  if (brief) {
    news.value = brief.topNews.find((n: TopNews) => n.id === route.params.id)
  }
  loading.value = false
})

const openSourceUrl = (url?: string) => {
  if (url) window.open(url, '_blank', 'noopener')
}

const tagColorPool = ['bg-blue-50 text-blue-600 border-blue-100', 'bg-green-50 text-green-600 border-green-100', 'bg-amber-50 text-amber-600 border-amber-100', 'bg-purple-50 text-purple-600 border-purple-100']
const getTagColor = (tag: string) => tagColorPool[tag.length % tagColorPool.length]

const keyDataColorMap: Record<string, string> = {
  blue: 'text-xl font-extrabold text-blue-600',
  green: 'text-xl font-extrabold text-green-600',
  amber: 'text-xl font-extrabold text-amber-600',
  purple: 'text-xl font-extrabold text-purple-600',
  red: 'text-xl font-extrabold text-red-600',
  indigo: 'text-xl font-extrabold text-indigo-600',
}
const getKeyDataColor = (color: string) => keyDataColorMap[color] || keyDataColorMap['blue']
</script>
