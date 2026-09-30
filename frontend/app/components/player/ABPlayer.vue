<script setup lang="ts">
import { matchGain } from '~/utils/lufs'

const props = defineProps<{
  beforeUrl: string
  afterUrl: string
  beforeLufs: number | null
  afterLufs: number | null
  title: string
  artist: string
}>()

const side = ref<'before' | 'after'>('after')
const playing = ref(false)
const beforeEl = ref<HTMLAudioElement | null>(null)
const afterEl = ref<HTMLAudioElement | null>(null)
const root = ref<HTMLElement | null>(null)
let context: AudioContext | null = null
let beforeGain: GainNode | null = null
let afterGain: GainNode | null = null
const store = usePlayerStore()

function applyGains(seconds: number) {
  if (!context || !beforeGain || !afterGain) return
  const now = context.currentTime
  const beforeTarget = side.value === 'before' ? matchGain(props.beforeLufs, props.afterLufs) : 0
  const afterTarget = side.value === 'after' ? matchGain(props.afterLufs, props.beforeLufs) : 0
  beforeGain.gain.cancelScheduledValues(now)
  afterGain.gain.cancelScheduledValues(now)
  beforeGain.gain.setValueAtTime(beforeGain.gain.value, now)
  afterGain.gain.setValueAtTime(afterGain.gain.value, now)
  beforeGain.gain.linearRampToValueAtTime(beforeTarget, now + seconds)
  afterGain.gain.linearRampToValueAtTime(afterTarget, now + seconds)
}

async function ensureGraph() {
  if (context || !beforeEl.value || !afterEl.value) return
  context = new AudioContext()
  const beforeSource = context.createMediaElementSource(beforeEl.value)
  const afterSource = context.createMediaElementSource(afterEl.value)
  beforeGain = context.createGain()
  afterGain = context.createGain()
  beforeGain.gain.value = 0
  afterGain.gain.value = 0
  beforeSource.connect(beforeGain).connect(context.destination)
  afterSource.connect(afterGain).connect(context.destination)
}

async function toggle() {
  await ensureGraph()
  await context?.resume()
  store.stopOthers('ab')
  if (playing.value) {
    beforeEl.value?.pause()
    afterEl.value?.pause()
    playing.value = false
    return
  }
  const time = beforeEl.value?.currentTime ?? 0
  if (afterEl.value) afterEl.value.currentTime = time
  await Promise.all([beforeEl.value?.play(), afterEl.value?.play()])
  playing.value = true
  applyGains(0.03)
}

function setSide(next: 'before' | 'after') {
  side.value = next
  applyGains(0.03)
}

function onKey(event: KeyboardEvent) {
  if (event.key === 'a' || event.key === 'A') setSide('before')
  if (event.key === 'b' || event.key === 'B') setSide('after')
  if (event.key === ' ') {
    event.preventDefault()
    void toggle()
  }
}

const bus = useEventBus<string>('player:exclusive')
bus.on((id) => {
  if (id === 'ab') return
  beforeEl.value?.pause()
  afterEl.value?.pause()
  playing.value = false
})
</script>

<template>
  <div ref="root" class="embed-card" tabindex="0" @keydown="onKey">
    <div class="embed-label">
      <span class="embed-title">{{ title }}</span>
      <span class="embed-artist">{{ artist }}</span>
    </div>
    <div class="listen-row">
      <button class="btn btn-solid" type="button" @click="toggle">
        {{ playing ? 'Pausar' : 'Escuchar' }}
      </button>
      <div class="ab-switch" role="group" aria-label="Antes o después">
        <button
          type="button"
          role="switch"
          :aria-checked="side === 'before'"
          @click="setSide('before')"
        >
          Antes
        </button>
        <button
          type="button"
          role="switch"
          :aria-checked="side === 'after'"
          @click="setSide('after')"
        >
          Después
        </button>
      </div>
    </div>
    <audio ref="beforeEl" :src="beforeUrl" preload="none" crossorigin="anonymous" />
    <audio ref="afterEl" :src="afterUrl" preload="none" crossorigin="anonymous" />
  </div>
</template>
