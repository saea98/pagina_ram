<script setup lang="ts">
import { adminErrorMessage, adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const id = String(route.params.id)
const toast = useState('admin-toast', () => '')
const note = ref('')
const confirmText = ref('')
const error = ref('')

interface LeadEvent {
  id: string
  type: string
  from_status: string | null
  to_status: string | null
  note: string | null
  created_at: string
}
interface LeadDetail {
  id: string
  name: string
  email: string | null
  phone_e164: string | null
  service_title: string | null
  message: string
  demo_url: string | null
  has_demo: boolean
  status: string
  utm_source: string | null
  utm_medium: string | null
  utm_campaign: string | null
  utm_content: string | null
  utm_term: string | null
  events: LeadEvent[]
}

const lead = ref(await adminFetch<LeadDetail>(`/admin/leads/${id}`))
const statuses = ['new', 'contacted', 'quoted', 'won', 'lost']
const labels: Record<string, string> = {
  new: 'Nuevo',
  contacted: 'Contactado',
  quoted: 'Cotizado',
  won: 'Ganado',
  lost: 'Perdido',
}

const mailto = computed(() => {
  if (!lead.value.email) return ''
  const subject = encodeURIComponent('Cherry Studios')
  const body = encodeURIComponent(
    `Hola ${lead.value.name}, gracias por escribirnos sobre ${lead.value.service_title ?? 'tu proyecto'}.`,
  )
  return `mailto:${lead.value.email}?subject=${subject}&body=${body}`
})
const whatsapp = computed(() => {
  if (!lead.value.phone_e164) return ''
  const text = encodeURIComponent(`Hola ${lead.value.name}, te escribimos de Cherry Studios.`)
  return `https://wa.me/${lead.value.phone_e164.replace('+', '')}?text=${text}`
})

async function setStatus(status: string) {
  lead.value = await adminFetch(`/admin/leads/${id}`, { method: 'PATCH', body: { status } })
  toast.value = 'Estado actualizado'
}

async function addNote() {
  lead.value = await adminFetch(`/admin/leads/${id}/notes`, {
    method: 'POST',
    body: { note: note.value },
  })
  note.value = ''
  toast.value = 'Nota guardada'
}

async function remove() {
  if (confirmText.value !== 'ELIMINAR') {
    error.value = 'Escribe ELIMINAR para confirmar. Esto borra el mensaje por una solicitud ARCO.'
    return
  }
  try {
    await adminFetch(`/admin/leads/${id}`, { method: 'DELETE', query: { confirm: 'true' } })
    await navigateTo('/admin/leads')
  } catch (reason) {
    error.value = adminErrorMessage(reason)
  }
}
</script>

<template>
  <div>
    <h1>{{ lead.name }}</h1>
    <p>{{ lead.service_title ?? 'Sin servicio' }} · {{ labels[lead.status] }}</p>
    <p>{{ lead.message }}</p>
    <label>
      Estado
      <select :value="lead.status" @change="setStatus(($event.target as HTMLSelectElement).value)">
        <option v-for="status in statuses" :key="status" :value="status">
          {{ labels[status] }}
        </option>
      </select>
    </label>
    <p>
      <a v-if="mailto" :href="mailto">Responder por correo</a>
      <a v-if="whatsapp" :href="whatsapp" target="_blank" rel="noopener">WhatsApp</a>
      <a v-if="lead.demo_url" :href="lead.demo_url" target="_blank" rel="noopener"
        >Enlace de maqueta</a
      >
      <a v-if="lead.has_demo" :href="`/api/v1/admin/leads/${lead.id}/demo`">Escuchar maqueta</a>
    </p>
    <h2>Campaña</h2>
    <p>
      Fuente {{ lead.utm_source ?? '—' }} · medio {{ lead.utm_medium ?? '—' }} · campaña
      {{ lead.utm_campaign ?? '—' }}
    </p>
    <p>Contenido {{ lead.utm_content ?? '—' }} · término {{ lead.utm_term ?? '—' }}</p>
    <h2>Historial</h2>
    <p v-for="event in lead.events" :key="event.id">
      {{ event.note || `${event.from_status ?? '—'} → ${event.to_status ?? '—'}` }}
    </p>
    <label>
      Nota interna
      <textarea v-model="note" rows="3" />
    </label>
    <button class="admin-chip" type="button" @click="addNote">Guardar nota</button>
    <h2>Borrar definitivamente</h2>
    <p class="admin-hint">Solo si la persona pidió cancelar sus datos (ARCO). Escribe ELIMINAR.</p>
    <input v-model="confirmText" type="text" autocomplete="off" />
    <button class="admin-chip" type="button" @click="remove">Eliminar</button>
    <p v-if="error" class="admin-error">{{ error }}</p>
  </div>
</template>
