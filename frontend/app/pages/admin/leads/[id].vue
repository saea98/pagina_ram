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
  sent_from: string | null
  phone_e164: string | null
  service_title: string | null
  message: string
  demo_url: string | null
  has_demo: boolean
  status: string
  created_at: string
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
const weekdays = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB']

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
const campaign = computed(() =>
  [
    ['Fuente', lead.value.utm_source],
    ['Medio', lead.value.utm_medium],
    ['Campaña', lead.value.utm_campaign],
    ['Contenido', lead.value.utm_content],
    ['Término', lead.value.utm_term],
  ].filter((item): item is [string, string] => Boolean(item[1])),
)

function when(iso: string) {
  const date = new Date(iso)
  return {
    day: date.getDate(),
    weekday: weekdays[date.getDay()] ?? '',
    long: new Intl.DateTimeFormat('es-MX', { day: 'numeric', month: 'long' }).format(date),
  }
}

function eventTitle(event: LeadEvent) {
  if (event.note) return event.note
  const from = event.from_status ? labels[event.from_status] : '—'
  const to = event.to_status ? labels[event.to_status] : '—'
  return `${from} → ${to}`
}

async function setStatus(status: string) {
  if (status === lead.value.status) return
  lead.value = await adminFetch(`/admin/leads/${id}`, { method: 'PATCH', body: { status } })
  toast.value = 'Estado actualizado'
}

async function addNote() {
  if (!note.value.trim()) return
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
  <div class="lead-board">
    <header class="lead-toolbar">
      <h1>{{ lead.name }}</h1>
      <a v-if="mailto" class="lead-add" :href="mailto">Responder</a>
    </header>

    <article class="agenda-card">
      <div class="agenda-date">
        <strong>{{ when(lead.created_at).day }}</strong>
        <span>{{ when(lead.created_at).weekday }}</span>
      </div>
      <div class="agenda-body">
        <h2>{{ lead.service_title ?? 'Sin servicio' }}</h2>
        <p class="agenda-line">
          <span class="agenda-status" :data-status="lead.status">{{ labels[lead.status] }}</span>
          <span>{{ when(lead.created_at).long }}</span>
          <span v-if="lead.email">· {{ lead.email }}</span>
        </p>
        <p class="agenda-copy">{{ lead.message }}</p>
      </div>
    </article>

    <section class="agenda-panel">
      <div class="panel-head">
        <h2>Contacto</h2>
      </div>
      <dl class="contact-rows">
        <div v-if="lead.email">
          <dt>Correo</dt>
          <dd>{{ lead.email }}</dd>
        </div>
        <div v-if="lead.sent_from">
          <dt>Cuenta de Google</dt>
          <dd>{{ lead.sent_from }}</dd>
        </div>
        <div v-if="lead.phone_e164">
          <dt>Teléfono</dt>
          <dd>{{ lead.phone_e164 }}</dd>
        </div>
      </dl>
      <div class="status-row" role="group" aria-label="Estado">
        <button
          v-for="status in statuses"
          :key="status"
          class="agenda-status status-choice"
          :data-status="status"
          type="button"
          :aria-pressed="lead.status === status"
          @click="setStatus(status)"
        >
          {{ labels[status] }}
        </button>
      </div>
      <div class="lead-links">
        <a
          v-if="whatsapp"
          class="lead-add lead-add-ghost"
          :href="whatsapp"
          target="_blank"
          rel="noopener"
          >WhatsApp</a
        >
        <a
          v-if="lead.demo_url"
          class="lead-add lead-add-ghost"
          :href="lead.demo_url"
          target="_blank"
          rel="noopener"
          >Maqueta</a
        >
        <a
          v-if="lead.has_demo"
          class="lead-add lead-add-ghost"
          :href="`/api/v1/admin/leads/${lead.id}/demo`"
          >Escuchar</a
        >
      </div>
    </section>

    <section v-if="campaign.length" class="agenda-panel">
      <div class="panel-head">
        <h2>Campaña</h2>
      </div>
      <p class="agenda-line">
        <template v-for="([label, value], index) in campaign" :key="label">
          <span v-if="index">·</span>
          <span>{{ label }} {{ value }}</span>
        </template>
      </p>
    </section>

    <section class="agenda-panel">
      <div class="panel-head">
        <h2>Historial</h2>
      </div>
      <p v-if="!lead.events.length" class="agenda-empty">Todavía no hay notas ni cambios.</p>
      <article v-for="event in lead.events" :key="event.id" class="agenda-card">
        <div class="agenda-date">
          <strong>{{ when(event.created_at).day }}</strong>
          <span>{{ when(event.created_at).weekday }}</span>
        </div>
        <div class="agenda-body">
          <h2>{{ eventTitle(event) }}</h2>
          <p class="agenda-line">
            <span class="agenda-status" :data-status="event.to_status || 'note'">{{
              event.note ? 'Nota' : labels[event.to_status || ''] || 'Cambio'
            }}</span>
            <span>{{ when(event.created_at).long }}</span>
          </p>
        </div>
      </article>
    </section>

    <section class="agenda-panel">
      <div class="panel-head">
        <h2>Nota interna</h2>
        <button class="lead-add" type="button" :disabled="!note.trim()" @click="addNote">
          Guardar
        </button>
      </div>
      <textarea v-model="note" rows="3" placeholder="Escribe una nota" />
    </section>

    <section class="agenda-panel danger-panel">
      <div class="panel-head">
        <h2>Borrar definitivamente</h2>
      </div>
      <p class="agenda-empty">Solo si la persona pidió cancelar sus datos. Escribe ELIMINAR.</p>
      <input v-model="confirmText" type="text" autocomplete="off" />
      <button class="lead-add lead-add-ghost" type="button" @click="remove">Eliminar</button>
      <p v-if="error" class="admin-error">{{ error }}</p>
    </section>
  </div>
</template>

<style scoped>
.lead-board {
  display: grid;
  gap: 14px;
  max-width: 760px;
}

.lead-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.lead-toolbar h1,
.agenda-body h2,
.panel-head h2 {
  margin: 0;
  font-family: var(--font-sans);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.lead-toolbar h1 {
  font-size: 1.7rem;
  line-height: 1.15;
}

.agenda-card,
.agenda-panel {
  background: #fff;
  border: 1px solid #f0e2da;
  border-radius: 18px;
  box-shadow: 0 1px 0 rgba(61, 13, 17, 0.03);
}

.agenda-card {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  gap: 14px;
  padding: 16px 18px;
}

.agenda-date {
  display: grid;
  justify-items: center;
  align-content: start;
  padding-top: 2px;
  color: #1c1b1b;
}

.agenda-date strong {
  font-size: 1.55rem;
  line-height: 1;
  font-weight: 700;
}

.agenda-date span {
  margin-top: 4px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #8a7b76;
}

.agenda-body h2,
.panel-head h2 {
  font-size: 1.05rem;
  line-height: 1.3;
}

.agenda-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 8px;
  margin: 8px 0 0;
  color: #8a7b76;
  font-size: 0.88rem;
}

.agenda-copy,
.agenda-empty {
  margin: 10px 0 0;
  color: #3d3330;
  line-height: 1.45;
}

.agenda-empty {
  color: #8a7b76;
}

.agenda-status {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border: 0;
  border-radius: 999px;
  background: #fff4e8;
  color: #c2610c;
  font: inherit;
  font-size: 0.75rem;
  font-weight: 700;
}

.agenda-status[data-status='contacted'] {
  background: #eef3ff;
  color: #314e9b;
}

.agenda-status[data-status='quoted'] {
  background: #f6efff;
  color: #6d3ea8;
}

.agenda-status[data-status='won'] {
  background: #e8f8ee;
  color: #17803d;
}

.agenda-status[data-status='lost'],
.agenda-status[data-status='note'] {
  background: #f3f1f0;
  color: #6d6562;
}

.status-choice {
  cursor: pointer;
  opacity: 0.55;
}

.status-choice[aria-pressed='true'] {
  opacity: 1;
  outline: 1.5px solid currentColor;
}

.agenda-panel {
  display: grid;
  gap: 12px;
  padding: 16px 18px 18px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.contact-rows {
  display: grid;
  gap: 10px;
  margin: 0;
}

.contact-rows div {
  display: grid;
  gap: 2px;
}

.contact-rows dt {
  color: #8a7b76;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.contact-rows dd {
  margin: 0;
  font-weight: 650;
}

.status-row,
.lead-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.lead-add {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 0 16px;
  border: 0;
  border-radius: 999px;
  background: #1c1b1b;
  color: #fff;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}

.lead-add:disabled {
  opacity: 0.4;
  cursor: default;
}

.lead-add-ghost {
  background: #fff;
  color: #1c1b1b;
  border: 1px solid #e6d9d2;
}

.agenda-panel textarea,
.danger-panel input {
  width: 100%;
  border: 1px solid #eadfd8;
  border-radius: 14px;
  background: #fff;
  color: inherit;
  font: inherit;
  font-size: 16px;
  padding: 12px 14px;
}

.danger-panel .lead-add {
  justify-self: start;
}
</style>
