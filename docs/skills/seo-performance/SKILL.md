---
name: seo-performance
description: SEO técnico, datos estructurados JSON-LD, Open Graph y vistas previas para redes, presupuestos de rendimiento (Core Web Vitals) y privacidad/analítica del sitio de Cherry Studios. Úsalo al crear páginas públicas, metadatos, imágenes, embeds o al auditar Lighthouse.
---

# SEO, compartibilidad y rendimiento

## Metadatos por página
Con `useSeoMeta` + `useHead`; valores del admin con fallback a `site.seo`:

| Página | title | description |
|--------|-------|-------------|
| `/` | `Cherry Studios · Estudio de producción musical en CDMX` | lema + servicios clave |
| `/servicios/[slug]` | `{Servicio} en CDMX · Cherry Studios` | `short_description` |
| `/portafolio` | `Portafolio · Cherry Studios` | |
| `/portafolio/[slug]` | `{Título} — {Artista} · Cherry Studios` | `credits_text` |
| `/equipo/[slug]` | `{Nombre} “{Apodo}” · Cherry Studios` | `bio_short` |
| `/links` | `Cherry Studios · Links` | `noindex` opcional (configurable) |

- `title_template`: `%s · Cherry Studios`. Canónica absoluta con `NUXT_PUBLIC_SITE_URL`.
- `lang="es-MX"`, `og:locale=es_MX`.

## Open Graph (clave para la campaña en redes)
- `og:title`, `og:description`, `og:image` (1200×630), `og:type` (`website` / `music.song` en piezas), `twitter:card=summary_large_image`.
- **Imagen OG dinámica** con `nuxt-og-image` (Satori): fondo maroon, título en Fraunces cream, artista en blush, cereza del riel y logo. Plantillas: `OgDefault`, `OgService`, `OgPortfolio`. Fuentes Fraunces/Work Sans cargadas en la plantilla.
- Verificar con opengraph.xyz y compartiendo en WhatsApp (el caché de WhatsApp tarda; usar `?v=` para pruebas).

## JSON‑LD (`nuxt-schema-org` o `useHead({ script: [{ type: 'application/ld+json' }] })`)
- Inicio: `ProfessionalService` (o `LocalBusiness`) con `name`, `url`, `logo`, `image`, `email`, `areaServed: "Ciudad de México"`, `sameAs` (redes), `founder` (2 `Person`), `hasOfferCatalog` con los servicios.
- Servicio: `Service` con `provider`, `areaServed`, `offers.priceSpecification` si hay “Desde $”.
- Pieza: `MusicRecording` con `byArtist` (`MusicGroup`/`Person`), `duration` ISO‑8601, `url`, `image`; `contributor` para créditos de Cherry.
- FAQ: `FAQPage`.
- Validar en https://validator.schema.org y Rich Results Test.

## Sitemap y robots
- `@nuxtjs/sitemap` alimentado por endpoint del backend (`/public/services`, `/public/portfolio`, `/public/team`) con `lastmod = updated_at`.
- `robots.txt`: permitir todo excepto `/admin`, `/api`; enlazar sitemap. En `ENVIRONMENT != production`: `Disallow: /`.

## Rendimiento (presupuestos en `02-arquitectura.md §8`)
- Hero: `<NuxtImg>`/`<NuxtPicture>` AVIF/WebP, `fetchpriority="high"`, `preload`, tamaños responsivos; el resto `loading="lazy"` + LQIP.
- Fuentes autoalojadas, `preload` solo de Fraunces 600 y Work Sans 400.
- **Cero iframes en la carga inicial**: Spotify/YouTube/SoundCloud detrás de `<EmbedFacade>`.
- wavesurfer y Web Audio cargados con `defineAsyncComponent` / import dinámico al primer play.
- Splash: no debe retrasar LCP → el hero se renderiza debajo y el splash es overlay que no bloquea; si Lighthouse lo penaliza, mostrar el splash solo si `performance.now() < 1500` al montar.
- Evitar CLS: dimensiones explícitas en imágenes/embeds; nav con altura fija.
- Lighthouse CI (`@lhci/cli`) en CI contra `/`, `/servicios/mezcla`, `/portafolio`, `/links` con `assertions` de presupuestos.

## Privacidad y analítica
- Sin Google Analytics ni píxeles en Fase 1. Métricas propias (leads con UTM, clics de `/links`, plays) cubren la campaña.
- Fase 2: Umami autoalojado (sin cookies) → no requiere banner; mencionarlo en el aviso de privacidad.
- Si en el futuro se agrega Meta Pixel/TikTok Pixel para anuncios: **solo** tras consentimiento explícito con banner y actualización del aviso.
- Embeds de terceros no cargan cookies hasta que el usuario pulsa play (fachada) y se usa `youtube-nocookie.com`.

## UTM y medición de campañas
- Convención para la campaña de lanzamiento: `utm_source` (instagram, tiktok, whatsapp, facebook, email, qr), `utm_medium` (bio, story, post, reel, dm, flyer), `utm_campaign` (p. ej. `lanzamiento-sitio-2026`), `utm_content` (variante creativa).
- `/links` agrega UTM automáticamente a enlaces internos.
- Los leads guardan first‑touch UTM de la sesión → el dashboard muestra qué red trae proyectos reales, no solo visitas.
