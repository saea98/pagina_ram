<script setup lang="ts">
const visible = ref(false)

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
    <img src="/brand/logo-color.png" alt="" />
  </div>
</template>
