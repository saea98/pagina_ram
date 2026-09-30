// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'
import prettier from 'eslint-config-prettier'

export default withNuxt({ ignores: ['.pnpm-store/**'] }, prettier, {
  files: ['app/components/site/ServiceIcon.vue', 'app/pages/aviso-de-privacidad.vue'],
  rules: { 'vue/no-v-html': 'off' },
})
