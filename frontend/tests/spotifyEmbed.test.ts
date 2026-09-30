import { describe, expect, it } from 'vitest'
import { readSpotifyMessage, spotifyCommand, spotifyEmbedSrc } from '../app/utils/spotifyEmbed'

describe('spotify embed bridge', () => {
  it('asks the embed to enable the parent commands', () => {
    expect(spotifyEmbedSrc('track', 'abc')).toBe(
      'https://open.spotify.com/embed/track/abc?utm_source=iframe-api&theme=0',
    )
  })

  it('reads ready and playback notes from the embed', () => {
    expect(readSpotifyMessage({ type: 'ready' })).toEqual({ type: 'ready' })
    expect(readSpotifyMessage({ type: 'playback_update', payload: { isPaused: false } })).toEqual({
      type: 'playback',
      playing: true,
    })
    expect(readSpotifyMessage({ type: 'playback_started' })).toEqual({
      type: 'playback',
      playing: true,
    })
    expect(readSpotifyMessage({ type: 'other' })).toBeNull()
  })

  it('sends the commands the embed listens for', () => {
    expect(spotifyCommand('play')).toEqual({ command: 'play' })
    expect(spotifyCommand('pause')).toEqual({ command: 'pause' })
    expect(spotifyCommand('ack')).toEqual({ command: 'load_complete_ack' })
  })
})
