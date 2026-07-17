# Estado actual del LAB

La fuente estructurada es CURRENT_STATE.json.

- Versión: 2.3.1.
- Fase: AUTHORIZATION_REGISTRY_RECONCILED.
- Aprobador: Jonathan Martínez.
- Runtime, integración y cambios de producto: no autorizados.
- HEAD propio: verificar main en vivo; no almacenarlo como estado vigente.

## Corrección

ERR-LAB-006 registra dos findings del test con Terra 5.6 y razonamiento ligero:

- el HEAD propio del LAB no puede mantenerse dentro de su mismo commit;
- un claim cuyo núcleo es falso debe clasificarse REVERSED, no MODIFIED.

PROJECT_STATE.json usa VERIFY_LIVE_AT_USE y conserva verified_parent_head como evidencia de la baseline anterior.

## Fuentes del proyecto ChatGPT

Las reglas operativas del proyecto viven en `project-sources/chatgpt/` y se inician desde `START_HERE.md`. Los archivos adjuntos dejan de ser fuentes mantenibles y solo pueden usarse como punteros de bootstrap.

## Registro de autorizaciones

Las cinco transiciones consumidas 013–017 tienen registros `AUTH-*` canónicos. Cada registro declara `state_key`, permitiendo validar correspondencia exacta con `CURRENT_STATE.json`.

## Siguiente transición

No existe acción autorizada. La recomendación continúa siendo definir los schemas pendientes de Symphonie para las fases 1, 2, 5, 6 y 7.
