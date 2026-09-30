export function apiBase(): string {
  const config = useRuntimeConfig()
  if (import.meta.server) return `${config.apiInternalUrl}/api/v1`
  return config.public.apiBase
}

export function usePublic<T>(path: string, key: string) {
  const route = useRoute()
  const preview = route.query.preview
  const token = typeof preview === 'string' ? preview : ''
  const full = token
    ? `${path}${path.includes('?') ? '&' : '?'}preview=${encodeURIComponent(token)}`
    : path
  return useFetch<T>(full, { baseURL: apiBase(), key: token ? `${key}:${token}` : key })
}
