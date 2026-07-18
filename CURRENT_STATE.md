# Estado actual del LAB

La fuente estructurada es CURRENT_STATE.json.

- Versión: 2.5.0.
- Fase: FOUNDATION_LIBRARY_DOCUMENTED_AND_VALIDATED.
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

Las cinco transiciones del LAB 013–017 y la autorización documental de schemas de Symphonie tienen registros `AUTH-*` canónicos. Cada registro declara `state_key`, permitiendo validar correspondencia exacta con `CURRENT_STATE.json`.

## Symphonie y decisiones

El LAB referencia el HEAD verificado `9de9dcf5c58583cd46bece41a0e772e3671801ff` de Symphonie, con 49 archivos y schemas canónicos para las fases 1, 2, 5, 6 y 7. Las decisiones `DEC-LAB-012` a `DEC-LAB-015` usan la envolvente canónica y el validador aplica `schemas/decision.schema.json` a todas las instancias registradas.

## Foundation Library

`registry/foundation-library.json` registra cinco arquetipos de diseño y nueve patrones backend. Cada arquetipo define tipografía, color, espaciado, grilla, cuatro rangos responsivos continuos, tokens de componentes, estados, accesibilidad y deltas permitidos. Los patrones backend definen interfaces, invariantes, estados, fallos, idempotencia, auditoría, seguridad y pruebas sin contener implementación.

El contrato de pagos es neutral al proveedor. Separa configuración sustituible por cliente de referencias administradas por entorno y prohíbe capturar o almacenar datos de tarjeta, secretos o credenciales.

## Autorización 019

`AUTHORIZATION_LAB_FOUNDATION_LIBRARY_019` quedó consumida por publicación verificable. Runtime, integración, RAG, producto, despliegue y release permanecen sin autorización.

## Siguiente transición

No existe acción autorizada. La siguiente recomendación es definir un protocolo documental de evidencia sintética para evaluar la Foundation Library antes de cualquier implementación.
