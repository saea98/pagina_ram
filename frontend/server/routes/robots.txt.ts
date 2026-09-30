export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  if (config.public.environment !== 'production') {
    return 'User-agent: *\nDisallow: /\n'
  }
  return `User-agent: *\nDisallow: /admin\nDisallow: /api\nSitemap: ${config.public.siteUrl}/sitemap.xml\n`
})
