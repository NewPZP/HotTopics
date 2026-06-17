<template>
  <div class="fade-in">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">研报中心</h1>
        <p class="text-sm text-slate-500 mt-0.5">浏览、搜索所有AI生成的深度行业研报</p>
      </div>
      <div class="flex items-center gap-2">
        <div class="relative">
          <Search class="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input v-model="searchQuery" type="text" placeholder="搜索研报..." class="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm w-56 focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 outline-none">
        </div>
        <select v-model="topicFilter" class="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 cursor-pointer outline-none">
          <option value="">全部主题</option><option>金融</option><option>科技</option><option>能源</option><option>汽车</option>
        </select>
        <select v-model="sortBy" class="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 cursor-pointer outline-none">
          <option value="time">按时间排序</option><option value="importance">按重要性排序</option>
        </select>
      </div>
    </div>

    <!-- Featured Report -->
    <div v-if="featuredReport" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-4 hover:shadow-md transition-shadow cursor-pointer" @click="navigateTo(`/reports/${featuredReport.id}`)">
      <div class="flex items-start gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-2">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 text-red-600 border border-red-200">今日头条</span>
            <span class="text-xs text-slate-400">生成于 {{ featuredReport.generatedAt }}</span>
          </div>
          <h2 class="text-lg font-bold text-slate-800 mb-2">{{ featuredReport.title }}</h2>
          <p class="text-sm text-slate-500 leading-relaxed mb-4">{{ featuredReport.summary }}</p>
          <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400">
            <span>📖 引用{{ featuredReport.sourceCount }}篇来源</span><span>⭐ 重要性 {{ featuredReport.importance }}/5</span><span>📅 时间跨度 {{ featuredReport.timeSpan }}</span>
          </div>
          <div class="flex gap-2 mt-3">
            <button class="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors" @click="navigateTo(`/reports/${featuredReport.id}`)">阅读全文</button>
            <button class="px-4 py-2 border border-slate-200 text-sm rounded-lg hover:bg-slate-50 transition-colors">导出PDF</button>
            <button class="px-4 py-2 border border-slate-200 text-sm rounded-lg hover:bg-slate-50 transition-colors">分享</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="report in filteredReports" :key="report.id"
        class="bg-white rounded-xl border border-slate-200/80 p-5 hover:shadow-md transition-all cursor-pointer hover:-translate-y-0.5"
        @click="navigateTo(`/reports/${report.id}`)">
        <div class="text-xs text-slate-400 mb-2">{{ report.generatedAt }}</div>
        <h3 class="text-sm font-semibold text-slate-800 mb-2">{{ report.title }}</h3>
        <p class="text-xs text-slate-500 leading-relaxed mb-3">{{ report.summary.substring(0, 50) }}...</p>
        <div class="flex items-center gap-2 text-[10px] text-slate-400 mb-3">
          <span>{{ report.sourceCount }}篇引用</span><span>{{ '⭐'.repeat(report.importance) }}</span>
        </div>
        <div class="flex gap-1.5">
          <span v-for="tag in report.tags" :key="tag" class="px-1.5 py-0.5 rounded text-[10px]" :class="getTagColor(tag)">{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="text-sm text-slate-400">加载中...</div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-6">
      <button
        class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-sm transition-colors"
        :class="currentPage <= 1 ? 'text-slate-300 cursor-not-allowed' : 'text-slate-400 hover:bg-slate-50'"
        :disabled="currentPage <= 1"
        @click="goToPage(currentPage - 1)">
        &lsaquo;
      </button>
      <template v-for="(p, idx) in visiblePages" :key="p">
        <span v-if="p === -1" class="text-slate-300 text-xs px-1">...</span>
        <button v-else
          class="w-8 h-8 rounded-lg border text-sm font-medium transition-colors"
          :class="p === currentPage ? 'bg-brand-600 text-white border-brand-600' : 'border-slate-200 text-slate-600 hover:bg-slate-50'"
          @click="goToPage(p)">
          {{ p }}
        </button>
      </template>
      <button
        class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-sm transition-colors"
        :class="currentPage >= totalPages ? 'text-slate-300 cursor-not-allowed' : 'text-slate-400 hover:bg-slate-50'"
        :disabled="currentPage >= totalPages"
        @click="goToPage(currentPage + 1)">
        &rsaquo;
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search } from 'lucide-vue-next'
import { useReportsApi } from '~/composables/useApi'
import type { Report } from '~/types/report'

const { fetchList } = useReportsApi()

const searchQuery = ref('')
const topicFilter = ref('')
const sortBy = ref('time')

const allReports = ref<Report[]>([])
const loading = ref(true)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(9)
const totalCount = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

const featuredReport = computed(() => allReports.value.find(r => r.isFeatured))

const filteredReports = computed(() => {
  const list = allReports.value.filter(r => !r.isFeatured)
  return list
})

// 可见页码：≤7 页全部显示，>7 页用滑动窗口 + 省略号
const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  // 始终显示首尾，中间用省略号
  const pages: number[] = [1]
  if (cur > 3) pages.push(-1) // 省略号
  const start = Math.max(2, cur - 1)
  const end = Math.min(total - 1, cur + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  if (cur < total - 2) pages.push(-1) // 省略号
  pages.push(total)
  return pages
})

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const loadData = async () => {
  loading.value = true
  try {
    const result = await fetchList({
      page: currentPage.value,
      pageSize: pageSize.value,
      sort: sortBy.value,
      search: searchQuery.value || undefined,
      topic: topicFilter.value || undefined,
    })
    allReports.value = Array.isArray(result.data) ? result.data : []
    totalCount.value = result.pagination?.total ?? 0
  } catch (err) {
    console.error('加载研报列表失败:', err)
    allReports.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())

// 筛选条件变化时重置到第一页并重新加载
watch([topicFilter, sortBy], () => {
  currentPage.value = 1
  loadData()
})

// 搜索关键词变化时防抖重新加载
let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadData()
  }, 300)
})

const tagColorPool = ['bg-blue-50 text-blue-600', 'bg-green-50 text-green-600', 'bg-purple-50 text-purple-600', 'bg-orange-50 text-orange-600', 'bg-red-50 text-red-600']
const getTagColor = (tag: string) => tagColorPool[tag.length % tagColorPool.length]
</script>
