# Estado actual del LAB

La fuente estructurada es `CURRENT_STATE.json`.

- Versión: 2.5.14.
- Fase: `CHATGPT_CRITERION_LAYER_INTEGRATED_DOCUMENTARY_SELECTIVE`.
- Aprobador: Jonathan Martínez.
- HEAD propio: `VERIFY_LIVE_AT_USE`.
- Autorización activa reutilizable: ninguna.

## Capa de criterio para ChatGPT

`CHATGPT-CRITERION-LAYER-001@1.0.0` está integrada documentalmente mediante `DEC-LAB-016` e `INT-LAB-001`. Su fuente operativa es `project-sources/chatgpt/08_CRITERION_LAYER.md`.

El selector activa de forma contextual evidencia y claims, criterio de diseño, accesibilidad web y preferencia visual. La capa referencia las fuentes canónicas y no duplica sus contenidos.

## Límites

La integración no modifica pesos del modelo, no implementa RAG, embeddings, base vectorial, runtime ni Symphonie. No instala skills, no ejecuta tecnologías de asistencia y no establece conformidad WCAG.

La validación determinista de contrato y fixtures pasa. La evaluación empírica solicitada con Terra 5.6 LIGHT quedó `NOT_EXECUTED_MODEL_SURFACE_UNAVAILABLE`; por tanto, no existe un claim de comportamiento validado para ese modelo.

## Siguiente transición

Observar y evaluar la capa en respuestas reales del proyecto. Cualquier mutación posterior requiere una autorización nueva y explícita.
