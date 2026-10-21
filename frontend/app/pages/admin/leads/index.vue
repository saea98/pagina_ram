<script setup lang="ts">
import { adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: 'admin' })

interface LeadCard {
  id: string
  name: string
  service_title: string | null
  utm_source: string | null
  status: string
  created_at: string
}

const status = ref('')
const q = ref('')
const items = ref<LeadCard[]>([])
const labels: Record<string, string> = {
  new: 'Nuevo',
  contacted: 'Contactado',
  quoted: 'Cotizado',
  won: 'Ganado',
  lost: 'Perdido',
}
const weekdays = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB']

async function load() {
  const page = await adminFetch<{ items: LeadCard[] }>('/admin/leads', {
    query: { status: status.value || undefined, q: q.value, page_size: 50 },
  })
  items.value = page.items
}

function showStatus(next: string) {
  status.value = next
  void load()
}

function when(iso: string) {
  const date = new Date(iso)
  return {
    day: date.getDate(),
    weekday: weekdays[date.getDay()] ?? '',
    long: new Intl.DateTimeFormat('es-MX', { day: 'numeric', month: 'long' }).format(date),
  }
}

await load()

let searchTimer = 0
watch(q, () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => void load(), 250)
})
</script>

<template>
  <div class="lead-list">
    <header class="lead-toolbar">
      <h1>Leads</h1>
      <a class="lead-add lead-add-ghost" href="/api/v1/admin/leads/export.csv">Exportar</a>
    </header>

    <div class="status-row" role="group" aria-label="Filtrar por estado">
      <button
        class="filter-pill"
        type="button"
        :aria-pressed="status === ''"
        @click="showStatus('')"
      >
        Todos
      </button>
      <button
        v-for="(label, key) in labels"
        :key="key"
        class="filter-pill"
        type="button"
        :aria-pressed="status === key"
        @click="showStatus(String(key))"
      >
        {{ label }}
      </button>
    </div>

    <input v-model="q" class="lead-search" type="search" placeholder="Buscar" />

    <p v-if="!items.length" class="agenda-empty">No hay mensajes con ese filtro.</p>
    <NuxtLink
      v-for="lead in items"
      :key="lead.id"
      class="agenda-card"
      :to="`/admin/leads/${lead.id}`"
    >
      <div class="agenda-date">
        <strong>{{ when(lead.created_at).day }}</strong>
        <span>{{ when(lead.created_at).weekday }}</span>
      </div>
      <div class="agenda-body">
        <h2>{{ lead.name }}</h2>
        <p class="agenda-line">
          <span class="agenda-status" :data-status="lead.status">{{ labels[lead.status] }}</span>
          <span>{{ when(lead.created_at).long }}</span>
          <span>· {{ lead.service_title ?? 'Sin servicio' }}</span>
          <span>· {{ lead.utm_source ?? 'directo' }}</span>
        </p>
      </div>
    </NuxtLink>
  </div>
</template>

<style scoped>
.lead-list {
  display: grid;
  gap: 12px;
  max-width: 760px;
}

.lead-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.lead-toolbar h1,
.agenda-body h2 {
  margin: 0;
  font-family: var(--font-sans);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.lead-toolbar h1 {
  font-size: 1.7rem;
  line-height: 1.15;
}

.agenda-body h2 {
  font-size: 1.05rem;
  line-height: 1.3;
}

.status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-pill {
  min-height: 34px;
  padding: 0 14px;
  border: 1px solid #eadfd8;
  border-radius: 999px;
  background: #fff;
  color: #1c1b1b;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
}

.filter-pill[aria-pressed='true'] {
  background: #1c1b1b;
  border-color: #1c1b1b;
  color: #fff;
}

.lead-search {
  width: 100%;
  min-height: 44px;
  padding: 10px 16px;
  border: 1px solid #eadfd8;
  border-radius: 999px;
  background: #fff;
  color: inherit;
  font: inherit;
  font-size: 16px;
}

.agenda-card {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  gap: 14px;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid #f0e2da;
  border-radius: 18px;
  color: inherit;
  text-decoration: none;
}

.agenda-date {
  display: grid;
  justify-items: center;
  align-content: start;
  padding-top: 2px;
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

.agenda-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 8px;
  margin: 8px 0 0;
  color: #8a7b76;
  font-size: 0.88rem;
}

.agenda-empty {
  margin: 0;
  color: #8a7b76;
}

.agenda-status {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #fff4e8;
  color: #c2610c;
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

.agenda-status[data-status='lost'] {
  background: #f3f1f0;
  color: #6d6562;
}

.lead-add {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 700;
  text-decoration: none;
}

.lead-add-ghost {
  background: #fff;
  color: #1c1b1b;
  border: 1px solid #e6d9d2;
}
</style>
