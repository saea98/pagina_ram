<script setup lang="ts">
import type { ServiceCard, Site } from '~/types/public'

defineProps<{ site: Site; services: ServiceCard[] }>()
</script>

<template>
  <section id="contacto" class="surface-blush section-pad">
    <div class="wrap contact-grid">
      <div class="reveal">
        <p class="eyebrow">{{ site.contact.eyebrow }}</p>
        <h2 class="h-lg">{{ site.contact.title }}</h2>
        <SiteContactForm :site="site" :services="services" />
      </div>
      <aside class="direct-card reveal">
        <a class="direct-row" :href="`mailto:${site.contact.email}`">
          <span class="ic" aria-hidden="true">@</span>
          <span>
            <span class="lbl">Correo</span>
            <span class="val">{{ site.contact.email }}</span>
          </span>
        </a>
        <a
          v-if="site.social.instagram"
          class="direct-row"
          :href="site.social.instagram"
          target="_blank"
          rel="noopener"
        >
          <span class="ic" aria-hidden="true">IG</span>
          <span>
            <span class="lbl">Instagram</span>
            <span class="val">{{ site.social.instagram.replace(/\/$/, '').split('/').pop() }}</span>
          </span>
        </a>
      </aside>
    </div>
  </section>
</template>
