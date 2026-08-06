# Continuidad entre conversaciones

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Source: docs/CONTINUITY_PROTOCOL.md
Authority-Effect: NONE

## Activación

Aplicar cuando Jonathan solicite continuar un proyecto en otra conversación.

## Paquete

- `CURRENT_CONTINUITY.json`: fuente estructurada.
- `CURRENT_CONTINUITY.md`: vista humana.
- `ATTACHMENT_MANIFEST.json`: archivos y orden.
- `START_PROMPT.md`: primer mensaje.
- `archive/`: paquetes reemplazados.

## Contenido

Proyecto, fecha, repositorios, ramas, política de HEAD, orden de lectura, hechos, propuestas, ideas, decisiones, autorizaciones, resultados, pendientes, errores, riesgos, experimentos, skills, integraciones posibles, roadmap, referencias, prohibiciones, una siguiente acción y la primera frase.

Todo elemento material conserva `source_refs`. No copiar transcripciones completas salvo que sean evidencia indispensable.

## Generación

1. Verificar HEAD.
2. Leer estado y registros.
3. Detectar información material no incorporada.
4. Clasificarla.
5. Construir el manifiesto.
6. Generar `START_PROMPT.md`.
7. Validar referencias.
8. Archivar el paquete anterior.

Solo puede existir un paquete `CURRENT`. Si cambia un HEAD externo, marcarlo `STALE` o exigir verificación en vivo. Para el HEAD propio del LAB se usa siempre `VERIFY_LIVE_AT_USE`.

El nuevo modelo entrega HEAD, estado, decisiones, autorizaciones, pendientes, divergencias y una siguiente acción antes de ejecutar.

## Reporte posterior a cada prueba

Después de cada prueba o intento terminal ejecutado directamente por ChatGPT o por Codex, entregar a Jonathan un reporte antes de iniciar otra prueba.

El reporte identifica resultado, estado actual, logros, evidencia, defectos o bloqueos, pruebas pendientes, gates faltantes para completar la aprobación, estado de autorización y una sola siguiente acción. Las pruebas no ejecutadas se marcan `NOT_RUN`.

El formato y los límites completos están en `docs/CONTINUITY_PROTOCOL.md`. El reporte no crea aprobación ni autorización.
