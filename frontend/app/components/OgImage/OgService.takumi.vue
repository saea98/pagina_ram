<script setup lang="ts">
const { title = 'Servicio', description = '' } = defineProps<{
  title?: string
  description?: string
}>()
</script>

<template>
  <div class="flex h-full w-full flex-col justify-end bg-[#3D0D11] p-16 text-[#FFF4EB]">
    <div class="text-2xl tracking-widest text-[#FFBEC5]">SERVICIO</div>
    <div class="mt-4 text-7xl leading-none">{{ title }}</div>
    <div class="mt-4 text-3xl">{{ description }}</div>
  </div>
</template>
