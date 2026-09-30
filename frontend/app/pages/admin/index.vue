<script setup lang="ts">
import { adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: 'admin' })

interface Point {
  label: string
  count: number
}
interface Stats {
  new_leads_7d: number
  close_rate: number | null
  top_source_month: string | null
  link_clicks_7d: number
  leads_by_source: Point[]
  leads_by_week: Point[]
  top_pieces: { title: string; plays: number }[]
}

const stats = await adminFetch<Stats>('/admin/stats/overview')
const maxSource = Math.max(1, ...stats.leads_by_source.map((item) => item.count))
const maxWeek = Math.max(1, ...stats.leads_by_week.map((item) => item.count))
</script>

<template>
  <div>
    <h1>Inicio</h1>
    <section class="admin-stats">
      <article class="admin-stat">
        <span>Leads nuevos (7 días)</span>
        <b>{{ stats.new_leads_7d }}</b>
      </article>
      <article class="admin-stat">
        <span>Tasa de cierre</span>
        <b>{{ stats.close_rate == null ? '—' : `${Math.round(stats.close_rate * 100)}%` }}</b>
      </article>
      <article class="admin-stat">
        <span>Fuente del mes</span>
        <b>{{ stats.top_source_month ?? '—' }}</b>
      </article>
      <article class="admin-stat">
        <span>Clics en /links (7 días)</span>
        <b>{{ stats.link_clicks_7d }}</b>
      </article>
    </section>
    <h2>Leads por fuente</h2>
    <div v-for="item in stats.leads_by_source" :key="item.label" class="admin-bar">
      <span>{{ item.label }}</span>
      <i :style="{ width: `${(item.count / maxSource) * 100}%` }" />
      <span>{{ item.count }}</span>
    </div>
    <h2>Leads por semana</h2>
    <div v-for="item in stats.leads_by_week" :key="item.label" class="admin-bar">
      <span>{{ item.label.slice(5) }}</span>
      <i :style="{ width: `${(item.count / maxWeek) * 100}%` }" />
      <span>{{ item.count }}</span>
    </div>
    <h2>Piezas más escuchadas</h2>
    <p v-for="piece in stats.top_pieces" :key="piece.title">
      {{ piece.title }} · {{ piece.plays }}
    </p>
  </div>
</template>
