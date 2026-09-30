# AGENTS.md — Cherry Studios (pagina_ram)

Instrucciones para agentes de código (Cursor, Claude Code, Codex, etc.).

## Qué es este repo
Sitio web administrable del estudio musical **Cherry Studios** (CDMX): Nuxt 4 (Vue) + FastAPI + PostgreSQL, todo en contenedores Docker detrás de Caddy.

## Cómo trabajar aquí (obligatorio)
Este proyecto usa **Spec‑Driven Development**.

1. Lee `docs/skills/sdd-workflow/SKILL.md` antes de cualquier cambio.
2. La especificación vive en `docs/sdd/` (constitución → especificación → arquitectura → datos → API → tareas → despliegue).
3. Trabaja la siguiente tarea sin marcar de `docs/sdd/05-plan-tareas.md`, salvo que el usuario pida otra.
4. Carga el skill del área antes de programar:

| Área | Skill |
|------|-------|
| Marca, UI, textos visibles | `docs/skills/cherry-brand-ui/SKILL.md` |
| `frontend/` | `docs/skills/nuxt-frontend/SKILL.md` |
| `backend/` | `docs/skills/fastapi-backend/SKILL.md` |
| Panel `/admin` | `docs/skills/admin-cms/SKILL.md` |
| `infra/`, Dockerfiles, CI | `docs/skills/docker-deploy/SKILL.md` |
| Metadatos, OG, JSON‑LD, rendimiento | `docs/skills/seo-performance/SKILL.md` |

5. Al terminar: DoD de `docs/sdd/00-constitucion.md`, marca la casilla, commit convencional con IDs (`feat(api): public leads endpoint (T-09, RF-07)`).

## Reglas rápidas
- La referencia visual es `cherry-studios-site/` (no modificar, no desplegar).
- UI en español de México; código y commits en inglés.
- Ningún contenido de negocio hardcodeado: todo sale de la API.
- No cambies el stack sin actualizar `docs/sdd/02-arquitectura.md`.
- Nunca commitear `.env` ni secretos.

## Comandos
```bash
# Levantar todo en local
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build
# Backend
cd backend && uv run pytest -q && uv run ruff check . && uv run mypy app
# Frontend
cd frontend && pnpm lint && pnpm typecheck && pnpm test
```
