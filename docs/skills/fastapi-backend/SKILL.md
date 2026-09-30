---
name: fastapi-backend
description: Convenciones del backend FastAPI de Cherry Studios (capas, SQLAlchemy async, Alembic, Pydantic v2, auth por cookies, subida y procesamiento de medios con worker, correo, rate limit, tests). Úsalo al trabajar en cualquier archivo dentro de backend/.
---

# Backend FastAPI — convenciones

## Stack
Python 3.12 · FastAPI · Uvicorn · Pydantic v2 + pydantic-settings · SQLAlchemy 2.0 async + asyncpg · Alembic · uv · pwdlib[argon2] · PyJWT · slowapi · aiosmtplib + Jinja2 (plantillas de correo) · Pillow (+ pillow-avif si hace falta) · ffmpeg (binario en la imagen) · python-magic · structlog · pytest + pytest-asyncio + httpx · ruff · mypy (strict).

## Capas (en `backend/app/`)
```
routers/public/*.py   -> HTTP, validación de entrada/salida, dependencias. SIN lógica de negocio.
routers/admin/*.py    -> ídem, con Depends(require_admin)
services/*.py         -> reglas de negocio, orquestación, encolar jobs
repositories/*.py     -> consultas SQLAlchemy (select/insert/update), sin HTTP
models/*.py           -> ORM (Mapped[], mapped_column)
schemas/*.py          -> Pydantic: *Create, *Update, *Out, *AdminOut
core/                 -> config, db (engine/session), security, storage, email, errors, ratelimit, logging
workers/              -> loop de jobs + handlers (process_image, process_audio, send_email, revalidate)
seed/                 -> carga inicial idempotente desde cherry-studios-site/
```
Regla: routers → services → repositories. Los routers nunca importan `models` directamente para consultar.

## Base de datos
- `AsyncSession` por request vía `Depends(get_session)`; commit en el service, no en el repositorio.
- PK UUIDv7 (`uuid6`/`uuid_utils`), `created_at/updated_at` con `server_default=func.now()` y `onupdate`.
- Enums como `sqlalchemy.Enum(..., native_enum=False)` + CHECK para migraciones fáciles.
- Toda modificación de modelos → `alembic revision --autogenerate -m "…"` y **revisar** el script. Test de CI: `alembic upgrade head && alembic check`.
- Mixins: `TimestampMixin`, `SoftDeleteMixin`, `OrderedMixin`, `PublishableMixin`.
- Consultas públicas siempre filtran `is_published = true AND deleted_at IS NULL`.

## Esquemas y errores
- Pydantic `model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)`.
- Mensajes de validación en **español**: handler global de `RequestValidationError` traduce al formato `{"error":{"code","message","fields"}}` de `docs/sdd/04-api.md`.
- Excepciones de dominio (`NotFound`, `Conflict`, `Forbidden`, `RateLimited`) mapeadas en `core/errors.py`.
- Markdown/HTML del admin se sanea con `nh3` antes de guardar (`privacy_html`, descripciones).

## Auth
- `POST /auth/login`: verifica Argon2, controla `failed_logins`/`locked_until`, emite access (15 min) y refresh (7 d, guardado hasheado en tabla `refresh_tokens` para rotación/revocación) como cookies `httpOnly; Secure; SameSite=Lax; Path=/api`.
- CSRF double‑submit: cookie `csrf_token` (no httpOnly) + cabecera `X-CSRF-Token` obligatoria en métodos mutantes de `/admin` y `/auth/logout`.
- Dependencias: `current_user`, `require_admin`, `require_superadmin`.

## Medios
- `core/storage.py`: `class StorageBackend(Protocol)` con `save(stream, key)`, `open(key)`, `delete(key)`, `url(key)`; implementación `LocalStorage(root=/srv/media)` con subcarpetas `public/` y `private/`.
- Subida por streaming (`UploadFile` en chunks de 1 MB) calculando sha256 y tamaño; aborta al exceder límite.
- Tipo por **magic bytes** (`python-magic`), lista blanca: `image/jpeg|png|webp|avif`, `audio/mpeg|wav|x-wav|flac|mp4|x-m4a|aac`.
- Keys: `public/img/<sha256[:2]>/<sha256>-<ancho>.webp`, `public/audio/<sha256>.m4a`, `private/demos/<uuid>.<ext>`.
- Procesamiento en worker (nunca en el request):
  - Imagen: EXIF orientation, strip metadata, 480/960/1600 px en WebP (q=78) y AVIF (q=50), LQIP 16 px base64.
  - Audio: `ffmpeg -i in -c:a aac -b:a 256k out.m4a`; mp3 320k; LUFS con `ffmpeg -af ebur128=framelog=quiet -f null -` (parsear `I:`); peaks: decodificar a PCM mono 8 kHz y reducir a 800 máximos normalizados → JSON.

## Cola de jobs
- Tabla `jobs`; `enqueue(type, payload, run_after=None)` desde services.
- Worker: loop `SELECT … WHERE status='queued' AND run_after<=now() ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1`, reintentos con backoff exponencial (máx. 5), `last_error`.
- Mismo código, comando `python -m app.workers`.

## Correo
- `core/email.py` con `aiosmtplib`, plantillas Jinja2 HTML+texto en `templates/email/` con la paleta Cherry.
- `lead_notification` (a `notify_emails`, `Reply-To` = email del lead), `lead_ack` (al visitante), `password_reset`.
- En dev apunta a Mailpit.

## Leads (RF-07)
- Honeypot → responder 201 sin persistir y loguear `spam_honeypot`.
- `slowapi` con key = `ip_hash`; límites de `02-arquitectura.md §7`. Detrás de Caddy usar `X-Forwarded-For` (configurar `--proxy-headers --forwarded-allow-ips`).
- Turnstile: si `TURNSTILE_SECRET_KEY` existe, verificar token contra `https://challenges.cloudflare.com/turnstile/v0/siteverify`.
- Guardar `consent_text_version` = fecha de `legal.privacy_updated_at`.

## Revalidación
Al guardar contenido en admin, el service encola `revalidate` con las rutas afectadas (p. ej. servicio → `/`, `/servicios/<slug>`, `/sitemap.xml`).

## Tests
- `tests/conftest.py`: BD Postgres de pruebas (servicio `db` o testcontainers), transacción por test con rollback, cliente `httpx.AsyncClient(app=…)`, fábricas simples.
- Cubrir: validaciones, permisos por rol, honeypot, rate limit, CSRF, orden/reorder, soft delete, pipeline de medios (fixtures WAV/JPG pequeños), formato de errores.
- Cobertura ≥ 80 % en `services/` y `routers/`.

## Comandos
```
uv run fastapi dev app/main.py
uv run pytest -q
uv run ruff check . && uv run ruff format --check . && uv run mypy app
uv run alembic revision --autogenerate -m "msg" && uv run alembic upgrade head
uv run python -m app.seed
```
