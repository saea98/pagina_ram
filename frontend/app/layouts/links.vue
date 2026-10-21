<template>
  <div class="links-shell">
    <slot />
  </div>
</template>

<style scoped>
.links-shell {
  min-height: 100svh;
  background:
    radial-gradient(1100px 620px at 50% -12%, rgba(126, 15, 13, 0.55), transparent 60%),
    linear-gradient(180deg, var(--maroon) 0%, var(--maroon) 68%, var(--ink) 100%);
  color: var(--cream);
  padding: 56px max(16px, env(safe-area-inset-right)) 48px max(16px, env(safe-area-inset-left));
}
</style>
