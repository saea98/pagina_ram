<script setup lang="ts">
import * as v from 'valibot'
import type { ServiceCard, Site } from '~/types/public'
import { apiBase } from '~/composables/useApi'
import { useUtm } from '~/composables/useUtm'
import { leadSchema } from '~/utils/lead'

const props = defineProps<{ site: Site; services: ServiceCard[] }>()
const route = useRoute()
const name = ref('')
const contact = ref('')
const message = ref('')
const serviceSlug = ref(typeof route.query.servicio === 'string' ? route.query.servicio : '')
const consent = ref(false)
const website = ref('')
const status = ref<'idle' | 'sending' | 'sent' | 'error'>('idle')
const errors = ref<Record<string, string>>({})

const consentCopy = computed(() => {
  const text = props.site.contact.consent_text
  const marker = 'Aviso de Privacidad'
  const index = text.toLowerCase().indexOf(marker.toLowerCase())
  if (index === -1) return { before: text, linked: false }
  return { before: text.slice(0, index), linked: true }
})

const instagram = computed(() => props.site.social.instagram || '')
const handle = computed(() => {
  const raw = instagram.value.replace(/\/$/, '').split('/').pop() || ''
  return raw.startsWith('@') ? raw : raw ? `@${raw}` : ''
})

watch(
  () => props.services,
  (list) => {
    if (!serviceSlug.value && list[0]) serviceSlug.value = list[0].slug
  },
  { immediate: true },
)

function splitContact() {
  const value = contact.value.trim()
  if (value.includes('@')) return { email: value, phone: '' }
  return { email: '', phone: value }
}

function validate() {
  const { email, phone } = splitContact()
  const parsed = v.safeParse(leadSchema, {
    name: name.value,
    email,
    phone,
    message: message.value,
    consent: consent.value,
  })
  if (parsed.success) {
    errors.value = {}
    return true
  }
  const next: Record<string, string> = {}
  for (const issue of parsed.issues) {
    const key = String(issue.path?.[0]?.key ?? 'form')
    if (!next[key]) next[key] = issue.message
  }
  errors.value = next
  return false
}

async function submit() {
  if (website.value) return
  if (!validate()) return
  status.value = 'sending'
  const utm = useUtm()
  const { email, phone } = splitContact()
  try {
    await $fetch(`${apiBase()}/public/leads`, {
      method: 'POST',
      body: {
        name: name.value,
        email: email || null,
        phone: phone || null,
        service_slug: serviceSlug.value || null,
        message: message.value,
        demo_url: null,
        demo_upload_token: null,
        tentative_date: null,
        consent: true,
        source_page: route.path,
        referrer: utm.referrer,
        utm: {
          source: utm.source,
          medium: utm.medium,
          campaign: utm.campaign,
          content: utm.content,
          term: utm.term,
        },
        website: '',
      },
    })
    status.value = 'sent'
  } catch {
    status.value = 'error'
  }
}
</script>

<template>
  <div class="contact-grid reveal">
    <form class="reach" @submit.prevent="submit">
      <div class="field">
        <label for="lead-name">Nombre</label>
        <input
          id="lead-name"
          v-model="name"
          name="name"
          autocomplete="name"
          placeholder="¿Cómo te llamas?"
          required
        />
        <p v-if="errors.name" class="field-error">{{ errors.name }}</p>
      </div>
      <div class="field">
        <label for="lead-email">Correo o teléfono</label>
        <input
          id="lead-email"
          v-model="contact"
          name="email"
          type="text"
          autocomplete="email"
          placeholder="Para responderte"
        />
        <p v-if="errors.email || errors.phone" class="field-error">
          {{ errors.email || errors.phone }}
        </p>
      </div>
      <div class="field">
        <label for="lead-service">Servicio que buscas</label>
        <select id="lead-service" v-model="serviceSlug">
          <option v-for="service in services" :key="service.slug" :value="service.slug">
            {{ service.title }}
          </option>
          <option value="">Aún no estoy seguro</option>
        </select>
      </div>
      <div class="field">
        <label for="lead-message">Cuéntanos de tu proyecto / maqueta</label>
        <textarea
          id="lead-message"
          v-model="message"
          name="message"
          placeholder="Cuéntanos qué tienes en mente…"
          required
        />
        <p v-if="errors.message" class="field-error">{{ errors.message }}</p>
      </div>
      <div class="honeypot" aria-hidden="true">
        <label for="lead-website">Sitio web</label>
        <input
          id="lead-website"
          v-model="website"
          name="website"
          tabindex="-1"
          autocomplete="off"
        />
      </div>
      <button
        class="btn btn-dark submit"
        type="button"
        :disabled="status === 'sending'"
        @click="submit"
      >
        {{ status === 'sending' ? 'Enviando…' : 'Enviar mensaje →' }}
      </button>
      <p v-if="status === 'sent'" id="lead-thanks" class="form-status" role="status">
        ¡Gracias! Recibimos tu mensaje y te contactaremos pronto.
      </p>
      <p v-if="status === 'error'" class="form-status field-error" role="alert">
        No pudimos enviar tu mensaje. Escríbenos a {{ site.contact.email }}.
      </p>
    </form>

    <aside class="direct-card">
      <a class="direct-row" :href="`mailto:${site.contact.email}`">
        <span class="ic" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="5" width="18" height="14" rx="2" />
            <path d="m4 7 8 6 8-6" />
          </svg>
        </span>
        <span>
          <span class="lbl">Correo</span><br />
          <span class="val">{{ site.contact.email }}</span>
        </span>
      </a>
      <a v-if="instagram" class="direct-row" :href="instagram" target="_blank" rel="noopener">
        <span class="ic" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="3" width="18" height="18" rx="5" />
            <circle cx="12" cy="12" r="4" />
            <circle cx="17.2" cy="6.8" r="1" />
          </svg>
        </span>
        <span>
          <span class="lbl">Instagram</span><br />
          <span class="val">{{ handle }}</span>
        </span>
      </a>
      <label class="consent">
        <input v-model="consent" type="checkbox" name="consent" />
        <span
          >{{ consentCopy.before
          }}<NuxtLink v-if="consentCopy.linked" to="/aviso-de-privacidad"
            >Aviso de privacidad</NuxtLink
          ><template v-if="consentCopy.linked">.</template></span
        >
      </label>
      <p v-if="errors.consent" class="field-error">{{ errors.consent }}</p>
    </aside>
  </div>
</template>
