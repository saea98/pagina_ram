<script setup lang="ts">
const { title = 'Pieza', artist = '' } = defineProps<{
  title?: string
  artist?: string
}>()
</script>

<template>
  <div class="flex h-full w-full flex-col justify-end bg-[#3D0D11] p-16 text-[#FFF4EB]">
    <div class="text-7xl leading-none">{{ title }}</div>
    <div class="mt-4 text-4xl text-[#FFBEC5]">{{ artist }}</div>
  </div>
</template>
