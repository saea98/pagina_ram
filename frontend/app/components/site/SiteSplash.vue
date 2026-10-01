<script setup lang="ts">
const splashKey = 'cherry-intro-6'
const visible = ref(true)
const hide = ref(false)
const wrap = ref<HTMLElement | null>(null)
const timers: number[] = []

useHead({
  script: [
    {
      key: 'cherry-splash-gate',
      innerHTML: `(function(){try{if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches&&!sessionStorage.getItem('${splashKey}')){document.documentElement.classList.add('show-splash')}}catch(e){}})();`,
      tagPriority: 'critical',
    },
  ],
})

function finish() {
  visible.value = false
  document.documentElement.classList.remove('show-splash')
  document.documentElement.style.overflow = ''
}

onMounted(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const already = sessionStorage.getItem(splashKey) === '1'
  if (reduce || already || !document.documentElement.classList.contains('show-splash')) {
    finish()
    return
  }

  sessionStorage.setItem(splashKey, '1')
  document.documentElement.style.overflow = 'hidden'

  timers.push(
    window.setTimeout(() => {
      const navBrand = document.querySelector('header .brand')
      const node = wrap.value
      if (!navBrand || !node) {
        hide.value = true
        timers.push(window.setTimeout(finish, 500))
        return
      }
      const navRect = navBrand.getBoundingClientRect()
      const wrapRect = node.getBoundingClientRect()
      if (navRect.width === 0 || wrapRect.width === 0) {
        hide.value = true
        timers.push(window.setTimeout(finish, 500))
        return
      }
      const scale = navRect.height / wrapRect.height
      const deltaX = navRect.left + navRect.width / 2 - (wrapRect.left + wrapRect.width / 2)
      const deltaY = navRect.top + navRect.height / 2 - (wrapRect.top + wrapRect.height / 2)
      node.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(${scale})`
      hide.value = true
      timers.push(window.setTimeout(finish, 1100))
    }, 600),
  )
})

onUnmounted(() => {
  for (const id of timers) window.clearTimeout(id)
  document.documentElement.classList.remove('show-splash')
  document.documentElement.style.overflow = ''
})
</script>

<template>
  <div v-if="visible" class="splash" :class="{ 'splash-hide': hide }" aria-hidden="true">
    <div ref="wrap" class="splash-logo">
      <img src="/brand/logo-crudo.png" alt="" />
    </div>
  </div>
</template>
