# Ejecución, eficiencia y briefs

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: docs/MODEL_OPERATING_RULES.md; schemas/brief.schema.json; docs/BRIEF_PRESERVATION_AND_VERSIONING_POLICY.md
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
- No repetir contexto del brief en la respuesta, pero sí preservarlo en el artefacto canónico.
- No producir resúmenes genéricos.
- Recomendar una sola acción.

## Brief JSON

Priorizar JSON para Claude y Codex. Incluir `task_id`, objetivo, repositorios, ramas, HEAD, autoridad, `authorization_ref`, scope, `forbidden_actions`, `source_refs`, `required_outputs`, `acceptance_checks`, `stop_conditions` y `response_contract`.

Transmitir el contexto mínimo suficiente para ejecutar, sin borrar el contexto material acumulado. Un resumen de ejecución no reemplaza al briefing completo que lo origina.

## Preservación y versionado obligatorios

Todo briefing creado debe documentarse y publicarse en el repositorio canónico correspondiente.

Un briefing sucesor debe declarar su parent, fuentes, contenido preservado, adiciones, modificaciones, eliminaciones autorizadas y omisiones detectadas. No puede sustituir silenciosamente información más completa por una formulación más breve o menos sólida.

La relación válida es:

`SUCCESSOR_CONTENT = PRESERVED_PARENT_CONTENT + APPROVED_ADDITIONS + EXPLICITLY_AUTHORIZED_CHANGES`

Toda omisión material detectada se clasifica `OMITTED_IN_ERROR` y bloquea ejecución hasta su restauración.

El contenido aportado directamente por Jonathan Martínez debe preservarse como artefacto fuente antes de crear una versión derivada. La política completa está en `docs/BRIEF_PRESERVATION_AND_VERSIONING_POLICY.md`.

## Cierre

Validar antes de publicar, verificar el remoto después y registrar la autorización como consumida cuando corresponda. Un briefing documentado no crea por sí solo autoridad de ejecución.
