<script setup lang="ts">
import type { PortfolioCard, Site } from '~/types/public'

defineProps<{ site: Site; portfolio: PortfolioCard[] }>()
const store = usePlayerStore()

function listen(piece: PortfolioCard) {
  if (!piece.audio) return
  if (store.current?.id === piece.slug && store.isPlaying) {
    store.toggle()
    return
  }
  store.play({
    id: piece.slug,
    title: piece.title,
    artist: piece.artist_name,
    coverUrl: piece.cover ? (piece.cover.webp['480'] ?? null) : null,
    audioUrl: piece.audio.m4a_url || piece.audio.mp3_url || '',
    peaksUrl: piece.audio.peaks_url,
    duration: piece.audio.duration_s,
    lufs: piece.audio.lufs,
  })
}
</script>

<template>
  <section id="portafolio" class="surface-maroon section-pad">
    <div class="wrap">
      <div class="reveal">
        <p class="eyebrow">{{ site.portfolio.eyebrow }}</p>
        <h2 class="h-lg">{{ site.portfolio.title }}</h2>
      </div>
      <div class="embeds">
        <template v-for="piece in portfolio" :key="piece.slug">
          <div v-if="piece.audio" class="embed-card">
            <div class="embed-label">
              <span class="embed-title">{{ piece.title }}</span>
              <span class="embed-artist">{{ piece.artist_name }}</span>
            </div>
            <div class="listen-row">
              <button class="btn btn-solid" type="button" @click="listen(piece)">
                {{ store.current?.id === piece.slug && store.isPlaying ? 'Pausar' : 'Escuchar' }}
              </button>
              <a
                v-if="piece.external_url"
                class="btn btn-ghost"
                :href="piece.external_url"
                target="_blank"
                rel="noopener"
              >
                Ver en YouTube
              </a>
            </div>
          </div>
          <PlayerEmbedFacade v-else :piece="piece" />
        </template>
      </div>
      <p v-if="site.portfolio.note" class="portfolio-note">{{ site.portfolio.note }}</p>
      <NuxtLink class="btn btn-ghost" to="/portafolio" style="margin-top: 22px">Ver todo</NuxtLink>
    </div>
  </section>
</template>
