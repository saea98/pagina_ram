<script setup lang="ts">
import { adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: false })
const email = ref('')
const sent = ref(false)

async function submit() {
  await adminFetch('/auth/password/forgot', { method: 'POST', body: { email: email.value } })
  sent.value = true
}
</script>

<template>
  <main class="admin-login">
    <h1>Recuperar acceso</h1>
    <p v-if="sent">Si el correo existe, te enviamos un enlace para elegir otra contraseña.</p>
    <form v-else @submit.prevent="submit">
      <label>
        Correo
        <input v-model="email" type="email" required />
      </label>
      <button class="admin-save" type="submit" style="position: static">Enviar enlace</button>
    </form>
  </main>
</template>
