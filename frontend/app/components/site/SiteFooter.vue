<script setup lang="ts">
import type { Site } from '~/types/public'

const props = defineProps<{ site?: Site | null }>()
const year = new Date().getFullYear()
const instagram = computed(() => props.site?.social.instagram || '')
const handle = computed(() => instagram.value.replace(/\/$/, '').split('/').pop() || '')
</script>

<template>
  <footer class="site-foot">
    <div class="brand-mini">
      <img src="/brand/logo-crudo.png" :alt="site?.brand.name || 'Cherry Studios'" />
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
