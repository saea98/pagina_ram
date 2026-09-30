<script setup lang="ts">
import type { Privacy } from '~/types/public'

const { data, error } = await usePublic<Privacy>('/public/legal/privacy', 'privacy')
if (error.value || !data.value) {
  throw createError({ statusCode: 404, statusMessage: 'El aviso no está disponible.' })
}
usePageMeta({
  title: 'Aviso de privacidad',
  description: 'Aviso de privacidad de Cherry Studios.',
  path: '/aviso-de-privacidad',
})
</script>

<template>
  <main class="surface-paper">
    <article v-if="data" class="wrap page-hero prose" v-html="data.html" />
  </main>
</template>
