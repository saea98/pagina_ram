<script setup lang="ts">
import type { PortfolioCard } from '~/types/public'

interface SpotifyController {
  pause: () => void
  play: () => void
}

interface SpotifyApi {
  createController: (
    element: HTMLElement,
    options: { uri: string; width?: string | number; height?: string | number },
    callback: (controller: SpotifyController) => void,
  ) => void
}

interface YoutubePlayer {
  pauseVideo: () => void
}

declare global {
  interface Window {
    onSpotifyIframeApiReady?: (api: SpotifyApi) => void
    onYouTubeIframeAPIReady?: () => void
    YT?: {
      Player: new (element: HTMLElement, options?: object) => YoutubePlayer
    }
  }
}

const props = defineProps<{ piece: PortfolioCard }>()
const open = ref(false)
const host = ref<HTMLElement | null>(null)
const store = usePlayerStore()
let spotify: SpotifyController | null = null
let youtube: YoutubePlayer | null = null

const spotifyUri = computed(() => {
  if (props.piece.kind !== 'spotify' || !props.piece.external_id) return ''
  const type = props.piece.external_url?.includes('/album/') ? 'album' : 'track'
  return `spotify:${type}:${props.piece.external_id}`
})

const youtubeSrc = computed(() => {
  if (!props.piece.external_id || props.piece.kind === 'spotify') return ''
  if (props.piece.kind !== 'youtube' && !props.piece.external_url?.includes('youtu')) return ''
  const start = props.piece.youtube_start_s ? `&start=${props.piece.youtube_start_s}` : ''
  return `https://www.youtube-nocookie.com/embed/${props.piece.external_id}?enablejsapi=1${start}`
})

function loadScript(src: string): Promise<void> {
  return new Promise((resolve) => {
    const existing = document.querySelector(`script[src="${src}"]`)
    if (existing) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.onload = () => resolve()
    document.head.appendChild(script)
  })
}

function loadSpotify(): Promise<SpotifyApi> {
  return new Promise((resolve) => {
    const previous = window.onSpotifyIframeApiReady
    window.onSpotifyIframeApiReady = (api) => {
      previous?.(api)
      resolve(api)
    }
    void loadScript('https://open.spotify.com/embed/iframe-api/v1')
  })
}

async function activate() {
  store.stopOthers(props.piece.slug)
  open.value = true
  await nextTick()
  if (spotifyUri.value && host.value) {
    const api = await loadSpotify()
    api.createController(
      host.value,
      { uri: spotifyUri.value, width: '100%', height: 152 },
      (controller) => {
        spotify = controller
        controller.play()
      },
    )
    return
  }
  if (youtubeSrc.value && host.value && window.YT?.Player) {
    youtube = new window.YT.Player(host.value)
  }
}

function pause() {
  spotify?.pause()
  youtube?.pauseVideo()
  open.value = false
}

const bus = useEventBus<string>('player:exclusive')
bus.on((id) => {
  if (id !== props.piece.slug) pause()
})

onMounted(() => {
  if (youtubeSrc.value) {
    const previous = window.onYouTubeIframeAPIReady
    window.onYouTubeIframeAPIReady = () => previous?.()
    void loadScript('https://www.youtube.com/iframe_api')
  }
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
    <div v-else-if="spotifyUri" ref="host" class="facade" />
    <div v-else-if="youtubeSrc" class="youtube-wrap">
      <iframe
        ref="host"
        :src="youtubeSrc"
        :title="piece.title"
        allow="autoplay; encrypted-media"
        allowfullscreen
      />
    </div>
  </div>
</template>
