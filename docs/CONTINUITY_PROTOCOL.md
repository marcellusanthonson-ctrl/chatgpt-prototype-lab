# Protocolo estándar de continuidad

Se activa cuando Jonathan solicita continuar un proyecto en otra conversación.

## Archivos

- continuity/CURRENT_CONTINUITY.json: fuente estructurada.
- continuity/CURRENT_CONTINUITY.md: vista humana.
- continuity/ATTACHMENT_MANIFEST.json: archivos y orden.
- continuity/START_PROMPT.md: primer mensaje listo para usar.
- continuity/archive/: paquetes reemplazados.

## Contenido obligatorio

Proyecto; fecha; repositorios, ramas y HEAD; orden de lectura; hechos; propuestas; ideas; integraciones posibles; decisiones; autorizaciones activas y consumidas; resultados; pendientes; errores; riesgos; experimentos; skills; roadmap; attachments; límites y una siguiente acción.

Todo elemento material debe incluir source_refs. Las transcripciones completas solo se adjuntan cuando son evidencia indispensable.

## Generación

1. Verificar HEAD.
2. Leer estado y registros canónicos.
3. Extraer información material no incorporada.
4. Clasificar cada elemento.
5. Construir manifiesto de attachments.
6. Generar la primera frase.
7. Validar referencias y marcar el paquete anterior ARCHIVED.
8. Si cambia un HEAD, marcar el paquete STALE.

## Primera respuesta del nuevo modelo

Debe presentar contexto reconstruido, HEAD verificados, estado, decisiones, autorizaciones, pendientes, divergencias y una siguiente acción. No debe ejecutar hasta identificar una autorización vigente.

## Reporte obligatorio posterior a cada prueba

Después de cada prueba o intento terminal ejecutado directamente por ChatGPT en la conversación o por Codex, se debe entregar a Jonathan un reporte de estado antes de iniciar otra prueba.

La obligación aplica a resultados `PASS`, `FAIL`, `BLOCKED`, `INSUFFICIENT_EVIDENCE`, cancelaciones y detenciones preventivas. Un conjunto de subpasos que forma una sola prueba puede recibir un reporte al cierre del intento; pruebas independientes requieren reportes independientes.

El reporte debe indicar como mínimo:

1. ID de la prueba, intento, fecha, ejecutor y entorno.
2. Objetivo, alcance autorizado y criterios de aprobación aplicables.
3. Resultado exacto y límites del claim.
4. Estado actual antes y después de la prueba.
5. Qué se consiguió y qué quedó demostrado.
6. Qué no se consiguió, defectos, bloqueos, riesgos y divergencias.
7. Evidencia verificable: métricas, artefactos, commits, PR, logs o hashes aplicables.
8. Pruebas ejecutadas y pruebas todavía pendientes.
9. Gates faltantes para completar la aprobación y estado de aprobación: `NOT_APPROVED`, `PARTIALLY_SATISFIED_AWAITING_TESTS` o `APPROVED`, según la evidencia y la decisión humana aplicable.
10. Estado de la autorización usada, consumo y autoridad residual.
11. Una única siguiente acción recomendada o autorizada.

Las pruebas no ejecutadas deben marcarse `NOT_RUN`; no pueden omitirse. Un reporte no convierte evidencia en aprobación ni crea autorización. Ningún agente puede declarar aprobación completa mientras existan pruebas o gates obligatorios pendientes.

## Proyecto ChatGPT

La introducción del proyecto ChatGPT referencia `project-sources/chatgpt/START_HERE.md`. Las reglas operativas se leen desde el repositorio; no se duplican como archivos adjuntos. Cualquier adjunto de bootstrap solo puede declarar repositorio, rama y entrypoint.

Al reconstruir continuidad, toda transición consumida declarada en `CURRENT_STATE.json` debe resolverse a un registro canónico en `registry/authorizations.json` mediante `state_key`.
