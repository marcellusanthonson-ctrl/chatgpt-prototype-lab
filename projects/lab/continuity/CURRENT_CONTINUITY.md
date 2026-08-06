# Continuidad vigente del LAB

Estado: `AUTHORIZATION_203_GRANTED_INDEPENDENT_BENCHMARK_VALIDATION_AWAITING_CODEX_A_EXECUTION`

## Autoridad activa

La autorización `AUTHORIZATION_LAB_INDEPENDENT_REPRODUCIBLE_BENCHMARK_INSTRUMENT_VALIDATION_203` está concedida y limitada exclusivamente a validar el instrumento `CONTEXTUAL-BOOTSTRAP-REPRODUCIBLE-OPERATIONAL-BENCHMARK-001`.

- Codex Desktop A: ejecutor técnico primario.
- Claude: auditor independiente read-only después del cierre de Codex A.
- Codex Desktop B: replay independiente en una sesión y worktree nuevos.
- ChatGPT: coordinación, reportes posteriores a cada intento terminal y reconciliación canónica.

## Estado del instrumento

El paquete continúa `CREATED_NOT_VALIDATED_NOT_EXECUTED`. La autorización 203 no presupone PASS y no permite modificar el benchmark.

Todas las pruebas `VAL-001` a `VAL-009` permanecen `NOT_RUN`.

## Límites

No se autoriza:

- ejecutar o modificar resolver 001 o 002;
- usar Codex o cualquier modelo como sujeto del benchmark operacional;
- corregir findings durante la validación;
- mutar el paquete del benchmark;
- integrar, desplegar o cambiar producto/runtime;
- declarar equivalencia con 198;
- aprobar operacionalmente un resolver;
- reconciliar vistas agregadas fuera de los registros 203.

El acceso al oracle convierte a Codex A, Claude y Codex B en inelegibles para operar un futuro blind run del resolver sobre el split held-out.

## Secuencia obligatoria

1. Codex Desktop A ejecuta sus controles en un worktree limpio.
2. ChatGPT entrega el reporte obligatorio del intento.
3. Claude audita read-only.
4. ChatGPT entrega el reporte obligatorio de la auditoría.
5. Codex Desktop B ejecuta el replay independiente sin reutilizar estado de A.
6. ChatGPT reconcilia y publica el resultado terminal.

No se inicia el siguiente operador antes del reporte del anterior.

## Estado de aprobación

`NOT_APPROVED`

Un eventual PASS de 203 validaría únicamente el instrumento. No validaría ni autorizaría un resolver o integración.

## Divergencias preservadas

`CURRENT_STATE.json`, `projects/lab/PROJECT_STATE.json`, `registry/index.json`, `PEND-LAB-048` y Product Leadership readiness continúan desactualizados y fuera del alcance.

## Única siguiente acción

Ejecutar el brief de Codex Desktop A en un worktree limpio y devolver su `TERMINAL_REPORT.json` antes de iniciar Claude.
