<script setup lang="ts">
import type { Site } from '~/types/public'
import { siteImage } from '~/utils/media'

const props = defineProps<{ site?: Site | null }>()
const visible = ref(false)
const logo = computed(() =>
  props.site ? siteImage(props.site, props.site.brand.logo_alt_media_id) : null,
)

onMounted(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce || sessionStorage.getItem('cherry-splash')) return
  sessionStorage.setItem('cherry-splash', '1')
  visible.value = true
  window.setTimeout(() => {
    visible.value = false
  }, 1400)
})
</script>

<template>
  <div v-if="visible" class="splash" aria-hidden="true">
    <img v-if="logo" :src="logo.webp['960'] || Object.values(logo.webp)[0]" alt="" />
  </div>
</template>
