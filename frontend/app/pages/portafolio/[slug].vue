<script setup lang="ts">
import type { PortfolioDetail } from '~/types/public'
import { recordingJsonLd } from '~/utils/jsonld'

const route = useRoute()
const slug = String(route.params.slug)
const { data, error } = await usePublic<PortfolioDetail>(
  `/public/portfolio/${slug}`,
  `piece-${slug}`,
)
if (error.value || !data.value) {
  throw createError({ statusCode: 404, statusMessage: 'No encontramos esa pieza.' })
}
const piece = data.value
const config = useRuntimeConfig()
const store = usePlayerStore()
usePageMeta({
  title: `${piece.title} — ${piece.artist_name}`,
  description: piece.credits_text || piece.description || piece.title,
  path: `/portafolio/${piece.slug}`,
  type: 'music.song',
})
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(
        recordingJsonLd(piece, `${config.public.siteUrl}/portafolio/${piece.slug}`),
      ),
    },
  ],
})
defineOgImage('OgPortfolio', { title: piece.title, artist: piece.artist_name })

function listen() {
  if (!piece.audio) return
  store.play({
    id: piece.slug,
    title: piece.title,
    artist: piece.artist_name,
    coverUrl: piece.cover?.webp['480'] ?? null,
    audioUrl: piece.audio.m4a_url || piece.audio.mp3_url || '',
    peaksUrl: piece.audio.peaks_url,
    duration: piece.audio.duration_s,
    lufs: piece.audio.lufs,
  })
}
</script>

<template>
  <main class="surface-maroon">
    <article class="wrap page-hero">
      <p class="eyebrow">{{ piece.artist_name }}</p>
      <h1 class="h-lg">{{ piece.title }}</h1>
      <p v-if="piece.description" class="lede">{{ piece.description }}</p>
      <p v-if="piece.credits_text">{{ piece.credits_text }}</p>
      <div class="listen-row" style="margin-top: 24px">
        <button v-if="piece.audio" class="btn btn-solid" type="button" @click="listen">
          Escuchar
        </button>
        <PlayerABPlayer
          v-if="piece.audio && piece.audio_before"
          :title="piece.title"
          :artist="piece.artist_name"
          :before-url="piece.audio_before.m4a_url || piece.audio_before.mp3_url || ''"
          :after-url="piece.audio.m4a_url || piece.audio.mp3_url || ''"
          :before-lufs="piece.audio_before.lufs"
          :after-lufs="piece.audio.lufs"
        />
        <PlayerEmbedFacade v-else-if="!piece.audio" :piece="piece" />
      </div>
    </article>
  </main>
</template>
