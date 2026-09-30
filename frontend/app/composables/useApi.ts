export function apiBase(): string {
  const config = useRuntimeConfig()
  if (import.meta.server) return `${config.apiInternalUrl}/api/v1`
  return config.public.apiBase
}

export function usePublic<T>(path: string, key: string) {
  return useFetch<T>(path, { baseURL: apiBase(), key })
}
