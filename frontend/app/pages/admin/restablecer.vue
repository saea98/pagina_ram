<script setup lang="ts">
import { adminErrorMessage, adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: false })
const route = useRoute()
const password = ref('')
const error = ref('')
const done = ref(false)

async function submit() {
  error.value = ''
  try {
    await adminFetch('/auth/password/reset', {
      method: 'POST',
      body: { token: String(route.query.token ?? ''), new_password: password.value },
    })
    done.value = true
  } catch (reason) {
    error.value = adminErrorMessage(reason)
  }
}
</script>

<template>
  <main class="admin-login">
    <h1>Nueva contraseña</h1>
    <p v-if="done">Listo. Ya puedes entrar.</p>
    <form v-else @submit.prevent="submit">
      <label>
        Contraseña nueva
        <input
          v-model="password"
          type="password"
          minlength="8"
          autocomplete="new-password"
          required
        />
      </label>
      <p v-if="error" class="admin-error">{{ error }}</p>
      <button class="admin-save" type="submit" style="position: static">Guardar</button>
    </form>
    <NuxtLink to="/admin/login">Ir al acceso</NuxtLink>
  </main>
</template>
