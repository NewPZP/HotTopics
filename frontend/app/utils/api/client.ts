// 统一 API 客户端 — 基于 Nuxt $fetch，自动代理到后端
import type { PaginationInfo } from '~/types/common'

// 开发环境通过 Nuxt devProxy 代理，生产环境使用同源或环境变量
const API_BASE = '/api/v1'

interface ApiResponse<T = any> {
  success?: boolean
  message?: string
  data?: T
  pagination?: PaginationInfo
}

export const apiClient = {
  async get<T = any>(path: string, params?: Record<string, any>): Promise<T> {
    const query = params ? '?' + new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v !== undefined && v !== '').map(([k, v]) => [k, String(v)])
    ).toString() : ''
    const res = await $fetch<ApiResponse<T> | T>(`${API_BASE}${path}${query}`, {
      method: 'GET',
    })
    // 兼容 { data: T } 和直接返回 T 两种格式
    if (res && typeof res === 'object' && 'data' in res) {
      return (res as ApiResponse<T>).data as T
    }
    return res as T
  },

  async post<T = any>(path: string, body?: any): Promise<T> {
    const res = await $fetch<ApiResponse<T> | T>(`${API_BASE}${path}`, {
      method: 'POST',
      body,
    })
    if (res && typeof res === 'object' && 'data' in res) {
      return (res as ApiResponse<T>).data as T
    }
    return res as T
  },

  async put<T = any>(path: string, body?: any): Promise<T> {
    const res = await $fetch<ApiResponse<T> | T>(`${API_BASE}${path}`, {
      method: 'PUT',
      body,
    })
    if (res && typeof res === 'object' && 'data' in res) {
      return (res as ApiResponse<T>).data as T
    }
    return res as T
  },

  async delete<T = any>(path: string): Promise<T> {
    const res = await $fetch<ApiResponse<T> | T>(`${API_BASE}${path}`, {
      method: 'DELETE',
    })
    if (res && typeof res === 'object' && 'data' in res) {
      return (res as ApiResponse<T>).data as T
    }
    return res as T
  },

  /** 获取分页响应，返回 { data, pagination } */
  async getPaginated<T = any>(path: string, params?: Record<string, any>): Promise<{ data: T; pagination: PaginationInfo }> {
    const query = params ? '?' + new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v !== undefined && v !== '').map(([k, v]) => [k, String(v)])
    ).toString() : ''
    return await $fetch<{ data: T; pagination: PaginationInfo }>(`${API_BASE}${path}${query}`, {
      method: 'GET',
    })
  },
}

/** WebSocket 连接地址 */
export const WS_BASE = `ws://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`
