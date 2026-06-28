# ChatGPT Prototype Lab

Repositorio canónico para la memoria externa, versionada y auditable del laboratorio de diseño, prototipado, integración y mejora continua dirigido por el usuario y asistido por ChatGPT.

## Propósito

Conservar de forma estructurada:

- propuestas;
- errores y sus causas;
- decisiones aprobadas;
- patrones reutilizables;
- experimentos exitosos y rechazados;
- estado operativo de proyectos;
- registros de continuidad entre conversaciones.

## Principios

1. GitHub es la fuente de verdad documental del laboratorio.
2. `CURRENT_STATE.md` es el punto de entrada para recuperar continuidad.
3. Las instrucciones críticas permanecen también en el Project de ChatGPT.
4. Una observación no equivale a una decisión aprobada.
5. El repositorio no autoriza cambios en código de producto.
6. Codex ejecuta únicamente órdenes explícitas, delimitadas y autorizadas.
7. No se almacenan secretos, credenciales ni datos personales innecesarios.

## Inicio rápido de continuidad

Leer, en este orden:

1. `LAB_CONTRACT.md`
2. `CURRENT_STATE.md`
3. `registry/projects.json`
4. archivo del proyecto activo en `projects/`
5. decisiones vigentes relacionadas;
6. errores abiertos;
7. patrones aplicables;
8. última sesión relevante.

## Tipos de registro

| Prefijo | Tipo |
|---|---|
| `PROP-*` | Propuesta |
| `ERR-*` | Error |
| `DEC-*` | Decisión |
| `PAT-*` | Patrón |
| `EXP-*` | Experimento |
| `SES-*` | Sesión |

## Estados

`observed`, `hypothesis`, `proposed`, `validated`, `approved`, `rejected`, `deprecated`, `superseded`, `resolved`.

## Versión inicial

- Repository schema: `0.1.0`
- Effective date: `2026-06-28`
