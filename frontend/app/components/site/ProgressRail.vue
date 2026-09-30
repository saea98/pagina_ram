<template>
  <div class="rail" aria-hidden="true">
    <div class="rail-track" />
    <div ref="fill" class="rail-fill" />
    <div ref="dot" class="rail-dot">
      <svg viewBox="0 0 32 32" width="100%" height="100%">
        <path
          d="M16 3c-2.6 2.6-4.4 5.4-5.4 8.6"
          fill="none"
          stroke="var(--maroon)"
          stroke-width="2.1"
          stroke-linecap="round"
        />
        <path
          d="M16 3c2.6 2.2 4.6 4.6 5.8 7.4"
          fill="none"
          stroke="var(--maroon)"
          stroke-width="2.1"
          stroke-linecap="round"
        />
        <circle cx="9.5" cy="20.5" r="7.6" fill="var(--cherry-2)" />
        <circle cx="22" cy="19" r="7.6" fill="var(--cherry-2)" />
        <circle cx="7" cy="18" r="1.7" fill="rgba(255,244,235,0.55)" />
        <circle cx="19.5" cy="16.5" r="1.7" fill="rgba(255,244,235,0.55)" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
const fill = ref<HTMLElement | null>(null)
const dot = ref<HTMLElement | null>(null)

function update() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight
  const fraction = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0
  if (fill.value) fill.value.style.transform = `scaleY(${fraction})`
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
