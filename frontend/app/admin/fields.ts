export type FieldType =
  | 'text'
  | 'textarea'
  | 'markdown'
  | 'slug'
  | 'url'
  | 'email'
  | 'phone'
  | 'number'
  | 'money'
  | 'select'
  | 'multiselect'
  | 'switch'
  | 'date'
  | 'media'
  | 'icon'
  | 'json-list'

export interface FieldOption {
  value: string
  label: string
}

export interface FieldDef {
  key: string
  label: string
  type: FieldType
  required?: boolean
  hint?: string
  from?: string
  options?: FieldOption[]
  source?: 'services' | 'team' | 'portfolio'
  accept?: 'image' | 'audio'
  aspect?: number
  showIf?: (form: Record<string, unknown>) => boolean
}

export interface AdminSection {
  api: string
  title: string
  singular: string
  empty: string
  label: (row: Record<string, unknown>) => string
  meta: (row: Record<string, unknown>) => string
  fields: FieldDef[]
  preview?: (row: Record<string, unknown>) => string
}

function options(pairs: [string, string][]): FieldOption[] {
  return pairs.map(([value, label]) => ({ value, label }))
}

const icons = options([
  ['composicion', 'Composición'],
  ['grabacion', 'Grabación'],
  ['mezcla', 'Mezcla'],
  ['master', 'Máster'],
  ['producciones', 'Producciones'],
  ['beat-making', 'Beat making'],
  ['podcast', 'Podcast'],
  ['post-audiovisual', 'Post audiovisual'],
])

const kinds = options([
  ['own_audio', 'Audio propio'],
  ['spotify', 'Spotify'],
  ['youtube', 'YouTube'],
  ['soundcloud', 'SoundCloud'],
  ['apple_music', 'Apple Music'],
  ['bandcamp', 'Bandcamp'],
])

export const sections: Record<string, AdminSection> = {
  servicios: {
    api: 'services',
    title: 'Servicios',
    singular: 'servicio',
    empty: 'Aún no hay servicios. Agrega el primero.',
    label: (row) => String(row.title ?? ''),
    meta: (row) => String(row.slug ?? ''),
    preview: (row) => `/servicios/${String(row.slug ?? '')}`,
    fields: [
      { key: 'title', label: 'Título', type: 'text', required: true },
      { key: 'slug', label: 'URL', type: 'slug', from: 'title', required: true },
      {
        key: 'number_label',
        label: 'Número',
        type: 'text',
        hint: 'Ej. 01. Si lo dejas vacío, se asigna solo.',
      },
      { key: 'icon', label: 'Ícono', type: 'icon', options: icons, required: true },
      {
        key: 'short_description',
        label: 'Descripción corta',
        type: 'textarea',
        required: true,
        hint: 'Máximo 180 caracteres. Sale en la tarjeta.',
      },
      { key: 'long_description', label: 'Descripción larga', type: 'markdown', required: true },
      { key: 'image_media_id', label: 'Imagen', type: 'media', accept: 'image', aspect: 1.4 },
      {
        key: 'price_from_mxn',
        label: 'Precio desde (MXN)',
        type: 'money',
        hint: 'Se guarda, pero no se publica en el sitio.',
      },
      { key: 'seo_title', label: 'Título SEO', type: 'text' },
      { key: 'seo_description', label: 'Descripción SEO', type: 'textarea' },
      { key: 'is_published', label: 'Publicado', type: 'switch' },
    ],
  },
  equipo: {
    api: 'team',
    title: 'Equipo',
    singular: 'integrante',
    empty: 'Aún no hay integrantes. Agrega el primero.',
    label: (row) => String(row.full_name ?? ''),
    meta: (row) => String(row.role_label ?? ''),
    preview: (row) => `/equipo/${String(row.slug ?? '')}`,
    fields: [
      { key: 'full_name', label: 'Nombre', type: 'text', required: true },
      { key: 'nickname', label: 'Cómo le dicen', type: 'text', required: true },
      { key: 'slug', label: 'URL', type: 'slug', from: 'full_name', required: true },
      { key: 'role_label', label: 'Rol', type: 'text', required: true },
      { key: 'bio_short', label: 'Bio corta', type: 'textarea', required: true },
      { key: 'bio_long', label: 'Bio larga', type: 'markdown' },
      { key: 'photo_media_id', label: 'Foto', type: 'media', accept: 'image', aspect: 1 },
      {
        key: 'socials',
        label: 'Redes',
        type: 'json-list',
        hint: 'Una por línea: instagram https://…',
      },
      { key: 'is_published', label: 'Publicado', type: 'switch' },
    ],
  },
  portafolio: {
    api: 'portfolio',
    title: 'Portafolio',
    singular: 'pieza',
    empty: 'Aún no hay piezas. Agrega la primera.',
    label: (row) => String(row.title ?? ''),
    meta: (row) => `${String(row.artist_name ?? '')} · ${String(row.kind ?? '')}`,
    preview: (row) => `/portafolio/${String(row.slug ?? '')}`,
    fields: [
      { key: 'title', label: 'Título', type: 'text', required: true },
      { key: 'artist_name', label: 'Artista', type: 'text', required: true },
      { key: 'slug', label: 'URL', type: 'slug', from: 'title', required: true },
      { key: 'kind', label: 'Tipo', type: 'select', options: kinds, required: true },
      {
        key: 'external_url',
        label: 'Enlace',
        type: 'url',
        showIf: (form) => form.kind !== 'own_audio',
      },
      {
        key: 'audio_after_media_id',
        label: 'Audio (Después)',
        type: 'media',
        accept: 'audio',
        showIf: (form) => form.kind === 'own_audio',
      },
      {
        key: 'audio_before_media_id',
        label: 'Audio (Antes) — habilita A/B',
        type: 'media',
        accept: 'audio',
      },
      { key: 'cover_media_id', label: 'Portada', type: 'media', accept: 'image', aspect: 1 },
      { key: 'service_ids', label: 'Servicios', type: 'multiselect', source: 'services' },
      { key: 'year', label: 'Año', type: 'number' },
      { key: 'genre', label: 'Género', type: 'text' },
      {
        key: 'credits_text',
        label: 'Créditos',
        type: 'text',
        hint: 'Ej. Mezcla y máster por Chemita',
      },
      { key: 'description', label: 'Descripción', type: 'markdown' },
      { key: 'is_featured', label: 'Destacar en inicio', type: 'switch' },
      { key: 'is_ab_featured', label: 'Destacar en Escucha la diferencia', type: 'switch' },
      { key: 'is_published', label: 'Publicado', type: 'switch' },
    ],
  },
  testimonios: {
    api: 'testimonials',
    title: 'Testimonios',
    singular: 'testimonio',
    empty: 'Aún no hay testimonios. Agrega el primero.',
    label: (row) => String(row.author_name ?? ''),
    meta: (row) => String(row.project_label ?? ''),
    fields: [
      { key: 'quote', label: 'Cita', type: 'textarea', required: true },
      { key: 'author_name', label: 'Nombre', type: 'text', required: true },
      { key: 'author_role', label: 'Rol', type: 'text', hint: 'Ej. Cantautor' },
      { key: 'project_label', label: 'Proyecto', type: 'text' },
      { key: 'photo_media_id', label: 'Foto', type: 'media', accept: 'image', aspect: 1 },
      { key: 'portfolio_item_id', label: 'Pieza relacionada', type: 'select', source: 'portfolio' },
      { key: 'is_published', label: 'Publicado', type: 'switch' },
    ],
  },
  preguntas: {
    api: 'faqs',
    title: 'Preguntas',
    singular: 'pregunta',
    empty: 'Aún no hay preguntas. Agrega la primera.',
    label: (row) => String(row.question ?? ''),
    meta: (row) => (row.service_id ? 'De un servicio' : 'General'),
    fields: [
      { key: 'question', label: 'Pregunta', type: 'text', required: true },
      { key: 'answer', label: 'Respuesta', type: 'markdown', required: true },
      {
        key: 'service_id',
        label: 'Servicio',
        type: 'select',
        source: 'services',
        hint: 'Vacío = pregunta general.',
      },
      { key: 'is_published', label: 'Publicado', type: 'switch' },
    ],
  },
  enlaces: {
    api: 'links',
    title: 'Enlaces',
    singular: 'enlace',
    empty: 'Aún no hay enlaces. Agrega el primero.',
    label: (row) => String(row.label ?? ''),
    meta: (row) => String(row.url ?? ''),
    preview: () => '/links',
    fields: [
      { key: 'label', label: 'Texto', type: 'text', required: true },
      { key: 'url', label: 'URL', type: 'url', required: true },
      { key: 'icon', label: 'Ícono', type: 'text', hint: 'instagram, mail, music…' },
      { key: 'is_internal', label: 'Es una página del sitio', type: 'switch' },
      { key: 'highlight', label: 'Destacar', type: 'switch' },
      { key: 'starts_at', label: 'Visible desde', type: 'date' },
      { key: 'ends_at', label: 'Visible hasta', type: 'date' },
      { key: 'is_published', label: 'Publicado', type: 'switch' },
    ],
  },
}

export function slugify(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}
