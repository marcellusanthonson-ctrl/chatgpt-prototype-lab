# Ejecución, eficiencia y briefs

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: docs/MODEL_OPERATING_RULES.md; schemas/brief.schema.json
Authority-Effect: NONE

## Orden técnica

Toda ejecución que modifique estado identifica objetivo, resultado esperado, agente, repositorio, rama, HEAD, paths, acciones permitidas y prohibidas, validaciones, condiciones de detención, commit y push.

Una aprobación normativa no reemplaza autorización técnica.

## Continuidad de ejecución

Con autorización suficiente:

- continuar hasta completar el alcance;
- resolver correcciones menores internas sin pedir otra confirmación;
- preguntar solo por decisiones materiales, autoridad faltante, riesgo irreversible o contradicción canónica;
- no detenerse por preguntas no bloqueantes.

## Tiempo y tokens

- Agrupar lecturas, búsquedas y validaciones.
- No releer si el HEAD no cambió.
- No narrar operaciones rutinarias.
- Comunicar hitos, desviaciones, bloqueos y resultados.
- No repetir contexto del brief.
- No producir resúmenes genéricos.
- Recomendar una sola acción.

## Brief JSON

Priorizar JSON para Claude y Codex. Incluir `task_id`, objetivo, repositorios, ramas, HEAD, autoridad, `authorization_ref`, scope, `forbidden_actions`, `source_refs`, `required_outputs`, `acceptance_checks`, `stop_conditions` y `response_contract`.

Transmitir el contexto mínimo suficiente, no la historia completa.

## Cierre

Validar antes de publicar, verificar el remoto después y registrar la autorización como consumida.
