export const SPOTIFY_ORIGIN = 'https://open.spotify.com'

export function spotifyEmbedSrc(kind: 'track' | 'album', id: string) {
  return `${SPOTIFY_ORIGIN}/embed/${kind}/${id}?utm_source=iframe-api&theme=0`
}

export type SpotifyNote = { type: 'ready' } | { type: 'playback'; playing: boolean }

export function readSpotifyMessage(data: unknown): SpotifyNote | null {
  if (!data || typeof data !== 'object') return null
  const message = data as { type?: unknown; payload?: { isPaused?: unknown } }
  if (message.type === 'ready') return { type: 'ready' }
  if (message.type === 'playback_started') return { type: 'playback', playing: true }
  if (message.type !== 'playback_update' || typeof message.payload?.isPaused !== 'boolean')
    return null
  return { type: 'playback', playing: !message.payload.isPaused }
}

export function spotifyCommand(command: 'play' | 'pause' | 'ack') {
  if (command === 'ack') return { command: 'load_complete_ack' }
  return { command }
}

type SpotifyHandler = (event: MessageEvent) => void

const handlers = new Set<SpotifyHandler>()
let listening = false

export function listenSpotify(handler: SpotifyHandler) {
  if (!listening) {
    listening = true
    window.addEventListener('message', (event) => {
      handlers.forEach((fn) => fn(event))
    })
  }
  handlers.add(handler)
  return () => {
    handlers.delete(handler)
  }
}
