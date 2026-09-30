export interface AdminUser {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'superadmin'
}

interface ErrorBody {
  error?: { message?: string; fields?: Record<string, string> }
}

function csrfToken(): string {
  if (!import.meta.client) return ''
  const row = document.cookie.split('; ').find((item) => item.startsWith('csrf_token='))
  return row ? decodeURIComponent(row.slice('csrf_token='.length)) : ''
}

function statusOf(error: unknown): number | undefined {
  if (typeof error === 'object' && error && 'status' in error) {
    const status = (error as { status?: number }).status
    if (typeof status === 'number') return status
  }
  if (typeof error === 'object' && error && 'statusCode' in error) {
    const status = (error as { statusCode?: number }).statusCode
    if (typeof status === 'number') return status
  }
  return undefined
}

export function adminErrorMessage(error: unknown): string {
  const data = (error as { data?: ErrorBody }).data
  return data?.error?.message ?? 'No se pudo completar. Intenta de nuevo.'
}

export function adminErrorFields(error: unknown): Record<string, string> {
  const data = (error as { data?: ErrorBody }).data
  return data?.error?.fields ?? {}
}

export async function adminFetch<T>(
  path: string,
  options: {
    method?: string
    body?: unknown
    query?: Record<string, string | number | undefined>
  } = {},
  retry = true,
): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase() as
    'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  const headers: Record<string, string> = {}
  if (method !== 'GET') headers['X-CSRF-Token'] = csrfToken()
  try {
    return (await $fetch(`/api/v1${path}`, {
      method,
      body: options.body as Record<string, unknown> | undefined,
      query: options.query,
      headers,
      credentials: 'include',
    })) as T
  } catch (error) {
    if (statusOf(error) === 401 && retry && path !== '/auth/refresh' && path !== '/auth/login') {
      await $fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken() },
        credentials: 'include',
      })
      return adminFetch(path, options, false)
    }
    throw error
  }
}

export function useAdminSession() {
  const user = useState<AdminUser | null>('admin-user', () => null)
  return { user }
}
