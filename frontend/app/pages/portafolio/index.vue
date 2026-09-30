<script setup lang="ts">
import type { PortfolioCard, ServiceCard, Site } from '~/types/public'

const route = useRoute()
const { data: site } = await usePublic<Site>('/public/site', 'site')
const { data: pieces } = await usePublic<PortfolioCard[]>('/public/portfolio', 'portfolio')
const { data: services } = await usePublic<ServiceCard[]>('/public/services', 'services')
const selected = computed(() =>
  typeof route.query.servicio === 'string' ? route.query.servicio : '',
)
const filtered = computed(() => {
  const list = pieces.value ?? []
  if (!selected.value) return list
  return list.filter((piece) => piece.service_slugs.includes(selected.value))
})
usePageMeta({
  title: site.value?.portfolio.title || 'Portafolio',
  description: site.value?.portfolio.note || site.value?.seo.default_description || '',
  path: '/portafolio',
})
defineOgImage('OgDefault', {
  title: site.value?.portfolio.title || 'Portafolio',
  description: site.value?.portfolio.note || '',
})
</script>

<template>
  <main class="surface-maroon">
    <div class="wrap page-hero">
      <p class="eyebrow">{{ site?.portfolio.eyebrow }}</p>
      <h1 class="h-lg">{{ site?.portfolio.title }}</h1>
      <div class="filters">
        <NuxtLink to="/portafolio" :class="{ on: !selected }">Todo</NuxtLink>
        <NuxtLink
          v-for="service in services"
          :key="service.slug"
          :to="`/portafolio?servicio=${service.slug}`"
          :class="{ on: selected === service.slug }"
        >
          {{ service.title }}
        </NuxtLink>
      </div>
      <div class="embeds">
        <article v-for="piece in filtered" :key="piece.slug" class="embed-card">
          <NuxtLink :to="`/portafolio/${piece.slug}`" class="embed-label">
            <span class="embed-title">{{ piece.title }}</span>
            <span class="embed-artist">{{ piece.artist_name }}</span>
          </NuxtLink>
          <PlayerEmbedFacade v-if="piece.kind !== 'own_audio'" :piece="piece" />
        </article>
      </div>
    </div>
  </main>
</template>
