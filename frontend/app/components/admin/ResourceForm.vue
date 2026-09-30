<script setup lang="ts">
import type { FieldDef, AdminSection } from '~/admin/fields'
import { slugify } from '~/admin/fields'
import { adminErrorFields, adminErrorMessage, adminFetch } from '~/composables/useAdminApi'
import { useResource, type ResourceRow } from '~/composables/useResource'

const props = defineProps<{ section: AdminSection; id: string }>()
const toast = defineModel<string>('toast', { default: '' })
const api = useResource<ResourceRow>(props.section.api)
const isNew = computed(() => props.id === 'nuevo')
const form = reactive<Record<string, unknown>>({})
const socialText = ref('')
const fieldErrors = ref<Record<string, string>>({})
const error = ref('')
const dirty = ref(false)
const slugTouched = ref(false)
const options = reactive<Record<string, { value: string; label: string }[]>>({})

function blank(field: FieldDef): unknown {
  if (field.type === 'switch') return false
  if (field.type === 'multiselect') return []
  if (field.type === 'json-list') return {}
  return ''
}

function textValue(key: string) {
  const value = form[key]
  return value == null ? '' : String(value)
}

function setText(key: string, value: string) {
  form[key] = value
}

function visible(field: FieldDef) {
  return field.showIf ? field.showIf(form) : true
}

if (isNew.value) {
  for (const field of props.section.fields) form[field.key] = blank(field)
} else {
  const row = await api.get(props.id)
  Object.assign(form, row)
  socialText.value = Object.entries((row.socials as Record<string, string> | undefined) ?? {})
    .map(([key, value]) => `${key} ${value}`)
    .join('\n')
}

for (const field of props.section.fields) {
  if (!field.source) continue
  const name =
    field.source === 'services' ? 'services' : field.source === 'team' ? 'team' : 'portfolio'
  const page = await adminFetch<{ items: ResourceRow[] }>(`/admin/${name}`, {
    query: { page_size: 100 },
  })
  options[field.key] = page.items.map((item) => ({
    value: item.id,
    label: String(item.title ?? item.full_name ?? item.question ?? item.label ?? item.id),
  }))
}

watch(
  form,
  () => {
    dirty.value = true
  },
  { deep: true },
)

watch(
  () => form.title ?? form.full_name,
  (value) => {
    const slug = props.section.fields.find((field) => field.type === 'slug')
    if (!slug || slugTouched.value || typeof value !== 'string') return
    form[slug.key] = slugify(value)
  },
)

onBeforeRouteLeave(() => {
  if (dirty.value && !confirm('Tienes cambios sin guardar. ¿Salir de todos modos?')) return false
})

async function inspectUrl() {
  const url = String(form.external_url ?? '')
  if (!url.startsWith('http')) return
  const found = await adminFetch<{
    kind: string | null
    external_id: string | null
    youtube_start_s: number | null
    title: string | null
    artist_name: string | null
  }>('/admin/portfolio/inspect', { method: 'POST', body: { url } })
  if (found.kind) form.kind = found.kind
  if (found.external_id) form.external_id = found.external_id
  if (found.youtube_start_s != null) form.youtube_start_s = found.youtube_start_s
  if (found.title && !form.title) form.title = found.title
  if (found.artist_name && !form.artist_name) form.artist_name = found.artist_name
  toast.value = 'Revisamos el enlace y completamos lo que pudimos.'
}

function payload(): Record<string, unknown> {
  const body: Record<string, unknown> = {}
  for (const field of props.section.fields) {
    if (!visible(field)) continue
    let value = form[field.key]
    if (field.type === 'json-list') {
      const socials: Record<string, string> = {}
      for (const line of socialText.value.split('\n')) {
        const [key, ...rest] = line.trim().split(/\s+/)
        if (key && rest.length) socials[key] = rest.join(' ')
      }
      value = socials
    }
    if (value === '') value = null
    if ((field.type === 'number' || field.type === 'money') && value != null && value !== '') {
      value = Number(value)
    }
    body[field.key] = value
  }
  return body
}

async function save() {
  error.value = ''
  fieldErrors.value = {}
  try {
    const saved = isNew.value ? await api.create(payload()) : await api.update(props.id, payload())
    dirty.value = false
    toast.value = 'Guardado'
    if (isNew.value) await navigateTo(`/admin/${currentSection()}/${saved.id}`)
  } catch (reason) {
    error.value = adminErrorMessage(reason)
    fieldErrors.value = adminErrorFields(reason)
  }
}

function currentSection() {
  const route = useRoute()
  return String(route.params.section)
}

async function preview() {
  const token = await adminFetch<{ token: string }>('/admin/preview-token', { method: 'POST' })
  const path = props.section.preview?.(form)
  if (!path) return
  window.open(`${path}?preview=${encodeURIComponent(token.token)}`, '_blank', 'noopener')
}
</script>

<template>
  <h1>{{ isNew ? `Nuevo ${section.singular}` : section.label(form) }}</h1>
  <p v-if="dirty" class="admin-hint">Tienes cambios sin guardar.</p>
  <form @submit.prevent="save">
    <template v-for="field in section.fields" :key="field.key">
      <div v-if="visible(field)" class="admin-field">
        <label v-if="field.type !== 'media' && field.type !== 'switch'" :for="field.key">{{
          field.label
        }}</label>
        <input
          v-if="['text', 'slug', 'url', 'email', 'phone', 'number', 'money'].includes(field.type)"
          :id="field.key"
          :value="textValue(field.key)"
          :type="
            field.type === 'number' || field.type === 'money'
              ? 'number'
              : field.type === 'email'
                ? 'email'
                : 'text'
          "
          :required="field.required"
          @input="setText(field.key, ($event.target as HTMLInputElement).value)"
          @change="
            field.type === 'slug'
              ? (slugTouched = true)
              : field.key === 'external_url'
                ? inspectUrl()
                : undefined
          "
        />
        <textarea
          v-else-if="field.type === 'textarea' || field.type === 'markdown'"
          :id="field.key"
          :value="textValue(field.key)"
          rows="5"
          :required="field.required"
          @input="setText(field.key, ($event.target as HTMLTextAreaElement).value)"
        />
        <textarea
          v-else-if="field.type === 'json-list'"
          :id="field.key"
          v-model="socialText"
          rows="4"
        />
        <select
          v-else-if="field.type === 'select' || field.type === 'icon'"
          :id="field.key"
          :value="textValue(field.key)"
          @change="setText(field.key, ($event.target as HTMLSelectElement).value)"
        >
          <option value="">Elige…</option>
          <option
            v-for="option in field.options ?? options[field.key] ?? []"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
        <select
          v-else-if="field.type === 'multiselect'"
          :id="field.key"
          multiple
          :value="Array.isArray(form[field.key]) ? form[field.key] : []"
          @change="
            form[field.key] = Array.from(($event.target as HTMLSelectElement).selectedOptions).map(
              (option) => option.value,
            )
          "
        >
          <option
            v-for="option in options[field.key] ?? []"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
        <label v-else-if="field.type === 'switch'" class="admin-switch">
          {{ field.label }}
          <input
            :checked="Boolean(form[field.key])"
            type="checkbox"
            @change="form[field.key] = ($event.target as HTMLInputElement).checked"
          />
        </label>
        <input
          v-else-if="field.type === 'date'"
          :id="field.key"
          type="datetime-local"
          :value="textValue(field.key)"
          @input="setText(field.key, ($event.target as HTMLInputElement).value)"
        />
        <AdminMediaPicker
          v-else-if="field.type === 'media'"
          :model-value="typeof form[field.key] === 'string' ? String(form[field.key]) : null"
          :accept="field.accept ?? 'image'"
          :aspect="field.aspect"
          :label="field.label"
          @update:model-value="form[field.key] = $event"
        />
        <p v-if="field.hint" class="admin-hint">{{ field.hint }}</p>
        <p v-if="fieldErrors[field.key]" class="admin-error">{{ fieldErrors[field.key] }}</p>
      </div>
    </template>
    <p v-if="form.audio_before_media_id && form.audio_after_media_id" class="admin-hint">
      Hay audio de antes y después. El comparador se muestra en el sitio.
    </p>
    <p v-if="error" class="admin-error">{{ error }}</p>
    <button v-if="section.preview" class="admin-chip" type="button" @click="preview">
      Vista previa
    </button>
    <button class="admin-save" type="submit">Guardar</button>
  </form>
</template>
