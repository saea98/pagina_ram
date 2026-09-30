// https://nuxt.com/docs/api/configuration/nuxt-config
const hmrClientPort = process.env.NUXT_VITE_HMR_CLIENT_PORT

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  vite: {
    server: {
      allowedHosts: true,
      ...(hmrClientPort
        ? {
            ws: {
              protocol: 'wss',
              host: 'localhost',
              clientPort: Number(hmrClientPort),
            },
          }
        : {}),
    },
  },
  modules: ['@nuxt/eslint'],
  eslint: {
    config: {
      stylistic: false,
    },
  },
  typescript: {
    strict: true,
  },
  runtimeConfig: {
    apiInternalUrl: 'http://api:8000',
    public: {
      apiBase: '/api/v1',
      siteUrl: 'http://localhost:3000',
    },
  },
})
