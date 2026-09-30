# 04 · Contrato de API

> Base: `/api/v1`. JSON UTF‑8. Fechas ISO‑8601 con zona. La **fuente de verdad** es el OpenAPI generado por FastAPI (`/api/v1/openapi.json`); este documento define la intención y debe mantenerse alineado.
> El frontend genera tipos con `openapi-typescript` → `frontend/app/types/api.ts` (`pnpm gen:api`).

## Convenciones

- Errores: `{"error": {"code": "validation_error", "message": "…", "fields": {"email": "Formato inválido"}}}` con mensajes en español.
- Paginación: `?page=1&page_size=20` → `{"items": [...], "total": n, "page": 1, "page_size": 20}`.
- Orden: `?sort=-created_at`.
- Admin: cookie de sesión + cabecera `X-CSRF-Token` en `POST/PUT/PATCH/DELETE`.
- IDs públicos en URLs por `slug`; en admin por `id`.

## Público (`/api/v1/public`) — sin auth, cacheable

| Método | Ruta | Descripción | RF |
|--------|------|-------------|----|
| GET | `/site` | Settings públicos (sin `notify_emails`) + redes + features | RF-01, RF-23 |
| GET | `/home` | Agregado para la portada: settings, servicios, equipo, portafolio destacado, A/B destacados, testimonios | RF-01 |
| GET | `/services` | Servicios publicados ordenados | RF-02 |
| GET | `/services/{slug}` | Servicio + FAQs + portafolio relacionado | RF-02 |
| GET | `/team` | Integrantes | RF-05 |
| GET | `/team/{slug}` | Integrante + créditos | RF-05 |
| GET | `/portfolio` | Filtros `?service=slug&genre=&featured=true` | RF-03 |
| GET | `/portfolio/{slug}` | Detalle con URLs de medios, peaks y LUFS | RF-03, RF-04 |
| POST | `/portfolio/{slug}/events` | `{"event":"play"\|"ab_toggle"\|"complete"}` → 204 (rate‑limited) | RF-21 |
| GET | `/testimonials` | | RF-06 |
| GET | `/faqs` | `?service=slug` | RF-11 |
| GET | `/links` | Enlaces vigentes de `/links` | RF-08 |
| GET | `/links/{id}/go` | Registra clic y responde 302 a la URL (con UTM si aplica) | RF-08 |
| GET | `/legal/privacy` | HTML saneado + fecha | RF-10 |
| POST | `/leads/uploads` | Subida de maqueta (multipart, ≤ 30 MB) → `{"upload_token": "…"}` válido 1 h | RF-07 |
| POST | `/leads` | Crear lead (ver esquema) → 201 `{"ok": true}` | RF-07 |

### `POST /public/leads`
```json
{
  "name": "Ana López",
  "email": "ana@mail.com",
  "phone": "+525512345678",
  "service_slug": "mezcla",
  "message": "Tengo 3 canciones…",
  "demo_url": "https://drive.google.com/…",
  "demo_upload_token": "opcional",
  "tentative_date": "2026-11-15",
  "consent": true,
  "source_page": "/servicios/mezcla",
  "referrer": "https://instagram.com/",
  "utm": {"source": "instagram", "medium": "bio", "campaign": "lanzamiento-sitio", "content": null, "term": null},
  "website": "",               
  "turnstile_token": "opcional"
}
```
Reglas: `email` o `phone` requerido; `consent` debe ser `true`; `website` es honeypot (si trae valor → responder 201 **sin** guardar); 5/min y 30/día por IP.
Efectos: crea `lead`, encola `send_email` (notificación a `notify_emails` con Reply‑To + acuse al visitante), responde 201.

## Autenticación (`/api/v1/auth`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/login` | `{email, password}` → set cookies (access, refresh, csrf) + `{user}` |
| POST | `/refresh` | Rota refresh |
| POST | `/logout` | Revoca refresh y limpia cookies |
| GET | `/me` | Usuario actual |
| POST | `/password/forgot` | Envía enlace (respuesta siempre 204) |
| POST | `/password/reset` | `{token, new_password}` |

## Admin (`/api/v1/admin`) — rol `admin`+

Recursos CRUD con el mismo patrón: `services`, `team`, `portfolio`, `testimonials`, `faqs`, `links`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/{recurso}` | Lista (incluye no publicados), `?q=` búsqueda |
| POST | `/{recurso}` | Crear |
| GET | `/{recurso}/{id}` | Detalle |
| PATCH | `/{recurso}/{id}` | Actualización parcial |
| DELETE | `/{recurso}/{id}` | Borrado lógico |
| POST | `/{recurso}/reorder` | `{"ids": [...]}` en el nuevo orden |

Otros:

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/PUT | `/settings` | Leer/actualizar `site_settings` completos |
| POST | `/media` | Subir archivo (multipart) → `MediaAsset` (status `processing`) |
| GET | `/media/{id}` | Estado y variantes (polling) |
| GET | `/media` | Biblioteca de medios, `?kind=image` |
| GET | `/leads` | Filtros `status, service, utm_source, from, to, q` |
| GET | `/leads/{id}` | Detalle + eventos |
| PATCH | `/leads/{id}` | Cambiar `status` (genera `lead_event`) |
| POST | `/leads/{id}/notes` | Nota interna |
| GET | `/leads/{id}/demo` | Descarga/stream de la maqueta privada |
| DELETE | `/leads/{id}` | Borrado definitivo (ARCO) con confirmación `?confirm=true` |
| GET | `/leads/export.csv` | Exportar con filtros actuales |
| GET | `/stats/overview` | Datos del dashboard (RF-21) |
| POST | `/preview-token` | Token corto para ver borradores en el sitio público |

## Superadmin (`/api/v1/admin/users`)
CRUD de usuarios, reset de contraseña, desactivar.

## Internos
| Método | Ruta | Quién | Descripción |
|--------|------|-------|-------------|
| GET | `/api/health` | Docker | Liveness |
| GET | `/api/ready` | Docker | BD ok |
| POST | `web:3000/api/_revalidate` | backend → frontend | `{paths: []}` con `X-Internal-Token` |
