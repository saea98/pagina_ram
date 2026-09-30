---
name: cherry-brand-ui
description: Sistema de diseño e identidad de Cherry Studios (paleta cereza/crema, Fraunces + Work Sans, superficies, botones, microinteracciones y tono de voz). Úsalo al crear o modificar cualquier componente, página o texto visible del sitio público o del admin.
---

# Cherry Studios — marca y UI

La referencia visual aprobada es `cherry-studios-site/index.html`. **Se porta, no se rediseña.** Ante la duda, abre ese archivo y copia el comportamiento.

## Tokens (fuente de verdad → `frontend/app/assets/css/tokens.css`)

```css
:root{
  --ink:#1C1B1B;        /* texto principal, footer */
  --maroon:#3D0D11;     /* superficie oscura principal, nav */
  --maroon-2:#54141A;
  --cherry:#7E0F0D;     /* acentos, reverso de tarjetas */
  --cherry-2:#9E1613;   /* focus ring, cereza del riel */
  --blush:#FFBEC5;      /* CTA principal, acentos sobre oscuro */
  --cream:#FFF4EB;      /* texto sobre oscuro, superficie clara */
  --paper:#FFFAF5;      /* fondo base */
  --line-dark: rgba(255,244,235,0.18);
  --line-light: rgba(61,13,17,0.14);
  --shadow: 0 18px 40px rgba(61,13,17,0.22);
  --maxw: 1180px;
  --nav-h: 92px;
  --radius-card: 20px; --radius-pill: 999px; --radius-input: 12px;
}
```
Mapea en Tailwind v4 con `@theme { --color-maroon: var(--maroon); … }` para usar `bg-maroon`, `text-blush`, etc. **No introduzcas colores nuevos** sin agregarlos aquí primero. Para estados de error usa `#b3261e` (ya usado por el template).

## Tipografía

- **Fraunces** (serif, óptica variable 9–144; pesos 400–700; itálica 500/600) → `h1`, `h2`, `h3`, títulos de tarjetas, valores destacados. `text-wrap: balance`.
- **Work Sans** (400–800) → cuerpo, UI, botones, labels.
- Autoalojar ambas (`@nuxt/fonts` o archivos en `public/fonts`), subset latino.
- Escalas del template: hero `clamp(2.6rem, 7.4vw, 5.6rem)`, `h2.h-lg` `clamp(2rem, 4vw, 3.1rem)`, lede `1.08rem / 1.75`.
- `.eyebrow`: 0.76rem, `letter-spacing: .16em`, mayúsculas, 700.
- Itálica en `--blush` para palabras con emoción en titulares (“*nuestra cereza.*”).

## Superficies (alternan por sección)

| Clase | Fondo | Texto | Uso |
|-------|-------|-------|-----|
| `surface-maroon` | maroon | cream | Portafolio, tarjetas de contacto directo |
| `surface-cream` | cream | ink | Estudio, Servicios |
| `surface-blush` | blush | maroon | Equipo, Contacto |
| `surface-paper` | paper | ink | Páginas internas |

Secuencia de la portada: hero (foto+velo) → cream → blush → cream → maroon → (testimonios: paper) → blush → footer ink.

## Componentes base

- **Botones** (`.btn`, pastilla, 700, padding 15×28, hover `translateY(-2px)`): `btn-solid` (blush→cream), `btn-ghost` (borde cream 55 %), `btn-dark` (maroon→ink).
- **Nav**: fija, `rgba(61,13,17,.86)` + `backdrop-filter: blur(10px)`, links color blush con subrayado animado; CTA “Contacto” en pastilla blush.
- **Frame** de imagen: radio 20, sombra `--shadow`, etiqueta flotante (`frame-tag`).
- **Tarjeta de servicio**: flip 3D (`perspective:1400px`, `.6s cubic-bezier(.2,.7,.2,1)`), frente maroon, reverso cherry, `button[aria-pressed]`.
- **Embed card** (portafolio): fondo `rgba(255,244,235,.05)`, borde `--line-dark`, radio 18.
- **Inputs**: radio 12, borde `1.5px rgba(61,13,17,.25)`, focus borde cherry; labels en mayúsculas 0.78rem.
- **Riel de progreso** con **cereza SVG** (dos círculos cherry-2 + tallos maroon) — elemento de marca, conservarlo.
- **Pastilla “Aviso de privacidad”** fija abajo‑izquierda.
- **Íconos de servicios**: SVG de trazo 1.6 del template (`viewBox 0 0 40 40`, `stroke=currentColor`). Extráelos a `components/icons/` con nombres `composicion`, `grabacion`, `mezcla`, `master`, `producciones`, `beatmaking`, `podcast`, `post-audiovisual`.

### Componentes nuevos (mantener el mismo lenguaje)
- **GlobalPlayer**: barra inferior maroon 96 % con blur, waveform en blush (progreso) sobre `--line-dark`, botones pastilla. Alto 72 px; en móvil deja espacio para el botón de WhatsApp.
- **ABPlayer**: switch grande tipo pastilla con dos estados “Antes” (cream sobre ink) / “Después” (maroon sobre blush), etiqueta del estado activo en Fraunces itálica.
- **WhatsApp flotante**: círculo blush con ícono maroon, abajo‑derecha, no tapa la pastilla de privacidad.
- **Admin**: base `paper`, sidebar maroon, acentos cherry; misma tipografía. Denso pero amable.

## Movimiento

- Reveal al hacer scroll: `opacity 0→1`, `translateY(28px→0)`, `.7s ease`, umbral 0.12, una sola vez.
- Titular del hero: palabras con `animation-delay` escalonado (~70 ms).
- Parallax del hero: `translateY(scrollY * .18) scale(1.06)`.
- Splash: logo centrado que “vuela” al lugar del logo del nav (FLIP) en ~700 ms; **solo primera visita de la sesión**.
- **Siempre** envolver con `@media (prefers-reduced-motion: reduce)` para desactivar.

## Tono de voz (español de México)

- Cercano, de tú, cálido y artístico; habla de **emoción, proceso, identidad**. Nunca corporativo.
- Frases cortas. Ejemplos del template: “Cuéntanos de tu proyecto.”, “De la idea al máster.”, “Algo de lo que hemos hecho.”
- CTAs en primera persona del artista o imperativo suave: “Cuéntanos tu proyecto →”, “Escucha la diferencia”, “Cotizar este servicio”.
- Nombres: “Chemita” y “Ramzy” (con comillas tipográficas “ ” cuando van junto al nombre completo).
- Usa comillas tipográficas, raya (—) y flecha (→) como el template.

## Accesibilidad

- Contraste: blush sobre maroon y cream sobre maroon cumplen AA; **no** uses blush sobre cream para texto.
- Focus visible: `outline: 2px solid var(--cherry-2); outline-offset: 3px`.
- Todo `alt` en español y descriptivo (el template tiene buenos ejemplos).
- Objetivos táctiles ≥ 44 px.
