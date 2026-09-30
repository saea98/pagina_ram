<script setup lang="ts">
import type { Site } from '~/types/public'

const props = defineProps<{ site: Site }>()
const route = useRoute()

const visible = computed(
  () => props.site.features.whatsapp_float && Boolean(props.site.contact.whatsapp_e164),
)
const href = computed(() => {
  const number = props.site.contact.whatsapp_e164.replace('+', '')
  const extra = typeof route.params.slug === 'string' ? ` (${route.params.slug})` : ''
  const text = encodeURIComponent(`${props.site.contact.whatsapp_default_msg}${extra}`.trim())
  return text ? `https://wa.me/${number}?text=${text}` : `https://wa.me/${number}`
})
</script>

<template>
  <a
    v-if="visible"
    class="whatsapp-float"
    :href="href"
    target="_blank"
    rel="noopener"
    aria-label="WhatsApp"
  >
    <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true">
      <path
        d="M12 3a9 9 0 0 0-7.7 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3zm5 12.4c-.2.6-1.2 1.1-1.7 1.1-.4.1-.9.2-2.9-.6-2.4-1-4-3.4-4.1-3.6-.1-.2-1-1.3-1-2.5s.6-1.8.9-2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5.2.6.7 2 .8 2.1.1.2.1.3 0 .5-.1.2-.2.3-.3.5l-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.4.3.1.5.1.6-.1l.8-1c.2-.2.4-.2.6-.1.3.1 1.6.8 1.9.9.3.2.4.2.5.3.1.3 0 .8-.2 1.4z"
      />
    </svg>
  </a>
</template>
