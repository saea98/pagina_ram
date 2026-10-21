<script setup lang="ts">
import type { Site } from '~/types/public'

definePageMeta({ layout: 'links' })

const { data: site } = await usePublic<Site>('/public/site', 'site')
const config = useRuntimeConfig()
const copied = ref(false)
let copiedTimer = 0

usePageMeta({
  title: `${site.value?.brand.name || 'Cherry Studios'} · Links`,
  description: 'WhatsApp, Instagram, TikTok y correo de Cherry Studios.',
  path: '/links',
})
defineOgImage('OgDefault', {
  title: site.value?.brand.name || 'Cherry Studios',
  description: site.value?.brand.tagline || '',
})

const email = computed(() => site.value?.contact.email || '')
const instagram = computed(() => site.value?.social.instagram || '')
const instagramHandle = computed(() => {
  const raw = instagram.value.replace(/\/$/, '').split('/').pop() || ''
  if (!raw) return ''
  return raw.startsWith('@') ? raw : `@${raw}`
})
const tiktok = computed(
  () => site.value?.social.tiktok || 'https://www.tiktok.com/@cherry.studios4',
)
const tiktokHandle = computed(() => {
  const raw = tiktok.value.replace(/\/$/, '').split('/').pop() || ''
  if (!raw) return ''
  return raw.startsWith('@') ? raw : `@${raw}`
})
const whatsappDigits = computed(() => (site.value?.contact.whatsapp_e164 || '').replace(/\D/g, ''))
const whatsappHref = computed(() =>
  whatsappDigits.value ? `https://wa.me/${whatsappDigits.value}` : '',
)
const whatsappNumber = computed(() => {
  const digits = whatsappDigits.value
  if (digits.length === 12 && digits.startsWith('52')) {
    return `+52 ${digits.slice(2, 4)} ${digits.slice(4, 8)} ${digits.slice(8)}`
  }
  if (digits.length === 10) {
    return `${digits.slice(0, 2)} ${digits.slice(2, 6)} ${digits.slice(6)}`
  }
  return (site.value?.contact.whatsapp_e164 || '').trim()
})
const siteHref = computed(() => config.public.siteUrl || 'https://cherrystudios.com.mx')
const siteHost = computed(() => {
  try {
    return new URL(siteHref.value).host
  } catch {
    return 'cherrystudios.com.mx'
  }
})

async function copyEmail() {
  if (!email.value) return
  try {
    await navigator.clipboard.writeText(email.value)
    copied.value = true
    window.clearTimeout(copiedTimer)
    copiedTimer = window.setTimeout(() => {
      copied.value = false
    }, 1600)
  } catch {
    copied.value = false
  }
}

onUnmounted(() => window.clearTimeout(copiedTimer))
</script>

<template>
  <div class="links-page">
    <header class="links-hero">
      <h1>
        <img class="mark" src="/brand/logo-links.png" :alt="site?.brand.name || 'Cherry Studios'" />
      </h1>
      <p class="tagline">Estudio de grabación y producción musical en la Ciudad de México.</p>
    </header>

    <div class="links">
      <a v-if="whatsappHref" class="pill" :href="whatsappHref" target="_blank" rel="noopener">
        <span class="ico" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M12 4.2a7.3 7.3 0 0 0-6.3 10.9L4.6 19.4l4.4-1.1A7.3 7.3 0 1 0 12 4.2z" />
            <path
              d="M9.35 11.55c.7-.7 1.15-.55 1.45.05.3.6.15 1.05-.15 1.4.55.35 1.15.7 1.7 1.25.35-.3.8-.45 1.4-.15.6.3.75.75.05 1.45"
            />
          </svg>
        </span>
        <span class="txt">
          <span class="label">Escríbenos por WhatsApp</span>
          <span class="sub">{{ whatsappNumber }}</span>
        </span>
      </a>

      <a v-if="instagram" class="pill" :href="instagram" target="_blank" rel="noopener">
        <span class="ico" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="3" width="18" height="18" rx="5" />
            <circle cx="12" cy="12" r="4.2" />
            <circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none" />
          </svg>
        </span>
        <span class="txt">
          <span class="label">Instagram</span>
          <span class="sub">{{ instagramHandle }}</span>
        </span>
      </a>

      <a v-if="tiktok" class="pill" :href="tiktok" target="_blank" rel="noopener">
        <span class="ico" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M16.3 3c.4 2.1 1.8 3.6 3.9 3.8v2.8c-1.4.1-2.7-.3-3.9-1.1v6.4c0 3.1-2.5 5.4-5.5 5.1-2.6-.3-4.6-2.5-4.6-5.2 0-2.9 2.4-5.2 5.3-5.1v2.9c-1.3-.2-2.4.8-2.4 2.1 0 1.2.9 2.2 2.1 2.3 1.3.1 2.5-1 2.5-2.4V3h2.6z"
            />
          </svg>
        </span>
        <span class="txt">
          <span class="label">TikTok</span>
          <span class="sub">{{ tiktokHandle }}</span>
        </span>
      </a>

      <a class="pill" :href="siteHref">
        <span class="ico" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="12" r="9" />
            <ellipse cx="12" cy="12" rx="4" ry="9" />
            <path d="M3 12h18M4.5 7.5h15M4.5 16.5h15" />
          </svg>
        </span>
        <span class="txt">
          <span class="label">Sitio web</span>
          <span class="sub">{{ siteHost }}</span>
        </span>
      </a>

      <div v-if="email" class="pill">
        <a class="pill-hit" :href="`mailto:${email}`">
          <span class="ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <rect x="3" y="5" width="18" height="14" rx="2.5" />
              <path d="M3.5 6.5l8.5 7 8.5-7" />
            </svg>
          </span>
          <span class="txt">
            <span class="label">Correo</span>
            <span class="sub">{{ email }}</span>
          </span>
        </a>
        <button
          class="copy-btn"
          type="button"
          :aria-label="copied ? 'Correo copiado' : 'Copiar correo'"
          :data-copied="copied ? 'true' : undefined"
          @click="copyEmail"
        >
          <svg v-if="copied" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12.5l4.2 4.2L19 7" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="8" y="8" width="12" height="12" rx="2" />
            <path d="M5 15.5V5.5A1.5 1.5 0 016.5 4h9" />
          </svg>
        </button>
      </div>
    </div>

    <footer>Ciudad de México · Cherry Studios</footer>
  </div>
</template>

<style scoped>
.links-page {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
}

.links-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
  margin-bottom: 34px;
}

.links-hero h1 {
  margin: 0;
}

.mark {
  width: min(78vw, 300px);
  height: auto;
  filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.45));
}

.tagline {
  margin: 0;
  font-size: 0.92rem;
  color: rgba(255, 244, 235, 0.72);
  max-width: 30ch;
  line-height: 1.5;
}

.links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pill,
.pill-hit {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: inherit;
  width: 100%;
  font: inherit;
  text-align: left;
}

.pill {
  padding: 15px 18px;
  border-radius: 16px;
  border: 1px solid rgba(255, 244, 235, 0.16);
  background: rgba(255, 244, 235, 0.06);
}

a.pill,
.pill-hit {
  transition:
    transform 0.15s ease,
    background 0.15s ease,
    border-color 0.15s ease;
}

a.pill:hover,
.pill:hover {
  transform: translateY(-1px);
  border-color: rgba(255, 190, 197, 0.4);
  background: rgba(255, 190, 197, 0.1);
}

a.pill:focus-visible,
.pill-hit:focus-visible,
.copy-btn:focus-visible {
  outline: 2px solid var(--blush);
  outline-offset: 3px;
}

.pill-hit {
  min-width: 0;
  flex: 1;
}

.ico {
  flex: none;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 244, 235, 0.1);
}

.ico svg {
  width: 22px;
  height: 22px;
}

.txt {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  flex: 1;
}

.label {
  font-weight: 600;
}

.sub {
  font-size: 0.82rem;
  color: rgba(255, 244, 235, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.copy-btn {
  flex: none;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(255, 244, 235, 0.2);
  background: transparent;
  color: var(--cream);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.copy-btn svg {
  width: 16px;
  height: 16px;
}

.copy-btn[data-copied='true'] {
  background: rgba(76, 122, 61, 0.35);
  border-color: rgba(76, 122, 61, 0.6);
}

footer {
  margin-top: 36px;
  text-align: center;
  font-size: 0.78rem;
  color: rgba(255, 244, 235, 0.45);
}
</style>
