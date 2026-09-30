export type SpotifyPlayback = {
  data: {
    isPaused: boolean
  }
}

export type SpotifyController = {
  play: () => void
  pause: () => void
  destroy: () => void
  addListener: (event: 'playback_update', callback: (event: SpotifyPlayback) => void) => void
}

type SpotifyApi = {
  createController: (
    element: HTMLElement,
    options: { uri: string; width: string; height: number },
    callback: (controller: SpotifyController) => void,
  ) => void
}

declare global {
  interface Window {
    onSpotifyIframeApiReady?: (api: SpotifyApi) => void
  }
}

let loading: Promise<SpotifyApi> | null = null

export function loadSpotifyEmbedApi(): Promise<SpotifyApi> {
  if (loading) return loading
  loading = new Promise((resolve, reject) => {
    window.onSpotifyIframeApiReady = (api) => {
      resolve(api)
    }
    const script = document.createElement('script')
    script.src = 'https://open.spotify.com/embed/iframe-api/v1'
    script.async = true
    script.onerror = () => {
      loading = null
      reject(new Error('No se pudo cargar el reproductor de Spotify.'))
    }
    document.head.appendChild(script)
  })
  return loading
}
