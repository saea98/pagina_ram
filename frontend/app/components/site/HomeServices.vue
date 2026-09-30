<script setup lang="ts">
import type { ServiceCard, Site } from '~/types/public'

defineProps<{ site: Site; services: ServiceCard[] }>()
const open = ref<string | null>(null)
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
      <div class="svc-grid">
        <article
          v-for="service in services"
          :key="service.slug"
          class="svc-card"
          :class="{ flipped: open === service.slug }"
        >
          <button
            type="button"
            class="svc-face svc-front"
            :aria-pressed="open === service.slug"
            :aria-expanded="open === service.slug"
            @click="open = open === service.slug ? null : service.slug"
          >
            <div class="num">{{ service.number_label }}</div>
            <SiteServiceIcon :name="service.icon" />
            <h3>{{ service.title }}</h3>
            <p v-if="open === service.slug" class="svc-copy">{{ service.short_description }}</p>
            <span v-else class="tap">{{ site.services.hint }}</span>
          </button>
          <NuxtLink
            v-if="open === service.slug"
            class="svc-quote"
            :to="`/servicios/${service.slug}`"
            >Cotizar este servicio</NuxtLink
          >
        </article>
      </div>
    </div>
  </section>
</template>
