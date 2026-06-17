<template>
  <div class="fade-in">
    <div class="flex items-center gap-3 mb-6">
      <button @click="goBack" class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-500 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors cursor-pointer">
        <ArrowLeft class="w-4 h-4" /> 返回
      </button>
      <span class="text-xs text-slate-300">|</span>
      <span class="text-xs text-slate-400">聚类分析</span>
    </div>

    <template v-if="cluster">
      <!-- Cluster Header -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-6 mb-4">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-2"><span class="text-2xl">{{ cluster.icon }}</span><span class="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">主题簇</span></div>
            <h1 class="text-xl font-bold text-slate-800 mb-1">{{ cluster.label }}</h1>
            <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
              <span>📖 包含 {{ cluster.articleCount }} 篇文章</span><span>📅 时间跨度 {{ cluster.timeSpan }}</span><span>⭐ 重要性 {{ cluster.importance }}/5</span>
            </div>
            <div class="flex gap-1.5 mt-2">
              <span v-for="tag in cluster.tags" :key="tag" class="text-[10px] px-1.5 py-0.5 rounded border" :class="getTagStyle(tag)">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Event Timeline -->
      <div v-if="cluster.timeline.length > 0" class="bg-white rounded-xl border border-slate-200/80 p-6 mb-4">
        <h2 class="text-base font-bold text-slate-800 mb-4 flex items-center gap-2"><span class="w-1.5 h-5 bg-purple-500 rounded-full"></span> 事件时间线</h2>
        <div class="space-y-0">
          <div v-for="(item, idx) in cluster.timeline" :key="idx" class="step-line" :class="{ 'pb-5': idx < cluster.timeline.length - 1 }">
            <div class="step-dot" :class="item.done ? 'done' : 'pending'">{{ item.done ? '✓' : '○' }}</div>
            <div class="text-xs text-slate-400">{{ item.date }}</div>
            <p class="text-sm text-slate-700 font-medium mt-0.5">{{ item.title }}</p>
            <p class="text-xs text-slate-500">{{ item.description }}</p>
          </div>
        </div>
      </div>

      <!-- Related Articles -->
      <div v-if="cluster.articles.length > 0" class="bg-white rounded-xl border border-slate-200/80 p-6">
        <h2 class="text-base font-bold text-slate-800 mb-4 flex items-center gap-2"><span class="w-1.5 h-5 bg-green-500 rounded-full"></span> 相关文章列表（{{ cluster.articleCount }}篇）</h2>
        <div class="space-y-2 max-h-[500px] overflow-y-auto scrollbar-thin">
          <div v-for="(article, idx) in cluster.articles" :key="idx"
            class="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
            @click="openArticleUrl(article.url)">
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-slate-700">{{ article.title }}</p>
              <p class="text-xs text-slate-400 mt-0.5">{{ article.source }} · {{ article.date }} · 阅读量 {{ article.views }}</p>
            </div>
            <span class="text-brand-600 text-xs hover:underline ml-3 whitespace-nowrap">查看原文 ↗</span>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-12 text-slate-400">
      <template v-if="loading">
        <Loader class="w-6 h-6 text-brand-500 animate-spin mx-auto mb-2" />
        <p>加载中...</p>
      </template>
      <p v-else>聚类未找到</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, Loader } from 'lucide-vue-next'
import { useClustersApi } from '~/composables/useApi'
import type { NewsCluster } from '~/types/cluster'

const { fetchById } = useClustersApi()

const router = useRouter()
const route = useRoute()

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/clusters')
  }
}
const cluster = ref<NewsCluster | null>(null)
const loading = ref(true)

const loadData = async () => {
  const id = route.params.id as string
  cluster.value = await fetchById(id)
  loading.value = false
}

onMounted(() => loadData())

const openArticleUrl = (url?: string) => {
  if (url) window.open(url, '_blank', 'noopener')
}

const tagStyles = ['bg-blue-50 text-blue-600 border-blue-100', 'bg-green-50 text-green-600 border-green-100', 'bg-purple-50 text-purple-600 border-purple-100', 'bg-orange-50 text-orange-600 border-orange-100']
const getTagStyle = (tag: string) => tagStyles[tag.length % tagStyles.length]
</script>
