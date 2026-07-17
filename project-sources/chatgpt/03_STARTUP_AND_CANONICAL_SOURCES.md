# Inicio y fuentes canónicas

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: METHODOLOGY.md; CURRENT_STATE.json; registry/index.json
Authority-Effect: NONE

## Reconstrucción

1. Verificar repositorio, rama y HEAD remoto.
2. Leer `LAB_CONTRACT.md`.
3. Leer `METHODOLOGY.md`.
4. Leer `CURRENT_STATE.json`.
5. Leer `registry/index.json` y `registry/projects.json`.
6. Identificar el proyecto activo.
7. Leer `PROJECT_STATE.json`.
8. Leer decisiones y autorizaciones.
9. Leer errores, pendientes y roadmap.
10. Leer evidencia, patrones y continuidad vigente.

Markdown se consulta después del JSON.

## Política de HEAD

- `VERIFY_LIVE_AT_USE`: resolver el HEAD de `main` al comenzar cada uso material.
- El LAB no almacena su propio HEAD como estado vigente porque el commit que lo contiene lo vuelve obsoleto.
- Un HEAD histórico debe identificarse como parent, baseline o evidencia, nunca como HEAD actual.
- No asumir que un HEAD recordado o conversacional sigue vigente.

## Reglas

- No sustituir el repositorio por memoria conversacional o archivos adjuntos.
- No presentar reportes históricos como estado actual.
- Conservar `source_refs`.
- Declarar contradicciones y detener solo la acción afectada.
- Si GitHub no está disponible, informar la limitación y no inventar.
- Usar `registry/index.json` para descubrir registros; una búsqueda libre no basta.

El estado operativo se obtiene exclusivamente desde GitHub.
