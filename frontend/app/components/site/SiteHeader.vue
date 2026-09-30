<script setup lang="ts">
import type { Site } from '~/types/public'

defineProps<{ site?: Site | null }>()
const open = ref(false)
const scrolled = ref(false)
const active = ref('')
const route = useRoute()
const solid = computed(() => route.path === '/aviso-de-privacidad')

const links = [
  { href: '/#estudio', id: 'estudio', label: 'Estudio' },
  { href: '/#equipo', id: 'equipo', label: 'Equipo' },
  { href: '/#servicios', id: 'servicios', label: 'Servicios' },
  { href: '/#portafolio', id: 'portafolio', label: 'Portafolio' },
]

function close() {
  open.value = false
}

onMounted(() => {
  const onScroll = () => {
    scrolled.value = window.scrollY > 12
  }
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  const sections = links
    .map((link) => document.getElementById(link.id))
    .filter((section): section is HTMLElement => section !== null)
  const spy = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) active.value = entry.target.id
      }
    },
    { rootMargin: '-45% 0px -50% 0px', threshold: 0 },
  )
  sections.forEach((section) => spy.observe(section))
  onUnmounted(() => {
    window.removeEventListener('scroll', onScroll)
    spy.disconnect()
  })
})
</script>

<template>
  <header class="nav" :class="{ scrolled, solid }">
    <div class="nav-inner">
      <NuxtLink class="brand" to="/#inicio">
        <img src="/brand/logo-color.png" :alt="site?.brand.name || 'Cherry Studios'" />
      </NuxtLink>
      <nav class="links" aria-label="Secciones">
        <NuxtLink
          v-for="link in links"
          :key="link.id"
          :to="link.href"
          :class="{ active: active === link.id }"
          :data-sec="link.id"
        >
          {{ link.label }}
        </NuxtLink>
      </nav>
      <NuxtLink class="nav-cta" to="/#contacto">Contacto</NuxtLink>
      <button
        class="nav-burger"
        type="button"
        :aria-expanded="open"
        aria-label="Abrir menú"
        @click="open = !open"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
    </div>
  </header>
  <div class="mobile-menu" :class="{ open }">
    <NuxtLink v-for="link in links" :key="link.id" :to="link.href" @click="close">{{
      link.label
    }}</NuxtLink>
    <NuxtLink to="/#contacto" @click="close">Contacto</NuxtLink>
  </div>
</template>
