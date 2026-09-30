import tailwindcss from '@tailwindcss/vite'

const hmrClientPort = process.env.NUXT_VITE_HMR_CLIENT_PORT

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: process.env.NODE_ENV !== 'production' },
  css: ['~/assets/css/main.css', '~/assets/css/admin.css'],
  modules: [
    '@nuxt/eslint',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxt/fonts',
    '@nuxtjs/sitemap',
    'nuxt-og-image',
  ],
  fonts: {
    families: [
      {
        name: 'Fraunces',
        provider: 'google',
        weights: [400, 500, 600, 700],
        styles: ['normal', 'italic'],
      },
      { name: 'Work Sans', provider: 'google', weights: [400, 500, 600, 700, 800] },
    ],
  },
  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'https://cherrystudios.com.mx',
    name: 'Cherry Studios',
  },
  sitemap: {
    sources: ['/api/_sitemap'],
  },
  ogImage: {
    defaults: { width: 1200, height: 630 },
  },
  routeRules: {
    '/': { swr: 60 },
    '/servicios/**': { swr: 60 },
    '/portafolio/**': { swr: 60 },
    '/equipo/**': { swr: 60 },
    '/links': { swr: 60 },
    '/aviso-de-privacidad': { swr: 3600 },
    '/admin/**': { ssr: false, robots: false },
    '/_styleguide': { robots: false },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'es-MX' },
      meta: [{ property: 'og:locale', content: 'es_MX' }],
    },
  },
  vite: {
    plugins: [tailwindcss()],
    server: {
      allowedHosts: true,
      ...(hmrClientPort
        ? {
            ws: {
              protocol: 'wss' as const,
              host: 'localhost',
              clientPort: Number(hmrClientPort),
            },
          }
        : {}),
    },
  },
  eslint: {
    config: { stylistic: false },
  },
  typescript: { strict: true },
  runtimeConfig: {
    apiInternalUrl: 'http://api:8000',
    internalRevalidateToken: process.env.INTERNAL_REVALIDATE_TOKEN || '',
    public: {
      apiBase: '/api/v1',
      siteUrl: 'https://localhost',
      turnstileSiteKey: '',
      environment: process.env.ENVIRONMENT || 'development',
    },
  },
})
