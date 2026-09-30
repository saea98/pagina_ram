import { defineStore } from 'pinia'

export type PlayerSource = 'own' | 'spotify' | 'youtube' | 'soundcloud' | 'apple_music' | 'bandcamp'

export interface PlayerTrack {
  id: string
  title: string
  artist: string
  coverUrl: string | null
  audioUrl: string
  peaksUrl: string | null
  duration: number | null
  lufs: number | null
}

export const usePlayerStore = defineStore('player', () => {
  const current = ref<PlayerTrack | null>(null)
  const queue = ref<PlayerTrack[]>([])
  const isPlaying = ref(false)
  const position = ref(0)
  const duration = ref(0)
  const seekAt = ref(0)
  const source = ref<PlayerSource | null>(null)
  const sourceId = ref<string | null>(null)
  const bus = useEventBus<string>('player:exclusive')
  let engage: ((track: PlayerTrack) => void) | null = null

  function bindEngine(start: (track: PlayerTrack) => void) {
    engage = start
  }

  function play(track: PlayerTrack, nextQueue: PlayerTrack[] = []) {
    current.value = track
    queue.value = nextQueue
    source.value = 'own'
    sourceId.value = track.id
    isPlaying.value = true
    bus.emit('own')
    engage?.(track)
  }

  function toggle() {
    if (!current.value) return
    isPlaying.value = !isPlaying.value
    if (isPlaying.value) bus.emit('own')
  }

  function seek(seconds: number) {
    position.value = seconds
    seekAt.value = seconds
  }

  function stopOthers(id: string) {
    sourceId.value = id
    if (id !== 'own') isPlaying.value = false
    bus.emit(id)
  }

  function setProgress(nextPosition: number, nextDuration: number) {
    position.value = nextPosition
    duration.value = nextDuration
  }

  function pause() {
    isPlaying.value = false
  }

  return {
    current,
    queue,
    isPlaying,
    position,
    duration,
    seekAt,
    source,
    sourceId,
    play,
    bindEngine,
    toggle,
    seek,
    stopOthers,
    setProgress,
    pause,
  }
})
