<script setup lang="ts">
import type { PortfolioCard } from '~/types/public'

const props = defineProps<{ piece: PortfolioCard; art: string }>()
const store = usePlayerStore()

const active = computed(() => store.current?.id === props.piece.slug)
const playing = computed(() => active.value && store.isPlaying)

const length = computed(() => {
  if (active.value && store.duration > 0) return store.duration
  return props.piece.audio?.duration_s ?? 0
})

const ratio = computed(() => {
  if (!active.value || length.value <= 0) return 0
  return Math.min(1, store.position / length.value)
})

function clock(seconds: number) {
  const whole = Math.max(0, Math.floor(seconds))
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, '0')}`
}

const elapsed = computed(() => clock(active.value ? store.position : 0))
const total = computed(() => (length.value > 0 ? clock(length.value) : ''))

function toggle() {
  const audio = props.piece.audio
  const audioUrl = audio?.m4a_url || audio?.mp3_url || ''
  if (!audio || !audioUrl) return
  if (store.current?.id === props.piece.slug) {
    store.toggle()
    return
  }
  store.play({
    id: props.piece.slug,
    title: props.piece.title,
    artist: props.piece.artist_name,
    coverUrl: props.art,
    audioUrl,
    peaksUrl: audio.peaks_url,
    duration: audio.duration_s,
    lufs: audio.lufs,
  })
}

function seek(event: MouseEvent) {
  if (length.value <= 0) return
  const bar = event.currentTarget as HTMLElement
  const rect = bar.getBoundingClientRect()
  const next = ((event.clientX - rect.left) / rect.width) * length.value
  if (!active.value) toggle()
  store.seek(Math.max(0, Math.min(length.value, next)))
}

function skip(delta: number) {
  const base = active.value ? store.position : 0
  if (!active.value) toggle()
  store.seek(Math.max(0, Math.min(length.value || base + delta, base + delta)))
}
</script>

<template>
  <div class="play-strip">
    <img class="play-strip-art" :src="art" alt="" />
    <div class="play-strip-main">
      <span class="play-strip-title">{{ piece.title }}</span>
      <span class="play-strip-artist">{{ piece.artist_name }}</span>
      <button class="play-strip-track" type="button" aria-label="Avanzar en la pista" @click="seek">
        <span :style="{ width: `${ratio * 100}%` }" />
      </button>
      <span class="play-strip-time"
        >{{ elapsed }}<template v-if="total"> / {{ total }}</template></span
      >
    </div>
    <div class="play-strip-controls">
      <button class="play-strip-icon" type="button" aria-label="Retroceder" @click="skip(-10)">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 6v12h2V6H6zm3.5 6 8.5 5.5V6.5L9.5 12z" />
        </svg>
      </button>
      <button class="play-strip-icon" type="button" aria-label="Adelantar" @click="skip(10)">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M16 6v12h2V6h-2zM6 6.5v11L14.5 12 6 6.5z" />
        </svg>
      </button>
      <button
        class="play-strip-btn"
        type="button"
        :aria-label="playing ? 'Pausar reproducción' : 'Reproducir'"
        @click="toggle"
      >
        <svg v-if="playing" viewBox="0 0 24 24" aria-hidden="true">
          <rect x="6" y="5" width="4" height="14" rx="1" />
          <rect x="14" y="5" width="4" height="14" rx="1" />
        </svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true">
          <path d="M8 5.5v13l11-6.5-11-6.5z" />
        </svg>
      </button>
    </div>
  </div>
</template>
