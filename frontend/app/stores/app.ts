// 全局应用状态
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { StepStatus } from '~/types/workflow'

export const useAppStore = defineStore('app', () => {
  // 侧边栏
  const sidebarCollapsed = ref(false)

  // 导航历史
  const navHistory = ref<Array<{ type: string; name?: string; id?: string }>>([])

  // 全局日期范围
  const dateRange = ref<[string, string]>(['', ''])

  // 工作流简要状态（由 API 更新）
  const workflowStatus = ref({
    isRunning: false,
    steps: [] as Array<{ name: string; label: string; status: StepStatus; count: string }>,
    progress: 0,
  })

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  /** 从 API 获取的工作流状态更新本地 store */
  const updateFromApi = (data: {
    isRunning?: boolean
    pipelineSteps?: Array<{ name: string; label: string; status: string; count: string; progress?: number }>
    totalProgress?: number
  }) => {
    if (data.isRunning !== undefined) workflowStatus.value.isRunning = data.isRunning
    if (data.pipelineSteps) {
      workflowStatus.value.steps = data.pipelineSteps.map(s => ({
        name: s.name,
        label: s.label,
        status: s.status as StepStatus,
        count: s.count,
      }))
    }
    if (data.totalProgress !== undefined) workflowStatus.value.progress = data.totalProgress
  }

  return {
    sidebarCollapsed,
    navHistory,
    dateRange,
    workflowStatus,
    toggleSidebar,
    updateFromApi,
  }
})
