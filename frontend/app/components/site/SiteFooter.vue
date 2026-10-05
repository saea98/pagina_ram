<script setup lang="ts">
import type { Site } from '~/types/public'

const props = defineProps<{ site?: Site | null }>()
const year = new Date().getFullYear()
const email = computed(() => props.site?.contact.email || '')
const instagram = computed(() => props.site?.social.instagram || '')
const handle = computed(() => instagram.value.replace(/\/$/, '').split('/').pop() || '')
const socials = computed(() => {
  const social = props.site?.social
  if (!social) return []
  return [
    { key: 'youtube', href: social.youtube, label: 'YouTube' },
    { key: 'tiktok', href: social.tiktok, label: 'TikTok' },
    { key: 'spotify', href: social.spotify, label: 'Spotify' },
    { key: 'facebook', href: social.facebook, label: 'Facebook' },
    { key: 'x', href: social.x, label: 'X' },
  ].filter((item) => item.href)
})
</script>

<template>
  <footer class="site-foot">
    <div class="foot-desktop">
      <div class="brand-mini">
        <img src="/brand/logo-crudo.png" :alt="site?.brand.name || 'Cherry Studios'" />
      </div>
      <div class="foot-center">
        <NuxtLink to="/nosotros">Acerca de Nosotros</NuxtLink>
        <NuxtLink to="/aviso-de-privacidad">Aviso de privacidad</NuxtLink>
        <div>Ciudad de México · © {{ year }} {{ site?.brand.name || 'Cherry Studios' }}</div>
      </div>
      <div class="foot-contact">
        <a v-if="instagram" :href="instagram" target="_blank" rel="noopener">@{{ handle }}</a>
        <a v-if="email" :href="`mailto:${email}`">{{ email }}</a>
      </div>
    </div>
    <div class="foot-phone">
      <div class="brand-mini">
        <img src="/brand/logo-crudo.png" :alt="site?.brand.name || 'Cherry Studios'" />
      </div>
      <nav class="foot-links" aria-label="Pie de página">
        <NuxtLink to="/#servicios">Servicios</NuxtLink>
        <NuxtLink to="/#portafolio">Portafolio</NuxtLink>
        <NuxtLink to="/nosotros">Acerca de Nosotros</NuxtLink>
        <NuxtLink to="/#contacto">Contacto</NuxtLink>
        <a v-if="email" :href="`mailto:${email}`">{{ email }}</a>
        <a v-if="instagram" :href="instagram" target="_blank" rel="noopener">@{{ handle }}</a>
        <p class="foot-label">Legal</p>
        <NuxtLink to="/aviso-de-privacidad">Aviso de privacidad</NuxtLink>
      </nav>
      <p class="foot-copy">
        Ciudad de México · © {{ year }} {{ site?.brand.name || 'Cherry Studios' }}
      </p>
      <div v-if="socials.length" class="foot-social">
        <a
          v-for="item in socials"
          :key="item.key"
          :href="item.href"
          target="_blank"
          rel="noopener"
          :aria-label="item.label"
        >
          <svg v-if="item.key === 'youtube'" viewBox="0 0 24 24" aria-hidden="true">
            <rect x="2" y="5" width="20" height="14" rx="4" />
            <path d="m10 9 6 3-6 3z" fill="currentColor" stroke="none" />
          </svg>
          <svg v-else-if="item.key === 'tiktok'" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M14 4v10.2a3.2 3.2 0 1 1-2.2-3V8.4A6.2 6.2 0 0 0 16 10V7.2A8 8 0 0 1 14 6.6V4z"
            />
          </svg>
          <svg v-else-if="item.key === 'spotify'" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="9" />
            <path
              d="M7.5 10.2c2.8-1 6.2-.8 8.8.6M8 13c2.2-.8 4.8-.6 6.8.5M8.6 15.6c1.7-.5 3.6-.4 5.2.4"
            />
          </svg>
          <svg v-else-if="item.key === 'facebook'" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h2.6l.4-3H13v-2c0-.6.4-1 1-1z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M14.5 10.2 21.2 3h-1.6l-5.8 6.3L9 3H3.2l7 9.5L3.2 21H4.8l6.1-6.7L15 21h5.8l-6.3-10.8z"
            />
          </svg>
        </a>
      </div>
    </div>
  </footer>
</template>
