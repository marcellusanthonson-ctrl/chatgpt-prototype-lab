# CAROLINA-ROADMAP-SECTION-SOURCE-FAITHFUL-002

Sucesor aislado de `CAROLINA-ROADMAP-SOURCE-FAITHFUL-001`. Contiene exclusivamente `.ca-roadmap-editorial` del commit fuente fijo `52654da574952148f96d051e439bff1cbc7b4b9d`.

Estado: `HUMAN_REVIEW_PENDING_LIVE_SCROLL_RANGE_REPAIR_READY_AUTOMATED_GATES_PASS`. Los gates automatizados no constituyen aprobación humana, reemplazo canónico, promoción reusable ni integración de producto.

Abra `HUMAN_COMPARISON.html` para la revisión completa. La superficie usa un único scroll exterior, mantiene ambos paneles fijos y sincronizados y mide el rango vivo después de `load`, `document.fonts.ready` y la estabilización dinámica del timeline.

La extracción aislada excluye las secciones posteriores de la landing. Como la fórmula fuente depende de un trigger situado al `64%` del viewport, el visor agrega únicamente un espaciador invisible de contexto de revisión, calculado en vivo, para reconstruir el rango de desplazamiento que aporta la landing completa. No modifica `REFERENCE_IMPLEMENTATION.html`, la fórmula del efecto ni el repositorio Carolina.

La barra solo debe alcanzar `100%` cuando, en ambos paneles, el tercer nodo está activo, el timeline contiene `is-end-active`, el terminal cap está en verde petróleo y `scrollTop` coincide con el máximo vivo. El encabezado debe mostrar `Terminal cap confirmado en ambos paneles`.

Si el navegador bloquea el acceso coordinado entre archivos locales, sirve esta carpeta mediante un servidor local o usa un navegador que permita acceso entre archivos del mismo directorio. El enlace de fallback abre la referencia aislada únicamente para inspección visual parcial; por sí sola no contiene el contexto posterior de la landing completa.
