<script setup lang="ts">
import type { Site } from '~/types/public'
import { siteImage } from '~/utils/media'

const props = defineProps<{ site: Site }>()
const image = computed(() => siteImage(props.site, props.site.studio.image_media_id))
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
        <SiteCherryPicture :image="image" />
        <span v-if="site.studio.image_caption" class="frame-tag">{{
          site.studio.image_caption
        }}</span>
      </div>
    </div>
  </section>
</template>
