<script setup lang="ts">
import { adminErrorMessage, adminFetch } from '~/composables/useAdminApi'

definePageMeta({ layout: 'admin' })
interface Account {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'superadmin'
  is_active: boolean
}
const toast = useState('admin-toast', () => '')
const error = ref('')
const accounts = ref(await adminFetch<Account[]>('/admin/users'))
const form = reactive({
  email: '',
  full_name: '',
  password: '',
  role: 'admin' as 'admin' | 'superadmin',
})

async function create() {
  error.value = ''
  try {
    const created = await adminFetch<Account>('/admin/users', { method: 'POST', body: form })
    accounts.value.push(created)
    toast.value = 'Cuenta creada'
  } catch (reason) {
    error.value = adminErrorMessage(reason)
  }
}

async function toggle(account: Account) {
  const updated = await adminFetch<Account>(`/admin/users/${account.id}`, {
    method: 'PATCH',
    body: { is_active: !account.is_active },
  })
  account.is_active = updated.is_active
}

async function reset(account: Account) {
  const password = prompt('Contraseña nueva (mínimo 8 caracteres)')
  if (!password) return
  await adminFetch(`/admin/users/${account.id}/password`, {
    method: 'POST',
    body: { new_password: password },
  })
  toast.value = 'Contraseña actualizada'
}
</script>

<template>
  <div>
    <h1>Usuarios</h1>
    <article v-for="account in accounts" :key="account.id" class="admin-card">
      <div>
        <strong>{{ account.full_name }}</strong>
        <span
          >{{ account.email }} · {{ account.role }} ·
          {{ account.is_active ? 'Activo' : 'Inactivo' }}</span
        >
      </div>
      <button class="admin-chip" type="button" @click="toggle(account)">
        {{ account.is_active ? 'Desactivar' : 'Activar' }}
      </button>
      <button class="admin-chip" type="button" @click="reset(account)">Nueva contraseña</button>
    </article>
    <h2>Nueva cuenta</h2>
    <form @submit.prevent="create">
      <label class="admin-field">Nombre <input v-model="form.full_name" required /></label>
      <label class="admin-field">Correo <input v-model="form.email" type="email" required /></label>
      <label class="admin-field"
        >Contraseña <input v-model="form.password" type="password" minlength="8" required
      /></label>
      <label class="admin-field">
        Rol
        <select v-model="form.role">
          <option value="admin">Admin</option>
          <option value="superadmin">Superadmin</option>
        </select>
      </label>
      <p v-if="error" class="admin-error">{{ error }}</p>
      <button class="admin-save" type="submit">Crear</button>
    </form>
  </div>
</template>
