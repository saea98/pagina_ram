<script setup lang="ts">
import * as v from 'valibot'
import type { ServiceCard, Site } from '~/types/public'
import { apiBase } from '~/composables/useApi'
import { useUtm } from '~/composables/useUtm'
import { leadSchema } from '~/utils/lead'

defineProps<{ site: Site; services: ServiceCard[] }>()
const route = useRoute()
const name = ref('')
const email = ref('')
const phone = ref('')
const message = ref('')
const demoUrl = ref('')
const tentative = ref('')
const serviceSlug = ref(typeof route.query.servicio === 'string' ? route.query.servicio : '')
const consent = ref(false)
const website = ref('')
const status = ref<'idle' | 'sending' | 'sent' | 'error'>('idle')
const errors = ref<Record<string, string>>({})
const uploadProgress = ref(0)
const uploadToken = ref('')

function validate() {
  const parsed = v.safeParse(leadSchema, {
    name: name.value,
    email: email.value,
    phone: phone.value,
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

function onFile(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadProgress.value = 0
  const body = new FormData()
  body.append('file', file)
  const xhr = new XMLHttpRequest()
  xhr.open('POST', `${apiBase()}/public/leads/uploads`)
  xhr.upload.onprogress = (progress) => {
    if (progress.lengthComputable) uploadProgress.value = progress.loaded / progress.total
  }
  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      uploadToken.value = JSON.parse(xhr.responseText).upload_token as string
    } else {
      status.value = 'error'
    }
  }
  xhr.send(body)
}

async function submit() {
  if (website.value) return
  if (!validate()) return
  status.value = 'sending'
  const utm = useUtm()
  try {
    await $fetch(`${apiBase()}/public/leads`, {
      method: 'POST',
      body: {
        name: name.value,
        email: email.value || null,
        phone: phone.value || null,
        service_slug: serviceSlug.value || null,
        message: message.value,
        demo_url: demoUrl.value || null,
        demo_upload_token: uploadToken.value || null,
        tentative_date: tentative.value || null,
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
  <form class="reach" @submit.prevent="submit">
    <div class="field">
      <label for="lead-name">Nombre</label>
      <input id="lead-name" v-model="name" name="name" autocomplete="name" required />
      <p v-if="errors.name" class="field-error">{{ errors.name }}</p>
    </div>
    <div class="field">
      <label for="lead-email">Correo</label>
      <input id="lead-email" v-model="email" name="email" type="email" autocomplete="email" />
      <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
    </div>
    <div class="field">
      <label for="lead-phone">Teléfono</label>
      <input
        id="lead-phone"
        v-model="phone"
        name="phone"
        type="tel"
        autocomplete="tel"
        placeholder="+52"
      />
      <p v-if="errors.phone" class="field-error">{{ errors.phone }}</p>
    </div>
    <div class="field">
      <label for="lead-service">Servicio</label>
      <select id="lead-service" v-model="serviceSlug">
        <option value="">Aún no estoy seguro</option>
        <option v-for="service in services" :key="service.slug" :value="service.slug">
          {{ service.title }}
        </option>
      </select>
    </div>
    <div class="field">
      <label for="lead-message">Mensaje</label>
      <textarea id="lead-message" v-model="message" name="message" required />
      <p v-if="errors.message" class="field-error">{{ errors.message }}</p>
    </div>
    <div class="field">
      <label for="lead-demo">Link de tu demo</label>
      <input id="lead-demo" v-model="demoUrl" name="demo" type="url" />
    </div>
    <div class="field">
      <label for="lead-date">Fecha tentativa</label>
      <input id="lead-date" v-model="tentative" name="fecha" type="date" />
    </div>
    <div class="field">
      <label for="lead-file">O sube un audio</label>
      <input id="lead-file" type="file" accept="audio/*" @change="onFile" />
      <div v-if="uploadProgress" class="progress">
        <span :style="{ width: `${uploadProgress * 100}%` }" />
      </div>
    </div>
    <label class="consent">
      <input v-model="consent" type="checkbox" name="consent" />
      <span>
        {{ site.contact.consent_text }}
        <NuxtLink to="/aviso-de-privacidad">Aviso de privacidad</NuxtLink>
      </span>
    </label>
    <p v-if="errors.consent" class="field-error">{{ errors.consent }}</p>
    <div class="honeypot" aria-hidden="true">
      <label for="lead-website">Sitio web</label>
      <input id="lead-website" v-model="website" name="website" tabindex="-1" autocomplete="off" />
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
</template>
