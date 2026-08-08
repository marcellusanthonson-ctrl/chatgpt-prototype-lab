# Continuidad vigente del LAB

Estado: `DECISION_032_APPROVED_AUTHORIZATION_204_GRANTED_A0_AWAITING_VERIFIED_REMOTE_PUBLICATION`

## Foco temporal aprobado

Jonathan Martínez aprobó `DEC-LAB-032`. El LAB adopta `ENFORCEMENT_FIRST` como foco temporal no destructivo. Todas las líneas no terminales permanecen preservadas; no existe cancelación, suspensión, promoción ni cambio de estado de integración.

## Autorización activa condicionada

`AUTHORIZATION_LAB_GITHUB_GOVERNANCE_READ_ONLY_PREFLIGHT_204` está concedida y solo se vuelve ejecutable cuando `DEC-LAB-032` y la propia autorización estén presentes en un HEAD remoto verificado de `main`.

A0 es estrictamente de solo lectura. Su máximo resultado es establecer viabilidad para diseñar una autorización A1 separada. No autoriza ninguna mutación del repositorio ni del control plane de GitHub.

## Portafolio preservado

- Contextual Bootstrap: autorización 203 consumida y bloqueada; benchmark creado, no validado y no ejecutado.
- Product Leadership (`INT-LAB-004`): candidato no activo y no integrado; 187, 192 y 196 consumidas; no existe autorización de retest.
- Software Solution Engineering (`INT-LAB-005`): candidato no activo; autorización 180 preservada sin consumir pero bloqueada y no ejecutable bajo el foco temporal.
- Codex Desktop operating model: estándar documental publicado; benchmark operacional pendiente.
- Todas las demás líneas no terminales: preservadas por `DEC-LAB-032`.

## Divergencias preservadas

`CURRENT_STATE.json`, `PROJECT_STATE.json`, registros agregados y vistas de readiness continúan divergentes. No fueron reconciliados porque `DEC-LAB-032` reserva esa fase hasta después de un A1 operacionalmente aprobado y exitoso.

## Autoridad

- Decisión normativa: `DEC-LAB-032`, aprobada.
- Autorización: 204, concedida para A0 read-only.
- A0 iniciado: no.
- A1: no autorizado.
- Cambios de settings, rulesets, branch protection, workflows, Actions, CODEOWNERS, colaboradores, aplicaciones y credenciales: no autorizados.
- Modelos, integraciones, runtime, producto y repositorios externos: no autorizados.

## Próxima acción única

Verificar la publicación remota y ejecutar A0 desde ese nuevo HEAD aplicando `VERIFY_LIVE_AT_USE`.
