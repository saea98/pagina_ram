---
name: nuxt-frontend
description: Convenciones del frontend Nuxt 4 + Vue 3 + TypeScript de Cherry Studios (estructura, fetch a la API, SSR/caché, reproductor global, A/B, formularios, tests). Úsalo al trabajar en cualquier archivo dentro de frontend/.
---

# Frontend Nuxt — convenciones

## Stack
Nuxt 4 · Vue 3.5 (`<script setup lang="ts">`) · TypeScript estricto · pnpm · Tailwind CSS v4 · Pinia · VueUse · Nuxt UI (solo admin) · `@nuxt/image` · `@nuxt/fonts` · `@nuxtjs/sitemap` + `nuxt-og-image` + `nuxt-schema-org` (o módulo `@nuxtjs/seo`) · `nuxt-security` · wavesurfer.js v7 · valibot (validación) · Vitest + `@nuxt/test-utils` · Playwright.

## Estructura (Nuxt 4 usa `app/`)
Ver `docs/sdd/02-arquitectura.md §3`. Reglas:
- Componentes de sitio público en `components/site/`, reproductor en `components/player/`, admin en `components/admin/`. Nombres en PascalCase inglés (`ServiceCard.vue`).
- Páginas en español para URLs públicas: `pages/servicios/[slug].vue`, `pages/portafolio/index.vue`, `pages/aviso-de-privacidad.vue`, `pages/links.vue`.
- Layouts: `default` (nav, footer, GlobalPlayer, WhatsApp), `links` (mínimo), `admin`.

## Acceso a la API
- Tipos **generados**: `pnpm gen:api` → `app/types/api.ts` desde `NUXT_API_INTERNAL_URL/api/v1/openapi.json`. Nunca escribas a mano tipos de respuesta.
- Composable único `useApi()` que resuelve base URL: en servidor `runtimeConfig.apiInternalUrl` (`http://api:8000`), en cliente `runtimeConfig.public.apiBase` (`/api/v1`).
- Páginas públicas: `const { data } = await useFetch('/public/home', { baseURL, key: 'home' })`. Maneja `error` con `showError({ statusCode: 404 })` en detalles.
- Admin: `$fetch` con `credentials: 'include'` y cabecera `X-CSRF-Token` leída de la cookie `csrf_token` (interceptor en `useAdminApi()`). En 401 intenta `/auth/refresh` una vez y si falla redirige a `/admin/login`.

## Render y caché (`nuxt.config.ts`)
```ts
routeRules: {
  '/': { swr: 60 },
  '/servicios/**': { swr: 60 },
  '/portafolio/**': { swr: 60 },
  '/equipo/**': { swr: 60 },
  '/links': { swr: 60 },
  '/aviso-de-privacidad': { swr: 3600 },
  '/admin/**': { ssr: false, robots: false },
}
```
Ruta Nitro `server/api/_revalidate.post.ts`: valida `X-Internal-Token` y borra las claves de caché de las rutas recibidas (`useStorage('cache')`).

## Reproductor global (RF-03)
- `stores/player.ts`: `current`, `queue`, `isPlaying`, `position`, `duration`, `source: 'own'|'spotify'|'youtube'|…`, acciones `play(item)`, `toggle()`, `seek()`, `stopOthers(sourceId)`.
- Un solo `HTMLAudioElement` creado en cliente (`onMounted` / `import.meta.client`), vive en `<GlobalPlayer>` del layout → no se destruye al navegar.
- El audio propio no muestra barra ni waveform. Escuchar y Pausar están en la tarjeta.
- Exclusividad: bus `useEventBus('player:exclusive')`. Spotify se controla con `postMessage` al iframe (`utm_source=iframe-api`): el script oficial de la IFrame API usa `eval` y la CSP de producción lo bloquea, así que Escuchar nunca llegaba a habilitarse. YouTube usa su IFrame API. Ambos escuchan el bus para pausar.
- `<EmbedFacade>`: muestra portada + botón; al clic monta el iframe (`youtube-nocookie.com`). Sin iframes en SSR.
- Media Session API: título/artista/portada en la pantalla de bloqueo del celular.

## A/B (RF-04)
- `<ABPlayer :before="…" :after="…">` con Web Audio: dos `MediaElementAudioSourceNode` → dos `GainNode` → destino. Ambos elementos reproducen sincronizados; el switch hace `gain.linearRampToValueAtTime` en 30 ms.
- Ganancia de igualación con `lufs` del backend: `10 ** ((target - lufs) / 20)`, `target = min(lufsA, lufsB)`.
- Teclado: `A`, `B`, espacio. `role="switch"` + `aria-checked`. Se integra con el store (pausa el GlobalPlayer al iniciar).
- Safari iOS: crear/reanudar `AudioContext` solo tras gesto del usuario.

## Formularios (RF-07)
- Esquemas valibot espejo de los Pydantic (mensajes en español).
- `useUtm()`: al cargar cualquier página lee `utm_*` y `document.referrer`, guarda en `sessionStorage` la primera vez (first‑touch de la sesión) con try/catch; el formulario los envía.
- Subida de maqueta con `XMLHttpRequest`/`$fetch` + `onUploadProgress` a `/public/leads/uploads`, luego `POST /public/leads` con el token.
- Honeypot `website` fuera de pantalla, `tabindex=-1`, `autocomplete=off`.
- Turnstile solo si `site.features.turnstile` es true (carga el script bajo demanda).
- Servicio preseleccionado desde query `?servicio=slug`.

## Estilo de código
- Composition API, `defineProps` tipado, `defineModel` para v-model, sin Options API.
- Sin `any`. Sin lógica de negocio en templates.
- Animaciones: composable `useReveal()` (IntersectionObserver) + clases del skill `cherry-brand-ui`.
- Accesibilidad: cada componente interactivo con test de teclado.

## Tests
- Unit (Vitest): stores, composables (`useUtm`, cálculo de ganancia A/B), componentes con lógica.
- E2E (Playwright, contra `docker compose`): portada carga, flip de tarjetas con teclado, envío de lead, reproductor persiste al navegar, A/B alterna, login admin + CRUD básico. Incluye `@axe-core/playwright`.

## Comandos
```
pnpm dev | pnpm build | pnpm lint | pnpm typecheck | pnpm test | pnpm test:e2e | pnpm gen:api
```
