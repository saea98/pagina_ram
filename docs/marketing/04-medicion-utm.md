# 04 · Medición y enlaces con UTM

> El sitio guarda los UTM de la primera visita de la sesión en cada lead (RF-07). Así se sabe qué red, qué publicación y qué alianza trajo proyectos reales.

## Convención

| Parámetro | Valores permitidos | Ejemplo |
|-----------|--------------------|---------|
| `utm_source` | `instagram`, `tiktok`, `youtube`, `google`, `qr`, `email`, `escuela-<nombre>`, `foro-<nombre>`, `referido`, `meta-ads` | `instagram` |
| `utm_medium` | `bio`, `story`, `reel`, `post`, `dm`, `perfil`, `flyer`, `masterclass`, `paid` | `story` |
| `utm_campaign` | `lanzamiento-2026`, `sesion-cereza-<mes>`, `cotizacion`, `alianzas`, `siempre` | `lanzamiento-2026` |
| `utm_content` | Código de pieza o variante: `s1-r1`, `b-02`, `flyer-a` | `b-02` |

Reglas: minúsculas, sin acentos ni espacios (usar guiones), no inventar valores nuevos sin agregarlos aquí.

## Enlaces listos

Dominio base: `https://cherrystudios.com.mx`

| Uso | Enlace |
|-----|--------|
| Bio de Instagram | `/links` (el sitio agrega `utm_source=instagram&utm_medium=bio` a los enlaces internos) |
| Stories de lanzamiento | `/?utm_source=instagram&utm_medium=story&utm_campaign=lanzamiento-2026` |
| Respuesta rápida de DM | `/?utm_source=instagram&utm_medium=dm&utm_campaign=cotizacion#contacto` |
| Sesión Cereza (convocatoria) | `/?utm_source=instagram&utm_medium=story&utm_campaign=sesion-cereza-<mes>#contacto` |
| Flyer / sticker QR | `/links?utm_source=qr&utm_medium=flyer&utm_campaign=siempre&utm_content=flyer-a` |
| Perfil de Empresa en Google | `/?utm_source=google&utm_medium=perfil&utm_campaign=siempre` |
| Masterclass en escuela | `/?utm_source=escuela-<nombre>&utm_medium=masterclass&utm_campaign=alianzas` |
| Referidos | `/?utm_source=referido&utm_medium=dm&utm_campaign=siempre&utm_content=<cliente>` |
| Anuncios Meta | `/?utm_source=meta-ads&utm_medium=paid&utm_campaign=lanzamiento-2026&utm_content=<anuncio>` |
| Firma de correo | `/?utm_source=email&utm_medium=firma&utm_campaign=siempre` |

## Revisión quincenal (30 minutos)

Los lunes de las semanas 2, 4, 6 y 8. Llenar esta tabla con datos del admin (Leads → exportar CSV) y de Instagram Insights:

| Métrica | Sem 2 | Sem 4 | Sem 6 | Sem 8 |
|---------|-------|-------|-------|-------|
| Leads nuevos (total) | | | | |
| Leads por fuente: instagram / qr / escuela / referido / google / otros | | | | |
| Leads → contactado en < 48 h (%) | | | | |
| Proyectos ganados | | | | |
| Clics en `/links` | | | | |
| Reel con más envíos (código) | | | | |
| Carrusel con más guardados (código) | | | | |
| Alcance a no seguidores (%) | | | | |
| Seguidores nuevos | | | | |
| Gasto en anuncios (MXN) / leads de `meta-ads` | | | | |

**Preguntas de la revisión:**
1. ¿Qué pilar trae leads, no solo vistas? → hacer más de ese.
2. ¿Qué pieza tuvo más envíos? → hacer una variante (o probarla como reel de prueba si la cuenta tiene acceso a esa función).
3. ¿Hay leads sin respuesta? → nadie espera más de 48 h.
4. ¿La meta de 60 días sigue siendo razonable? → ajustar.

## Instagram: qué mirar

- **Envíos (shares/sends) y guardados**: la señal más fuerte de distribución para reels.
- **Alcance a no seguidores**: indica si el contenido se está recomendando fuera de la comunidad.
- **Visitas al perfil → toques en el enlace**: conversión del perfil.
- **Reels de prueba (trial reels)**: se muestran primero a no seguidores. Úsenlos para probar ganchos distintos del mismo antes/después **cuando la cuenta tenga acceso** (Instagram lo habilita a cuentas profesionales públicas desde cierto número de seguidores).

Fuentes: [Metricool: Instagram Trial Reels](https://metricool.com/instagram-trial-reels/) · [Metricool: guía de Reels 2026](https://metricool.com/instagram-reels-guide/)
