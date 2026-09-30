export function usePageMeta(options: {
  title: string
  description: string
  path: string
  type?: 'website' | 'music.song'
  noindex?: boolean
}) {
  const config = useRuntimeConfig()
  const canonical = new URL(options.path, config.public.siteUrl).toString()
  useSeoMeta({
    title: options.title,
    titleTemplate: options.path === '/' ? '%s' : '%s · Cherry Studios',
    description: options.description,
    ogTitle: options.title,
    ogDescription: options.description,
    ogType: options.type ?? 'website',
    ogLocale: 'es_MX',
    ogUrl: canonical,
    twitterCard: 'summary_large_image',
  })
  useHead({
    link: [{ rel: 'canonical', href: canonical }],
    meta: options.noindex ? [{ name: 'robots', content: 'noindex' }] : [],
  })
}
