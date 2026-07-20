# Estado actual del LAB

La fuente estructurada es CURRENT_STATE.json.

- Versión: 2.5.4.
- Fase: FOUNDATION_PILOT_DEFINED_NOT_EXECUTED.
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

## Protocolos de evidencia

`foundation-library/evidence/` contiene cinco matrices de arquetipos y nueve matrices backend. Los protocolos definen entradas sintéticas, procedimientos, mediciones, condiciones de aprobación, condiciones de fallo y evidencia futura a capturar.

Los protocolos de diseño cubren 320, 639, 640, 1023, 1024, 1439, 1440 y 1920 px, además de zoom, reflujo, teclado, foco, lector de pantalla, contraste, movimiento y estados. El protocolo de pagos añade doce fronteras específicas sobre cálculo en servidor, captura alojada, webhooks, duplicados, aislamiento y trazabilidad.

Todos los documentos están marcados `EVIDENCE_PROTOCOL_DEFINED_NOT_EXECUTED`. No constituyen evidencia de funcionamiento.

## Autorización 020

`AUTHORIZATION_LAB_FOUNDATION_EVIDENCE_PROTOCOL_020` quedó consumida por publicación verificable. Ninguna autorización de ejecución fue habilitada.

## Continuidad 021

`AUTHORIZATION_LAB_CONTINUITY_METADATA_021` reconcilia la referencia de Foundation Library con su versión canónica 1.1.0 y exige que la fecha del registro de autorizaciones nunca sea anterior a la de sus registros. La fase y la transición recomendada no cambian.

## RAG transversal 022

`architecture/rag/FEDERATION_CONTRACT.json` define un servicio lógico federado sobre namespaces aislados LAB, Symphonie y PROJECT. La autoridad y el estado canónico se resuelven antes de la similitud semántica; cada resultado requiere trazabilidad a repositorio, ruta y commit.

El índice se define exclusivamente como caché derivado de solo lectura. Tool Calling puede emitir propuestas tipadas, pero validación y autorización activa son obligatorias antes de cualquier commit. El contrato está `DOCUMENTED_NOT_IMPLEMENTED`: no existen embeddings, almacenamiento vectorial, Node.js, API ni integración operativa.

## Piloto Premium E-commerce 023

`PILOT-PREMIUM-ECOMMERCE-001` selecciona el arquetipo `PREMIUM_ECOMMERCE` para el concepto completamente sintético Terra Volta. Codex figura como `BOUNDED_EXECUTOR_ONLY` y no recibe autoridad autónoma.

El brief, delta, fixtures y matriz de aceptación están definidos y fijan el arquetipo y su protocolo por commit y hash. El piloto permanece `DEFINED_NOT_EXECUTED`: no existe interfaz, aplicación, navegador, backend ni validación visual.

## Siguiente transición

No existe acción autorizada. La siguiente recomendación es seleccionar un único arquetipo o patrón como piloto y delimitar por separado su futura autorización de ejecución.

## Preferencia visual y protocolo 041

`AUTHORIZATION_LAB_VISUAL_PREFERENCE_AND_HIFI_PROTOCOL_041` quedó consumida
solo para documentación y validación. El perfil personal de Jonathan Martinez
es evidencia separada de la gobernanza global y el protocolo exige tres
direcciones visuales, revisión humana y el gate
`HIGH_FIDELITY_VISUAL_BASELINE_APPROVED`. No autoriza HTML, CSS, JavaScript,
runtime, RAG, cambios de producto, despliegue ni release.
