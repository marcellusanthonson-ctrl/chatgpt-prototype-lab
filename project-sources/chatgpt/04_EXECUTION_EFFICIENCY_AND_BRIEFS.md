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

Los briefs complejos deben incluir `learning_context` conforme a `schemas/brief-learning-context.schema.json`. Deben identificar el contrato transversal, las fuentes de incidentes aplicables, los controles preventivos obligatorios, la capacidad resolutiva y `LEARNING_APPLICATION_REPORT.json`.

Codex puede confirmar una recurrencia actual solo mediante evidencia observable. Puede adaptar el plan y corregir defectos menores únicamente dentro de la autoridad del brief. Un error histórico no prueba recurrencia; una recurrencia material no resoluble dentro de alcance obliga a detenerse.

Transmitir el contexto mínimo suficiente para ejecutar, sin borrar el contexto material acumulado. Un resumen de ejecución no reemplaza al briefing completo que lo origina.

## Codex Desktop y carga progresiva

Las ejecuciones creadas después de la autorización 194 usan `CODEX-DESKTOP-CONTEXT-OPTIMIZATION-001`:

1. `AGENTS.md` aporta únicamente reglas estables.
2. Un `EXECUTION_ENVELOPE` proyecta la tarea activa y referencia el brief completo y su digest.
3. Un perfil fija la función del hilo.
4. Un `CONTEXT_MANIFEST` decide qué leer inicialmente, filtrar, cargar por trigger o reservar para auditoría.
5. Los presupuestos miden líneas no vacías, bytes, tokens estimados, fuentes cargadas e incidentes aplicables.
6. El routing usa un hilo para tareas pequeñas y separa discovery, implementación, validación y auditoría únicamente cuando el riesgo lo exige.
7. El paralelismo se limita a trabajo independiente; los mismos paths, el estado y la publicación son secuenciales.
8. Toda afirmación de mejora de velocidad requiere benchmark operacional sin regresión de calidad o autoridad.

## Preservación y versionado obligatorios

Todo briefing creado debe documentarse y publicarse en el repositorio canónico correspondiente.

Un briefing sucesor debe declarar su parent, fuentes, contenido preservado, adiciones, modificaciones, eliminaciones autorizadas y omisiones detectadas. No puede sustituir silenciosamente información más completa por una formulación más breve o menos sólida.

La relación válida es:

`SUCCESSOR_CONTENT = PRESERVED_PARENT_CONTENT + APPROVED_ADDITIONS + EXPLICITLY_AUTHORIZED_CHANGES`

Toda omisión material detectada se clasifica `OMITTED_IN_ERROR` y bloquea ejecución hasta su restauración.

El contenido aportado directamente por Jonathan Martínez debe preservarse como artefacto fuente antes de crear una versión derivada. La política completa está en `docs/BRIEF_PRESERVATION_AND_VERSIONING_POLICY.md`.

Un execution envelope es una proyección operativa y no sustituye al brief completo.

## Cierre

Validar antes de publicar, verificar el remoto después y registrar la autorización como consumida cuando corresponda. Un briefing documentado no crea por sí solo autoridad de ejecución.
