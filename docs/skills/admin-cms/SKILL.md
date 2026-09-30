---
name: admin-cms
description: Patrón del panel de administración de Cherry Studios en /admin (CRUD genérico, reordenamiento, publicar/borrador, biblioteca de medios, ajustes del sitio, bandeja de leads y dashboard). Úsalo al construir o modificar cualquier pantalla o endpoint del admin.
---

# Admin CMS — patrón

Usuarios reales: **Chemita y Ramzy**, desde el celular, con poco tiempo. Cada pantalla debe poder usarse con el pulgar y sin leer instrucciones.

## Principios de UX
1. **Una acción principal por pantalla**, botón fijo abajo en móvil (“Guardar”, “Publicar”).
2. **Autoguardado de borrador** local (en memoria + aviso “Tienes cambios sin guardar” al salir).
3. **Vista previa** siempre a un toque: abre la página pública con `?preview=<token>`.
4. **Lenguaje humano**: “Publicado / Oculto” en vez de `is_published`; “Destacar en inicio” en vez de `is_featured`.
5. **Confirmaciones** solo para acciones destructivas; toasts para todo lo demás.
6. Estados vacíos con explicación y CTA (“Aún no hay testimonios. Agrega el primero”).

## Navegación (layout `admin`)
Sidebar maroon (drawer en móvil): Inicio (dashboard) · Leads (con badge de nuevos) · Portafolio · Servicios · Equipo · Testimonios · FAQ · Enlaces (/links) · Medios · Ajustes · Usuarios (solo superadmin).

## CRUD genérico
Crea una sola vez y reutiliza:
- `useResource<T>(name)` → `list`, `get`, `create`, `update`, `remove`, `reorder` contra `/api/v1/admin/{name}`.
- `<ResourceList>`: búsqueda, filtro publicado/oculto, filas arrastrables (`vuedraggable`/`@vueuse/integrations/useSortable`) que al soltar llaman `reorder`, switch de publicar inline, menú de acciones.
- `<ResourceForm>`: recibe un **esquema de campos** declarativo:
```ts
const fields: FieldDef[] = [
  { key: 'title', label: 'Título', type: 'text', required: true },
  { key: 'slug', label: 'URL', type: 'slug', from: 'title' },
  { key: 'kind', label: 'Tipo', type: 'select', options: portfolioKinds },
  { key: 'external_url', label: 'Enlace', type: 'url', showIf: f => f.kind !== 'own_audio' },
  { key: 'audio_after_media_id', label: 'Audio (Después)', type: 'media', accept: 'audio', showIf: f => f.kind === 'own_audio' },
  { key: 'audio_before_media_id', label: 'Audio (Antes) — habilita A/B', type: 'media', accept: 'audio' },
  { key: 'cover_media_id', label: 'Portada', type: 'media', accept: 'image', aspect: 1 },
  { key: 'services', label: 'Servicios', type: 'multiselect', source: 'services' },
  { key: 'credits_text', label: 'Créditos', type: 'text', hint: 'Ej. Mezcla y máster por Chemita' },
  { key: 'is_featured', label: 'Destacar en inicio', type: 'switch' },
]
```
  Tipos soportados: `text`, `textarea`, `markdown`, `richtext` (TipTap), `slug`, `url`, `email`, `phone`, `number`, `money`, `select`, `multiselect`, `switch`, `date`, `media`, `icon`, `json-list` (p. ej. redes).
- Validación: valibot en cliente + errores del backend mapeados a `fields`.

## Portafolio: ayudas inteligentes
- Al pegar una URL de Spotify/YouTube/SoundCloud/Apple Music/Bandcamp, detectar `kind` y `external_id`, y pedir al backend oEmbed para sugerir título, artista y portada.
- YouTube: aceptar `?t=137` y guardarlo en `youtube_start_s`.
- Si hay audio “Antes” y “Después”, mostrar mini ABPlayer de prueba dentro del form.

## Biblioteca de medios
- `<MediaPicker>`: pestañas “Subir” / “Biblioteca”; drag & drop; barra de progreso; tras subir, polling a `/admin/media/{id}` cada 1.5 s hasta `ready` (spinner “Procesando audio… calculando loudness”).
- Imágenes: recorte con aspecto sugerido por campo; `alt_text` obligatorio antes de guardar.

## Ajustes del sitio
Formulario por pestañas siguiendo `SiteSettingsSchema` (`docs/sdd/03-modelo-datos.md`): Marca · Portada · Estudio · Secciones · Contacto y redes · SEO · Legal · Funciones. Guardar dispara revalidación.

## Leads (RF-24)
- Vista lista tipo bandeja: nombre, servicio, fuente (chip con `utm_source`), antigüedad (“hace 2 h”), estado con color.
- Filtros rápidos por estado (chips) y selector de fuente/servicio/fechas.
- Detalle: datos, mensaje, reproductor de la maqueta (endpoint privado), enlace de maqueta, UTM completos, línea de tiempo de `lead_events`, notas.
- Acciones: cambiar estado (menú), **Responder por correo** (mailto con plantilla: “Hola {nombre}, gracias por escribirnos sobre {servicio}…”), **WhatsApp** (`https://wa.me/<e164>?text=…`), Exportar CSV, Eliminar definitivamente (doble confirmación, explica que es por solicitud ARCO).

## Dashboard (RF-21)
Tarjetas: Leads nuevos (7 d), Tasa de cierre (ganados/(ganados+perdidos)), Top fuente del mes, Clics en /links (7 d). Gráficas: leads por fuente (barras), leads por semana (línea), top 5 piezas por reproducciones. Usa colores de la marca con suficiente contraste.

## Permisos
- `admin`: todo excepto Usuarios y ajustes “Funciones” técnicas.
- `superadmin`: todo.
- El backend es quien valida; el front solo oculta.
