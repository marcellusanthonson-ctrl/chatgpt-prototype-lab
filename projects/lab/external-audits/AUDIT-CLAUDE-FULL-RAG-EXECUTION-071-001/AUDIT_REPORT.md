# AUDIT-CLAUDE-FULL-RAG-EXECUTION-071-001

Auditoría externa independiente, estrictamente read-only, del paquete publicado por la autorización 071.

- Auditor: CLAUDE · Modo: STRICT_READ_ONLY
- Autorización: AUTHORIZATION_072 (audita PEND-LAB-018 / EXP-LAB-002 / EVD-LAB-EXP-002)
- Paquete: `FULL-RAG-STAGES-5-6-DISCRIMINATING-TEST-EXECUTION-001` (88 archivos)
- Repo/rama: `marcellusanthonson-ctrl/chatgpt-prototype-lab` @ `main`
- HEAD esperado = HEAD observado = `404819e4a622bf7e5e7a55bf1a45b17abb5a74cb`

## Resultado global

**AUDIT_CONFIRMS_EXECUTION_MODIFIES_INTERPRETATION**

Los 12 claims se confirman individualmente sobre la evidencia. El calificador global es *MODIFIES_INTERPRETATION* (no *CONFIRMS_RESULT*) por dos motivos, ninguno de los cuales revierte un número:

1. El `EXECUTION_SUMMARY.md` publicado afirma que el brazo authority-first fue "viable", contradiciendo directamente a `EXECUTION_SUMMARY.json`, `METRICS.json` y `GATE_RESULTS.json`, que lo registran como **NON_VIABLE**. El `.md` es una cadena fija incrustada en `execute.mjs`, no derivada del resultado computado. Por precedencia del LAB_CONTRACT (JSON = fuente estructurada; Markdown = vista humana), gobierna el JSON.
2. La no-viabilidad debe leerse como resultado de la **implementación ensayada bajo condiciones sintéticas**, no como refutación de la **clase arquitectónica** authority-first RAG.

## Veredictos por claim (todos CONFIRMED)

| # | Claim | Veredicto |
|---|-------|-----------|
| 1 | PACKAGE_COMPLETE_REPRODUCIBLE | CONFIRMED |
| 2 | CORPUS_INDEPENDENT | CONFIRMED |
| 3 | LEAKAGE_CONTROL_PASS | CONFIRMED |
| 4 | FREEZE_STABLE | CONFIRMED |
| 5 | POSITIVE_CONTROL_PASS | CONFIRMED |
| 6 | NEGATIVE_CONTROL_DISCRIMINATES | CONFIRMED |
| 7 | METRICS_CORRECT | CONFIRMED |
| 8 | GATES_CORRECT | CONFIRMED |
| 9 | NO_CANDIDATE_VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS | CONFIRMED |
| 10 | FULL_RAG_AUTHORITY_FIRST_NON_VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS | CONFIRMED (scope-modified) |
| 11 | NO_ARCHITECTURE_SELECTED | CONFIRMED |
| 12 | NO_PRODUCT_OR_RUNTIME_EFFECT | CONFIRMED |

## Método y evidencia central

**Integridad.** 88 archivos declarados = 88 en disco, sin faltantes ni extras. Los 87 hashes de `HASHES.json` (auto-excluido) recomputan sin desviación. HEAD coincide con `EXPECTED_HEAD`.

**Reproducción.** Se ejecutó el propio harness (`node harness/execute.mjs --output <dir externo vacío>`, Node v22, sin instalar dependencias, sin red) en un directorio fuera del repo. 86/88 archivos byte-idénticos, incluidos `METRICS.json` y `GATE_RESULTS.json`, y los fingerprints de los 30 runs. Solo difieren `REPRODUCIBILITY_REPORT.json` (bloque `runtime`: entorno original Windows/node v24.6.0 vs auditor Linux/node v22) y, en cascada, `HASHES.json`. Clasificación: **NEAR_EXACT_REPRODUCTION**.

**Freeze.** 15 entradas congeladas + 20 hashes de fuentes de diseño = 0 cambios. `post_freeze_mutations = 0`. El harness re-valida los hashes congelados antes y después de evaluar y falla-cerrado ante cualquier cambio.

**Leakage / aislamiento.** 24 runs de selector, 120 lecturas registradas, **0 privadas**. El selector solo leyó 5 rutas allowlisted (`public/*` + `frozen/ARM_PARAMETERS.json`) y `selector.mjs` lanza excepción ante cualquier ruta `private/`. El canary (`sha256` recomputado = `84edb305...`) coincide con el reporte y no aparece en ningún archivo fuera de `private/`. Sin nombres de campos de oráculo en el payload público. Selector y evaluador corren en procesos separados; solo el evaluador accede a `PRIVATE_ORACLES.json`.

**Métricas y gates (recomputación independiente).** Se reimplementaron las fórmulas documentadas en Python, sin importar el harness, sobre los 30 archivos de runs + oráculo + catálogo. Coinciden exactamente con lo publicado: authority-first (precision 0.234127, recall 0.458333, macro_f1 0.261243, 48 críticos), control positivo (todo 1.0, 0 críticos), control negativo (249 críticos, authority_inversion 180). Gate B/C recomputados dan la misma viabilidad por brazo.

**Controles.** Positivo (oráculo, solo-evaluador) alcanza F1=1 y 0 fallos críticos, demostrando que el evaluador PUEDE otorgar viabilidad (no está amañado para reprobar todo). Negativo (relevancia-antes-que-autoridad) discrimina el ordenamiento inseguro. Ambos correctamente marcados NOT_PROMOTABLE.

## Perfil de fallo — FULL_RAG_AUTHORITY_FIRST_SIMULATION

NON_VIABLE por Gate B (48 críticos: `BINDING_NEGATIVE_OMITTED`, `UNSUPPORTED_CONCLUSION`) y Gate C (recall 0.458 < 0.8; precision 0.234 < 0.7; macro_f1 0.261 < 0.72; safe_failure_f1 0.5 < 0.9). Es, sin embargo, el candidato **más seguro** (authority_inversion = 0, forbidden = 0, conflict_detection = 1.0, citation_correctness = 1.0).

Atribución del fallo:

- **PRIMARIO — representación semántica.** El brazo se describe como "semantic retrieval" pero se implementa con `embeddings=false`, `provider=NONE` y un mapa de sinónimos trivial (`rule<->guidance`, `conceptNN<->notionNN`). La contribución semántica medida sobre la referencia determinista es **2.78%**. El componente que define a un RAG real (recuperación densa) no se ejercita.
- **CONTRIBUYENTE — contrato/harness.** `budget_k=2` (congelado) no alcanza para los conjuntos requeridos multi-documento; y el safe-refusal solo se activa cuando 0 documentos son elegibles, de modo que los decoys léxicos que sobreviven a los filtros de gobierno provocan `UNSUPPORTED_CONCLUSION` en fixtures que esperaban abstención.
- **NO CULPABLES.** El ranking authority-first funciona; el evaluador es sólido; los thresholds están preregistrados y el control positivo los supera; el coste no es factor (Gate D pasa).

**Distinción clave:** el resultado refuta la simulación léxica acotada, **no** la clase arquitectónica authority-first RAG. Leerlo como refutación arquitectónica sería REVERSED por la evidencia.

## Limitaciones

- Reproducción NEAR_EXACT (2 archivos ligados al entorno no son byte-reproducibles).
- No se consultó el HEAD remoto vivo (frontera sin-red); se verificó contra la copia local montada cuyo HEAD = EXPECTED_HEAD.
- Resultado acotado a 180 docs sintéticos, 42 fixtures, `budget_k=2`, sin embeddings.
- Solo se verificó independencia de *artefactos* del corpus respecto de EXP-LAB-001, no independencia de *diseño* (no reclamada).
- Esta auditoría NO crea autoridad, no selecciona ni aprueba nada.

## Salida final

```
AUTHORIZATION_072_STATUS = CONSUMED_ON_DELIVERY_OF_COMPLETE_EXTERNAL_AUDIT_PACKAGE
AUDITOR = CLAUDE
AUDIT_MODE = STRICT_READ_ONLY
CANONICAL_MUTATIONS = 0
COMMITS = 0
PUSHES = 0
DEPENDENCIES_INSTALLED = 0
EXTERNAL_APIS_USED = 0
REAL_DATA_USED = NO
ARCHITECTURE_SELECTED = NO
IMPLEMENTATION_SELECTED = NO
IMPLEMENTATION_APPROVED = NO
AUDIT_RESULT = AUDIT_CONFIRMS_EXECUTION_MODIFIES_INTERPRETATION
NEXT_AUTHORIZED_ACTION = NONE_AFTER_CONSUMPTION
```
