<script setup lang="ts">
import type { Site, TeamCard } from '~/types/public'

defineProps<{ site: Site; team: TeamCard[] }>()
</script>

<template>
  <section id="equipo" class="surface-blush section-pad">
    <div class="wrap">
      <div class="svc-head reveal">
        <p class="eyebrow">{{ site.team.eyebrow }}</p>
        <h2 class="h-lg">{{ site.team.title }}</h2>
      </div>
      <div class="founders">
        <NuxtLink
          v-for="member in team"
          :key="member.slug"
          class="founder reveal"
          :to="`/equipo/${member.slug}`"
        >
          <SiteCherryPicture :image="member.photo" class-name="founder-photo" />
          <div>
            <div class="role">{{ member.role_label }}</div>
            <h3>{{ member.full_name }}</h3>
            <p>{{ member.bio_short }}</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>
