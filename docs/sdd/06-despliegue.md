# 06 · Despliegue y operación

## Requisitos del servidor

- Linux (Ubuntu 24.04 LTS recomendado), **2 vCPU / 4 GB RAM / 40 GB SSD** mínimo (el procesamiento de audio con ffmpeg es lo más pesado).
- Docker Engine + plugin Compose v2.
- Puertos 80 y 443 los publica **Nginx Proxy Manager** (`jc21/nginx-proxy-manager`), que ya atiende otros sitios. Cherry no los enlaza.
- Caddy publica solo **HTTP `8090`** (`infra/docker-compose.server.yml` + `Caddyfile.server`). No pide certificado: el TLS lo termina NPM.
- El frontend de Cherry escucha en el **3010** de la red interna. El 3000 del host lo usa otro proyecto; el 3001 queda reservado para Umami.
- DNS: `A`/`AAAA` de `cherrystudios.com.mx` y `www` al servidor. En NPM, un proxy host del dominio hacia el **gateway de Docker** en el puerto 8090 (no `127.0.0.1`: NPM corre en un contenedor y esa dirección es él mismo). Websockets activos. El 8090 no se abre en el firewall de GCP: solo 80 y 443, que ya usa NPM.
- 22 solo con llave SSH.

## Servicios de `docker-compose`

| Servicio | Imagen | Puerto interno | Volúmenes | Healthcheck |
|----------|--------|----------------|-----------|-------------|
| `caddy` | `caddy:2.11.4-alpine` | 80 interno; en este servidor el host expone **8090**. En local, 80/443 | `caddy_data`, `caddy_config`, `media:ro` | — |
| `web` | `ghcr.io/saea98/pagina_ram-web` | 3010 | — | `GET /healthz` |
| `api` | `ghcr.io/saea98/pagina_ram-api` | 8000 | `media` | `GET /api/ready` |
| `worker` | misma que `api` (`command: python -m app.workers`) | — | `media` | proceso vivo |
| `db` | `postgres:17.11-alpine` | 5432 (solo red interna) | `pg_data` | `pg_isready` |
| `backup` | `postgres:17.11-alpine` + cron | — | `backups`, `media:ro` | — |
| `mailpit` | `axllent/mailpit:v1.31.3` (solo dev) | 8025 | — | — |
| `umami` | Fase 2, perfil `analytics` | 3001 | — | — |

Todos con `restart: unless-stopped` y rotación de logs (`max-size: 10m`, `max-file: 3`).

## Variables de entorno (`infra/.env.example`)

```dotenv
# General
DOMAIN=cherrystudios.com.mx
ENVIRONMENT=production            # development | production
TZ=America/Mexico_City

# Base de datos
POSTGRES_DB=cherry
POSTGRES_USER=cherry
POSTGRES_PASSWORD=cambia-esto
DATABASE_URL=postgresql+asyncpg://cherry:cambia-esto@db:5432/cherry

# Seguridad
SECRET_KEY=genera-con-openssl-rand-hex-32
IP_HASH_SALT=otro-valor-aleatorio
INTERNAL_REVALIDATE_TOKEN=otro-valor-aleatorio
SEED_ADMIN_EMAIL=
SEED_ADMIN_PASSWORD=

# Correo (SMTP de Google Workspace; ver 07-preguntas-abiertas.md)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=no-reply@cherrystudios.com.mx
SMTP_PASSWORD=
SMTP_FROM="Cherry Studios <no-reply@cherrystudios.com.mx>"

# Anti-spam (opcional)
TURNSTILE_SITE_KEY=
TURNSTILE_SECRET_KEY=

# Frontend
NUXT_PUBLIC_SITE_URL=https://cherrystudios.com.mx
NUXT_API_INTERNAL_URL=http://api:8000
NUXT_PUBLIC_API_BASE=/api/v1

# Límites
MAX_UPLOAD_MB_ADMIN=200
MAX_UPLOAD_MB_LEAD=30

# Observabilidad (opcional)
SENTRY_DSN=

# Imagen (deploy.sh) y copia offsite del respaldo. Ver infra/.env.example.
IMAGE_TAG=latest
GHCR_USER=
GHCR_TOKEN=
# OFFSITE_RESTIC_REPOSITORY=
# OFFSITE_RESTIC_PASSWORD=
```

En este servidor el archivo activo es `infra/Caddyfile.server` (`:80`, sin TLS propio, con HSTS y CSP). `infra/Caddyfile.prod` es el mismo sitio para una máquina donde Caddy pueda usar 80/443. El de desarrollo (`infra/Caddyfile`) no lleva HSTS ni CSP.

## Caddyfile (referencia, máquina dedicada)

```caddy
{$DOMAIN}, www.{$DOMAIN} {
  @www host www.{$DOMAIN}
  redir @www https://{$DOMAIN}{uri} permanent

  encode zstd gzip

  handle_path /media/* {
    root * /srv/media/public
    header Cache-Control "public, max-age=31536000, immutable"
    file_server
  }
  handle /api/* {
    reverse_proxy api:8000
  }
  handle {
    reverse_proxy web:3010
  }

  redir /aviso-de-privacidad.html /aviso-de-privacidad permanent

  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    Referrer-Policy "strict-origin-when-cross-origin"
    Permissions-Policy "camera=(), microphone=(), geolocation=()"
    Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com https://open.spotify.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; media-src 'self' blob:; connect-src 'self' https://challenges.cloudflare.com; frame-src 'self' https://open.spotify.com https://www.youtube-nocookie.com https://w.soundcloud.com https://challenges.cloudflare.com; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'"
    -Server
  }
  request_body {
    max_size 210MB
  }
}
```
La CSP la envía Caddy. `script-src` incluye `'unsafe-inline'` por el bootstrap de Nuxt (Q23).

## Primer despliegue (servidor compartido)

No uses `docker-compose.dev.yml` aquí: ese archivo publica 80, 443 y 8025.

```bash
ssh deploy@servidor
cd /home/saes98/cherry/cherry
git pull
cd infra
docker compose -f docker-compose.yml -f docker-compose.server.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.server.yml exec api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.server.yml run --rm --no-deps --user root api \
  sh -c 'mkdir -p /srv/media/public /srv/media/private && chown -R app:app /srv/media'
docker compose -f docker-compose.yml -f docker-compose.server.yml exec api python -m app.seed
# El override de servidor monta cherry-studios-site en /seed-source (TEMPLATE_ROOT).
# No hace falta meter esa carpeta en la imagen.
```

En NPM, proxy host `cherrystudios.com.mx` (y `www` → el dominio sin www) hacia `http://<gateway-docker>:8090`. Scheme HTTP, websockets on. El certificado lo emite NPM. El gateway sale de `ip -4 addr show docker0` (suele ser `172.17.0.1`).

El `docker compose` de desarrollo sigue siendo el de local: `docker-compose.yml` + `docker-compose.dev.yml` → `https://localhost`.

## Despliegues siguientes (CI)

1. Push a `main` → `.github/workflows/ci.yml` corre tests, lint y `docker compose config` de producción. En `main` también levanta el stack y corre Playwright + axe.
2. `.github/workflows/release.yml` construye `web` y `api` (target `runtime`, `linux/amd64`) y publica `ghcr.io/saea98/pagina_ram-web` y `pagina_ram-api` con tags `sha-<7>` y `latest`.
3. `.github/workflows/deploy.yml` espera el environment `production` (aprobación manual en GitHub) y por SSH ejecuta `infra/scripts/deploy.sh sha-<7>`:
   - compose: `docker-compose.yml` + `docker-compose.prod.yml` + `docker-compose.server.yml` (puerto **8090**).
   - `docker compose pull`, `alembic upgrade head`, `up -d`, healthchecks 120 s.
   - Si falla, `deploy.sh rollback` vuelve al tag de `infra/.last_tag`.
   - Máquina dedicada (80/443 y `Caddyfile.prod`): `CHERRY_DEDICATED=1`.
4. Secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`. En el servidor, si el paquete GHCR es privado, `GHCR_USER` y `GHCR_TOKEN` en `infra/.env`.
5. Lighthouse (manual): `.github/workflows/lighthouse.yml`. No cambia DNS; eso es T-29.

## Respaldos

- `backup` ejecuta a las 03:30 (hora CDMX): `pg_dump -Fc` + `tar` de `media` → volumen `backups`, retención 14 días.
- **Recomendado:** copiar fuera del servidor (restic a Backblaze B2 / Cloudflare R2) — variable `OFFSITE_BACKUP_*`.
- Restauración: `infra/scripts/restore.sh <fecha>` (probar una vez al mes).

## Checklist de lanzamiento

- [ ] Todos los textos revisados por Chemita y Ramzy.
- [ ] Aviso de privacidad actualizado (menciona formulario, maquetas, analítica sin cookies).
- [ ] Correos de notificación llegan (probar Gmail y Outlook) y no caen en spam (SPF/DKIM/DMARC).
- [ ] WhatsApp abre con mensaje correcto en iOS y Android.
- [ ] Vistas previas OG correctas en WhatsApp, Instagram DM, X, Facebook.
- [ ] Lighthouse móvil cumple presupuestos. Corrida local del 2026-09-30 (imagen `runtime`, gzip, móvil simulado, 1 pasada): accesibilidad 100, SEO 100, buenas prácticas 96–100, JS 101–122 KB. Performance 90 / 94 / 80 / 95 en `/`, `/servicios/mezcla`, `/portafolio`, `/links`. LCP 3.1 / 2.6 / 2.6 / 2.4 s. CLS de `/portafolio` 0.27. Aún no cumple RNF-01 y RNF-02 en todas las páginas.
- [ ] Respaldo y restauración probados.
- [ ] Google Search Console y Bing Webmaster verificados, sitemap enviado.
- [ ] Perfil de Google Business actualizado con el nuevo sitio.
- [ ] `/links` configurado y puesto en la bio de Instagram/TikTok.
- [ ] Netlify desactivado; redirecciones 301 verificadas.
