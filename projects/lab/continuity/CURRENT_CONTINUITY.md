# Continuidad actual — Fábrica estandarizada de integraciones

Fecha: 2026-07-30T17:19:00-04:00  
Repositorio: `marcellusanthonson-ctrl/chatgpt-prototype-lab`  
Rama: `main`  
Política HEAD: `VERIFY_LIVE_AT_USE`  
HEAD padre verificado durante la generación: `fb9c0d22fba7e45fc4f22f4a296e4df2c892a47c` — referencia histórica; verificar nuevamente en la nueva conversación.

## Primera lectura obligatoria

1. Verificar el HEAD remoto vigente de `main`.
2. Leer `project-sources/chatgpt/START_HERE.md`.
3. Seguir exactamente el orden indicado allí.
4. Leer después `CURRENT_CONTINUITY.json`, este archivo y `ATTACHMENT_MANIFEST.json`.

## Línea de desarrollo vigente

Se documentó una fábrica estandarizada para acelerar nuevas integraciones sin debilitar gobierno, evidencia, rollback, pruebas ni trazabilidad.

La arquitectura tiene estas restricciones aprobadas:

- núcleo neutral respecto de proveedor y tecnología;
- stack seleccionado por proyecto, no stack global obligatorio;
- posibilidad futura de stacks preferidos solo cuando exista evidencia acumulada entre proyectos;
- AWS utilizado como entorno de validación de referencia, nunca como dependencia obligatoria ni selección automática de producción;
- `PORTABLE_OPERATIONAL_TRUST_PREFLIGHT` condicional antes de una prueba funcional cuando existan infraestructura, escrituras, credenciales, persistencia, costes, límites de seguridad o teardown;
- una prueba o auditoría no crea autorización, activación ni integración.

## Trabajo completado

- `STANDARDIZED_INTEGRATION_FACTORY_001` documentado, no implementado.
- `PORTABLE_OPERATIONAL_TRUST_STANDARD_001` documentado.
- `AWS_OPERATIONAL_TRUST_REFERENCE_PROFILE_001` documentado como adaptador reemplazable.
- Política de neutralidad tecnológica y futuro registro de confianza documentados.
- Catálogo de schemas, catálogo de templates y plan de migración documentados.
- M0 completado con cuatro módulos, 27 señales distintas, seis reglas de composición, un bloque de exclusión y 13 fixtures congelados mediante Git blob SHA.
- M1 ejecutado y cerrado como bloqueado con evidencia.

## Estado M1

Los archivos `INTEGRATION_PACKAGE_SCHEMA_SET_001.json` e `INTEGRATION_TEMPLATE_CATALOG_001.json` son catálogos descriptivos. Todavía no existen los artefactos ejecutables que nombran.

Resultado:

```text
ALL_COMMON_SCHEMAS_VALID = BLOCKED
ALL_PROFILE_OVERLAYS_RESOLVE = BLOCKED
NO_AUTHORITY_INFERENCE = PASS
M1 = BLOCKED
M2 = NOT_READY_AND_NOT_AUTHORIZED
```

Pendiente canónico: `projects/lab/pending/PEND-LAB-033.json`.

La resolución exige:

- seleccionar y declarar un dialecto JSON Schema ejecutable;
- materializar 10 schemas comunes;
- materializar 13 templates comunes;
- materializar 3 overlays de `CRITERION_MODULE`;
- conservar templates de autorización solo como borradores incapaces de conceder autoridad;
- generar cuatro paquetes aislados para los módulos actuales;
- ejecutar validación mecánica reproducible y repetir M1 antes de M2.

## SSE: línea separada

`AUTHORIZATION_LAB_SSE_TEST_EXECUTION_AND_READ_ONLY_AUDIT_147` continúa en estado `GRANTED`, pero la prueba no ha comenzado.

Contrato SSE:

- 32 fixtures;
- 3 brazos;
- mínimo 96 outputs;
- scoring ciego y auditoría externa read-only;
- SSE permanece inactivo y no integrado.

Esta autorización no desbloquea M1, no autoriza M1A, no permite seleccionar stack o infraestructura y no permite activar ni integrar SSE.

## Autoridad

- Autorizaciones 148–151: consumidas en sus alcances documentales.
- Autorización 147: concedida para la prueba SSE separada, todavía no iniciada.
- M1A: no autorizado.
- M2 y registro shadow: no autorizados.
- Selector activo, comportamiento de ChatGPT y runtime: sin autorización de modificación.
- AWS, Terraform, provisioning, selección de stack o proveedor: no autorizados para esta línea.

## Divergencias que el nuevo modelo debe reconocer

`CURRENT_STATE.json`, `PROJECT_STATE.json` y varios punteros de `registry/index.json` están detrás de los deltas recientes 147–152. Deben leerse como bases canónicas complementadas por los registros y deltas posteriores, no como inventario exhaustivo de la situación actual.

No debe confundirse la autorización SSE 147 con autoridad para continuar la migración de la fábrica.

## Riesgos

- declarar ejecutables simples catálogos descriptivos;
- comenzar M2 antes de un M1 mecánicamente validado;
- acoplar el estándar portable a AWS u otro proveedor;
- imponer un stack global sin evidencia entre proyectos;
- mezclar resultados SSE con la migración de la fábrica;
- convertir generación, prueba o auditoría en autoridad implícita.

## Siguiente acción única

Preparar y someter a autorización explícita un brief Codex delimitado para `M1A_EXECUTABLE_SCHEMA_TEMPLATE_AND_OVERLAY_MATERIALIZATION`, con validación mecánica reproducible y prohibición de modificar el selector activo, crear el registro shadow, comenzar M2 o producir efectos de runtime.
