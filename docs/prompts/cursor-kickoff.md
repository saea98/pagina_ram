# Prompts para Cursor

Úsalos en modo **Agent**. Uno por hito; revisa y haz commit entre cada uno.

---

## 1 · Arranque (Hito 0: T-01 a T-04)

```
Vamos a construir el sitio de Cherry Studios siguiendo Spec-Driven Development.

1. Lee AGENTS.md, docs/skills/sdd-workflow/SKILL.md y toda la carpeta docs/sdd/.
2. Lee docs/skills/docker-deploy/SKILL.md, docs/skills/fastapi-backend/SKILL.md y docs/skills/nuxt-frontend/SKILL.md.
3. Ejecuta las tareas T-01, T-02, T-03 y T-04 de docs/sdd/05-plan-tareas.md, en orden.
   - Antes de cada tarea, dime en 3-5 líneas qué archivos crearás y cómo lo verificarás.
   - Después de cada tarea, corre los comandos de verificación y marca la casilla.
4. Al final, dame el resumen con la plantilla del skill sdd-workflow y los comandos para levantar todo con docker compose.

No implementes nada fuera de esas tareas. Si algo no está especificado, agrégalo a docs/sdd/07-preguntas-abiertas.md con un supuesto y continúa.
```

## 2 · Datos y API pública (Hito 1: T-05 a T-09)

```
Continúa con el Hito 1 (T-05 a T-09) de docs/sdd/05-plan-tareas.md siguiendo el skill sdd-workflow.
Usa docs/sdd/03-modelo-datos.md y docs/sdd/04-api.md como contrato exacto.
Para el seed (T-07) toma textos, imágenes y audio de cherry-studios-site/ sin modificar esa carpeta.
Verifica cada tarea con pytest dentro de docker compose.
```

## 3 · Sitio público (Hito 2: T-10 a T-17)

```
Continúa con el Hito 2 (T-10 a T-17). Carga docs/skills/cherry-brand-ui/SKILL.md, nuxt-frontend y seo-performance.
La portada debe ser visualmente fiel a cherry-studios-site/index.html (ábrelo y compáralo sección por sección),
pero con todo el contenido proveniente de la API. Genera los tipos con pnpm gen:api antes de consumir endpoints.
Implementa el reproductor global persistente (T-14) y el comparador A/B (T-15) exactamente como indica el skill nuxt-frontend.
Ejecuta Playwright + axe al terminar cada página.
```

## 4 · Admin (Hito 3: T-18 a T-24)

```
Continúa con el Hito 3 (T-18 a T-24). Carga docs/skills/admin-cms/SKILL.md.
Construye primero el CRUD genérico (ResourceList, ResourceForm con FieldDef, MediaPicker) y luego aplícalo a cada recurso.
Prioriza que todo sea cómodo en un celular de 375 px.
```

## 5 · Producción (Hito 4: T-25 a T-29)

```
Continúa con el Hito 4 (T-25 a T-28). Carga docs/skills/docker-deploy/SKILL.md y docs/sdd/06-despliegue.md.
Deja listos docker-compose.prod.yml, Caddyfile, scripts deploy/backup/restore y los workflows de GitHub Actions.
Corre Lighthouse CI con los presupuestos y reporta resultados. No ejecutes T-29 (DNS) sin confirmación.
```

## Prompt de corrección (cuando algo no cumple)

```
La tarea T-xx no cumple el criterio "<criterio>" de RF-xx. Revisa la spec, explica la causa en 2 líneas,
corrige, agrega un test que lo cubra y vuelve a correr la DoD.
```
