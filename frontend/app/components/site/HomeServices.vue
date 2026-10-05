<script setup lang="ts">
import type { ServiceCard, Site } from '~/types/public'

defineProps<{ site: Site; services: ServiceCard[] }>()
const open = ref<Record<string, boolean>>({})
const grid = ref<HTMLElement | null>(null)
const activeSlide = ref(0)

function toggle(slug: string) {
  open.value = { ...open.value, [slug]: !open.value[slug] }
}

function syncSlide() {
  const el = grid.value
  if (!el) return
  const edge = el.getBoundingClientRect().left + 24
  const cards = [...el.querySelectorAll<HTMLElement>('.svc-card')]
  let best = 0
  let bestDist = Infinity
  cards.forEach((card, index) => {
    const dist = Math.abs(card.getBoundingClientRect().left - edge)
    if (dist < bestDist) {
      best = index
      bestDist = dist
    }
  })
  activeSlide.value = best
}

function goTo(index: number) {
  const el = grid.value
  const card = el?.querySelectorAll<HTMLElement>('.svc-card')[index]
  if (!el || !card) return
  el.scrollTo({ left: card.offsetLeft - 20, behavior: 'smooth' })
}
</script>

<template>
  <section id="servicios" class="surface-cream section-pad">
    <div class="wrap">
      <div class="svc-head reveal">
        <p class="eyebrow">{{ site.services.eyebrow }}</p>
        <h2 class="h-lg">{{ site.services.title }}</h2>
        <p class="lede">{{ site.services.lede }}</p>
        <p v-if="site.services.hint" class="svc-hint">{{ site.services.hint }}</p>
      </div>
      <div ref="grid" class="svc-grid" @scroll.passive="syncSlide">
        <button
          v-for="service in services"
          :key="service.slug"
          type="button"
          class="svc-card"
          :aria-pressed="Boolean(open[service.slug])"
          @click="toggle(service.slug)"
        >
          <div class="svc-inner">
            <div class="svc-face svc-front">
              <span class="num">{{ service.number_label }}</span>
              <SiteServiceIcon :name="service.icon" />
              <h3>{{ service.title }}</h3>
              <span class="tap">Ver detalle →</span>
            </div>
            <div class="svc-face svc-back">
              <h3>{{ service.title }}</h3>
              <p>{{ service.short_description }}</p>
            </div>
          </div>
        </button>
      </div>
      <div class="svc-dots">
        <button
          v-for="(service, index) in services"
          :key="service.slug"
          type="button"
          :class="{ on: activeSlide === index }"
          :aria-label="service.title"
          @click="goTo(index)"
        />
      </div>
      <div class="svc-more reveal">
        <NuxtLink class="btn svc-more-btn" to="/#contacto">Cuéntanos más</NuxtLink>
      </div>
    </div>
  </section>
</template>
