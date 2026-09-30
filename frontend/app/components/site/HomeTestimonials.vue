<script setup lang="ts">
import type { Testimonial } from '~/types/public'

defineProps<{ items: Testimonial[] }>()
</script>

<template>
  <section v-if="items.length" id="testimonios" class="surface-paper section-pad">
    <div class="wrap">
      <article v-for="item in items" :key="item.author_name + item.quote" class="reveal">
        <p class="lede">{{ item.quote }}</p>
        <p>{{ item.author_name }} · {{ item.author_role }}</p>
      </article>
    </div>
  </section>
</template>
