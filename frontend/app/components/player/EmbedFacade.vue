<script setup lang="ts">
import type { PortfolioCard } from '~/types/public'
import { loadSpotifyEmbedApi, type SpotifyController } from '~/utils/spotifyEmbed'

const props = defineProps<{ piece: PortfolioCard }>()
const open = ref(false)
const playing = ref(false)
const ready = ref(false)
const store = usePlayerStore()
const host = ref<HTMLElement | null>(null)
let controller: SpotifyController | null = null
let wasPlaying = false
let ignoreUntil = 0

const isSpotify = computed(() => props.piece.kind === 'spotify' && Boolean(props.piece.external_id))
const spotifyUri = computed(() => {
  if (!isSpotify.value || !props.piece.external_id) return ''
  const type = props.piece.external_url?.includes('/album/') ? 'album' : 'track'
  return `spotify:${type}:${props.piece.external_id}`
})

const embedSrc = computed(() => {
  if (!props.piece.external_id || props.piece.kind === 'spotify') return ''
  if (props.piece.kind !== 'youtube' && !props.piece.external_url?.includes('youtu')) return ''
  const start = props.piece.youtube_start_s ? `&start=${props.piece.youtube_start_s}` : ''
  return `https://www.youtube-nocookie.com/embed/${props.piece.external_id}?autoplay=1&enablejsapi=1${start}`
})

function activate() {
  if (!embedSrc.value) return
  store.stopOthers(props.piece.slug)
  open.value = true
}

function pause() {
  open.value = false
  ignoreUntil = Date.now() + 500
  controller?.pause()
  playing.value = false
  wasPlaying = false
}

function toggleSpotify() {
  if (!controller) return
  if (playing.value) {
    pause()
    return
  }
  ignoreUntil = 0
  store.stopOthers(props.piece.slug)
  controller.play()
}

onMounted(() => {
  if (!isSpotify.value || !host.value || !spotifyUri.value) return
  const element = host.value
  const uri = spotifyUri.value
  void loadSpotifyEmbedApi()
    .then((api) => {
      if (!host.value) return
      api.createController(element, { uri, width: '100%', height: 152 }, (created) => {
        controller = created
        ready.value = true
        created.addListener('playback_update', (event) => {
          const now = !event.data.isPaused
          playing.value = now
          if (Date.now() < ignoreUntil) {
            wasPlaying = now
            return
          }
          if (now && !wasPlaying) store.stopOthers(props.piece.slug)
          wasPlaying = now
        })
      })
    })
    .catch(() => {
      ready.value = false
    })
})

onUnmounted(() => {
  controller?.destroy()
  controller = null
})

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
    <template v-if="isSpotify">
      <div ref="host" class="embed-player" />
      <div class="listen-row embed-actions">
        <button class="btn btn-solid" type="button" :disabled="!ready" @click="toggleSpotify">
          {{ playing ? 'Pausar' : 'Escuchar' }}
        </button>
      </div>
    </template>
    <template v-else>
      <div v-if="!open" class="facade">
        <SiteCherryPicture v-if="piece.cover" :image="piece.cover" />
        <button class="btn btn-solid" type="button" @click="activate">Escuchar</button>
      </div>
      <div v-else class="embed-player is-video">
        <iframe
          :src="embedSrc"
          :title="piece.title"
          allow="autoplay; encrypted-media; fullscreen"
          allowfullscreen
        />
      </div>
    </template>
  </div>
</template>
