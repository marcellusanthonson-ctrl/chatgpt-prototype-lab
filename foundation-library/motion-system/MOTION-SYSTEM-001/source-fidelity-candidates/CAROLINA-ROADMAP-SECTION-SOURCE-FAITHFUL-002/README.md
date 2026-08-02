# CAROLINA-ROADMAP-SECTION-SOURCE-FAITHFUL-002

Sucesor aislado de `CAROLINA-ROADMAP-SOURCE-FAITHFUL-001`. Contiene exclusivamente `.ca-roadmap-editorial` del commit fuente fijo `52654da574952148f96d051e439bff1cbc7b4b9d`.

Estado: `HUMAN_APPROVED_SOURCE_FIDELITY`.

Jonathan Martínez aprobó explícitamente la fidelidad de fuente el 2 de agosto de 2026 después de completar la revisión real mediante `localhost`. La revisión confirmó el recorrido íntegro, la paridad visual entre baseline y candidato, la liberación inmediata después del terminal cap y la disposición responsive alternada de las tarjetas al superar el breakpoint aplicable.

Los gates automatizados permanecen registrados: 64 estados, 16 pares de píxeles, SSIM mínimo 1.0, cero diferencias de estilos computados, geometría, eje, concentricidad, solicitudes externas, fallos de aislamiento y overflow horizontal.

Abra `HUMAN_COMPARISON.html` para reproducir la superficie de revisión. Usa un único scroll exterior, mantiene ambos paneles sincronizados, mide el rango vivo después de `load`, `document.fonts.ready` y la estabilización dinámica, y libera el panel sticky con un margen técnico de 16 px una vez confirmado el estado terminal real.

La extracción aislada excluye las secciones posteriores de la landing. Como la fórmula fuente depende de un trigger situado al `64%` del viewport, el visor agrega únicamente un espaciador invisible de contexto de revisión, calculado en vivo, para reconstruir el rango de desplazamiento que aporta la landing completa. No modifica `REFERENCE_IMPLEMENTATION.html`, la fórmula del efecto ni el repositorio Carolina.

La aprobación de fidelidad de fuente **no** autoriza por sí sola:

- designar el candidato como referencia canónica activa;
- reemplazar artefactos canónicos;
- extraer o publicar un behavior core reusable;
- promover una adaptación neutral;
- integrar el efecto en un producto;
- modificar `marcellusanthonson-ctrl/carolina-md-next-landing`.

Cualquiera de esas acciones requiere una autorización explícita separada.
