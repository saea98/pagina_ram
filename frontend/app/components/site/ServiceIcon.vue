<script setup lang="ts">
const props = defineProps<{ name: string }>()

const paths: Record<string, string> = {
  composicion: '<path d="M14 27a4 4 0 1 1-4-4V9l16-3v17"/><path d="M26 23a4 4 0 1 1-4-4"/>',
  grabacion:
    '<rect x="15" y="6" width="10" height="17" rx="5"/><path d="M10 19a10 10 0 0 0 20 0"/><line x1="20" y1="29" x2="20" y2="35"/><line x1="14" y1="35" x2="26" y2="35"/>',
  mezcla:
    '<line x1="10" y1="8" x2="10" y2="32"/><circle cx="10" cy="16" r="3"/><line x1="20" y1="8" x2="20" y2="32"/><circle cx="20" cy="24" r="3"/><line x1="30" y1="8" x2="30" y2="32"/><circle cx="30" cy="12" r="3"/>',
  master:
    '<circle cx="20" cy="20" r="13"/><circle cx="20" cy="20" r="5"/><circle cx="20" cy="20" r="1.4" fill="currentColor" stroke="none"/>',
  producciones:
    '<circle cx="7" cy="30" r="3"/><path d="M10 28l7-9 7 5 9-14"/><circle cx="33" cy="10" r="3" fill="currentColor" stroke="none"/>',
  'beat-making':
    '<rect x="7" y="7" width="8" height="8" rx="1.5"/><rect x="16" y="7" width="8" height="8" rx="1.5"/><rect x="25" y="7" width="8" height="8" rx="1.5"/><rect x="7" y="16" width="8" height="8" rx="1.5"/><rect x="16" y="16" width="8" height="8" rx="1.5" fill="currentColor"/><rect x="25" y="16" width="8" height="8" rx="1.5"/>',
  beatmaking:
    '<rect x="7" y="7" width="8" height="8" rx="1.5"/><rect x="16" y="7" width="8" height="8" rx="1.5"/><rect x="25" y="7" width="8" height="8" rx="1.5"/><rect x="7" y="16" width="8" height="8" rx="1.5"/><rect x="16" y="16" width="8" height="8" rx="1.5" fill="currentColor"/><rect x="25" y="16" width="8" height="8" rx="1.5"/>',
  podcast:
    '<rect x="14" y="5" width="12" height="18" rx="6"/><path d="M9 18a11 11 0 0 0 22 0"/><line x1="20" y1="29" x2="20" y2="34"/><path d="M6 12c0 3 1.4 5.4 3 7M34 12c0 3-1.4 5.4-3 7"/>',
  'post-audiovisual':
    '<rect x="6" y="14" width="28" height="19" rx="2"/><path d="M6 14l4-8h6l-4 8zM17 14l4-8h6l-4 8zM28 14l3-8h3v8"/>',
}

const markup = computed(() => paths[props.name] ?? paths.composicion)
</script>

<template>
  <svg
    class="ico"
    viewBox="0 0 40 40"
    fill="none"
    stroke="currentColor"
    stroke-width="1.6"
    aria-hidden="true"
    v-html="markup"
  />
</template>
