<script setup lang="ts">
import type { Home } from '~/types/public'
import { homeJsonLd } from '~/utils/jsonld'

const { data, error } = await usePublic<Home>('/public/home', 'home')
if (error.value || !data.value) {
  throw createError({ statusCode: 500, statusMessage: 'No pudimos cargar la portada.' })
}
const home = data.value
const config = useRuntimeConfig()
usePageMeta({
  title: home.site.seo.default_title,
  description: home.site.seo.default_description,
  path: '/',
})
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(homeJsonLd(home, config.public.siteUrl)),
    },
  ],
})
defineOgImage('OgDefault', {
  title: home.site.brand.name,
  description: home.site.seo.default_description,
})
</script>

<template>
  <main>
    <SiteHomeHero :site="home.site" />
    <SiteHomeStudio :site="home.site" />
    <SiteHomeTeam :site="home.site" :team="home.team" />
    <SiteHomeServices :site="home.site" :services="home.services" />
    <SiteHomePortfolio :site="home.site" :portfolio="home.portfolio" />
    <SiteHomeCompare :items="home.ab_comparisons" />
    <SiteHomeTestimonials :items="home.testimonials" />
    <SiteHomeContact :site="home.site" :services="home.services" />
  </main>
</template>
