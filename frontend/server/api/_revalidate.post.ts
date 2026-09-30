export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const token = getHeader(event, 'x-internal-token')
  if (!config.internalRevalidateToken || token !== config.internalRevalidateToken) {
    throw createError({ statusCode: 401, statusMessage: 'No autorizado.' })
  }
  const body = await readBody<{ paths?: string[] }>(event).catch(() => ({ paths: [] as string[] }))
  const storage = useStorage('cache')
  const keys = await storage.getKeys()
  const paths = body?.paths ?? []
  for (const key of keys) {
    if (!paths.length || paths.some((path) => key.includes(path))) await storage.removeItem(key)
  }
  return { ok: true }
})
