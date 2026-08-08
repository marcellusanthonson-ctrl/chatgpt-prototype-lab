# Protocolo de respuesta textual para autorizaciones

Document-Role: CANONICAL_GOVERNANCE_PROTOCOL
Protocol-ID: LAB-AUTHORIZATION-APPROVAL-RESPONSE-PROTOCOL-001
Approved-By: Jonathan Martínez
Approval-Source: projects/lab/sources/USER_SOURCE_AUTHORIZATION_211_20260807.md
Effective-Authorization: AUTHORIZATION_LAB_AUTHORIZATION_APPROVAL_PROTOCOL_AND_GITHUB_GOVERNANCE_204_210_RECONCILIATION_211
Authority-Effect: NONE_BY_ITSELF

## Regla obligatoria

Toda solicitud de autorización de ejecución debe terminar con un bloque textual completo, autocontenido y copiable para que Jonathan Martínez pueda responderlo textualmente.

No se considera correctamente solicitada una autorización de ejecución si el bloque no está presente.

## Contenido mínimo del bloque

El bloque debe incluir, como mínimo:

1. `AUTHORIZATION_ID` exacto y previamente verificado como único.
2. `APPROVED_BY = Jonathan Martínez`.
3. repositorio y rama afectados cuando corresponda;
4. `EXPECTED_PARENT_HEAD` o baseline exacto aplicable;
5. `HEAD_POLICY`;
6. `AUTHORIZATION_STATUS = GRANTED`;
7. alcance positivo expresado con campos explícitos `= YES`;
8. exclusiones materiales expresadas con campos explícitos `= NO`;
9. permisos de commit, push, pull request, merge, publicación, settings, workflows, rulesets, credenciales, runtime, producto e integraciones cuando sean aplicables;
10. `EXPECTED_RESULT`;
11. una frase final inequívoca `AUTORIZO <AUTHORIZATION_ID> EN LOS TÉRMINOS EXACTOS INDICADOS ARRIBA.`

## Fail closed

Una autorización no debe tratarse como `GRANTED` cuando:

- falta el bloque;
- el ID no coincide;
- el parent/baseline cambió antes de la respuesta;
- la respuesta es parcial, ambigua o modifica materialmente el alcance;
- faltan exclusiones necesarias para delimitar la autoridad;
- el usuario responde únicamente con una expresión genérica que no reproduce o confirma inequívocamente el script solicitado.

Una modificación material del script constituye una nueva propuesta o contraoferta de alcance y debe reconciliarse antes de ejecutar.

## Regla de HEAD

El agente verifica `VERIFY_LIVE_AT_USE` antes de emitir el script. Si el HEAD relevante cambia antes de recibir la aprobación textual, el script anterior queda obsoleto y debe regenerarse con el nuevo baseline.

## Persistencia

La aprobación textual recibida debe preservarse como fuente humana y enlazarse desde la autorización canónica. El artifact de autorización debe indicar `grant_inferred: false`.

## Solicitud y ejecución

Una propuesta, un script preparado o una autorización con estado `PROPOSED` no permite ejecutar. Sólo la respuesta textual inequívoca de Jonathan, preservada y compatible con el baseline vigente, puede producir `GRANTED`.

Las autorizaciones consumidas, revocadas, expiradas o rechazadas no pueden reutilizarse.

## Formato

El template canónico está en `templates/AUTHORIZATION_APPROVAL_RESPONSE.template.txt`.

La representación estructurada mínima está definida por `schemas/authorization-approval-response.schema.json`.

## Presentación al usuario

Cuando ChatGPT solicite autorización, el script debe aparecer al final de la respuesta, sin texto sustantivo posterior que pueda volver ambiguo qué debe confirmar Jonathan.
