import { adminFetch, useAdminSession } from '~/composables/useAdminApi'

const OPEN = ['/admin/login', '/admin/recuperar', '/admin/restablecer']

export default defineNuxtRouteMiddleware(async (to) => {
  if (!to.path.startsWith('/admin') || import.meta.server) return
  if (OPEN.includes(to.path)) return
  const { user } = useAdminSession()
  try {
    user.value = await adminFetch('/auth/me')
  } catch {
    user.value = null
    return navigateTo('/admin/login')
  }
  if (to.path.startsWith('/admin/usuarios') && user.value?.role !== 'superadmin') {
    return navigateTo('/admin')
  }
})
