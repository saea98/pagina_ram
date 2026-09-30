# 07 · Preguntas abiertas y supuestos

> Decisiones que dependen de Chemita, Ramzy o de la infraestructura. Mientras no se respondan, el agente implementa el **supuesto** indicado (y es fácil cambiarlo después).

| # | Pregunta | Supuesto actual | Impacto si cambia |
|---|----------|-----------------|-------------------|
| Q1 | ¿Se muestran precios (“Desde $X”)? | Campo existe pero vacío → no se muestra. | Ninguno (solo contenido). |
| Q2 | Número de WhatsApp del estudio | Campo vacío → botón oculto. | Ninguno. |
| Q3 | ¿Dirección física visible / mapa? | No se muestra (solo “Ciudad de México”). | Agregar sección y `address` en JSON‑LD. |
| Q4 | Servidor destino (proveedor, specs, ¿ya tiene Docker?) | VPS Ubuntu 24.04, 2 vCPU/4 GB. | Ajustar límites y respaldos. |
| Q5 | Proveedor de correo SMTP | Brevo (plan gratuito 300/día). | Solo variables de entorno. |
| Q6 | ¿El correo `contacto@` está en Google Workspace / Zoho / otro? | Se conserva; el SMTP transaccional usa `no-reply@`. | Configurar SPF/DKIM correctamente. |
| Q7 | ¿Más piezas de portafolio y testimonios reales para el lanzamiento? | Se lanza con las 3 actuales; testimonios ocultos si no hay. | Contenido. |
| Q8 | ¿Tienen maquetas “antes” de alguna pieza para el A/B? | Sección A/B oculta hasta que exista al menos una. | Contenido; es el diferenciador más fuerte, conviene conseguir 1–2. |
| Q9 | ¿Quieren calendario de sesiones (Fase 2) con Google Calendar? | Fase 2. | Modelo `availability_blocks`. |
| Q10 | ¿TikTok, YouTube, Spotify del estudio? | Solo Instagram. | Settings. |
| Q11 | Mención “Ocho formas de trabajar tu proyecto” vs. 7 opciones en el select del template | El select se genera de la API (8 servicios + “Aún no estoy seguro”). | — |
