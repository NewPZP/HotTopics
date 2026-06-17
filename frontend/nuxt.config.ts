// https://nuxt.com/docs/api/configuration/nuxt-config
const apiTarget = process.env.NUXT_API_TARGET || 'http://localhost:8000'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  ssr: false,

  modules: ['@pinia/nuxt', '@nuxtjs/tailwindcss'],

  app: {
    head: {
      title: '智览 — AI自动化研报/新闻摘要生成平台',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1.0' },
      ],
      link: [
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500;600;700;900&display=swap',
        },
      ],
    },
  },

  nitro: {
    devProxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        prependPath: true,
      },
    },
  },

  vite: {
    server: {
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    config: {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            brand: {
              50: '#eef7ff', 100: '#d9edff', 200: '#bce0ff', 300: '#8ecdff',
              400: '#58b0ff', 500: '#2d8eff', 600: '#1a6ef5', 700: '#1359e1',
              800: '#1649b6', 900: '#18408f',
            },
            accent: {
              50: '#ecfdf5', 100: '#d1fae5', 200: '#a7f3d0', 300: '#6ee7b7',
              400: '#34d399', 500: '#10b981', 600: '#059669', 700: '#047857',
              800: '#065f46', 900: '#064e3b',
            },
            warm: {
              50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa', 300: '#fdba74',
              400: '#fb923c', 500: '#f97316', 600: '#ea580c', 700: '#c2410c',
              800: '#9a3412', 900: '#7c2d12',
            },
          },
        },
      },
    },
  },
})
