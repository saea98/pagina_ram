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
    <p class="admin-lede">Textos, fotos y datos de contacto del sitio.</p>
    <div class="admin-tabs" role="tablist">
      <button
        v-for="[key, label] in tabs"
        v-show="key !== 'funciones' || user?.role === 'superadmin'"
        :key="key"
        type="button"
        role="tab"
        :aria-selected="tab === key"
        @click="tab = key"
      >
        {{ label }}
      </button>
    </div>
    <form class="admin-panel" @submit.prevent="save">
      <section v-show="tab === 'marca'">
        <label class="admin-field">
          <span>Nombre</span>
          <input v-model="settings.brand.name" />
        </label>
        <label class="admin-field">
          <span>Lema</span>
          <input v-model="settings.brand.tagline" />
        </label>
      </section>
      <section v-show="tab === 'portada'">
        <label class="admin-field">
          <span>Cita</span>
          <textarea v-model="settings.hero.quote" rows="3" />
        </label>
        <label class="admin-field">
          <span>Título</span>
          <textarea v-model="settings.hero.title_html" rows="3" />
        </label>
        <p class="admin-hint">Para cursiva, rodea la palabra con &lt;em&gt; y &lt;/em&gt;.</p>
        <label class="admin-field">
          <span>Botón principal</span>
          <input v-model="settings.hero.cta_primary_text" />
        </label>
        <label class="admin-field">
          <span>Botón secundario</span>
          <input v-model="settings.hero.cta_secondary_text" />
        </label>
        <AdminMediaPicker
          v-model="settings.hero.image_media_id"
          accept="image"
          :aspect="1.5"
          label="Imagen del hero"
        />
      </section>
      <section v-show="tab === 'estudio'">
        <label class="admin-field">
          <span>Etiqueta</span>
          <input v-model="settings.studio.eyebrow" />
        </label>
        <label class="admin-field">
          <span>Título</span>
          <input v-model="settings.studio.title" />
        </label>
        <label class="admin-field">
          <span>Texto</span>
          <textarea v-model="settings.studio.body" rows="6" />
        </label>
        <label class="admin-field">
          <span>Pie de foto</span>
          <input v-model="settings.studio.image_caption" />
        </label>
        <AdminMediaPicker
          v-model="settings.studio.image_media_id"
          accept="image"
          label="Foto del estudio"
        />
      </section>
      <section v-show="tab === 'secciones'">
        <label class="admin-field">
          <span>Equipo, etiqueta</span>
          <input v-model="settings.team.eyebrow" />
        </label>
        <label class="admin-field">
          <span>Equipo, título</span>
          <input v-model="settings.team.title" />
        </label>
        <label class="admin-field">
          <span>Servicios, título</span>
          <input v-model="settings.services.title" />
        </label>
        <label class="admin-field">
          <span>Servicios, intro</span>
          <textarea v-model="settings.services.lede" rows="3" />
        </label>
        <label class="admin-field">
          <span>Portafolio, título</span>
          <input v-model="settings.portfolio.title" />
        </label>
        <label class="admin-field">
          <span>Portafolio, nota</span>
          <textarea v-model="settings.portfolio.note" rows="3" />
        </label>
      </section>
      <section v-show="tab === 'contacto'">
        <label class="admin-field">
          <span>Correo público</span>
          <input v-model="settings.contact.email" type="email" />
        </label>
        <label class="admin-field">
          <span>WhatsApp</span>
          <input v-model="settings.contact.whatsapp_e164" type="tel" />
        </label>
        <label class="admin-field">
          <span>Mensaje de WhatsApp</span>
          <textarea v-model="settings.contact.whatsapp_default_msg" rows="3" />
        </label>
        <label class="admin-field">
          <span>Correos que reciben leads</span>
          <textarea v-model="notify" rows="3" />
        </label>
        <p class="admin-hint">Un correo por línea.</p>
        <label class="admin-field">
          <span>Texto de consentimiento</span>
          <textarea v-model="settings.contact.consent_text" rows="3" />
        </label>
        <label class="admin-field">
          <span>Instagram</span>
          <input v-model="settings.social.instagram" />
        </label>
      </section>
      <section v-show="tab === 'seo'">
        <label class="admin-field">
          <span>Título por defecto</span>
          <input v-model="settings.seo.default_title" />
        </label>
        <label class="admin-field">
          <span>Plantilla</span>
          <input v-model="settings.seo.title_template" />
        </label>
        <label class="admin-field">
          <span>Descripción</span>
          <textarea v-model="settings.seo.default_description" rows="3" />
        </label>
      </section>
      <section v-show="tab === 'legal'">
        <AdminRichText v-model="settings.legal.privacy_html" />
        <label class="admin-field">
          <span>Fecha de actualización</span>
          <input v-model="settings.legal.privacy_updated_at" />
        </label>
      </section>
      <section v-show="tab === 'funciones' && user?.role === 'superadmin'">
        <label class="admin-switch">
          Comparador A/B
          <input v-model="settings.features.ab_player" type="checkbox" />
        </label>
        <label class="admin-switch">
          Testimonios
          <input v-model="settings.features.testimonials" type="checkbox" />
        </label>
        <label class="admin-switch">
          Turnstile
          <input v-model="settings.features.turnstile" type="checkbox" />
        </label>
        <label class="admin-switch">
          WhatsApp flotante
          <input v-model="settings.features.whatsapp_float" type="checkbox" />
        </label>
      </section>
      <p v-if="error" class="admin-error">{{ error }}</p>
      <button class="admin-save" type="submit">Guardar</button>
    </form>
  </div>
</template>
