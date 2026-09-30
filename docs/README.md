# Documentación — Cherry Studios

## Por qué SDD (y no ODD)

Elegimos **Spec‑Driven Development**: primero una especificación clara (qué, para quién, criterios de aceptación), luego un plan técnico y una lista de tareas que un agente como Cursor ejecuta una por una. Encaja mejor que un enfoque orientado a resultados (ODD) porque:

- El trabajo lo implementará un agente de IA: necesita requisitos verificables y un orden explícito, no solo objetivos.
- El diseño ya está aprobado (template de los chicos): el riesgo no es “qué construir” sino construirlo fiel, administrable y desplegable.
- Los **resultados de negocio** (leads, conversión por red social) sí quedan como objetivos medibles dentro de la spec y del dashboard, así que tomamos lo mejor de ODD sin su ambigüedad.

## Estructura

```
docs/
├── sdd/
│   ├── 00-constitucion.md       Principios y Definición de Terminado
│   ├── 01-especificacion.md     Requisitos RF-xx con criterios de aceptación (Fases 1–3)
│   ├── 02-arquitectura.md       Stack, decisiones, estructura, caché, medios, seguridad
│   ├── 03-modelo-datos.md       Tablas, campos, seed
│   ├── 04-api.md                Endpoints públicos, auth, admin
│   ├── 05-plan-tareas.md        T-01…T-29 en orden, con casillas
│   ├── 06-despliegue.md         Compose, env vars, Caddy, CI/CD, respaldos, checklist de lanzamiento
│   └── 07-preguntas-abiertas.md Decisiones pendientes y supuestos
├── skills/                      Skills (formato Agent Skills: SKILL.md con frontmatter)
│   ├── sdd-workflow/            Cómo trabajar el ciclo spec → tarea → verificación
│   ├── cherry-brand-ui/         Identidad visual, componentes y tono de voz
│   ├── nuxt-frontend/           Convenciones Nuxt 4 / Vue
│   ├── fastapi-backend/         Convenciones FastAPI / SQLAlchemy / worker
│   ├── admin-cms/               Patrón del panel administrable
│   ├── docker-deploy/           Contenedores, Caddy, CI/CD, respaldos
│   └── seo-performance/         SEO, OG para redes, JSON-LD, Core Web Vitals, UTM
└── prompts/
    └── cursor-kickoff.md        Prompts listos para pegar en Cursor
```

## Diferenciadores frente a otros estudios

| Diferenciador | Qué resuelve | Fase |
|---------------|--------------|------|
| **Comparador Antes/Después (A/B)** con volumen igualado | El artista *escucha* lo que Cherry aporta, no lo imagina | 1 |
| **Reproductor persistente** que sigue sonando al navegar | El portafolio se vive como una playlist | 1 |
| **Link‑in‑bio propio** con métricas | Sustituye Linktree y mide qué red convierte | 1 |
| **Leads con origen (UTM) + mini‑CRM** | Saber qué publicación trajo proyectos reales | 1 |
| **Subida de maqueta en el formulario** | Cotizaciones más rápidas y precisas | 1 |
| **Vistas previas OG generadas con la marca** | Cada link compartido se ve profesional | 1 |
| **Cotizador guiado** | Resuelve “¿cuánto cuesta?” sin llamada | 2 |
| **Solicitud de sesión con disponibilidad** | Menos ida y vuelta por WhatsApp | 2 |
| **Revisiones de mezcla comentadas al segundo** | Experiencia tipo plataforma profesional para clientes | 3 |

## Uso con Cursor
1. Abre el repo en Cursor. La regla `.cursor/rules/cherry-sdd.mdc` (siempre activa) y `AGENTS.md` hacen que el agente lea la spec y los skills.
2. Si tu versión de Cursor soporta Agent Skills nativos, puedes copiar `docs/skills/*` a `.cursor/skills/` (o `.claude/skills/` para Claude Code); el contenido es compatible.
3. Pega el prompt de `docs/prompts/cursor-kickoff.md` para arrancar el Hito 0.

## Siguiente documento previsto
`docs/marketing/` — plan de lanzamiento en redes sociales y círculos musicales (usa la convención UTM de `skills/seo-performance`).
