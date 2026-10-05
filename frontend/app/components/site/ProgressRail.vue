<template>
  <div class="rail" aria-hidden="true">
    <div class="rail-track" />
    <div ref="fill" class="rail-fill" />
    <div ref="dot" class="rail-dot">
      <img src="/brand/logo-cherries.png" alt="" />
    </div>
  </div>
</template>

<script setup lang="ts">
const fill = ref<HTMLElement | null>(null)
const dot = ref<HTMLElement | null>(null)

function update() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight
  const fraction = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0
  if (fill.value) fill.value.style.clipPath = `inset(0 0 ${(1 - fraction) * 100}% 0)`
  if (dot.value) {
    dot.value.style.top = `${24 + fraction * (window.innerHeight - 24 - 80 - 76)}px`
  }
}

onMounted(() => {
  update()
  window.addEventListener('scroll', update, { passive: true })
  window.addEventListener('resize', update)
})
onUnmounted(() => {
  window.removeEventListener('scroll', update)
  window.removeEventListener('resize', update)
})
</script>
