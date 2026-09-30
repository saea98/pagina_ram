<script setup lang="ts">
import type { PlayerTrack } from '~/stores/player'
import { apiBase } from '~/composables/useApi'

const store = usePlayerStore()
const audio = ref<HTMLAudioElement | null>(null)

function start(track: PlayerTrack) {
  const element = audio.value
  if (!element || !track.audioUrl) return
  element.src = track.audioUrl
  void element.play().catch(() => {
    store.pause()
  })
  if ('mediaSession' in navigator) {
    navigator.mediaSession.metadata = new MediaMetadata({
      title: track.title,
      artist: track.artist,
      artwork: track.coverUrl
        ? [{ src: track.coverUrl, sizes: '480x480', type: 'image/webp' }]
        : [],
    })
    navigator.mediaSession.setActionHandler('play', () => {
      store.isPlaying = true
    })
    navigator.mediaSession.setActionHandler('pause', () => store.pause())
  }
  void $fetch(`${apiBase()}/public/portfolio/${track.id}/events`, {
    method: 'POST',
    body: { event: 'play' },
  }).catch(() => undefined)
}

watch(
  () => store.isPlaying,
  (playing) => {
    const element = audio.value
    if (!element) return
    if (playing) void element.play()
    else element.pause()
  },
)

watch(
  () => store.seekAt,
  (seconds) => {
    if (audio.value) audio.value.currentTime = seconds
  },
)

function onTime() {
  const element = audio.value
  if (!element) return
  store.setProgress(element.currentTime, Number.isFinite(element.duration) ? element.duration : 0)
}

onMounted(() => {
  store.bindEngine(start)
  const bus = useEventBus<string>('player:exclusive')
  bus.on((id) => {
    if (id !== 'own') store.pause()
  })
})
</script>

<template>
  <audio
    ref="audio"
    data-testid="global-audio"
    aria-hidden="true"
    preload="none"
    @timeupdate="onTime"
    @ended="store.pause()"
  />
</template>
