# Inicio y fuentes canónicas

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: METHODOLOGY.md; docs/MODEL_OPERATING_RULES.md; CURRENT_STATE.json; registry/index.json
Authority-Effect: NONE

## Reconstrucción

1. Verificar repositorio, rama y HEAD remoto.
2. Leer `LAB_CONTRACT.md`.
3. Leer `METHODOLOGY.md`.
4. Leer `docs/MODEL_OPERATING_RULES.md`.
5. Leer `CURRENT_STATE.json`.
6. Leer `registry/index.json` y `registry/projects.json`.
7. Identificar el proyecto activo y leer `PROJECT_STATE.json`.
8. Leer decisiones y autorizaciones owner.
9. Leer errores, pendientes, roadmap y evidencia aplicables.
10. Leer `CURRENT_CONTINUITY.json` y la sesión activa indicada para reconstruir posición de trabajo.
11. Leer las fuentes de ChatGPT en el orden del manifiesto.

Markdown se consulta después del JSON cuando ambos representan la misma vista.

## Política de HEAD

- `VERIFY_LIVE_AT_USE`: resolver el HEAD de `main` al comenzar cada uso material.
- El LAB no almacena su propio HEAD como estado vigente dentro del mismo commit.
- Un HEAD histórico se identifica como parent, baseline o evidencia, nunca como HEAD actual.
- No asumir que un HEAD recordado o conversacional sigue vigente.

## Propiedad y agregados

`CURRENT_STATE.json`, `PROJECT_STATE.json`, `ROADMAP.json`, `PENDING.json` y los registros son proyecciones para navegación. Ante divergencia, resolver el owner-artifact específico antes de afirmar estado. Los registros pueden usar un historical base inmutable más un current overlay.

## Trabajo y ramas

La posición actual se resuelve mediante `PROGRESSIVE_CONVERSATION_CONTINUITY_001`. Una rama lateral mantiene el `return_node` y no cambia el main track por inferencia. El foco se gobierna mediante `FOCUS_AND_ROADMAP_PRESERVATION_001`.

## Reglas

- No sustituir el repositorio por memoria conversacional o archivos adjuntos.
- No presentar reportes históricos como estado actual.
- Conservar `source_refs`.
- Declarar contradicciones y detener solo la acción afectada.
- Si GitHub no está disponible, informar la limitación y no inventar.
- Usar `registry/index.json` para descubrir registros; una búsqueda libre no basta.
- Aplicar GOV-007 antes de una instrucción material; su preview no crea autoridad.

El estado operativo se obtiene exclusivamente desde GitHub.
