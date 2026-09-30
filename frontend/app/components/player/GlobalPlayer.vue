<script setup lang="ts">
import type { PlayerTrack } from '~/stores/player'
import { apiBase } from '~/composables/useApi'

const store = usePlayerStore()
const audio = ref<HTMLAudioElement | null>(null)
const waveHost = ref<HTMLElement | null>(null)
let wave: { destroy: () => void } | null = null

function start(track: PlayerTrack) {
  const element = audio.value
  if (!element) return
  element.src = track.audioUrl
  void element.play()
  void mountWave(track)
}

async function mountWave(track: PlayerTrack) {
  await nextTick()
  const element = audio.value
  const host = waveHost.value
  if (!element || !host) return
  wave?.destroy()
  const WaveSurfer = (await import('wavesurfer.js')).default
  let peaks = [Array.from({ length: 800 }, () => 0.15)]
  if (track.peaksUrl) {
    try {
      peaks = [await $fetch<number[]>(track.peaksUrl)]
    } catch {
      /* keep a flat waveform; do not decode the file */
    }
  }
  wave = WaveSurfer.create({
    container: host,
    media: element,
    peaks,
    duration: track.duration ?? 1,
    height: 48,
    waveColor: 'rgba(255,244,235,0.28)',
    progressColor: '#FFBEC5',
    cursorWidth: 0,
    barWidth: 2,
    barGap: 1,
    interact: true,
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
  await $fetch(`${apiBase()}/public/portfolio/${track.id}/events`, {
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

onUnmounted(() => wave?.destroy())
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
  <div v-if="store.current" class="global-player">
    <button type="button" class="btn btn-solid" @click="store.toggle()">
      {{ store.isPlaying ? 'Pausar' : 'Escuchar' }}
    </button>
    <img v-if="store.current.coverUrl" :src="store.current.coverUrl" alt="" />
    <div class="meta">
      <strong>{{ store.current.title }}</strong>
      <span>{{ store.current.artist }}</span>
    </div>
    <div ref="waveHost" class="wave" />
  </div>
</template>
