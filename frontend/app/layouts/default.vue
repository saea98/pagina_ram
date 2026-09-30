<script setup lang="ts">
import type { Site } from '~/types/public'

const { data: site } = await usePublic<Site>('/public/site', 'site')
const store = usePlayerStore()
</script>

<template>
  <div :class="{ 'has-player': Boolean(store.current) }">
    <SiteSplash />
    <SiteHeader :site="site" />
    <SiteProgressRail />
    <slot />
    <SiteFooter :site="site" />
    <NuxtLink class="privacy-pill" to="/aviso-de-privacidad">Aviso de privacidad</NuxtLink>
    <SiteWhatsAppFloat v-if="site" :site="site" />
    <ClientOnly>
      <PlayerGlobalPlayer />
    </ClientOnly>
  </div>
</template>
