<script setup lang="ts">
import type { ServiceCard, Site } from '~/types/public'

defineProps<{ site: Site; services: ServiceCard[] }>()
</script>

<template>
  <section id="contacto" class="surface-blush section-pad">
    <div class="wrap">
      <div class="reveal contact-intro">
        <p class="eyebrow">{{ site.contact.eyebrow }}</p>
        <h2 class="h-lg">{{ site.contact.title }}</h2>
      </div>
      <SiteContactForm :site="site" :services="services" />
    </div>
  </section>
</template>
