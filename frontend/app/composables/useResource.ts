import { adminFetch } from '~/composables/useAdminApi'

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface ResourceRow {
  id: string
  is_published?: boolean
  sort_order?: number
  [key: string]: unknown
}

export function useResource<T extends ResourceRow>(name: string) {
  const base = `/admin/${name}`
  return {
    list(q = '') {
      return adminFetch<Page<T>>(base, { query: { q, page: 1, page_size: 100 } })
    },
    get(id: string) {
      return adminFetch<T>(`${base}/${id}`)
    },
    create(body: Record<string, unknown>) {
      return adminFetch<T>(base, { method: 'POST', body })
    },
    update(id: string, body: Record<string, unknown>) {
      return adminFetch<T>(`${base}/${id}`, { method: 'PATCH', body })
    },
    remove(id: string) {
      return adminFetch<null>(`${base}/${id}`, { method: 'DELETE' })
    },
    reorder(ids: string[]) {
      return adminFetch<null>(`${base}/reorder`, { method: 'POST', body: { ids } })
    },
  }
}
