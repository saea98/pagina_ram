# 07 · Preguntas abiertas y supuestos

> Las decisiones de abajo las cerraron Chemita y Ramzy (notas en `07.docx`). El agente las trata como spec. Lo que sigue abierto se implementa con el supuesto indicado.

## Decisiones cerradas

| # | Pregunta | Decisión |
|---|----------|----------|
| Q1 | ¿Se muestran precios (“Desde $X”)? | No se publica ningún precio. El campo puede existir vacío y la interfaz no lo muestra. |
| Q2 | Número de WhatsApp del estudio | No hay WhatsApp empresarial. El botón permanece oculto mientras el campo esté vacío. |
| Q3 | ¿Dirección física visible / mapa? | No se muestra dirección ni mapa. El texto público sigue diciendo “Ciudad de México”. |
| Q5 | Proveedor de correo SMTP | Google Workspace. Host `smtp.gmail.com`, puerto `587` (STARTTLS). Datos para la cuenta, más abajo. |
| Q6 | ¿El correo `contacto@` está en Google Workspace? | Sí. `contacto@cherrystudios.com.mx` se queda en Workspace. El correo transaccional del sitio sale de `no-reply@cherrystudios.com.mx`. |
| Q7 | ¿Más piezas de portafolio y testimonios para el lanzamiento? | Se lanza con las 3 piezas actuales. Las siguientes se agregan desde el admin. Sin testimonios, esa sección no aparece. |
| Q8 | ¿Hay maquetas “antes” para el comparador A/B? | No hay ninguna. La sección “Escucha la diferencia” permanece oculta hasta que exista al menos una. |
| Q9 | ¿Sincronizar el calendario de sesiones (Fase 2) con Google Calendar? | Ya tienen un Google Calendar. No se sincroniza en esta fase. |
| Q10 | ¿TikTok, YouTube, Spotify del estudio? | Solo Instagram. |
| Q11 | “Ocho formas de trabajar tu proyecto” vs. 7 opciones del template | Quedan los 8 servicios. Producciones (EP / Álbum) ya está en el HTML. El select sale de la API: 8 servicios + “Aún no estoy seguro”. |
| Q12 | ¿Qué hace el worker antes de la cola de jobs? | El comando `python -m app.workers` reclama jobs con `SKIP LOCKED` y procesa imagen y audio. |

## Parcial

| # | Pregunta | Decisión | Supuesto que sigue |
|---|----------|----------|--------------------|
| Q4 | Servidor destino | Máquina compartida del estudio (`/home/saes98/cherry/cherry`). Nginx Proxy Manager ya publica 80, 81 y 443. | Caddy de Cherry no enlaza esos puertos: HTTP en el host **8090**, TLS en NPM. Ver `docker-compose.server.yml`. |

## Siguen abiertas

| # | Pregunta | Supuesto actual | Impacto si cambia |
|---|----------|-----------------|-------------------|
| Q13 | ¿Qué tags exactos de imágenes base usamos? | Parches fijados: Caddy `2.11.4`, Postgres `17.11`, Node `22.23.3`, Python `3.12.14`, uv `0.12.19`, Mailpit `v1.31.3`. | Cambiar el tag en Dockerfiles y compose. |
| Q14 | ¿El Caddyfile de desarrollo incluye HSTS? | No. `infra/Caddyfile` sirve `localhost` con `tls internal`, sin HSTS. El bloque de producción de `06-despliegue.md` se aplica en T-25. | Añadir cabeceras al pasar a producción. |
| Q15 | ¿Las imágenes de desarrollo corren sin root? | El target `runtime` sí (usuario `app` / `node`). El target `dev` corre como root para que el hot reload escriba en el bind mount. | Endurecer el target `dev` si el equipo lo pide. |
| Q16 | ¿Qué código de error usa `/api/ready` si la base no responde? | HTTP 503, `{"error":{"code":"unavailable","message":"La base de datos no está disponible."}}`. | Ajustar el código si se acuerda otro. |
| Q17 | ¿Qué texto largo usan servicios y bios si el template solo trae el corto? | `long_description` y `bio_long` copian el texto corto. El admin puede ampliarlos después. | Reemplazar el seed si llega copy largo. |
| Q18 | Neto es MP3 propio y también YouTube. El modelo tiene un solo `kind`. | `kind=own_audio`, audio en `audio_after_media_id`, YouTube en `external_url`, `external_id` y `youtube_start_s=137`. | Partir la pieza en dos filas si el admin lo prefiere. |
| Q19 | El seed de `/links` pide WhatsApp y Spotify, pero no hay número (Q2) ni perfil de Spotify (Q10). | Esos dos enlaces se crean sin publicar. Contacto, Instagram y Portafolio sí. | Publicarlos cuando existan URL reales. |
| Q20 | ¿Cuál es el límite de `POST /portfolio/{slug}/events`? | 60 por minuto por `ip_hash` (IP + `IP_HASH_SALT`, confiando en `X-Forwarded-For`). | Ajustar el número si se quiere otro tope. |
| Q21 | ¿Nuxt Image optimiza los archivos de `/media`? | No. Caddy ya sirve WebP/AVIF con hash. El sitio usa `<picture>` con esas URLs. IPX dentro del contenedor `web` no alcanza el volumen de medios. | Cambiar a `@nuxt/image` si los medios se publican en un origen que el contenedor pueda leer. |
| Q22 | ¿Cuánto dura el bloqueo tras 5 intentos fallidos? | 15 minutos. El acceso dura 15 minutos y el refresh 7 días. El enlace de contraseña vence en 1 hora. La vista previa de borradores dura 2 horas. | Ajustar los tiempos en `app/core/security.py`. |

## Datos para el correo en Google Workspace

El sitio envía por SMTP. En local, Mailpit recibe los mensajes. En producción, Workspace.

1. En [admin.google.com](https://admin.google.com), crear el buzón o alias `no-reply@cherrystudios.com.mx`.
2. En esa cuenta, activar la verificación en 2 pasos y generar una **contraseña de aplicación** (tipo Correo). Google muestra 16 caracteres una sola vez.
3. Completar en el servidor, dentro de `infra/.env` (no se commitea):

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=no-reply@cherrystudios.com.mx
SMTP_PASSWORD=la-contraseña-de-aplicación
SMTP_FROM="Cherry Studios <no-reply@cherrystudios.com.mx>"
```

4. En Admin → Gmail → Autenticar correo, confirmar que el dominio tiene SPF (`include:_spf.google.com`) y DKIM activos, para que los avisos de leads no caigan en spam.

La contraseña de aplicación no va en el repositorio ni en el chat. Cuando exista, se pega solo en el `.env` del servidor.
