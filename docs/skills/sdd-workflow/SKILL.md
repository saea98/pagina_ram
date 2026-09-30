---
name: sdd-workflow
description: Flujo Spec-Driven Development del proyecto Cherry Studios. Úsalo SIEMPRE antes de implementar, modificar o planear cualquier funcionalidad del repo pagina_ram, para saber qué leer, cómo elegir la siguiente tarea y cómo cerrarla.
---

# Flujo SDD — Cherry Studios

Este repo se construye con **Spec-Driven Development**: la especificación en `docs/sdd/` es la fuente de verdad; el código la implementa.

## Mapa de documentos

| Archivo | Úsalo para |
|---------|-----------|
| `docs/sdd/00-constitucion.md` | Principios no negociables y Definición de Terminado. Léelo una vez por sesión. |
| `docs/sdd/01-especificacion.md` | Qué construir: requisitos `RF-xx` con criterios de aceptación. |
| `docs/sdd/02-arquitectura.md` | Cómo: stack, estructura de carpetas, caché, medios, seguridad, presupuestos. |
| `docs/sdd/03-modelo-datos.md` | Tablas, campos, enums, seed. |
| `docs/sdd/04-api.md` | Endpoints y payloads. |
| `docs/sdd/05-plan-tareas.md` | Orden de trabajo `T-xx` con casillas. |
| `docs/sdd/06-despliegue.md` | Contenedores, env vars, Caddy, CI/CD, respaldos. |
| `docs/sdd/07-preguntas-abiertas.md` | Supuestos vigentes mientras el cliente decide. |
| `cherry-studios-site/` | Diseño aprobado (HTML/CSS/JS original). Referencia visual, no se despliega. |

## Ciclo por tarea

1. **Elegir**: toma la primera `T-xx` sin marcar en `05-plan-tareas.md` cuyas dependencias (tareas previas del mismo hito) estén hechas. Si el usuario pidió una tarea concreta, usa esa.
2. **Leer contexto mínimo**: los `RF-xx` que cita la tarea + la sección de arquitectura/datos/API relacionada + el skill del área:
   - UI pública → `cherry-brand-ui` y `nuxt-frontend`
   - Admin → `admin-cms` (+ `nuxt-frontend`)
   - API/BD/worker → `fastapi-backend`
   - Contenedores/CI/servidor → `docker-deploy`
   - Metadatos, rendimiento, JSON-LD → `seo-performance`
3. **Planear en voz alta** (breve): archivos a crear/modificar y cómo se verificará cada criterio de aceptación.
4. **Implementar** con tests junto al código (no al final).
5. **Verificar** contra la DoD de la constitución: tests, lint, tipos, `docker compose up`, textos en español MX.
6. **Cerrar**: marca `[x]` en `05-plan-tareas.md`, y si algo de la spec cambió o se descubrió, actualiza el documento correspondiente **en el mismo commit**.
7. **Commit** con Conventional Commits en inglés referenciando IDs: `feat(portfolio): persistent global player (T-14, RF-03)`.

## Reglas

- **No inventes requisitos.** Si algo no está especificado y afecta al usuario final, agrégalo a `07-preguntas-abiertas.md` con un supuesto razonable y sigue.
- **Si la spec y el código difieren, gana la spec** — salvo que la spec sea claramente un error; entonces corrige la spec primero y explica por qué en el commit.
- **No cambies el stack** (Nuxt 4, FastAPI, PostgreSQL, Caddy, Docker Compose) sin actualizar `02-arquitectura.md` y avisar al usuario.
- **Contenido nunca hardcodeado** en componentes públicos: viene de la API (excepto microcopys de UI genéricos como “Enviando…”).
- **Tareas grandes**: si una `T-xx` requiere > ~400 líneas de cambio, divídela en sub‑tareas `T-xx.a`, `T-xx.b` dentro del plan antes de empezar.
- **No toques** `cherry-studios-site/` salvo instrucción explícita.

## Plantilla de resumen al terminar una tarea

```
T-xx · <título> — HECHO
RF cubiertos: RF-..
Cambios: <archivos clave>
Cómo verificar: <comandos / URL>
Pendientes o supuestos nuevos: <si aplica, con referencia a 07-preguntas-abiertas>
```
