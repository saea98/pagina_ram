# 06 · Despliegue y operación

## Requisitos del servidor

- Linux (Ubuntu 24.04 LTS recomendado), **2 vCPU / 4 GB RAM / 40 GB SSD** mínimo (el procesamiento de audio con ffmpeg es lo más pesado).
- Docker Engine + plugin Compose v2.
- Puertos 80 y 443 abiertos; 22 solo con llave SSH.
- DNS: `A`/`AAAA` de `cherrystudios.com.mx` y `www` al servidor (Caddy emite certificados automáticamente).

## Servicios de `docker-compose`

| Servicio | Imagen | Puerto interno | Volúmenes | Healthcheck |
|----------|--------|----------------|-----------|-------------|
| `caddy` | `caddy:2.11.4-alpine` | 80, 443 (expuestos) | `caddy_data`, `caddy_config`, `media:ro` | — |
| `web` | `ghcr.io/saea98/pagina_ram-web` | 3000 | — | `GET /` |
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
```

## Caddyfile (referencia)

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
    reverse_proxy web:3000
  }

  redir /aviso-de-privacidad.html /aviso-de-privacidad permanent

  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    Referrer-Policy "strict-origin-when-cross-origin"
    Permissions-Policy "camera=(), microphone=(), geolocation=()"
    -Server
  }
  request_body {
    max_size 210MB
  }
}
```
(La CSP la define Nuxt vía `nuxt-security` para poder usar nonces.)

## Primer despliegue

```bash
ssh deploy@servidor
git clone git@github.com:saea98/pagina_ram.git && cd pagina_ram/infra
cp .env.example .env && nano .env            # completar secretos
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.seed
```

## Despliegues siguientes (CI)

1. Push a `main` → Actions corre tests → construye `web` y `api` → publica en GHCR con tags `sha-<commit>` y `latest`.
2. Job `deploy` (con aprobación manual del environment `production`) hace SSH y ejecuta `infra/scripts/deploy.sh <sha>`:
   - `docker compose pull`, `alembic upgrade head`, `up -d`, espera healthchecks.
   - Si falla, vuelve a la imagen previa (`deploy.sh rollback`).
3. Secrets de GitHub requeridos: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`.

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
- [ ] Lighthouse móvil cumple presupuestos.
- [ ] Respaldo y restauración probados.
- [ ] Google Search Console y Bing Webmaster verificados, sitemap enviado.
- [ ] Perfil de Google Business actualizado con el nuevo sitio.
- [ ] `/links` configurado y puesto en la bio de Instagram/TikTok.
- [ ] Netlify desactivado; redirecciones 301 verificadas.
