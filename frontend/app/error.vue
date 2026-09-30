<script setup lang="ts">
import type { NuxtError } from '#app'

defineProps<{ error: NuxtError }>()
</script>

<template>
  <main class="surface-cream" style="min-height: 100svh">
    <div class="wrap page-hero">
      <p class="eyebrow">{{ error.statusCode }}</p>
      <h1 class="h-lg">No encontramos esa página.</h1>
      <NuxtLink class="btn btn-dark" to="/" style="margin-top: 24px">Volver al inicio</NuxtLink>
    </div>
  </main>
</template>
