<script setup lang="ts">
import { adminErrorMessage, adminFetch, useAdminSession } from '~/composables/useAdminApi'

definePageMeta({ layout: false })
const email = ref('')
const password = ref('')
const error = ref('')
const { user } = useAdminSession()

async function submit() {
  error.value = ''
  try {
    user.value = await adminFetch('/auth/login', {
      method: 'POST',
      body: { email: email.value, password: password.value },
    })
    await navigateTo('/admin')
  } catch (reason) {
    error.value = adminErrorMessage(reason)
  }
}
</script>

<template>
  <main class="admin-login">
    <h1>Entra al panel</h1>
    <form @submit.prevent="submit">
      <label>
        Correo
        <input v-model="email" type="email" autocomplete="username" required />
      </label>
      <label>
        Contraseña
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>
      <p v-if="error" class="admin-error">{{ error }}</p>
      <button class="admin-save" type="submit" style="position: static">Entrar</button>
      <NuxtLink to="/admin/recuperar">Olvidé mi contraseña</NuxtLink>
    </form>
  </main>
</template>
