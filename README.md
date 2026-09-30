# pagina_ram — Cherry Studios

Sitio web administrable para **Cherry Studios**, estudio de producción musical en Ciudad de México.
*“Que la emoción te lleve a donde la mente no puede.”*

- **Frontend:** Nuxt 4 (Vue 3, TypeScript, Tailwind v4) — sitio público con SSR + panel `/admin`
- **Backend:** FastAPI + PostgreSQL 17 + worker de procesamiento de audio/imagen
- **Infra:** Docker Compose + Caddy (HTTPS automático), CI/CD con GitHub Actions → GHCR

## Estado
📐 Fase de especificación. La implementación se hace con Cursor siguiendo `docs/`.

## Empezar
1. Lee [`docs/README.md`](docs/README.md) — por qué SDD, estructura y diferenciadores.
2. Especificación completa en [`docs/sdd/`](docs/sdd/).
3. Instrucciones para agentes en [`AGENTS.md`](AGENTS.md) y skills en [`docs/skills/`](docs/skills/).
4. Prompts para arrancar en Cursor: [`docs/prompts/cursor-kickoff.md`](docs/prompts/cursor-kickoff.md).

## Carpetas
| Carpeta | Contenido |
|---------|-----------|
| `cherry-studios-site/` | Template de diseño aprobado (referencia visual; no se despliega) |
| `docs/` | Especificación SDD, skills y prompts |
| `frontend/`, `backend/`, `infra/` | Se crean en el Hito 0 (T-01) |
