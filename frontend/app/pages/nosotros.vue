<script setup lang="ts">
import type { Home } from '~/types/public'

const { data, error } = await usePublic<Home>('/public/home', 'home')
if (error.value || !data.value) {
  throw createError({ statusCode: 500, statusMessage: 'No pudimos cargar Nosotros.' })
}
const home = data.value
usePageMeta({
  title: 'Nosotros',
  description: home.site.studio.body,
  path: '/nosotros',
})
</script>

<template>
  <main class="surface-paper page-sheet">
    <SiteHomeStudio :site="home.site" />
    <SiteHomeTeam :site="home.site" :team="home.team" />
  </main>
</template>
