<script setup lang="ts">
import type { Site } from '~/types/public'

const { data: site } = await usePublic<Site>('/public/site', 'site')
const route = useRoute()
const sheet = computed(() => ['/aviso-de-privacidad', '/nosotros'].includes(route.path))
</script>

<template>
  <div>
    <SiteSplash />
    <SiteHeader :site="site" />
    <SiteProgressRail v-if="!sheet" />
    <div class="site-clip">
      <slot />
      <SiteFooter :site="site" />
    </div>
    <SiteWhatsAppFloat v-if="site" :site="site" variant="corner" />
    <SiteWhatsAppFloat v-if="site" :site="site" />
    <ClientOnly>
      <PlayerGlobalPlayer />
    </ClientOnly>
  </div>
</template>
