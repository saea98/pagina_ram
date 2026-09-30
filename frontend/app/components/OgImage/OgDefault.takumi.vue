<script setup lang="ts">
const { title = 'Cherry Studios', description = '' } = defineProps<{
  title?: string
  description?: string
}>()
</script>

<template>
  <div class="flex h-full w-full flex-col justify-end bg-[#3D0D11] p-16 text-[#FFF4EB]">
    <div class="h-12 w-12 rounded-full bg-[#9E1613]" />
    <div class="mt-6 text-7xl leading-none">{{ title }}</div>
    <div class="mt-4 text-3xl text-[#FFBEC5]">{{ description }}</div>
  </div>
</template>
