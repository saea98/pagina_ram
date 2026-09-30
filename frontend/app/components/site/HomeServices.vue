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
        <div
          v-for="service in services"
          :key="service.slug"
          class="svc-card reveal"
          :class="{ flipped: open === service.slug }"
        >
          <div class="svc-inner">
            <button
              type="button"
              class="svc-face svc-front"
              :aria-pressed="open === service.slug"
              :aria-label="service.title"
              :inert="open === service.slug"
              @click="open = open === service.slug ? null : service.slug"
            >
              <div>
                <div class="num">{{ service.number_label }}</div>
                <SiteServiceIcon :name="service.icon" />
                <h3>{{ service.title }}</h3>
              </div>
              <div class="tap">{{ site.services.hint }}</div>
            </button>
            <div class="svc-face svc-back" :inert="open !== service.slug">
              <h3>{{ service.title }}</h3>
              <p>{{ service.short_description }}</p>
              <NuxtLink class="svc-quote" :to="`/servicios/${service.slug}`"
                >Cotizar este servicio</NuxtLink
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
