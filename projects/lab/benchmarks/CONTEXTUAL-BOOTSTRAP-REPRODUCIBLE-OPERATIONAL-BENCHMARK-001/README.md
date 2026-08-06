# CONTEXTUAL-BOOTSTRAP-REPRODUCIBLE-OPERATIONAL-BENCHMARK-001

Estado: `CREATED_NOT_VALIDATED_NOT_EXECUTED`

Instrumento operacional reproducible creado desde cero bajo la autorización 202. No es una reemisión del benchmark 198 y no reutiliza su corpus, runner ni oracle recuperado.

## Alcance

El paquete define 20 tareas: una de desarrollo y una held-out para cada una de diez clases materiales. Evalúa routing, riesgo, estado terminal, autoridad, política de HEAD, conflictos, namespace, selección de fuentes, restricciones críticas y reducción de contexto.

## Separación obligatoria

- `corpus/TASKS.jsonl` es el corpus visible.
- `oracle/PRIVATE_ORACLE.json` es un oracle nuevo y separado.
- `runner/run_benchmark.py` fue creado pero no ejecutado.
- `VALIDATION_PLAN.json` y `FUTURE_EXECUTION_PLAN.json` requieren autorizaciones posteriores.
- Toda prueba figura `NOT_RUN`.

## Límites

Este paquete no valida el instrumento, no evalúa resolver 001, no crea resolver 002, no remedia defectos, no ejecuta Codex/modelos y no autoriza integración.
