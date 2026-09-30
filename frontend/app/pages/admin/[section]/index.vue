<script setup lang="ts">
import { sections } from '~/admin/fields'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const key = computed(() => String(route.params.section))
const section = computed(() => sections[key.value])
const toast = useState('admin-toast', () => '')
if (!section.value)
  throw createError({ statusCode: 404, statusMessage: 'No encontramos esa sección.' })
</script>

<template>
  <AdminResourceList v-if="section" v-model:toast="toast" :section="section" :section-key="key" />
</template>
