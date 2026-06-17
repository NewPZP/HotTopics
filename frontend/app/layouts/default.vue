<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Header -->
    <header class="fixed top-0 left-0 right-0 z-50 glass-card border-b border-slate-200/80" style="height: 56px">
      <div class="h-full max-w-[1400px] mx-auto px-6 flex items-center gap-1">
        <!-- Logo -->
        <NuxtLink to="/" class="flex items-center gap-2.5 mr-6 text-decoration-none">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-extrabold text-sm" style="background: linear-gradient(135deg, #2d8eff, #10b981)">
            智
          </div>
          <span class="font-bold text-lg tracking-tight text-slate-800">智览</span>
          <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-200/50 hidden sm:inline">AI</span>
        </NuxtLink>

        <!-- Navigation Links -->
        <nav class="flex items-center h-full gap-0.5">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="nav-link h-full flex items-center px-3.5 text-sm font-medium text-slate-600"
          >
            <component :is="item.icon" class="w-4 h-4 mr-1.5" />
            {{ item.label }}
          </NuxtLink>
        </nav>

        <!-- Right Side -->
        <div class="ml-auto flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-green-50 border border-green-200/60 text-xs font-medium text-green-700">
            <span class="w-1.5 h-1.5 rounded-full bg-green-500 pulse-dot"></span> 系统运行中
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-[56px] min-h-screen">
      <div class="max-w-[1400px] mx-auto px-6 py-6">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { LayoutDashboard, Newspaper, FileText, GitBranch, Activity, Settings } from 'lucide-vue-next'

const navItems = [
  { to: '/', label: '工作台', icon: LayoutDashboard },
  { to: '/briefs', label: '每日简报', icon: Newspaper },
  { to: '/reports', label: '研报中心', icon: FileText },
  { to: '/clusters', label: '聚类分析', icon: GitBranch },
  { to: '/monitor', label: '实时监控', icon: Activity },
  { to: '/settings', label: '配置', icon: Settings },
]
</script>
