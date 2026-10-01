<script setup lang="ts">
import type { ServiceCard, Site } from '~/types/public'

defineProps<{ site: Site; services: ServiceCard[] }>()
const open = ref<Record<string, boolean>>({})

function toggle(slug: string) {
  open.value = { ...open.value, [slug]: !open.value[slug] }
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
      <div class="svc-grid">
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
      <div class="svc-more reveal">
        <NuxtLink class="btn svc-more-btn" to="/#contacto">Cuéntanos más</NuxtLink>
        <NuxtLink class="svc-more-link" to="/nosotros#equipo"
          >¿Quieres saber más de nosotros?</NuxtLink
        >
      </div>
    </div>
  </section>
</template>
