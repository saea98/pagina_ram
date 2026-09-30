# 00 · Constitución del proyecto

> Principios no negociables. Si una tarea, spec o sugerencia del agente contradice este documento, **gana este documento**. Cambiarlo requiere acuerdo explícito del equipo (anotar en `CHANGELOG` de docs).

## Propósito

Construir el sitio de **Cherry Studios** (estudio de producción musical, CDMX) como un producto propio, administrable por los fundadores (Chemita y Ramzy) sin tocar código, que:

1. Convierta visitas en **proyectos cotizados** (leads calificados).
2. Haga que el **sonido** del estudio sea lo protagonista (el portafolio se escucha, no solo se lee).
3. Se diferencie de la competencia con herramientas que otros estudios no tienen (A/B antes-después, cotizador, reproductor persistente).
4. Esté listo para campañas en redes (links rastreables, página link‑in‑bio, vistas previas bonitas al compartir).

## Principios

1. **Spec primero.** Nada se implementa sin requisito en `01-especificacion.md` y tarea en `05-plan-tareas.md`. Si falta, se agrega primero a la spec.
2. **La identidad visual es la del template.** `cherry-studios-site/` es la referencia de diseño aprobada por los chicos. Se moderniza la arquitectura, **no** la marca. Paleta, tipografías, tono y microinteracciones se conservan (ver skill `cherry-brand-ui`).
3. **Todo contenido es administrable.** Ningún texto de negocio, servicio, integrante, pieza de portafolio, testimonio, enlace o dato de contacto queda “hardcodeado” en el frontend. Viene de la API.
4. **Español de México** en toda la interfaz pública y del admin. Código, nombres de variables y commits en inglés.
5. **Rendimiento y SEO son requisitos, no extras.** Presupuestos en `02-arquitectura.md §Presupuestos`. Un PR que los rompe no se integra.
6. **Accesible por defecto.** WCAG 2.2 AA; `prefers-reduced-motion` respetado en toda animación (el template ya lo hace; se mantiene).
7. **Privacidad conforme a la LFPDPPP.** Consentimiento explícito en formularios, aviso de privacidad editable desde el admin, datos de leads solo accesibles para administradores, sin rastreadores de terceros sin aviso.
8. **Contenedores de punta a punta.** Lo que corre en local con `docker compose` es lo mismo que corre en el servidor. Sin pasos manuales no documentados.
9. **Seguridad básica sin excusas.** Secretos solo por variables de entorno, HTTPS obligatorio, contraseñas con Argon2, rate‑limit en endpoints públicos, validación en backend aunque exista en frontend.
10. **Simple antes que ingenioso.** Monorepo, un solo frontend (Nuxt) que sirve sitio público + admin, un solo backend (FastAPI), una base de datos (PostgreSQL). Nada de microservicios.

## Definición de “terminado” (DoD) para cualquier tarea

- [ ] Cumple los criterios de aceptación de la historia en la spec.
- [ ] Tests pasan (`pytest` backend, `vitest` frontend; e2e si la tarea lo indica).
- [ ] Lint y tipos limpios (`ruff`, `mypy`, `eslint`, `vue-tsc`).
- [ ] Funciona dentro de `docker compose up` (no solo en local “a mano”).
- [ ] Textos visibles en español MX, sin lorem ipsum.
- [ ] Si agrega variables de entorno, están en `.env.example` y en `06-despliegue.md`.
- [ ] La casilla correspondiente en `05-plan-tareas.md` se marca `[x]`.
