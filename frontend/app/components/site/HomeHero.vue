<script setup lang="ts">
import type { Site } from '~/types/public'
import { splitHeroTitle } from '~/utils/hero'
import { siteImage } from '~/utils/media'

const props = defineProps<{ site: Site }>()
const photo = ref<HTMLImageElement | null>(null)
const words = computed(() => splitHeroTitle(props.site.hero.title_html))
const image = computed(() => siteImage(props.site, props.site.hero.image_media_id))

function onScroll() {
  const element = photo.value
  if (!element) return
  if (window.scrollY < window.innerHeight * 1.2) {
    element.style.transform = `translateY(${window.scrollY * 0.18}px) scale(1.06)`
  }
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <section id="inicio" class="hero">
    <img
      v-if="image"
      ref="photo"
      class="hero-photo"
      :src="image.webp['1600'] || Object.values(image.webp)[0]"
      :srcset="
        Object.entries(image.webp)
          .map(([width, url]) => `${url} ${width}w`)
          .join(', ')
      "
      sizes="100vw"
      :alt="image.alt || ''"
      fetchpriority="high"
      :style="
        image.lqip ? { backgroundImage: `url(${image.lqip})`, backgroundSize: 'cover' } : undefined
      "
    />
    <div class="hero-veil" />
    <div class="wrap hero-inner">
      <p v-if="site.hero.quote" class="hero-quote">{{ site.hero.quote }}</p>
      <h1 class="hero-h1">
        <template v-for="(word, index) in words" :key="index">
          <br v-if="word.breakBefore" />
          <em v-if="word.em" class="word" :style="{ animationDelay: `${index * 70}ms` }"
            >{{ word.text }}
          </em>
          <span v-else class="word" :style="{ animationDelay: `${index * 70}ms` }"
            >{{ word.text }}
          </span>
        </template>
      </h1>
      <div class="hero-cta-row">
        <NuxtLink class="btn btn-solid" to="/#servicios">{{ site.hero.cta_primary_text }}</NuxtLink>
        <NuxtLink class="btn btn-ghost" to="/#contacto">{{
          site.hero.cta_secondary_text
        }}</NuxtLink>
      </div>
    </div>
    <div class="scroll-cue">
      <span>scroll</span>
      <span class="line" />
    </div>
  </section>
</template>
