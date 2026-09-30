<script setup lang="ts">
import type { Site } from '~/types/public'

const { data: site } = await usePublic<Site>('/public/site', 'site')
</script>

<template>
  <div class="surface-maroon" style="min-height: 100svh">
    <div class="wrap page-hero" style="text-align: center">
      <p class="eyebrow">{{ site?.brand.name }}</p>
      <slot />
    </div>
  </div>
</template>
