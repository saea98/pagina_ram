<script setup lang="ts">
import type { PortfolioCard } from '~/types/public'
import {
  listenSpotify,
  readSpotifyMessage,
  SPOTIFY_ORIGIN,
  spotifyCommand,
  spotifyEmbedSrc,
} from '~/utils/spotifyEmbed'

const props = defineProps<{ piece: PortfolioCard }>()
const open = ref(false)
const playing = ref(false)
const ready = ref(false)
const activeSrc = ref('')
const store = usePlayerStore()
const frame = ref<HTMLIFrameElement | null>(null)
let wasPlaying = false
let ignoreUntil = 0
let stopListen = () => {}

const isSpotify = computed(() => props.piece.kind === 'spotify' && Boolean(props.piece.external_id))
const spotifyKind = computed(() =>
  props.piece.external_url?.includes('/album/') ? 'album' : 'track',
)
const spotifySrc = computed(() => {
  if (!isSpotify.value || !props.piece.external_id) return ''
  return spotifyEmbedSrc(spotifyKind.value, props.piece.external_id)
})

const embedSrc = computed(() => {
  if (!props.piece.external_id || props.piece.kind === 'spotify') return ''
  if (props.piece.kind !== 'youtube' && !props.piece.external_url?.includes('youtu')) return ''
  const start = props.piece.youtube_start_s ? `&start=${props.piece.youtube_start_s}` : ''
  return `https://www.youtube-nocookie.com/embed/${props.piece.external_id}?autoplay=1&enablejsapi=1${start}`
})

function post(command: 'play' | 'pause' | 'ack') {
  frame.value?.contentWindow?.postMessage(spotifyCommand(command), SPOTIFY_ORIGIN)
}

function onSpotifyMessage(event: MessageEvent) {
  if (event.origin !== SPOTIFY_ORIGIN || event.source !== frame.value?.contentWindow) return
  const message = readSpotifyMessage(event.data)
  if (!message) return
  if (message.type === 'ready') {
    ready.value = true
    post('ack')
    return
  }
  const now = message.playing
  playing.value = now
  if (Date.now() < ignoreUntil) {
    wasPlaying = now
    return
  }
  if (now && !wasPlaying) store.stopOthers(props.piece.slug)
  wasPlaying = now
}

function activate() {
  if (!embedSrc.value) return
  store.stopOthers(props.piece.slug)
  open.value = true
}

function pause() {
  open.value = false
  ignoreUntil = Date.now() + 500
  if (isSpotify.value) post('pause')
  playing.value = false
  wasPlaying = false
}

function toggleSpotify() {
  if (!ready.value) return
  if (playing.value) {
    pause()
    return
  }
  ignoreUntil = 0
  store.stopOthers(props.piece.slug)
  post('play')
}

onMounted(() => {
  if (!isSpotify.value || !spotifySrc.value) return
  stopListen = listenSpotify(onSpotifyMessage)
  activeSrc.value = spotifySrc.value
})

onUnmounted(() => {
  stopListen()
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
      <div class="embed-slot">
        <iframe
          v-if="activeSrc"
          ref="frame"
          class="embed-frame"
          :src="activeSrc"
          :title="piece.title"
          allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
        />
      </div>
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
