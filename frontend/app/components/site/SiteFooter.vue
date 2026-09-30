<script setup lang="ts">
import type { Site } from '~/types/public'
import { siteImage } from '~/utils/media'

const props = defineProps<{ site?: Site | null }>()
const logo = computed(() =>
  props.site ? siteImage(props.site, props.site.brand.logo_media_id) : null,
)
const year = new Date().getFullYear()
const instagram = computed(() => props.site?.social.instagram || '')
const handle = computed(() => instagram.value.replace(/\/$/, '').split('/').pop() || '')
</script>

<template>
  <footer class="site-foot">
    <div class="brand-mini">
      <img
        v-if="logo"
        :src="logo.webp['480'] || Object.values(logo.webp)[0]"
        :alt="site?.brand.name || 'Cherry Studios'"
      />
    </div>
    <div>Ciudad de México · © {{ year }} {{ site?.brand.name || 'Cherry Studios' }}</div>
    <div style="display: flex; gap: 18px">
      <a v-if="site?.contact.email" :href="`mailto:${site.contact.email}`">{{
        site.contact.email
      }}</a>
      <a v-if="instagram" :href="instagram" target="_blank" rel="noopener">@{{ handle }}</a>
    </div>
  </footer>
</template>
