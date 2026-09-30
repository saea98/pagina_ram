<script setup lang="ts">
import { useAdminSession } from '~/composables/useAdminApi'

const open = ref(false)
const { user } = useAdminSession()
const toast = useState('admin-toast', () => '')
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
        <NuxtLink v-for="[to, label] in links" :key="to" :to="to" @click="open = false">{{
          label
        }}</NuxtLink>
        <NuxtLink v-if="user?.role === 'superadmin'" to="/admin/usuarios" @click="open = false"
          >Usuarios</NuxtLink
        >
        <button class="linkish" type="button" @click="logout">Cerrar sesión</button>
      </nav>
      <button class="admin-backdrop" type="button" aria-label="Cerrar menú" @click="open = false" />
    </div>
    <aside class="admin-nav">
      <nav>
        <NuxtLink v-for="[to, label] in links" :key="`desk-${to}`" :to="to">{{ label }}</NuxtLink>
        <NuxtLink v-if="user?.role === 'superadmin'" to="/admin/usuarios">Usuarios</NuxtLink>
        <button class="linkish" type="button" @click="logout">Cerrar sesión</button>
      </nav>
    </aside>
    <div>
      <header class="admin-top">
        <button class="admin-menu" type="button" @click="open = true">Menú</button>
        <p class="admin-brand">Cherry</p>
      </header>
      <main class="admin-main">
        <p v-if="toast" class="admin-toast" role="status">{{ toast }}</p>
        <slot />
      </main>
    </div>
  </div>
</template>
