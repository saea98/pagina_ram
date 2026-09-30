<script setup lang="ts">
import type { PortfolioCard } from '~/types/public'

const props = defineProps<{ piece: PortfolioCard }>()
const open = ref(false)
const store = usePlayerStore()

const embedSrc = computed(() => {
  if (props.piece.kind === 'spotify' && props.piece.external_id) {
    const type = props.piece.external_url?.includes('/album/') ? 'album' : 'track'
    return `https://open.spotify.com/embed/${type}/${props.piece.external_id}`
  }
  if (!props.piece.external_id || props.piece.kind === 'spotify') return ''
  if (props.piece.kind !== 'youtube' && !props.piece.external_url?.includes('youtu')) return ''
  const start = props.piece.youtube_start_s ? `&start=${props.piece.youtube_start_s}` : ''
  return `https://www.youtube-nocookie.com/embed/${props.piece.external_id}?autoplay=1${start}`
})

function activate() {
  if (!embedSrc.value) return
  store.stopOthers(props.piece.slug)
  open.value = true
}

function pause() {
  open.value = false
}

const bus = useEventBus<string>('player:exclusive')
bus.on((id) => {
  if (id !== props.piece.slug) pause()
})
</script>

<template>
  <div class="embed-card">
    <div class="embed-label">
      <span class="embed-title">{{ piece.title }}</span>
      <span class="embed-artist">{{ piece.artist_name }}</span>
    </div>
    <div v-if="!open" class="facade">
      <SiteCherryPicture v-if="piece.cover" :image="piece.cover" />
      <button class="btn btn-solid" type="button" @click="activate">Escuchar</button>
    </div>
    <div v-else class="embed-player" :class="{ 'is-video': piece.kind !== 'spotify' }">
      <iframe
        :src="embedSrc"
        :title="piece.title"
        :class="{ 'is-album': piece.external_url?.includes('/album/') }"
        allow="autoplay; encrypted-media; fullscreen"
        allowfullscreen
      />
    </div>
  </div>
</template>
