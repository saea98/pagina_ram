<script setup lang="ts">
import type { AdminSection } from '~/admin/fields'
import { adminErrorMessage } from '~/composables/useAdminApi'
import { useResource, type ResourceRow } from '~/composables/useResource'

const props = defineProps<{ section: AdminSection; sectionKey: string }>()
const toast = defineModel<string>('toast', { default: '' })
const api = useResource<ResourceRow>(props.section.api)
const query = ref('')
const rows = ref<ResourceRow[]>([])
const error = ref('')

async function load() {
  const page = await api.list(query.value)
  rows.value = page.items
}

await load()

let searchTimer = 0
watch(query, () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => void load(), 250)
})

async function persistOrder() {
  await api.reorder(rows.value.map((row) => row.id))
  toast.value = 'Orden guardado'
}

async function move(index: number, direction: -1 | 1) {
  const next = index + direction
  if (next < 0 || next >= rows.value.length) return
  const copy = rows.value.slice()
  const [item] = copy.splice(index, 1)
  if (!item) return
  copy.splice(next, 0, item)
  rows.value = copy
  await persistOrder()
}

async function toggle(row: ResourceRow) {
  await api.update(row.id, { is_published: !row.is_published })
  row.is_published = !row.is_published
  toast.value = row.is_published ? 'Publicado' : 'Oculto'
}

async function remove(row: ResourceRow) {
  if (
    !confirm(
      `¿Eliminar “${props.section.label(row)}”? Deja de mostrarse en el sitio. Esta acción no se deshace desde el panel.`,
    )
  )
    return
  try {
    await api.remove(row.id)
    rows.value = rows.value.filter((item) => item.id !== row.id)
    toast.value = 'Eliminado'
  } catch (reason) {
    error.value = adminErrorMessage(reason)
  }
}
</script>

<template>
  <h1>{{ section.title }}</h1>
  <input v-model="query" class="admin-search" type="search" placeholder="Buscar" @search="load" />
  <p v-if="!rows.length" class="admin-empty">
    {{ query ? 'Nada coincide con esa búsqueda.' : section.empty }}
  </p>
  <article v-for="(row, index) in rows" :key="row.id" class="admin-card">
    <div class="admin-order">
      <button class="admin-icon-btn" type="button" aria-label="Subir" @click="move(index, -1)">
        ↑
      </button>
      <button class="admin-icon-btn" type="button" aria-label="Bajar" @click="move(index, 1)">
        ↓
      </button>
    </div>
    <NuxtLink class="admin-card-main" :to="`/admin/${sectionKey}/${row.id}`">
      <strong>{{ section.label(row) }}</strong>
      <span>{{ section.meta(row) }}</span>
    </NuxtLink>
    <div class="admin-actions">
      <button
        class="admin-icon-btn admin-status"
        type="button"
        :aria-pressed="Boolean(row.is_published)"
        @click="toggle(row)"
      >
        {{ row.is_published ? 'Publicado' : 'Oculto' }}
      </button>
      <button class="admin-icon-btn admin-danger" type="button" @click="remove(row)">
        Eliminar
      </button>
    </div>
  </article>
  <p v-if="error" class="admin-error">{{ error }}</p>
  <NuxtLink
    class="admin-save"
    :to="`/admin/${sectionKey}/nuevo`"
    style="display: grid; place-items: center; text-decoration: none"
  >
    Agregar {{ section.singular }}
  </NuxtLink>
</template>
