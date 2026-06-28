# Current State

Document-ID: `lab.current-state`
Version: `0.1.0`
Status: `ACTIVE`
Last-Updated: `2026-06-28`

## Active laboratory objective

Establecer una memoria externa versionada para conservar propuestas, errores, decisiones, experimentos y patrones reutilizables entre conversaciones.

## Current phase

`BOOTSTRAP`

## Approved constraints

- Repositorio dedicado y separado de productos.
- GitHub es la fuente de verdad documental.
- No guardar secretos.
- Los registros no autorizan ejecución.
- Codex permanece exclusivamente ejecutor.
- No registrar intercambios triviales.

## Decisions in force

- `DEC-LAB-001`: estructura aprobada.
- `DEC-LAB-002`: GitHub como memoria externa.
- `DEC-LAB-003`: protocolo de continuidad.

## Open problems

- Completar publicación y validación del bootstrap.
- Definir política de ramas para futuras actualizaciones.

## Pending proposals

- `PROP-LAB-001`: validación mediante JSON Schema.
- `PROP-LAB-002`: resumen de continuidad por sesión.

## Applicable patterns

- `PAT-LAB-001`: registrar eventos, no transcripciones.
- `PAT-LAB-002`: separar estados.
- `PAT-LAB-003`: lectura en orden fijo.
- `PAT-MA-001`: Codex ejecutor sin autoridad autónoma.

## Last validated result

La estructura documental y el protocolo de continuidad fueron aprobados el 28 de junio de 2026.

## Next authorized action

Validar la publicación inicial y comenzar a incorporar conocimiento confirmado del laboratorio.

## Continuity read order

1. `LAB_CONTRACT.md`
2. `CURRENT_STATE.md`
3. `registry/projects.json`
4. estado del proyecto activo
5. decisiones vigentes
6. errores abiertos
7. patrones aplicables
8. sesión más reciente relacionada
