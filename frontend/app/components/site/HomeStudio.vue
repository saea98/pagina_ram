<script setup lang="ts">
import type { Site } from '~/types/public'

defineProps<{ site: Site }>()
</script>

<template>
  <section id="estudio" class="surface-cream section-pad">
    <div class="wrap split">
      <div class="reveal">
        <p class="eyebrow">{{ site.studio.eyebrow }}</p>
        <h2 class="h-lg">{{ site.studio.title }}</h2>
        <p class="lede">{{ site.studio.body }}</p>
      </div>
      <div class="frame reveal">
        <img
          src="/images/estudio-equipo.jpg"
          width="1024"
          height="819"
          alt="Chemita y Ramzy en Cherry Studios, de pie con los brazos cruzados frente a los paneles rojos."
        />
        <span v-if="site.studio.image_caption" class="frame-tag">{{
          site.studio.image_caption
        }}</span>
      </div>
    </div>
  </section>
</template>
