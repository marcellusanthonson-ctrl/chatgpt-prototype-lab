# ChatGPT Prototype LAB

Repositorio canónico de gobierno, autoridad, decisiones, continuidad y auditoría entre proyectos.

## Inicio

Leer:

1. LAB_CONTRACT.md.
2. METHODOLOGY.md.
3. CURRENT_STATE.json.
4. registry/index.json.
5. PROJECT_STATE.json del proyecto activo.

Para el proyecto ChatGPT, comenzar en `project-sources/chatgpt/START_HERE.md`. La introducción configurable solo debe apuntar al repositorio, rama y entrypoint.

## Modelo v2

Cada proyecto mantiene estado, roadmap, pendientes y registros dedicados de decisiones, ideas e integraciones. Los proyectos activos pueden agregar experimentos, autorizaciones, errores, evidencia, briefs y continuidad.

JSON es canónico. Markdown es una vista humana. La propiedad de cada dato está definida en docs/CANONICAL_OWNERSHIP.md.

## Operación de modelos

docs/MODEL_OPERATING_RULES.md exige ejecución continua dentro del alcance, preguntas solo ante bloqueos materiales, independencia analítica y respuestas orientadas a deltas. docs/ERRORS_TO_AVOID.md registra fallas que no deben repetirse.

## Continuidad

Cuando se solicita continuar en otra conversación, aplicar docs/CONTINUITY_PROTOCOL.md y entregar CURRENT_CONTINUITY.json, ATTACHMENT_MANIFEST.json y START_PROMPT.md.

## Validación

Ejecutar:

```bash
python scripts/validate_repository.py
```

La validación comprueba JSON, claves duplicadas, registros, estados, referencias, estructura por proyecto, briefs, continuidad, reevaluaciones, propiedad canónica e índices.

## Límites

El LAB no autoriza runtime, integración, releases, despliegues ni cambios de producto. Jonathan Martínez es el único aprobador.
