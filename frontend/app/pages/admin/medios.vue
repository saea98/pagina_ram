<script setup lang="ts">
import { adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: 'admin' })
interface MediaItem {
  id: string
  original_filename: string
  status: string
  alt_text: string | null
  preview_url: string | null
  kind: string
}
const kind = ref('')
const items = ref<MediaItem[]>([])

async function load() {
  const page = await adminFetch<{ items: MediaItem[] }>('/admin/media', {
    query: { kind: kind.value || undefined, page_size: 40 },
  })
  items.value = page.items
}

function showKind(next: string) {
  kind.value = next
  void load()
}
await load()
</script>

<template>
  <div>
    <h1>Medios</h1>
    <div class="admin-chip-row">
      <button class="admin-chip" type="button" :aria-pressed="kind === ''" @click="showKind('')">
        Todo
      </button>
      <button
        class="admin-chip"
        type="button"
        :aria-pressed="kind === 'image'"
        @click="showKind('image')"
      >
        Imágenes
      </button>
      <button
        class="admin-chip"
        type="button"
        :aria-pressed="kind === 'audio'"
        @click="showKind('audio')"
      >
        Audio
      </button>
    </div>
    <article v-for="item in items" :key="item.id" class="admin-card">
      <img
        v-if="item.preview_url && item.kind === 'image'"
        :src="item.preview_url"
        alt=""
        width="64"
        height="64"
      />
      <div>
        <strong>{{ item.original_filename }}</strong>
        <span>{{ item.status }} · {{ item.alt_text ?? 'Sin texto alternativo' }}</span>
      </div>
    </article>
  </div>
</template>
