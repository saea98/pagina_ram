<script setup lang="ts">
definePageMeta({ path: '/_styleguide' })
const config = useRuntimeConfig()
if (config.public.environment === 'production') {
  throw createError({ statusCode: 404, statusMessage: 'No encontrada.' })
}
usePageMeta({
  title: 'Styleguide',
  description: 'Componentes base de Cherry Studios.',
  path: '/_styleguide',
  noindex: true,
})
</script>

<template>
  <main class="surface-paper">
    <div class="wrap page-hero">
      <p class="eyebrow">Sistema</p>
      <h1 class="h-lg">Styleguide</h1>
      <div class="hero-cta-row">
        <a class="btn btn-solid" href="#tokens">Sólido</a>
        <a
          class="btn btn-ghost"
          href="#tokens"
          style="color: var(--maroon); border-color: var(--maroon)"
          >Fantasma</a
        >
        <button class="btn btn-dark" type="button">Oscuro</button>
      </div>
      <div class="founders" style="margin-top: 40px">
        <article class="founder">
          <div>
            <div class="role">Rol</div>
            <h3>Tarjeta crema</h3>
            <p>Texto de ejemplo sobre paper.</p>
          </div>
        </article>
      </div>
    </div>
  </main>
</template>
