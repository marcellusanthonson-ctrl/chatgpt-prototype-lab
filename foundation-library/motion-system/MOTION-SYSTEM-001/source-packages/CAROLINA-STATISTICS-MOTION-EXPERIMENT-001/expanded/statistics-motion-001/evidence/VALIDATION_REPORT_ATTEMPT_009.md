# VALIDATION_REPORT_ATTEMPT_009

## Contexto

- Attempt: `ATTEMPT-009`.
- Autorización de implementación relacionada: `AUTHORIZATION_LOCAL_CAROLINA_STATS_STATIC_SUFFIX_CORRECTION_ATTEMPT_009`.
- Auditoría post hoc: `AUDIT_LOCAL_CAROLINA_STATS_ATTEMPT_009_POSTHOC_001`.
- Dictamen de auditoría: `IMPLEMENTATION_CONFIRMED_PARTIAL_EVIDENCE_PRESENT`.
- Protocolo de validación recuperado: navegador Chrome visible mediante `file://` directo.
- Viewport principal: `1440×1000`.
- Servidor local: no utilizado.
- Solicitudes de red observadas: `0`.
- Esta reconciliación registra la evidencia recuperada; no volvió a ejecutar ni modificar el HTML.

## Baseline y resultado

| Estado | Ruta | Bytes | SHA-256 | Procedencia |
|---|---|---:|---|---|
| ATTEMPT-008 | `archive/statistics-motion-001-attempt-008-human-reviewed-pre-static-plus-correction/CAROLINA_MD_STATISTICS_MOTION_EXPERIMENT_001.html` | 1.865.892 | `97D42264777EAD2C7EFE1EC6A24BF9F0D7578C49614FE1745ED1D5A8E891BA6A` | `VERIFIED_FROM_FILE` |
| ATTEMPT-009 | `experiments/statistics-motion-001/CAROLINA_MD_STATISTICS_MOTION_EXPERIMENT_001.html` | 1.866.483 | `74274E55FF1C8B9EDD849D433F12BF6FFE0ABB00097872FEB6BC7ADDE83B463E` | `VERIFIED_FROM_FILE` |

El inventario de ATTEMPT-008 tiene SHA-256 `DB611153953952BEB4402DC263E12D31A2B53EAA9134D5AB2807B0EFA7204814` (`VERIFIED_FROM_FILE`).

## Causa de la reconciliación

El patch quedó aplicado antes del corte de energía y no se completó el cierre documental original. El estado exacto de una eventual generación de evidencia original no pudo recuperarse porque no quedaron archivos parciales de ATTEMPT-009. La secuencia concreta dentro de esa ventana se clasifica como `NOT_RECOVERABLE`; la aplicación del patch antes de la ausencia documental se clasifica como `INFERRED` a partir del HTML final, su hash, el baseline archivado y la falta de documentos posteriores.

## Cinco reproducciones visibles recuperadas

Se registraron `833` frames totales en cinco reproducciones completas: una natural y cuatro replays manuales.

| Reproducción | Frames | Pacientes | Años | Indicador 3 | Portal | Estado final |
|---|---:|---|---|---|---|---|
| Natural | 154 | `0 → 1000` | `0 → 28` | `3` constante | `24 → 24/ → 24/7` | Estable |
| Replay 2 | 169 | `0 → 1000` | `0 → 28` | `3` constante | `24 → 24/ → 24/7` | Estable |
| Replay 3 | 170 | `0 → 1000` | `0 → 28` | `3` constante | `24 → 24/ → 24/7` | Estable |
| Replay 4 | 170 | `0 → -27 → … → 1000` | `0 → 28` | `3` constante | `24 → 24/ → 24/7` | Estable |
| Replay 5 | 170 | `0 → 1000` | `0 → 28` | `3` constante | `24 → 24/ → 24/7` | Estable |

Resultados agregados (`VERIFIED_FROM_BROWSER`):

- Un único nodo de sufijo durante todas las reproducciones.
- Identidad DOM del signo `+` estable.
- Eliminaciones del sufijo: `0`.
- Reinserciones del sufijo: `0`.
- Frames con indicadores vacíos: `0`.
- Frames con `+` aislado: `0`.
- Desapariciones del signo `+`: `0`.
- Loops: `0`.
- Errores de página o consola: `0`.
- `28` permaneció visible y alcanzó su estado final.
- `3` permaneció visible y constante.
- `24/7` conservó la secuencia aprobada y alcanzó su estado final.
- El estado final `1000+ / 28 / 3 / 24/7` permaneció estable durante al menos los últimos 500 ms de cada reproducción.

## Evidencia geométrica del signo `+`

| Propiedad | Resultado |
|---|---:|
| x representativa | `317.5469` |
| y representativa | `149` |
| width | `33.8125` |
| height | `65` |
| Variación X durante reproducción | `0.0000 CSS px` |
| Variación Y durante reproducción | `0.0000 CSS px` |
| Nodos de sufijo | `1` |
| opacity | `1` |
| transform | `none` |
| animation-name | `none` |
| transition-property | `none` |

La posición, tamaño, opacidad e identidad DOM del sufijo permanecieron constantes durante cada reproducción efectiva (`VERIFIED_FROM_BROWSER`). Antes de la reproducción natural se observó el ajuste inicial de fuente; la espera por `document.fonts.ready` hizo que la reproducción comenzara después de ese ajuste (`VERIFIED_FROM_FILE` y `VERIFIED_FROM_BROWSER`).

## Comparación responsive

ATTEMPT-008 y el estado final activo de ATTEMPT-009 se compararon en:

- `390×844`;
- `768×1024`;
- `1440×1000`.

En los tres viewports coincidieron exactamente grid, celdas, números, etiquetas, tipografía, color y geometría final (`VERIFIED_FROM_BROWSER`).

## Anomalía conocida no bloqueante

Clasificación exacta: `KNOWN_NONBLOCKING_PREEXISTING_TIMING_ANOMALY`.

En Replay 4 se observó durante un frame el valor transitorio `-27` (`VERIFIED_FROM_BROWSER`). No fue introducido por ATTEMPT-009 y es compatible con el motor temporal heredado de ATTEMPT-008. No produjo desaparición, flicker ni loop; no afectó el estado final y no fue observado por Jonathan Martínez. No bloquea el cierre documental y no autoriza cambios de código. No se registra como comportamiento esperado ni como problema corregido.

## Resultado humano

`HUMAN_REPORTED_AND_APPROVED`

Jonathan Martínez confirmó que ATTEMPT-009 funciona correctamente: los números se animan, el signo `+` permanece estático y el efecto se percibe correcto.

Esta afirmación es `HUMAN_REPORTED`; no se presenta como validación automatizada.

## Integración

Integración al landing: `NOT_AUTHORIZED_NOT_PERFORMED`.
