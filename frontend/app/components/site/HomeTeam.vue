<script setup lang="ts">
import type { Site, TeamCard } from '~/types/public'

defineProps<{ site: Site; team: TeamCard[] }>()
</script>

<template>
  <section id="equipo" class="surface-blush section-pad">
    <div class="wrap">
      <div class="team-head reveal">
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
          <span v-if="member.nickname === 'Chemita'" class="founder-avatar">
            <img
              class="founder-photo founder-photo-chemita"
              src="/images/chemita.jpg"
              width="819"
              height="1024"
              alt="Retrato de Alejandro Vega, “Chemita”"
            />
          </span>
          <span v-else-if="member.nickname === 'Ramzy'" class="founder-avatar">
            <img
              class="founder-photo founder-photo-ramzy"
              src="/images/ramzy.jpg"
              width="818"
              height="1024"
              alt="Retrato de Ramsés Jiménez Acosta, “Ramzy”"
            />
          </span>
          <SiteCherryPicture v-else :image="member.photo" class-name="founder-photo" />
          <div>
            <h3>
              {{ member.full_name
              }}<template v-if="member.nickname"> — “{{ member.nickname }}”</template>
            </h3>
            <p class="role">{{ member.role_label }}</p>
            <p>{{ member.bio_short }}</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>
