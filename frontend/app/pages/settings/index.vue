<template>
  <div class="fade-in">
    <!-- Toast 提示 -->
    <Transition name="toast">
      <div v-if="toast.show" :class="toast.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-red-50 border-red-300 text-red-800'" class="fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border shadow-lg text-sm font-medium">
        <CheckCircle v-if="toast.type === 'success'" class="w-4 h-4 text-emerald-500" />
        <XCircle v-else class="w-4 h-4 text-red-500" />
        {{ toast.message }}
      </div>
    </Transition>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight">系统配置</h1>
      <p class="text-sm text-slate-500 mt-0.5">管理监控主题 · 爬虫站点配置 · 采集频率 · 推送渠道</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 监控主题管理 -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><Tags class="w-4 h-4 text-brand-600" /> 监控主题管理</h3>
        <div class="space-y-2 mb-4">
          <div v-for="topic in topics" :key="topic.id" class="flex items-center justify-between p-3 bg-slate-50 rounded-lg group">
            <div class="flex-1 min-w-0">
              <span class="text-sm font-medium text-slate-700">{{ topic.name }}</span>
              <span v-if="editingTopicId !== topic.id" class="text-xs text-slate-400 ml-2">关键词: {{ (topic.keywords || []).join(', ') || '未设置' }}</span>
              <span v-if="editingTopicId !== topic.id" class="inline-flex items-center ml-1 cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity" @click="startEditTopic(topic)">
                <Pencil class="w-3 h-3 text-slate-400 hover:text-brand-600" />
              </span>
              <div v-if="editingTopicId === topic.id" class="flex items-center gap-1.5 mt-1">
                <input v-model="editingKeywords" type="text" placeholder="英文逗号分隔关键词，如：AI,芯片,监管" class="flex-1 text-xs border border-slate-200 rounded-md px-2 py-1 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500" @keyup.enter="saveTopicKeywords(topic.id)" @keyup.escape="cancelEditTopic">
                <button class="p-1 text-emerald-500 hover:text-emerald-700" @click="saveTopicKeywords(topic.id)"><Check class="w-3.5 h-3.5" /></button>
                <button class="p-1 text-slate-400 hover:text-slate-600" @click="cancelEditTopic"><XCircle class="w-3.5 h-3.5" /></button>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span class="w-2 h-2 rounded-full" :class="topic.enabled ? 'bg-green-500' : 'bg-slate-300'"></span>
              <span class="text-xs" :class="topic.enabled ? 'text-green-600' : 'text-slate-400'">{{ topic.enabled ? '启用' : '暂停' }}</span>
              <button class="text-xs text-slate-400 hover:text-red-500" @click="removeTopic(topic.id)">✕</button>
            </div>
          </div>
        </div>
        <div class="space-y-2">
          <input v-model="newTopicName" type="text" placeholder="输入新主题名称..." class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
          <input v-model="newTopicKeywords" type="text" placeholder="关键词（英文逗号分隔，如：AI,芯片,监管）" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
          <button class="w-full py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors" @click="addTopic">添加主题</button>
        </div>
      </div>

      <!-- 爬虫站点配置 -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-slate-700 flex items-center gap-2"><Globe class="w-4 h-4 text-orange-600" /> 爬虫站点配置</h3>
          <button class="text-xs px-3 py-1.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors flex items-center gap-1" @click="showSiteForm = !showSiteForm">
            <Plus class="w-3.5 h-3.5" />
            {{ showSiteForm ? '取消' : '新增站点' }}
          </button>
        </div>

        <!-- 新增/编辑表单 -->
        <div v-if="showSiteForm" class="mb-4 p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-3">
          <p class="text-xs font-medium text-slate-500">{{ editingSite ? '编辑站点' : '新增站点' }}</p>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-500 block mb-1">站点名称</label>
              <input v-model="siteForm.name" type="text" placeholder="如：新浪财经" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
            </div>
            <div>
              <label class="text-xs text-slate-500 block mb-1">分类标签</label>
              <select v-model="siteForm.category" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none">
                <option value="金融">金融</option>
                <option value="AI">AI</option>
                <option value="科技">科技</option>
                <option value="综合">综合</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="text-xs text-slate-500 block mb-1">站点 URL</label>
              <input v-model="siteForm.url" type="text" placeholder="https://example.com/news" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
            </div>
            <div class="col-span-2">
              <label class="text-xs text-slate-500 block mb-1">CSS 选择器</label>
              <input v-model="siteForm.selector" type="text" placeholder=".news-list a, .headline h2 a" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
            </div>
            <div>
              <label class="text-xs text-slate-500 block mb-1">链接属性</label>
              <input v-model="siteForm.linkAttr" type="text" placeholder="href" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
            </div>
          </div>
          <div class="flex gap-2 pt-1">
            <button class="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors" @click="saveSite">{{ editingSite ? '保存修改' : '确认添加' }}</button>
            <button v-if="editingSite" class="px-4 py-2 text-sm text-slate-500 hover:text-slate-700" @click="resetSiteForm">取消编辑</button>
          </div>
        </div>

        <!-- 站点列表 -->
        <div class="space-y-2">
          <div v-for="site in crawlerSites" :key="site.id" class="flex items-center justify-between p-3 bg-slate-50 rounded-lg group">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-slate-700 truncate">{{ site.name }}</span>
                <span class="text-xs px-1.5 py-0.5 rounded-full font-medium" :class="categoryBadge(site.category)">{{ site.category }}</span>
              </div>
              <p class="text-xs text-slate-400 mt-0.5 truncate" :title="site.url">{{ site.url }}</p>
            </div>
            <div class="flex items-center gap-2 ml-3 shrink-0">
              <button class="text-xs text-slate-400 hover:text-brand-600 opacity-0 group-hover:opacity-100 transition-all" title="编辑" @click="editSite(site)"><Pencil class="w-3.5 h-3.5" /></button>
              <button class="text-xs text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all" title="删除" @click="removeSite(site)"><Trash2 class="w-3.5 h-3.5" /></button>
              <button class="w-9 h-5 rounded-full cursor-pointer relative transition-colors" :class="site.enabled ? 'bg-green-500' : 'bg-slate-300'" @click="toggleSite(site)">
                <div class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all" :class="site.enabled ? 'right-0.5' : 'left-0.5'"></div>
              </button>
            </div>
          </div>
          <div v-if="crawlerSites.length === 0" class="text-center text-sm text-slate-400 py-4">
            暂无爬虫站点，点击"新增站点"添加
          </div>
        </div>
      </div>

      <!-- 采集与调度配置 -->
      <div class="bg-white rounded-xl border border-slate-200/80 p-5">
        <h3 class="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><Clock class="w-4 h-4 text-amber-600" /> 采集与调度配置</h3>
        <div class="space-y-4">
          <div>
            <label class="text-xs text-slate-500 block mb-1.5">采集频率（Cron 表达式）</label>
            <select v-model="collectCron" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none cursor-pointer">
              <option value="0 */2 * * *">0 */2 * * * — 每2小时</option>
              <option value="0 */1 * * *">0 */1 * * * — 每小时</option>
              <option value="0 */4 * * *">0 */4 * * * — 每4小时</option>
              <option value="0 8,12,16,20 * * *">0 8,12,16,20 * * * — 每天4次</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-500 block mb-1.5">日报生成时间</label>
            <select v-model="briefGenTime" class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none cursor-pointer">
              <option value="18:00">每日 18:00</option>
              <option value="08:00">每日 08:00</option>
              <option value="12:00">每日 12:00</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-500 block mb-1.5">推送渠道</label>
            <div class="flex gap-4">
              <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input v-model="pushChannels" type="checkbox" value="api" class="rounded border-slate-300 text-brand-600"> REST API</label>
              <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input v-model="pushChannels" type="checkbox" value="file" class="rounded border-slate-300 text-brand-600"> 文件下载</label>
            </div>
          </div>
          <button class="w-full py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors disabled:opacity-50" :disabled="saving" @click="saveConfig">{{ saving ? '保存中...' : '保存配置' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Tags, Clock, Globe, Plus, Pencil, Trash2, CheckCircle, XCircle, Check } from 'lucide-vue-next'
import { useTopicsApi, useConfigApi, useCrawlerSitesApi } from '~/composables/useApi'
import type { TopicItem, CrawlerSite } from '~/types/common'

const { fetchList: fetchTopics, create: createTopic, update: updateTopic, remove: removeTopicApi } = useTopicsApi()
const { fetchConfig, updateConfig } = useConfigApi()
const { fetchSites, createSite, updateSite, deleteSite } = useCrawlerSitesApi()

const topics = ref<TopicItem[]>([])
const crawlerSites = ref<CrawlerSite[]>([])
const collectCron = ref('0 */2 * * *')
const briefGenTime = ref('18:00')
const pushChannels = ref<string[]>(['api', 'file'])
const newTopicName = ref('')
const newTopicKeywords = ref('')
const editingTopicId = ref<string | null>(null)
const editingKeywords = ref('')
const saving = ref(false)
const toast = ref<{ show: boolean; type: 'success' | 'error'; message: string }>({ show: false, type: 'success', message: '' })

// 爬虫站点表单
const showSiteForm = ref(false)
const editingSite = ref<CrawlerSite | null>(null)
const siteForm = reactive({ name: '', url: '', selector: '', linkAttr: 'href', category: '综合' })

const categoryBadge = (cat: string) => {
  const map: Record<string, string> = {
    '金融': 'bg-blue-100 text-blue-700',
    'AI': 'bg-purple-100 text-purple-700',
    '科技': 'bg-cyan-100 text-cyan-700',
    '综合': 'bg-slate-200 text-slate-600',
    '其他': 'bg-amber-100 text-amber-700',
  }
  return map[cat] || 'bg-slate-200 text-slate-600'
}

const loadData = async () => {
  topics.value = await fetchTopics()
  crawlerSites.value = await fetchSites()
  const config = await fetchConfig()
  collectCron.value = config.collectCron || '0 */2 * * *'
  briefGenTime.value = config.briefGenTime || '18:00'
  if (config.pushChannels) {
    pushChannels.value = typeof config.pushChannels === 'string'
      ? config.pushChannels.split(',').filter(Boolean)
      : config.pushChannels
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await updateConfig({
      collectCron: collectCron.value,
      briefGenTime: briefGenTime.value,
      pushChannels: pushChannels.value.join(','),
    })
    toast.value = { show: true, type: 'success', message: '采集与调度配置已保存' }
  } catch {
    toast.value = { show: true, type: 'error', message: '保存失败，请稍后重试' }
  } finally {
    saving.value = false
    setTimeout(() => { toast.value.show = false }, 3000)
  }
}

const addTopic = async () => {
  if (newTopicName.value.trim()) {
    const keywords = newTopicKeywords.value
      .split(',')
      .map(k => k.trim())
      .filter(Boolean)
    await createTopic({
      id: `topic-${Date.now()}`,
      name: newTopicName.value.trim(),
      keywords,
      enabled: true,
    })
    newTopicName.value = ''
    newTopicKeywords.value = ''
    await loadData()
  }
}

const startEditTopic = (topic: TopicItem) => {
  editingTopicId.value = topic.id
  editingKeywords.value = (topic.keywords || []).join(', ')
}

const saveTopicKeywords = async (id: string) => {
  const keywords = editingKeywords.value
    .split(',')
    .map(k => k.trim())
    .filter(Boolean)
  await updateTopic(id, { keywords })
  editingTopicId.value = null
  editingKeywords.value = ''
  await loadData()
}

const cancelEditTopic = () => {
  editingTopicId.value = null
  editingKeywords.value = ''
}

const removeTopic = async (id: string) => {
  await removeTopicApi(id)
  await loadData()
}

const toggleSite = async (site: CrawlerSite) => {
  site.enabled = !site.enabled
  await updateSite(site.id, { enabled: site.enabled })
}

const editSite = (site: CrawlerSite) => {
  editingSite.value = site
  siteForm.name = site.name
  siteForm.url = site.url
  siteForm.selector = site.selector
  siteForm.linkAttr = site.linkAttr || 'href'
  siteForm.category = site.category
  showSiteForm.value = true
}

const resetSiteForm = () => {
  editingSite.value = null
  siteForm.name = ''
  siteForm.url = ''
  siteForm.selector = ''
  siteForm.linkAttr = 'href'
  siteForm.category = '综合'
  showSiteForm.value = false
}

const saveSite = async () => {
  if (!siteForm.name || !siteForm.url || !siteForm.selector) {
    toast.value = { show: true, type: 'error', message: '请填写站点名称、URL 和选择器' }
    setTimeout(() => { toast.value.show = false }, 3000)
    return
  }
  try {
    if (editingSite.value) {
      await updateSite(editingSite.value.id, { ...siteForm })
      toast.value = { show: true, type: 'success', message: '站点已更新' }
    } else {
      await createSite({ ...siteForm })
      toast.value = { show: true, type: 'success', message: '站点已添加' }
    }
    resetSiteForm()
    crawlerSites.value = await fetchSites()
  } catch {
    toast.value = { show: true, type: 'error', message: '保存失败，请稍后重试' }
  } finally {
    setTimeout(() => { toast.value.show = false }, 3000)
  }
}

const removeSite = async (site: CrawlerSite) => {
  if (!confirm(`确定删除站点「${site.name}」？`)) return
  try {
    await deleteSite(site.id)
    crawlerSites.value = await fetchSites()
    toast.value = { show: true, type: 'success', message: '站点已删除' }
  } catch {
    toast.value = { show: true, type: 'error', message: '删除失败，请稍后重试' }
  } finally {
    setTimeout(() => { toast.value.show = false }, 3000)
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(1rem);
}
</style>
