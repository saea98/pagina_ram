<script setup lang="ts">
import type { Site } from '~/types/public'

const props = withDefaults(defineProps<{ site: Site; variant?: 'float' | 'corner' }>(), {
  variant: 'float',
})
const route = useRoute()

const hasNumber = computed(() => Boolean(props.site.contact.whatsapp_e164))
const visible = computed(() =>
  props.variant === 'corner' ? true : props.site.features.whatsapp_float && hasNumber.value,
)
const href = computed(() => {
  const number = (props.site.contact.whatsapp_e164 || '').replace('+', '')
  if (!number) return ''
  const extra = typeof route.params.slug === 'string' ? ` (${route.params.slug})` : ''
  const text = encodeURIComponent(`${props.site.contact.whatsapp_default_msg}${extra}`.trim())
  return text ? `https://wa.me/${number}?text=${text}` : `https://wa.me/${number}`
})

const onFoot = ref(false)

function cornerButton() {
  return document.querySelector<HTMLElement>('.whatsapp-corner')
}

function syncFoot() {
  const button = cornerButton()
  const footer = document.querySelector('footer.site-foot')
  if (!button || !footer) return
  const buttonBox = button.getBoundingClientRect()
  const footerBox = footer.getBoundingClientRect()
  onFoot.value = footerBox.top < buttonBox.bottom && footerBox.bottom > buttonBox.top
}

function pinToScreen() {
  const button = cornerButton()
  const viewport = window.visualViewport
  if (!button || !viewport) return
  const margin = 16
  const width = button.offsetWidth || 52
  const height = button.offsetHeight || 52
  button.style.left = `${viewport.offsetLeft + viewport.width - width - margin}px`
  button.style.top = `${viewport.offsetTop + viewport.height - height - margin}px`
  button.style.right = 'auto'
  button.style.bottom = 'auto'
  syncFoot()
}

onMounted(() => {
  if (props.variant !== 'corner') return
  pinToScreen()
  window.addEventListener('scroll', pinToScreen, { passive: true })
  window.addEventListener('resize', pinToScreen)
  window.visualViewport?.addEventListener('resize', pinToScreen)
  window.visualViewport?.addEventListener('scroll', pinToScreen)
})
onUnmounted(() => {
  window.removeEventListener('scroll', pinToScreen)
  window.removeEventListener('resize', pinToScreen)
  window.visualViewport?.removeEventListener('resize', pinToScreen)
  window.visualViewport?.removeEventListener('scroll', pinToScreen)
})
</script>

<template>
  <a
    v-if="visible"
    :class="[variant === 'corner' ? 'whatsapp-corner' : 'whatsapp-float', { 'on-foot': onFoot }]"
    :href="hasNumber ? href : undefined"
    :target="hasNumber ? '_blank' : undefined"
    :rel="hasNumber ? 'noopener' : undefined"
    aria-label="WhatsApp"
  >
    <svg v-if="variant === 'corner'" viewBox="0 0 24 24" width="34" height="34" aria-hidden="true">
      <path fill="var(--cream)" d="M12 3a9 9 0 0 0-7.7 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3z" />
      <path
        class="wa-phone"
        fill="currentColor"
        d="M17 15.4c-.2.6-1.2 1.1-1.7 1.1-.4.1-.9.2-2.9-.6-2.4-1-4-3.4-4.1-3.6-.1-.2-1-1.3-1-2.5s.6-1.8.9-2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5.2.6.7 2 .8 2.1.1.2.1.3 0 .5-.1.2-.2.3-.3.5l-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.4.3.1.5.1.6-.1l.8-1c.2-.2.4-.2.6-.1.3.1 1.6.8 1.9.9.3.2.4.2.5.3.1.3 0 .8-.2 1.4z"
      />
    </svg>
    <svg v-else viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true">
      <path
        d="M12 3a9 9 0 0 0-7.7 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3zm5 12.4c-.2.6-1.2 1.1-1.7 1.1-.4.1-.9.2-2.9-.6-2.4-1-4-3.4-4.1-3.6-.1-.2-1-1.3-1-2.5s.6-1.8.9-2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5.2.6.7 2 .8 2.1.1.2.1.3 0 .5-.1.2-.2.3-.3.5l-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.4.3.1.5.1.6-.1l.8-1c.2-.2.4-.2.6-.1.3.1 1.6.8 1.9.9.3.2.4.2.5.3.1.3 0 .8-.2 1.4z"
      />
    </svg>
  </a>
</template>
