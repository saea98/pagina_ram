<script setup lang="ts">
import type { BioLink, Site } from '~/types/public'

definePageMeta({ layout: 'links' })
const { data: site } = await usePublic<Site>('/public/site', 'site')
const { data } = await usePublic<BioLink[]>('/public/links', 'links')
usePageMeta({
  title: `${site.value?.brand.name || 'Cherry Studios'} · Links`,
  description: site.value?.seo.default_description || '',
  path: '/links',
})
defineOgImage('OgDefault', {
  title: site.value?.brand.name || 'Cherry Studios',
  description: site.value?.brand.tagline || '',
})
</script>

<template>
  <div>
    <h1 class="h-lg">{{ site?.brand.name }}</h1>
    <div class="link-list">
      <a
        v-for="link in data"
        :key="link.id"
        :class="{ highlight: link.highlight }"
        :href="link.is_internal ? link.url : `/api/v1/public/links/${link.id}/go`"
      >
        {{ link.label }}
      </a>
    </div>
  </div>
</template>
