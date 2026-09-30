<script setup lang="ts">
import { adminFetch, useAdminSession } from '~/composables/useAdminApi'

const open = ref(false)
const route = useRoute()
const { user } = useAdminSession()
const toast = useState('admin-toast', () => '')
const newLeads = ref(0)
const links = [
  ['/admin', 'Inicio'],
  ['/admin/leads', 'Leads'],
  ['/admin/portafolio', 'Portafolio'],
  ['/admin/servicios', 'Servicios'],
  ['/admin/equipo', 'Equipo'],
  ['/admin/testimonios', 'Testimonios'],
  ['/admin/preguntas', 'FAQ'],
  ['/admin/enlaces', 'Enlaces'],
  ['/admin/medios', 'Medios'],
  ['/admin/ajustes', 'Ajustes'],
] as const

const here = computed(() => {
  if (route.path.startsWith('/admin/usuarios')) return 'Usuarios'
  const match = links.find(
    ([to]) => to !== '/admin' && (route.path === to || route.path.startsWith(`${to}/`)),
  )
  return match?.[1] ?? 'Inicio'
})

watch(toast, (message) => {
  if (!import.meta.client || !message) return
  const current = message
  window.setTimeout(() => {
    if (toast.value === current) toast.value = ''
  }, 3200)
})

onMounted(() => {
  void adminFetch<{ total: number }>('/admin/leads', {
    query: { status: 'new', page_size: 1 },
  })
    .then((page) => {
      newLeads.value = page.total
    })
    .catch(() => undefined)
})

async function logout() {
  const token = document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrf_token='))
    ?.slice('csrf_token='.length)
  await $fetch('/api/v1/auth/logout', {
    method: 'POST',
    credentials: 'include',
    headers: token ? { 'X-CSRF-Token': decodeURIComponent(token) } : {},
  }).catch(() => undefined)
  user.value = null
  await navigateTo('/admin/login')
}
</script>

<template>
  <div class="admin-shell">
    <div v-if="open" class="admin-drawer">
      <nav>
        <p class="admin-mark">Cherry Studios</p>
        <NuxtLink v-for="[to, label] in links" :key="to" :to="to" @click="open = false">
          {{ label }}
          <span v-if="to === '/admin/leads' && newLeads" class="admin-badge">{{ newLeads }}</span>
        </NuxtLink>
        <NuxtLink v-if="user?.role === 'superadmin'" to="/admin/usuarios" @click="open = false"
          >Usuarios</NuxtLink
        >
        <button class="linkish" type="button" @click="logout">Cerrar sesión</button>
      </nav>
      <button class="admin-backdrop" type="button" aria-label="Cerrar menú" @click="open = false" />
    </div>
    <aside class="admin-nav">
      <nav>
        <p class="admin-mark">Cherry Studios</p>
        <NuxtLink v-for="[to, label] in links" :key="`desk-${to}`" :to="to">
          {{ label }}
          <span v-if="to === '/admin/leads' && newLeads" class="admin-badge">{{ newLeads }}</span>
        </NuxtLink>
        <NuxtLink v-if="user?.role === 'superadmin'" to="/admin/usuarios">Usuarios</NuxtLink>
        <button class="linkish" type="button" @click="logout">Cerrar sesión</button>
      </nav>
    </aside>
    <div class="admin-content">
      <header class="admin-top">
        <button class="admin-menu" type="button" @click="open = true">Menú</button>
        <p class="admin-brand">{{ here }}</p>
      </header>
      <main class="admin-main">
        <p v-if="toast" class="admin-toast" role="status">{{ toast }}</p>
        <slot />
      </main>
    </div>
  </div>
</template>
