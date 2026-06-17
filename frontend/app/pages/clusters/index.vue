<template>
  <div class="fade-in">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">聚类分析</h1>
        <p class="text-sm text-slate-500 mt-0.5">语义聚类 + 力导向图，洞察资讯之间的深层关联</p>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="topicFilter" class="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 cursor-pointer outline-none"><option value="">全部主题</option><option value="AI监管">AI监管</option><option value="半导体">半导体</option><option value="新能源">新能源</option></select>
        <select v-model="timeRange" class="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 cursor-pointer outline-none"><option value="today">今日</option><option value="3days">近3天</option><option value="7days">近7天</option></select>
        <select v-model="sortBy" class="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 cursor-pointer outline-none"><option value="importance">按重要性</option><option value="time">按时间</option></select>
      </div>
    </div>

    <!-- Graph + Clusters -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <div class="lg:col-span-3 bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">聚类关系图（力导向图）</h3>
        <p class="text-xs text-slate-400 mb-3">节点大小表示簇重要性 · 连线表示主题关联度</p>
        <div ref="clusterChartRef" style="height: 420px;"></div>
      </div>

      <div class="lg:col-span-2 space-y-3">
        <h3 class="text-sm font-semibold text-slate-700">主题簇列表（共{{ totalCount }}簇）</h3>
        <div ref="listRef" class="space-y-3 max-h-[440px] overflow-y-auto scrollbar-thin pr-1" @scroll="onScroll">
          <div v-for="cluster in clusters" :key="cluster.id"
            class="bg-white rounded-xl border border-slate-200/80 p-4 hover:border-brand-300 hover:shadow-sm transition-all cursor-pointer"
            @click="navigateTo(`/clusters/${cluster.id}`)">
            <div class="flex items-center gap-2 mb-2"><span class="text-lg">{{ cluster.icon }}</span><span class="text-sm font-semibold text-slate-800">{{ cluster.label }}</span></div>
            <div class="flex items-center gap-3 text-[11px] text-slate-400 mb-2"><span>{{ cluster.articleCount }}篇文章</span><span>时间跨度 {{ cluster.timeSpan }}</span></div>
            <div class="text-xs text-amber-500 mb-2">{{ '⭐'.repeat(cluster.importance) }}</div>
            <p class="text-xs text-slate-500 leading-relaxed mb-2">{{ cluster.summary }}</p>
            <div class="flex gap-1 flex-wrap">
              <span v-for="tag in cluster.tags" :key="tag" class="text-[10px] px-1.5 py-0.5 rounded" :class="getClusterTagColor(tag)">{{ tag }}</span>
            </div>
            <button class="mt-2 text-xs text-brand-600 hover:underline" @click.stop="navigateTo(`/clusters/${cluster.id}`)">查看详情 &rarr;</button>
          </div>
          <!-- 滚动加载指示器 -->
          <div v-if="loadingMore" class="text-center py-2 text-xs text-slate-400">加载中...</div>
          <div v-else-if="!hasMore && clusters.length > 0" class="text-center py-2 text-xs text-slate-300">已加载全部</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { useClustersApi } from '~/composables/useApi'
import type { NewsCluster, ClusterNode, ClusterLink } from '~/types/cluster'

const { fetchList, fetchGraph } = useClustersApi()

const clusters = ref<NewsCluster[]>([])
const graphData = ref<{ nodes: ClusterNode[]; links: ClusterLink[] }>({ nodes: [], links: [] })
const loading = ref(true)

const topicFilter = ref('')
const timeRange = ref('today')
const sortBy = ref('importance')

// 无限滚动状态
const listRef = ref<HTMLElement | null>(null)
const currentPage = ref(1)
const pageSize = 10
const totalCount = ref(0)
const loadingMore = ref(false)
const hasMore = computed(() => clusters.value.length < totalCount.value)

const clusterChartRef = ref<HTMLDivElement | null>(null)
let clusterChart: echarts.ECharts | null = null

const initChart = () => {
  if (clusterChartRef.value) {
    clusterChart?.dispose()
    clusterChart = echarts.init(clusterChartRef.value)
    clusterChart.setOption({
      tooltip: {},
      series: [{
        type: 'graph', layout: 'force', roam: true, draggable: true,
        force: { repulsion: 300, edgeLength: [80, 200], gravity: 0.1 },
        data: graphData.value.nodes, links: graphData.value.links,
        label: { show: true, fontSize: 10, color: '#334155', fontWeight: 500 },
        edgeSymbol: ['none', 'arrow'],
        lineStyle: { color: '#cbd5e1', width: 1, curveness: 0.15, opacity: 0.7 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 2 } },
      }],
    })
  }
}

/** 滚动到底部时自动加载下一页 */
const onScroll = () => {
  const el = listRef.value
  if (!el || loadingMore.value || !hasMore.value) return
  const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40
  if (nearBottom) loadMore()
}

/** 加载下一页，追加到列表 */
const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  try {
    const nextPage = currentPage.value + 1
    const result = await fetchList({
      page: nextPage,
      pageSize,
      sort: sortBy.value,
      topic: topicFilter.value || undefined,
    })
    clusters.value.push(...(Array.isArray(result.data) ? result.data : []))
    totalCount.value = result.pagination?.total ?? totalCount.value
    currentPage.value = nextPage
  } catch (err) {
    console.error('加载更多聚类失败:', err)
  } finally {
    loadingMore.value = false
  }
}

/** 首次加载 / 筛选条件变化时重新加载 */
const loadData = async (reset = false) => {
  if (reset) {
    currentPage.value = 1
    clusters.value = []
  }
  loading.value = true
  try {
    const result = await fetchList({
      page: 1,
      pageSize,
      sort: sortBy.value,
      topic: topicFilter.value || undefined,
    })
    clusters.value = Array.isArray(result.data) ? result.data : []
    totalCount.value = result.pagination?.total ?? 0
    currentPage.value = 1
    graphData.value = await fetchGraph()
  } catch (err) {
    console.error('加载聚类列表失败:', err)
    clusters.value = []
  } finally {
    loading.value = false
    nextTick(() => initChart())
  }
}

onMounted(async () => {
  await loadData()
  window.addEventListener('resize', () => clusterChart?.resize())
})

// 筛选条件变化时重置
watch([topicFilter, timeRange, sortBy], () => loadData(true))

onBeforeUnmount(() => { clusterChart?.dispose() })

const tagColors = ['bg-blue-50 text-blue-600', 'bg-green-50 text-green-600', 'bg-purple-50 text-purple-600', 'bg-orange-50 text-orange-600', 'bg-red-50 text-red-600']
const getClusterTagColor = (tag: string) => tagColors[tag.length % tagColors.length]
</script>
