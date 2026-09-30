<script setup lang="ts">
import type { ServiceDetail } from '~/types/public'
import { faqJsonLd, serviceJsonLd } from '~/utils/jsonld'

const route = useRoute()
const slug = String(route.params.slug)
const { data, error } = await usePublic<ServiceDetail>(
  `/public/services/${slug}`,
  `service-${slug}`,
)
if (error.value || !data.value) {
  throw createError({ statusCode: 404, statusMessage: 'No encontramos ese servicio.' })
}
const service = data.value
const config = useRuntimeConfig()
usePageMeta({
  title: `${service.title} en CDMX`,
  description: service.short_description,
  path: `/servicios/${service.slug}`,
})
const scripts: { type: 'application/ld+json'; innerHTML: string }[] = [
  {
    type: 'application/ld+json',
    innerHTML: JSON.stringify(
      serviceJsonLd(
        service,
        `${config.public.siteUrl}/servicios/${service.slug}`,
        'Cherry Studios',
      ),
    ),
  },
]
if (service.faqs.length) {
  scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(faqJsonLd(service.faqs)) })
}
useHead({ script: scripts })
defineOgImage('OgService', { title: service.title, description: service.short_description })
</script>

<template>
  <main class="surface-cream">
    <article class="wrap page-hero prose">
      <p class="eyebrow">{{ service.number_label }}</p>
      <h1 class="h-lg">{{ service.title }}</h1>
      <p class="lede">{{ service.long_description }}</p>
      <section v-if="service.faqs.length">
        <h2>Preguntas</h2>
        <details v-for="faq in service.faqs" :key="faq.question">
          <summary>{{ faq.question }}</summary>
          <p>{{ faq.answer }}</p>
        </details>
      </section>
      <NuxtLink
        class="btn btn-dark"
        :to="`/?servicio=${service.slug}#contacto`"
        style="margin-top: 28px"
      >
        Cotizar este servicio
      </NuxtLink>
    </article>
  </main>
</template>
