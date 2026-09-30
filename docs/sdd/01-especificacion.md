# 01 · Especificación funcional

> **Qué** construimos y **para quién**. El **cómo** está en `02-arquitectura.md`.
> Cada requisito tiene ID (`RF-xx`) para referenciarlo desde tareas, PRs y tests.

## 1. Contexto

- **Negocio:** Cherry Studios — producción musical en Ciudad de México.
- **Fundadores:** Alejandro Vega “Chemita” (producción vocal, mezcla, mastering) y Ramsés Jiménez “Ramzy” (ingeniería de audio, producción, composición).
- **Lema:** “Que la emoción te lleve a donde la mente no puede”.
- **Sitio actual:** https://cherrystudios.com.mx (HTML estático en Netlify, formulario con Netlify Forms).
- **Referencia de diseño aprobada:** carpeta `cherry-studios-site/` en este repo.
- **Contacto actual:** contacto@cherrystudios.com.mx · Instagram @_cherrystudios_

### Servicios (contenido inicial / seed)

| # | Servicio | Descripción corta |
|---|----------|-------------------|
| 01 | Composición | Desarrollo de idea, letra, estructura y arreglos desde cero — solo o junto a Chemita y Ramzy. |
| 02 | Grabación | Tracking, comping y entrega de sesión, stems o multitrack, con acompañamiento en cabina. |
| 03 | Mezcla | Balance, espacio y textura en estéreo para que cada elemento de tu canción tenga su lugar. |
| 04 | Máster | El acabado final: loudness, translación entre bocinas y consistencia entre plataformas. |
| 05 | Producciones | Desde la composición hasta la entrega final de tu máster para EP o álbum. |
| 06 | Beat Making | Beats exclusivos o personalizados, construidos desde cero para tu proyecto. |
| 07 | Grabación de podcast | Grabación multipista para conversaciones y episodios, lista para editar y publicar. |
| 08 | Post audiovisual | Edición y mezcla de audio para video, clips y contenido audiovisual. |

### Portafolio (seed)

| Título | Artista | Fuente |
|--------|---------|--------|
| Palenque | Alan Säräs | Spotify track `7KYnE3dclseuAX5pect1TM` |
| Esta Noche | Ramzy | Spotify album `7yU2Q7sAuPpaSsdU1claQr` |
| Neto — Tec Live Session | Me llamo Neto | MP3 propio `audio/neto-live-session.mp3` + YouTube `pLuaWY0WsTI?t=137` |

## 2. Actores

| Actor | Descripción | Objetivo principal |
|-------|-------------|--------------------|
| **Artista visitante** | Músico/a independiente, banda, productor, podcaster o creador audiovisual. Llega desde Instagram, TikTok, Google o recomendación. Casi siempre en celular. | Escuchar si el estudio “suena bien”, entender qué ofrecen y contactar sin fricción. |
| **Administrador** | Chemita o Ramzy. Poco tiempo, usa el celular. | Actualizar portafolio y servicios, responder leads, ver qué campaña trae clientes. |
| **Superadmin** | Quien mantiene la plataforma (desarrollo). | Gestionar usuarios, configuración técnica, respaldos. |

## 3. Alcance por fases

- **Fase 1 — MVP (lanzamiento):** sitio público equivalente al template + mejoras diferenciadoras básicas + admin CMS + leads + despliegue en contenedores.
- **Fase 2 — Crecimiento:** cotizador guiado, solicitud de sesión con disponibilidad, casos de estudio, novedades/blog, analítica propia.
- **Fase 3 — Plataforma:** portal de clientes con revisiones de mezcla comentadas por segundo, anticipos en línea, newsletter.

Solo la **Fase 1** está especificada a nivel de criterios de aceptación completos. Fases 2 y 3 están a nivel de historia para no bloquear el diseño del modelo de datos.

---

## 4. Requisitos — Sitio público (Fase 1)

### RF-01 Página de inicio (one‑page con secciones)
Réplica funcional y visual del template: splash con logo → hero → Estudio → Equipo → Servicios → Portafolio → Testimonios (nuevo) → Contacto → footer.

**Criterios de aceptación**
- Dado un visitante en móvil, cuando carga `/`, entonces ve el hero con la frase y titular animado palabra por palabra en < 2.5 s (LCP).
- El splash del logo se muestra **solo en la primera visita de la sesión** y nunca con `prefers-reduced-motion`.
- La navegación fija resalta la sección activa (scrollspy) y el menú móvil cierra al elegir una opción.
- El riel de progreso con la cereza aparece en ≥ 980 px, igual que el template.
- Todos los textos (hero, estudio, equipo, títulos de sección) provienen de `SiteSettings` / entidades de la API.

### RF-02 Servicios
- Tarjetas con volteo (flip) accesibles: `button` con `aria-pressed`, operables con teclado.
- Orden, ícono, título, descripción corta y descripción larga administrables.
- Campo opcional **“Desde $X MXN”** por servicio; si está vacío no se muestra precio.
- Cada tarjeta tiene CTA “Cotizar este servicio” que lleva al formulario con el servicio **preseleccionado** (`/?servicio=mezcla#contacto` o equivalente).
- Cada servicio tiene página propia `/servicios/[slug]` (SEO) con descripción larga, piezas de portafolio relacionadas, FAQ del servicio y CTA.

### RF-03 Portafolio con reproductor persistente ★ diferenciador
- Soporta piezas de tipo: `audio_propio` (archivo subido), `spotify`, `youtube`, `soundcloud`, `apple_music`, `bandcamp`.
- **Reproductor global persistente:** al reproducir un audio propio, aparece una mini‑barra inferior (portada, título, artista, waveform, play/pausa, progreso) que **sigue sonando al navegar** entre páginas del sitio.
- Solo suena una fuente a la vez (conserva la lógica `__pauseAllExcept` del template, extendida a todas las fuentes).
- Filtros por servicio (mezcla, máster, producción…) y por género.
- Cada pieza muestra créditos (qué hizo Cherry en esa pieza: “Mezcla y máster por Chemita”).
- Piezas marcadas como **destacadas** aparecen en el inicio (máx. configurable, default 4); el resto en `/portafolio`.
- Los embeds de terceros cargan **solo al interactuar** (fachada con portada + botón play) para no penalizar rendimiento ni cargar cookies de terceros sin acción del usuario.

### RF-04 Comparador Antes/Después (A/B) ★ diferenciador
- Una pieza de tipo `audio_propio` puede tener **dos pistas sincronizadas**: “Antes” (maqueta/sin mezcla) y “Después” (mezcla/máster).
- El usuario alterna A/B **sin cortar la reproducción** (misma posición de tiempo, cross‑fade ≤ 50 ms) mediante un switch grande y la tecla `A`/`B`.
- Niveles igualados en loudness (el backend calcula LUFS al subir y el front compensa ganancia) para que la comparación sea honesta; toggle “igualar volumen” activado por defecto.
- Sección en inicio: “Escucha la diferencia” con 1–3 comparaciones destacadas.

### RF-05 Equipo
- Tarjetas de integrantes: foto, nombre, apodo, rol, bio corta, redes personales opcionales, orden.
- Página `/equipo/[slug]` opcional con bio larga y piezas donde participó.

### RF-06 Testimonios
- Cita, nombre del artista, proyecto, foto opcional, enlace opcional a la pieza del portafolio.
- Carrusel accesible (pausa, controles, sin autoplay con reduced‑motion).

### RF-07 Contacto y captura de leads
- Formulario: nombre, correo **o** teléfono/WhatsApp, servicio (select desde API + “Aún no estoy seguro”), mensaje, **enlace a maqueta** (URL) y/o **archivo de maqueta** (mp3/wav/m4a ≤ 30 MB), fecha tentativa opcional, checkbox de consentimiento con enlace al aviso de privacidad (**obligatorio**).
- Anti‑spam: honeypot (como el template) + rate‑limit por IP + Cloudflare Turnstile opcional (activable por variable de entorno).
- Captura automática y oculta: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `referrer`, página de origen. Los UTM se guardan en `sessionStorage` al aterrizar para no perderlos si el usuario navega antes de enviar.
- Al enviar: respuesta inline sin recargar (“¡Gracias! Recibimos tu mensaje…”), correo de notificación a los administradores con todos los datos y `Reply-To` del visitante si dio correo, y correo de acuse al visitante (si dio correo).
- Si falla el envío, mensaje con contacto directo (igual que el template).
- **Botón de WhatsApp** (número administrable) con mensaje prellenado según la sección/servicio desde donde se pulsa. Flotante en móvil.
- Tarjeta de contacto directo: correo, Instagram, WhatsApp, TikTok, YouTube, Spotify (los que existan en settings).

### RF-08 Página link‑in‑bio `/links` ★ para redes
- Página ligera tipo Linktree con la marca Cherry: logo, frase, lista de botones administrables (texto, URL, ícono, orden, activo, fecha de inicio/fin opcional para promos).
- Cada clic se registra (conteo por botón) y los enlaces internos agregan UTM automáticamente (`utm_source=instagram&utm_medium=bio` configurable).
- Reemplaza cualquier servicio externo de link‑in‑bio.

### RF-09 SEO y compartibilidad
- SSR/SSG de todas las páginas públicas.
- `title`, `description`, Open Graph y Twitter Card por página, editables en admin (con defaults).
- **Imagen OG generada** automáticamente por pieza de portafolio y por servicio con la paleta Cherry (título + artista + logo).
- `sitemap.xml`, `robots.txt`, URLs canónicas.
- Datos estructurados JSON‑LD: `LocalBusiness`/`ProfessionalService` (inicio), `Service` (servicios), `MusicRecording` (piezas), `Person` (equipo), `FAQPage` (FAQ).

### RF-10 Páginas legales
- `/aviso-de-privacidad` con contenido editable (se migra el texto actual del template; fecha de actualización visible).
- Pastilla flotante “Aviso de privacidad” como en el template.

### RF-11 FAQ
- Preguntas frecuentes administrables, globales y por servicio (“¿Cuánto tarda una mezcla?”, “¿Qué necesito llevar?”, “¿Cuántas revisiones incluye?”).

### RF-12 Estados y errores
- Página 404 con la marca y enlaces útiles.
- Estados vacíos elegantes (si no hay testimonios, la sección no aparece).

---

## 5. Requisitos — Panel de administración (Fase 1)

Ruta `/admin`, solo usuarios autenticados. Debe ser **cómodo en celular**.

### RF-20 Autenticación
- Login con correo + contraseña. Sesión en cookie httpOnly. Cierre de sesión.
- Recuperar contraseña por correo.
- Bloqueo temporal tras 5 intentos fallidos.
- Roles: `admin` (contenido + leads) y `superadmin` (además usuarios y ajustes técnicos).

### RF-21 Dashboard
- Leads nuevos de la semana, leads por estado, leads por fuente (UTM) últimos 30 días, clics en `/links`, piezas más reproducidas.

### RF-22 CRUD de contenido
Para **Servicios, Equipo, Portafolio, Testimonios, FAQ, Enlaces (/links)**:
- Listado con búsqueda, reordenamiento **drag & drop**, publicar/ocultar (borrador).
- Formulario con validación y **vista previa** (abre la página pública en modo preview).
- Subida de imágenes con recorte sugerido y conversión automática a WebP/AVIF en varios tamaños.
- Subida de audio (mp3/wav/flac ≤ 200 MB): el backend genera versión web (AAC/MP3 320k), waveform (peaks JSON) y LUFS.
- Borrado lógico con confirmación.

### RF-23 Ajustes del sitio (`SiteSettings`)
- Textos del hero, estudio, títulos de secciones, lema.
- Datos de contacto: correo, WhatsApp, redes.
- Correos que reciben notificación de leads.
- SEO por defecto y OG por defecto.
- Imagen del hero y del estudio.
- Aviso de privacidad (editor de texto enriquecido) y fecha.

### RF-24 Bandeja de leads (mini‑CRM)
- Lista con filtros por estado, servicio, fuente y fecha.
- Estados: `nuevo → contactado → cotizado → ganado | perdido`.
- Notas internas por lead, historial de cambios de estado.
- Botones rápidos: responder por correo (mailto con plantilla), abrir WhatsApp con el número.
- Escuchar/descargar la maqueta adjunta.
- Exportar CSV.
- Eliminar lead (derecho ARCO de cancelación).

### RF-25 Usuarios (superadmin)
- Alta/baja de administradores, reset de contraseña.

---

## 6. Requisitos — Fase 2 (historias)

- **RF-30 Cotizador guiado “Arma tu proyecto”** ★ — wizard de 4 pasos (¿qué necesitas? → ¿cuántas canciones? → ¿tienes maqueta? → ¿para cuándo?) que muestra un **rango estimado** calculado con reglas administrables y termina creando un lead con todo el contexto.
- **RF-31 Solicitud de sesión con disponibilidad** — calendario público con bloques disponibles (definidos en admin), el visitante solicita un bloque, el admin confirma; se envía `.ics`. Opcional: sincronizar con Google Calendar.
- **RF-32 Casos de estudio** — página por proyecto: historia, reto, proceso, créditos, galería, A/B, testimonio.
- **RF-33 Novedades/Blog** — artículos (tips de grabación, lanzamientos de clientes) para SEO y para alimentar redes.
- **RF-34 Analítica propia** — Umami autoalojado; eventos: play, A/B toggle, envío de formulario, clic WhatsApp.

## 7. Requisitos — Fase 3 (historias)

- **RF-40 Portal de clientes** ★ — el cliente recibe un enlace privado con sus versiones de mezcla, las escucha con waveform y **deja comentarios anclados al segundo exacto** (“0:47 subir la voz”). El admin responde y sube la siguiente versión. Aprobación final con un clic.
- **RF-41 Anticipos en línea** — Mercado Pago / Stripe para apartar sesión.
- **RF-42 Newsletter** — alta con doble opt‑in, envío de lanzamientos.

---

## 8. Requisitos no funcionales

| ID | Requisito |
|----|-----------|
| RNF-01 | Lighthouse móvil ≥ 90 en Performance, ≥ 95 en Accesibilidad, SEO y Buenas prácticas (inicio, servicio, portafolio, links). |
| RNF-02 | LCP < 2.5 s, CLS < 0.1, INP < 200 ms en 4G simulado. |
| RNF-03 | JS inicial de páginas públicas ≤ 170 KB gzip (sin contar embeds diferidos). |
| RNF-04 | API p95 < 300 ms en endpoints públicos (con caché). |
| RNF-05 | Disponibilidad objetivo 99.5 %; reinicio automático de contenedores. |
| RNF-06 | Respaldo diario de base de datos y medios; retención 14 días; restauración probada y documentada. |
| RNF-07 | Soporte: últimas 2 versiones de Safari iOS, Chrome Android, Chrome, Firefox, Edge, Safari macOS. |
| RNF-08 | Toda la UI funciona desde 320 px de ancho. |
| RNF-09 | Sin cookies de terceros antes de interacción del usuario. |
| RNF-10 | Cobertura de tests backend ≥ 80 % en servicios y routers. |

## 9. Fuera de alcance (por ahora)

- Tienda de beats con licencias y descargas pagadas (evaluar en Fase 3+).
- Multi‑idioma (se deja preparado `i18n` con `es-MX` único).
- App móvil nativa.
