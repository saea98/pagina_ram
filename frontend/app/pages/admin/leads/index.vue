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

function ago(iso: string) {
  const hours = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 3600000))
  if (hours < 1) return 'hace un momento'
  if (hours < 24) return `hace ${hours} h`
  return `hace ${Math.round(hours / 24)} d`
}

await load()
</script>

<template>
  <div>
    <h1>Leads</h1>
    <div class="admin-chip-row">
      <button
        class="admin-chip"
        type="button"
        :aria-pressed="status === ''"
        @click="showStatus('')"
      >
        Todos
      </button>
      <button
        v-for="(label, key) in labels"
        :key="key"
        class="admin-chip"
        type="button"
        :aria-pressed="status === key"
        @click="showStatus(String(key))"
      >
        {{ label }}
      </button>
    </div>
    <input v-model="q" class="admin-search" type="search" placeholder="Buscar" @change="load" />
    <p v-if="!items.length">No hay mensajes con ese filtro.</p>
    <NuxtLink
      v-for="lead in items"
      :key="lead.id"
      class="admin-card"
      :to="`/admin/leads/${lead.id}`"
    >
      <strong>{{ lead.name }}</strong>
      <span>{{ lead.service_title ?? 'Sin servicio' }} · {{ labels[lead.status] }}</span>
      <span>{{ lead.utm_source ?? 'directo' }} · {{ ago(lead.created_at) }}</span>
    </NuxtLink>
    <a class="admin-chip" href="/api/v1/admin/leads/export.csv">Exportar CSV</a>
  </div>
</template>
