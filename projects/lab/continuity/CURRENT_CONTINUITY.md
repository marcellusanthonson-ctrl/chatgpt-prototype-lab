# LAB continuity — autorización 198 consumida, benchmark operacional FAIL crítico

Canonical repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`  
Branch: `main`  
Entrypoint: `project-sources/chatgpt/START_HERE.md`  
HEAD policy: `VERIFY_LIVE_AT_USE`

## Estado alcanzado

La autorización 198 fue aprobada, ejecutada y publicada mediante el PR 58. La publicación del benchmark quedó verificada en `main` en `ab957cfa4f33fce41aca34bd5adc957ea32a409b`.

Estado: `CONSUMED_VERIFIED_REMOTE_PUBLICATION`  
Autoridad activa: `NONE`  
Autoridad residual: `NONE`

## Resultado

`CONTEXTUAL_BOOTSTRAP_RESOLVER_001` terminó el benchmark shadow sobre paths reales del LAB con `REAL_REPOSITORY_BENCHMARK_FAIL_CRITICAL`.

- 21 tareas y 126 iteraciones;
- macro path F1 `0.925243`;
- recall de restricciones críticas `0.935484`;
- precisión de prohibiciones `1.0`;
- reducción mediana de bytes representados `70.045%`;
- reducción mediana de fuentes `75%`;
- 16 issues críticos y 2 no críticos.

## Defectos críticos

1. Un cambio pequeño de código que contenía la palabra “estado” fue clasificado como consulta de estado/autoridad.
2. La ruta `STATUS_OR_AUTHORITY` omitió continuidad vigente y lifecycle de autorización.
3. Dos conflictos materiales fueron tratados como `READ_ONLY_READY` en vez de `RESOLUTION_REQUIRED`.
4. Casos de auditoría omitieron lifecycle o estado agregado requerido y seleccionaron evidencia no relacionada.
5. `STATUS_OR_AUTHORITY` redujo solo `14.104%` de bytes en la mediana.

## Controles que sí pasaron

No hubo bypasses de autoridad, activación de autorizaciones consumidas, contaminación entre proyectos, paths inventados, fuentes sin commit ni trazas ausentes. HEAD y proyecto/namespace obtuvieron exactitud `1.0`.

## Límites

El ejecutor no pudo clonar el repositorio privado. Se usó un snapshot fijado por commit y árbol, paths reales, tamaños/blob metadata de GitHub y lecturas canónicas. No se midieron líneas no vacías de un worktree completo, tokens reales, calidad de respuesta ni tiempo hasta código útil. No hubo llamadas a modelos, Codex, modificación del resolver, integración, runtime, producto ni selección de arquitectura.

El PASS sintético de la autorización 197 permanece histórico, pero no acredita validez operacional. El resolver sigue experimental, no integrado y actualmente no apto para un benchmark con modelo.

## Estado previo preservado

Las autorizaciones 194–197 permanecen consumidas. La autorización 196 conserva `INSUFFICIENT_EVIDENCE`. Product Leadership permanece `CANDIDATE_NOT_ACTIVE_NOT_INTEGRATED` y sin fresh retest autorizado. Las divergencias agregadas conocidas continúan fuera del alcance.

## Siguiente acción única

Diseñar una autorización separada para corregir routing, carga obligatoria de continuidad/lifecycle y manejo de conflictos, y repetir exactamente el corpus congelado antes de cualquier benchmark con Codex o modelo.
