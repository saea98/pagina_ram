<script setup lang="ts">
import type { TeamDetail } from '~/types/public'

const route = useRoute()
const slug = String(route.params.slug)
const { data, error } = await usePublic<TeamDetail>(`/public/team/${slug}`, `team-${slug}`)
if (error.value || !data.value) {
  throw createError({ statusCode: 404, statusMessage: 'No encontramos a esa persona.' })
}
const member = data.value
const nickname = member.nickname ? ` “${member.nickname}”` : ''
usePageMeta({
  title: `${member.full_name}${nickname}`,
  description: member.bio_short,
  path: `/equipo/${member.slug}`,
})
defineOgImage('OgDefault', { title: member.full_name, description: member.role_label })
</script>

<template>
  <main class="surface-blush">
    <article class="wrap page-hero">
      <SiteCherryPicture :image="member.photo" />
      <p class="eyebrow">{{ member.role_label }}</p>
      <h1 class="h-lg">{{ member.full_name }}</h1>
      <p class="lede">{{ member.bio_long }}</p>
      <ul v-if="member.credits.length">
        <li v-for="credit in member.credits" :key="credit.portfolio_slug">
          <NuxtLink :to="`/portafolio/${credit.portfolio_slug}`">{{
            credit.portfolio_title
          }}</NuxtLink>
          · {{ credit.role_label }}
        </li>
      </ul>
    </article>
  </main>
</template>
