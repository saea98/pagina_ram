---
name: docker-deploy
description: Contenedores, docker compose (dev y prod), Caddy, Dockerfiles multi-stage, variables de entorno, CI/CD con GitHub Actions a GHCR, despliegue por SSH, respaldos y rollback para Cherry Studios. Úsalo al tocar infra/, Dockerfiles, .github/workflows o al preparar el servidor.
---

# Contenedores y despliegue

Referencia completa de servicios, variables y Caddyfile: `docs/sdd/06-despliegue.md`. Este skill define **cómo** escribir esos archivos.

## Compose
- Archivo base `infra/docker-compose.yml` + overrides `docker-compose.dev.yml` y `docker-compose.prod.yml`. Nombre de proyecto: `name: cherry`.
- Red interna única `internal`; solo `caddy` publica puertos. En local: 80/443 y 8025 (Mailpit). En el servidor compartido (`docker-compose.server.yml`): solo `8090:80`, porque Nginx Proxy Manager ya usa 80/443.
- Volúmenes nombrados: `pg_data`, `media`, `caddy_data`, `caddy_config`, `backups`.
- `depends_on` con `condition: service_healthy` (web → api → db).
- `env_file: .env` + `environment` solo para valores no secretos.
- Logging: `driver: json-file`, `max-size: 10m`, `max-file: 3`.
- Límites en prod: `api` 1 GB, `worker` 1.5 GB (ffmpeg), `web` 512 MB, `db` 1 GB.

### Dev
- `api`: monta `../backend:/app`, comando `uvicorn app.main:app --reload --host 0.0.0.0 --proxy-headers`.
- `web`: monta `../frontend:/app` (excepto `node_modules` en volumen anónimo), `pnpm dev --host`.
- `caddy` con `localhost` y `tls internal`.
- `mailpit` para ver correos en `http://localhost:8025`.

## Dockerfiles

### backend/Dockerfile (multi-stage)
```dockerfile
FROM python:3.12-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libmagic1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM base AS runtime
RUN useradd -u 10001 -m app
COPY --from=deps /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/api/ready')"
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers","--forwarded-allow-ips=*","--workers","2"]
```
(Fija la versión de la imagen `uv` a un tag concreto en el repo real.)

### frontend/Dockerfile
```dockerfile
FROM node:22-alpine AS build
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOST=0.0.0.0
COPY --from=build /app/.output ./.output
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost:3000/ >/dev/null || exit 1
CMD ["node",".output/server/index.mjs"]
```

## Caddy
- Usa el Caddyfile de `06-despliegue.md`. `/media/*` sirve solo `public/`; `private/` **nunca** se expone.
- `request_body max_size` ≥ `MAX_UPLOAD_MB_ADMIN`.
- En dev: sitio `localhost { tls internal … }`.

## CI/CD (`.github/workflows/`)
- `ci.yml` (PR y push): 
  - backend: `uv sync`, `ruff`, `mypy`, `pytest` con servicio `postgres:17`.
  - frontend: `pnpm i`, `lint`, `typecheck`, `test`, `build`.
  - e2e (en `main`): `docker compose up -d` + Playwright.
- `release.yml` (push a `main`): build con `docker/build-push-action` y caché GHA → `ghcr.io/saea98/pagina_ram-api` y `-web` con tags `sha-<short>` y `latest`.
- `deploy.yml` (manual o tras release, environment `production` con aprobación): SSH con `appleboy/ssh-action` → `infra/scripts/deploy.sh sha-<short>`.

## Scripts (`infra/scripts/`)
- `deploy.sh <tag>`: guarda tag actual en `.last_tag`, exporta `IMAGE_TAG`, `docker compose pull`, `run --rm api alembic upgrade head`, `up -d`, espera healthchecks (timeout 120 s); si falla → `deploy.sh rollback`.
- `backup.sh`: `pg_dump -Fc` + `tar -czf media-<fecha>.tgz`, borra > 14 días; opcional `restic backup` si hay variables `OFFSITE_*`.
- `restore.sh <fecha>`: detiene web/api, `pg_restore --clean`, restaura media, levanta.
- Todos con `set -euo pipefail` y mensajes claros en español.

## Reglas
- Nunca commitear `.env`; mantener `.env.example` completo y comentado.
- Imágenes sin root, con healthcheck, versiones de base fijadas (sin `latest` para imágenes de terceros en prod).
- Migraciones corren **antes** de levantar la nueva versión de `api`; deben ser compatibles hacia atrás durante el despliegue (expand → migrate → contract).
- Probar `docker compose -f … -f docker-compose.prod.yml config` en CI para detectar errores de compose.
