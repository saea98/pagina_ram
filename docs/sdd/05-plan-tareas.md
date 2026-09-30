# 05 · Plan de tareas (Fase 1)

> Orden de ejecución para el agente. **Una tarea = un PR/commit coherente.** Marca `[x]` al terminar (cumpliendo la DoD de `00-constitucion.md`).
> Formato: `T-xx · título` — *RF relacionados* — criterios de salida.

## Hito 0 · Cimientos

- [x] **T-01 · Scaffold del monorepo** — `frontend/` (Nuxt 4 + TS + pnpm), `backend/` (FastAPI + uv), `infra/`. Linters: ruff, mypy, eslint (config Nuxt), prettier, vue-tsc. `pre-commit` con hooks. *Salida:* `pnpm lint`, `uv run ruff check`, `uv run mypy` corren limpios.
- [ ] **T-02 · Docker Compose dev** — servicios `caddy`, `web`, `api`, `worker`, `db`; hot‑reload en `web` y `api`; `.env.example`. *Salida:* `docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up` sirve `https://localhost` (Caddy interno) con página “hola” y `/api/health` = 200.
- [ ] **T-03 · Backend base** — config con `pydantic-settings`, sesión async SQLAlchemy, Alembic, logging JSON, manejo de errores con formato de `04-api.md`, `/api/health`, `/api/ready`. Tests con `pytest` + BD de prueba en contenedor. *Salida:* `pytest` verde en CI.
- [ ] **T-04 · CI GitHub Actions** — jobs: lint+test backend, lint+typecheck+test frontend, build de imágenes. *Salida:* PR muestra checks verdes.

## Hito 1 · Datos y API pública

- [x] **T-05 · Modelos + migración inicial** — todas las tablas Fase 1 de `03-modelo-datos.md`. *Salida:* `alembic upgrade head` limpio; test que verifica que el modelo coincide con la migración (`alembic check`).
- [x] **T-06 · Storage + MediaAsset + worker** — `StorageBackend` local, subida streaming, validación magic bytes, cola `jobs` con `SKIP LOCKED`, procesamiento imagen (WebP/AVIF/LQIP) y audio (m4a/mp3, LUFS, peaks). Imagen Docker del backend incluye `ffmpeg`. *RF-22.* *Salida:* test sube WAV de 5 s → queda `ready` con LUFS y peaks.
- [x] **T-07 · Seed desde el template** — *RF-01..RF-11.* Copia imágenes/audio de `cherry-studios-site/` vía pipeline de medios. *Salida:* `python -m app.seed` idempotente.
- [x] **T-08 · Endpoints públicos de lectura** — `/site`, `/home`, `/services`, `/team`, `/portfolio`, `/testimonials`, `/faqs`, `/links`, `/legal/privacy` con caché/ETag. *Salida:* tests por endpoint; OpenAPI publicado.
- [x] **T-09 · Leads público** — `POST /leads`, `/leads/uploads`, honeypot, rate limit (`slowapi`), Turnstile opcional, `ip_hash`, correo de notificación y acuse vía job. *RF-07.* *Salida:* tests de validación, honeypot, rate limit y email (SMTP falso tipo `aiosmtpd`/Mailpit en dev).

## Hito 2 · Sitio público

- [x] **T-10 · Tokens y base visual** — portar `:root` del template a `assets/css/tokens.css`, `@theme` Tailwind, fuentes autoalojadas, utilidades `.wrap`, `.eyebrow`, `.btn-*`, superficies. Ver skill `cherry-brand-ui`. *Salida:* página `/_styleguide` (solo dev) con todos los componentes base.
- [x] **T-11 · Layout y navegación** — header fijo con blur, scrollspy, menú móvil, riel de progreso con cereza, footer, pastilla de privacidad, splash (1 vez por sesión). *RF-01.*
- [x] **T-12 · Secciones de la portada** — Hero (palabras animadas, parallax), Estudio, Equipo, Servicios (flip accesible), Portafolio destacado, Testimonios, Contacto; todo desde `/public/home`. *RF-01, 02, 05, 06.* *Salida:* comparación visual lado a lado con el template ≥ 95 % fiel.
- [x] **T-13 · Formulario de contacto** — validación cliente (zod/valibot), subida de maqueta con progreso, captura UTM (`useUtm`), consentimiento, estados de envío, WhatsApp flotante con mensaje contextual. *RF-07.* *Salida:* e2e Playwright envía lead y aparece en BD.
- [x] **T-14 · Reproductor global persistente** — store Pinia, `<GlobalPlayer>` con wavesurfer (peaks precalculados), exclusividad entre fuentes, fachadas para Spotify/YouTube/SoundCloud (`youtube-nocookie`). *RF-03.* *Salida:* e2e: reproducir, navegar a `/portafolio`, el audio sigue.
- [x] **T-15 · Comparador A/B** — `<ABPlayer>` Web Audio, cross‑fade, igualación LUFS, teclas A/B, accesible. Sección “Escucha la diferencia”. *RF-04.*
- [x] **T-16 · Páginas internas** — `/servicios/[slug]`, `/portafolio` (filtros), `/portafolio/[slug]`, `/equipo/[slug]`, `/aviso-de-privacidad`, `/links`, 404. *RF-02, 03, 05, 08, 10, 12.*
- [x] **T-17 · SEO** — `useSeoMeta` por página, JSON‑LD, sitemap, robots, canónicas, OG image dinámica (`nuxt-og-image` o ruta Nitro con Satori). *RF-09.* *Salida:* validador de datos estructurados sin errores; vista previa correcta en WhatsApp/Instagram (probar con opengraph.xyz).

## Hito 3 · Admin

- [ ] **T-18 · Auth backend + frontend** — login, refresh, logout, forgot/reset, bloqueo, CSRF, middleware de ruta `/admin/**`. *RF-20.*
- [ ] **T-19 · CRUD genérico admin** — patrón reutilizable (lista + form + reorder drag&drop + publicar) aplicado a servicios, equipo, portafolio, testimonios, FAQ, links. Selector de medios con subida y polling. *RF-22.* Ver skill `admin-cms`.
- [ ] **T-20 · Ajustes del sitio** — formulario por secciones de `SiteSettingsSchema`, editor enriquecido (TipTap) para aviso de privacidad. Revalidación de caché al guardar. *RF-23.*
- [ ] **T-21 · Bandeja de leads** — lista con filtros, detalle, cambio de estado, notas, reproducir/descargar maqueta, CSV, borrado ARCO. *RF-24.*
- [ ] **T-22 · Dashboard** — tarjetas y gráficas simples (leads por estado/fuente, clics links, reproducciones). *RF-21.*
- [ ] **T-23 · Usuarios (superadmin)** — *RF-25.*
- [ ] **T-24 · Vista previa de borradores** — token de preview que permite ver contenido no publicado en el sitio público.

## Hito 4 · Producción

- [ ] **T-25 · Imágenes de producción** — Dockerfiles multi‑stage (usuario no root, healthchecks), `docker-compose.prod.yml`, Caddyfile con dominio, cabeceras de seguridad y CSP. Ver skill `docker-deploy`.
- [ ] **T-26 · Respaldos** — contenedor `backup` con `pg_dump` diario + tar de media, retención 14 días, `restore.sh` probado. *RNF-06.*
- [ ] **T-27 · Pipeline de despliegue** — Actions: build → GHCR con tag `sha` y `latest` → deploy por SSH (`deploy.sh`) con rollback a tag anterior. Documentar en `06-despliegue.md`.
- [ ] **T-28 · Auditoría final** — Lighthouse CI con presupuestos (RNF-01..03), axe en e2e, pruebas en iPhone/Android reales, checklist de lanzamiento de `06-despliegue.md`.
- [ ] **T-29 · Migración de dominio** — bajar Netlify, apuntar DNS al servidor, redirecciones 301 (`/aviso-de-privacidad.html` → `/aviso-de-privacidad`), verificar correo del dominio (SPF/DKIM/DMARC del proveedor SMTP).

## Backlog Fase 2 (no iniciar sin aprobación)
- [ ] T-30 Cotizador guiado (RF-30) · [ ] T-31 Disponibilidad y solicitudes de sesión (RF-31) · [ ] T-32 Casos de estudio (RF-32) · [ ] T-33 Blog (RF-33) · [ ] T-34 Umami + eventos (RF-34)
