<script setup lang="ts">
import { adminErrorMessage, adminFetch, useAdminSession } from '~/composables/useAdminApi'

definePageMeta({ layout: 'admin' })
const { user } = useAdminSession()
const toast = useState('admin-toast', () => '')
const error = ref('')
const tab = ref('marca')
interface Settings {
  brand: { name: string; tagline: string }
  hero: {
    quote: string
    title_html: string
    cta_primary_text: string
    cta_secondary_text: string
    image_media_id: string | null
  }
  studio: {
    eyebrow: string
    title: string
    body: string
    image_caption: string
    image_media_id: string | null
  }
  team: { eyebrow: string; title: string }
  services: { title: string; lede: string }
  portfolio: { title: string; note: string }
  contact: {
    email: string
    whatsapp_e164: string
    whatsapp_default_msg: string
    notify_emails: string[]
    consent_text: string
  }
  social: { instagram: string }
  seo: { default_title: string; title_template: string; default_description: string }
  legal: { privacy_html: string; privacy_updated_at: string }
  features: {
    ab_player: boolean
    testimonials: boolean
    turnstile: boolean
    whatsapp_float: boolean
  }
}
const settings = reactive(await adminFetch<Settings>('/admin/settings'))
const notify = ref(settings.contact.notify_emails.join('\n'))
const tabs = [
  ['marca', 'Marca'],
  ['portada', 'Portada'],
  ['estudio', 'Estudio'],
  ['secciones', 'Secciones'],
  ['contacto', 'Contacto y redes'],
  ['seo', 'SEO'],
  ['legal', 'Legal'],
  ['funciones', 'Funciones'],
] as const

async function save() {
  error.value = ''
  try {
    settings.contact.notify_emails = notify.value
      .split('\n')
      .map((item) => item.trim())
      .filter(Boolean)
    const saved = await adminFetch<Settings>('/admin/settings', { method: 'PUT', body: settings })
    Object.assign(settings, saved)
    toast.value = 'Ajustes guardados'
  } catch (reason) {
    error.value = adminErrorMessage(reason)
  }
}
</script>

<template>
  <div>
    <h1>Ajustes</h1>
    <div class="admin-tabs">
      <button
        v-for="[key, label] in tabs"
        v-show="key !== 'funciones' || user?.role === 'superadmin'"
        :key="key"
        type="button"
        :aria-selected="tab === key"
        @click="tab = key"
      >
        {{ label }}
      </button>
    </div>
    <form @submit.prevent="save">
      <section v-show="tab === 'marca'">
        <label class="admin-field">Nombre <input v-model="settings.brand.name" /></label>
        <label class="admin-field">Lema <input v-model="settings.brand.tagline" /></label>
      </section>
      <section v-show="tab === 'portada'">
        <label class="admin-field">Cita <textarea v-model="settings.hero.quote" rows="3" /></label>
        <label class="admin-field"
          >Título <textarea v-model="settings.hero.title_html" rows="3" />
        </label>
        <label class="admin-field"
          >Botón principal <input v-model="settings.hero.cta_primary_text"
        /></label>
        <label class="admin-field"
          >Botón secundario <input v-model="settings.hero.cta_secondary_text"
        /></label>
        <AdminMediaPicker
          v-model="settings.hero.image_media_id"
          accept="image"
          :aspect="1.5"
          label="Imagen del hero"
        />
      </section>
      <section v-show="tab === 'estudio'">
        <label class="admin-field">Etiqueta <input v-model="settings.studio.eyebrow" /></label>
        <label class="admin-field">Título <input v-model="settings.studio.title" /></label>
        <label class="admin-field"
          >Texto <textarea v-model="settings.studio.body" rows="6" />
        </label>
        <label class="admin-field"
          >Pie de foto <input v-model="settings.studio.image_caption"
        /></label>
        <AdminMediaPicker
          v-model="settings.studio.image_media_id"
          accept="image"
          label="Foto del estudio"
        />
      </section>
      <section v-show="tab === 'secciones'">
        <label class="admin-field"
          >Equipo, etiqueta <input v-model="settings.team.eyebrow"
        /></label>
        <label class="admin-field">Equipo, título <input v-model="settings.team.title" /></label>
        <label class="admin-field"
          >Servicios, título <input v-model="settings.services.title"
        /></label>
        <label class="admin-field"
          >Servicios, intro <textarea v-model="settings.services.lede" rows="3" />
        </label>
        <label class="admin-field"
          >Portafolio, título <input v-model="settings.portfolio.title"
        /></label>
        <label class="admin-field"
          >Portafolio, nota <textarea v-model="settings.portfolio.note" rows="3" />
        </label>
      </section>
      <section v-show="tab === 'contacto'">
        <label class="admin-field"
          >Correo público <input v-model="settings.contact.email" type="email"
        /></label>
        <label class="admin-field"
          >WhatsApp <input v-model="settings.contact.whatsapp_e164" type="tel"
        /></label>
        <label class="admin-field"
          >Mensaje de WhatsApp <textarea v-model="settings.contact.whatsapp_default_msg" rows="3" />
        </label>
        <label class="admin-field"
          >Correos que reciben leads <textarea v-model="notify" rows="3" />
        </label>
        <label class="admin-field"
          >Texto de consentimiento <textarea v-model="settings.contact.consent_text" rows="3" />
        </label>
        <label class="admin-field">Instagram <input v-model="settings.social.instagram" /></label>
      </section>
      <section v-show="tab === 'seo'">
        <label class="admin-field"
          >Título por defecto <input v-model="settings.seo.default_title"
        /></label>
        <label class="admin-field">Plantilla <input v-model="settings.seo.title_template" /></label>
        <label class="admin-field"
          >Descripción <textarea v-model="settings.seo.default_description" rows="3" />
        </label>
      </section>
      <section v-show="tab === 'legal'">
        <AdminRichText v-model="settings.legal.privacy_html" />
        <label class="admin-field"
          >Fecha de actualización <input v-model="settings.legal.privacy_updated_at"
        /></label>
      </section>
      <section v-show="tab === 'funciones' && user?.role === 'superadmin'">
        <label class="admin-switch"
          >Comparador A/B <input v-model="settings.features.ab_player" type="checkbox"
        /></label>
        <label class="admin-switch"
          >Testimonios <input v-model="settings.features.testimonials" type="checkbox"
        /></label>
        <label class="admin-switch"
          >Turnstile <input v-model="settings.features.turnstile" type="checkbox"
        /></label>
        <label class="admin-switch"
          >WhatsApp flotante <input v-model="settings.features.whatsapp_float" type="checkbox"
        /></label>
      </section>
      <p v-if="error" class="admin-error">{{ error }}</p>
      <button class="admin-save" type="submit">Guardar</button>
    </form>
  </div>
</template>
