// 工作流与监控相关类型

export type StepStatus = 'done' | 'running' | 'pending'

export interface PipelineStep {
  name: string
  label: string
  status: StepStatus
  count: string
  progress?: number
}

export interface AgentStatus {
  name: string
  label: string
  status: 'idle' | 'running' | 'pending'
  detail: string
}

export interface LogEntry {
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR'
  agent: string
  message: string
}

export interface SystemMetrics {
  cpu: number
  memory: { used: number; total: number }
  redis: number
  dbConnections: number
}

export interface WorkflowState {
  isRunning: boolean
  lastCollectTime: string
  nextCollectTime: string
  totalProgress: number
  estimatedRemaining: string
  pipelineSteps: PipelineStep[]
  agents: AgentStatus[]
  logs: LogEntry[]
  metrics: SystemMetrics
}
