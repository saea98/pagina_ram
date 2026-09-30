<script setup lang="ts">
import type { PortfolioCard } from '~/types/public'

defineProps<{ items: PortfolioCard[] }>()

function url(audio: PortfolioCard['audio']) {
  return audio?.m4a_url || audio?.mp3_url || ''
}
</script>

<template>
  <section v-if="items.length" id="comparar" class="surface-paper section-pad">
    <div class="wrap">
      <div class="reveal">
        <p class="eyebrow">Escucha</p>
        <h2 class="h-lg">Escucha la diferencia</h2>
      </div>
      <div class="embeds">
        <PlayerABPlayer
          v-for="piece in items"
          :key="piece.slug"
          :title="piece.title"
          :artist="piece.artist_name"
          :before-url="url(piece.audio_before)"
          :after-url="url(piece.audio)"
          :before-lufs="piece.audio_before?.lufs ?? null"
          :after-lufs="piece.audio?.lufs ?? null"
        />
      </div>
    </div>
  </section>
</template>
