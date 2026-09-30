<script setup lang="ts">
import type { ImageAsset } from '~/types/public'
import { largestUrl, toSrcset } from '~/utils/media'

const props = defineProps<{
  image: ImageAsset | null
  eager?: boolean
  className?: string
}>()

const src = computed(() => largestUrl(props.image?.webp) || largestUrl(props.image?.avif))
const webp = computed(() => toSrcset(props.image?.webp))
const avif = computed(() => toSrcset(props.image?.avif))
</script>

<template>
  <picture v-if="image && src">
    <source v-if="avif" type="image/avif" :srcset="avif" sizes="(min-width: 880px) 50vw, 100vw" />
    <source v-if="webp" type="image/webp" :srcset="webp" sizes="(min-width: 880px) 50vw, 100vw" />
    <img
      :src="src"
      :alt="image.alt || ''"
      :width="image.width || undefined"
      :height="image.height || undefined"
      :loading="eager ? 'eager' : 'lazy'"
      :fetchpriority="eager ? 'high' : 'auto'"
      :style="
        image.lqip ? { backgroundImage: `url(${image.lqip})`, backgroundSize: 'cover' } : undefined
      "
      :class="className"
    />
  </picture>
</template>
