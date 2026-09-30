<script setup lang="ts">
import { adminErrorMessage, adminFetch } from '~/composables/useAdminApi'

interface MediaItem {
  id: string
  kind: string
  status: string
  original_filename: string
  alt_text: string | null
  preview_url: string | null
}

const props = defineProps<{
  accept: 'image' | 'audio'
  aspect?: number
  label: string
}>()
const model = defineModel<string | null>({ default: null })

const open = ref(false)
const tab = ref<'upload' | 'library'>('upload')
const alt = ref('')
const progress = ref(0)
const status = ref('')
const error = ref('')
const library = ref<MediaItem[]>([])
const current = ref<MediaItem | null>(null)

async function loadLibrary() {
  const page = await adminFetch<{ items: MediaItem[] }>('/admin/media', {
    query: { kind: props.accept === 'image' ? 'image' : 'audio', page_size: 40 },
  })
  library.value = page.items
}

async function refreshCurrent() {
  if (!model.value) {
    current.value = null
    return
  }
  current.value = await adminFetch<MediaItem>(`/admin/media/${model.value}`)
}

watch(open, (value) => {
  if (value) void loadLibrary()
})
watch(model, () => void refreshCurrent(), { immediate: true })

function cropCenter(file: File, aspect: number): Promise<File> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    const url = URL.createObjectURL(file)
    image.onload = () => {
      const ratio = image.width / image.height
      let width = image.width
      let height = image.height
      let x = 0
      let y = 0
      if (ratio > aspect) {
        width = image.height * aspect
        x = (image.width - width) / 2
      } else {
        height = image.width / aspect
        y = (image.height - height) / 2
      }
      const canvas = document.createElement('canvas')
      canvas.width = Math.round(width)
      canvas.height = Math.round(height)
      const context = canvas.getContext('2d')
      if (!context) {
        reject(new Error('canvas'))
        return
      }
      context.drawImage(image, x, y, width, height, 0, 0, canvas.width, canvas.height)
      canvas.toBlob(
        (blob) => {
          URL.revokeObjectURL(url)
          if (!blob) {
            reject(new Error('blob'))
            return
          }
          resolve(new File([blob], file.name.replace(/\.\w+$/, '.jpg'), { type: 'image/jpeg' }))
        },
        'image/jpeg',
        0.9,
      )
    }
    image.onerror = () => reject(new Error('image'))
    image.src = url
  })
}

async function upload(file: File) {
  error.value = ''
  if (props.accept === 'image' && !alt.value.trim()) {
    error.value = 'Escribe el texto alternativo antes de subir la imagen.'
    return
  }
  const payload =
    props.accept === 'image' && props.aspect ? await cropCenter(file, props.aspect) : file
  const body = new FormData()
  body.append('file', payload)
  if (alt.value.trim()) body.append('alt_text', alt.value.trim())
  const token = document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrf_token='))
    ?.slice('csrf_token='.length)
  progress.value = 1
  status.value = 'Subiendo…'
  const created = await new Promise<MediaItem>((resolve, reject) => {
    const request = new XMLHttpRequest()
    request.open('POST', '/api/v1/admin/media')
    request.withCredentials = true
    if (token) request.setRequestHeader('X-CSRF-Token', decodeURIComponent(token))
    request.upload.onprogress = (event) => {
      if (event.lengthComputable) progress.value = Math.round((event.loaded / event.total) * 100)
    }
    request.onload = () => {
      if (request.status >= 200 && request.status < 300)
        resolve(JSON.parse(request.responseText) as MediaItem)
      else reject(new Error(request.responseText))
    }
    request.onerror = () => reject(new Error('red'))
    request.send(body)
  }).catch((reason: unknown) => {
    error.value = adminErrorMessage(reason)
    status.value = ''
    return null
  })
  if (!created) return
  model.value = created.id
  current.value = created
  status.value =
    created.kind === 'audio' ? 'Procesando audio… calculando loudness' : 'Procesando imagen…'
  for (
    let attempt = 0;
    attempt < 40 && created.status !== 'ready' && created.status !== 'failed';
    attempt += 1
  ) {
    await new Promise((resolve) => setTimeout(resolve, 1500))
    const next = await adminFetch<MediaItem>(`/admin/media/${created.id}`)
    current.value = next
    if (next.status === 'ready' || next.status === 'failed') {
      status.value = next.status === 'ready' ? 'Listo' : 'No se pudo procesar el archivo.'
      break
    }
  }
  open.value = false
}

function choose(item: MediaItem) {
  if (props.accept === 'image' && !item.alt_text) {
    error.value = 'Esa imagen no tiene texto alternativo.'
    return
  }
  model.value = item.id
  current.value = item
  open.value = false
}
</script>

<template>
  <div class="admin-field">
    <span>{{ label }}</span>
    <button class="admin-chip" type="button" @click="open = true">
      {{ current ? current.original_filename : 'Elegir archivo' }}
    </button>
    <img v-if="current?.preview_url && accept === 'image'" :src="current.preview_url" alt="" />
    <p v-if="status" class="admin-hint">
      {{ status }} <span v-if="progress">{{ progress }}%</span>
    </p>
    <div v-if="open" class="admin-drawer" role="dialog" aria-modal="true" :aria-label="label">
      <div>
        <div class="admin-tabs">
          <button type="button" :aria-selected="tab === 'upload'" @click="tab = 'upload'">
            Subir
          </button>
          <button type="button" :aria-selected="tab === 'library'" @click="tab = 'library'">
            Biblioteca
          </button>
        </div>
        <div v-if="tab === 'upload'" class="admin-field">
          <label v-if="accept === 'image'">
            Texto alternativo
            <input v-model="alt" type="text" required />
          </label>
          <p v-if="aspect" class="admin-hint">
            Recorte sugerido al centro, proporción {{ aspect }}.
          </p>
          <input
            type="file"
            :accept="accept === 'image' ? 'image/*' : 'audio/*'"
            @change="upload(($event.target as HTMLInputElement).files?.[0] as File)"
          />
        </div>
        <div v-else>
          <button
            v-for="item in library"
            :key="item.id"
            class="admin-card"
            type="button"
            @click="choose(item)"
          >
            <strong>{{ item.original_filename }}</strong>
          </button>
        </div>
        <p v-if="error" class="admin-error">{{ error }}</p>
        <button class="admin-chip" type="button" @click="open = false">Cerrar</button>
      </div>
      <button class="admin-backdrop" type="button" aria-label="Cerrar" @click="open = false" />
    </div>
  </div>
</template>
