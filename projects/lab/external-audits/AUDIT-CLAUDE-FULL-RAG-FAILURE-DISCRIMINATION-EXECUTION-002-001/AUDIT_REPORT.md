# AUDIT-CLAUDE-FULL-RAG-FAILURE-DISCRIMINATION-EXECUTION-002-001

Auditoría externa independiente, estrictamente read-only, de la ejecución 002 bajo autorización 076.

- Auditor: CLAUDE · Modo: STRICT_READ_ONLY
- Fuente: `FULL-RAG-AUTHORITY-FIRST-FAILURE-DISCRIMINATION-TEST-EXECUTION-002` (107 archivos, 66 runs)
- Repo/rama: `marcellusanthonson-ctrl/chatgpt-prototype-lab` @ `main`
- HEAD esperado = observado = `7054a1bfc9344065ad3bb9637ce8d7b808562d7a`
- Pendings: PEND-LAB-020 (ejecución) / PEND-LAB-021 (auditoría, no se cierra)

## Resultado global

**AUDIT_CONFIRMS_EXECUTION_MODIFIES_INTERPRETATION**

La ejecución y su estado publicado `TEST_VALID_DISCRIMINATING_RESULTS_PUBLISHED` se confirman: integridad, freeze, aislamiento, reproducción, métricas y gates verifican; los controles discriminan; las causas primarias se aíslan limpiamente. La interpretación se **modifica** (no se revierte) porque un subconjunto de las 14 hipótesis no se discrimina con contrastes frescos de 002 (hardcodeadas/históricas/confundidas) y el freeze no fija la procedencia del diseño. Ninguna de estas observaciones revierte un resultado ni una causa primaria.

## PREFLIGHT (fail-closed, superado)

HEAD = EXPECTED; 107 archivos; 66 runs; sin auditoría 076 previa; pending/experimento/evidencia/auth-075 presentes.

## Verificación

**Integridad.** 107 declarados = 107 en disco; 106/106 hashes coinciden (HASHES auto-excluye HASHES.json); `ordered_manifest_digest` y `freeze ordered_digest` coinciden con el registro (EXP-003 `32c099b8…`, EVD-003 `0e81fc24…`). `MANIFEST.source_pending=PEND-LAB-020` es el pending de ejecución (correcto), PEND-LAB-021 es el sucesor de auditoría.

**Freeze.** 24 entradas congeladas sin cambios; `POST_FREEZE_VALIDATION` cero mutaciones; 60 selecciones congeladas antes de la evaluación privada. **Hallazgo (MEDIO):** `frozen/SOURCE_DESIGN_HASHES.json` está vacío (`files: []`) por un bug de ruta (`repositoryRoot` se resuelve un nivel por encima del repo real); la procedencia del diseño no queda fijada por hash. Determinista (reproduce vacío) y **no afecta** runs/métricas/gates; los artefactos de ejecución sí están fijados.

**Run matrix.** 9 brazos, 11 celdas (ARM-02 en K4/K8/K16), 6 configs × 11 = 66 runs. Sin runs faltantes/duplicados, sin rutas huérfanas ni archivos no manifestados. EXECUTION_SUMMARY.md consistente con el JSON.

**Aislamiento / leakage.** 60 runs de selector con `oracle_access=false` y **0 lecturas privadas**; canary (`PRIVATE-CANARY-075-AE34…`) ausente fuera de `private/`; `PERFECT_CANDIDATES` sólo en ARM-08/09; evaluador (ARM-06) accede a oráculos **sólo tras** el freeze de selecciones. Nota (BAJO): el `read_log` del selector es una declaración estática, no instrumentación en runtime; el aislamiento se garantiza estructuralmente por el allowlist y el bloqueo de `private/`.

**Reproducción.** Re-ejecución completa del harness (Node v22, sin dependencias, sin red) → `PASS_EXACT`. Los 66 runs + CAUSAL + COST + LEAKAGE + GATE_RESULTS reproducen **byte a byte**; METRICS reproduce **parseado idéntico** (difiere sólo por compactación de whitespace declarada, "REPOSITORY_1200_PHYSICAL_LINE_POLICY"). Sólo 4 archivos difieren a nivel de bytes (METRICS whitespace; README y REPRODUCTION_REPORT con adiciones honestas que declaran esa normalización + huella de entorno; HASHES en cascada). Veredicto: **REPRODUCED_WITH_NON_MATERIAL_DIFFERENCES**.

**Métricas.** Recomputación **independiente** (evaluador propio en Python, sin importar el harness) sobre los 66 runs + oráculo + catálogo: recall, precision, macro_f1, fallos críticos y authority_inversion coinciden exactamente en las **11 celdas**.

**Gates.** Recomputados: coinciden. `AUTHORITY=FAIL` se explica por ARM-03 (authority_inversion=327) y ARM-05 (161) — reserva de negativos que desplaza documentos de mayor autoridad; es un resultado sustantivo, no un defecto, y no bloquea la validez del test.

**Controles.** Positivo (ARM-06): F1=1, 0 críticos → el evaluador puede otorgar viabilidad (no amañado). Negativo (ARM-07): 975 críticos, 402 inversiones → discrimina la estrategia insegura.

## Identificabilidad causal

Contrastes de variable única **limpios**: C-REP (representación, +0.040), C-K4/8/16 (k, +0.058…), C-NEG (negativos, +0.107), C-RETRIEVAL (recuperación, +0.190), C-SAFE-REFUSAL (política, −0.75 dentro del brazo). 

Causas primarias **confirmadas**: calidad de recuperación (mayor efecto de recall) y la heurística de safe-refusal (causa primaria de conclusiones no soportadas). Contribuyentes: k (sube recall pero colapsa precision 0.41→0.06), representación semántica (+0.04, +50% de cómputo), reserva de negativos (mejora retención pero induce inversión de autoridad).

**Hallazgo (MEDIO):** C-RANK (ARM-08 vs ARM-09) se etiqueta como variable única pero cambia **ranking Y representación**; su efecto medido es 0 y ARM-08≡ARM-09, así que H-RANKING=NOT_SUPPORTED se sostiene pero el nulo está **sub-identificado**. **Hallazgo (MEDIO):** 5 de 14 hipótesis (H-DECLARED-DECOYS, H-SYNONYM-EXPANSION, H-AUTHORITY-FILTERING y las derivadas H-PREDOMINANTLY-LEXICAL, H-CROSS-FIXTURE-DISTRACTORS) se resuelven por evidencia hardcodeada/histórica(071)/compuesta, no por contrastes frescos de 002.

## Límites de interpretación

El paquete **no** declara ni sostiene RAG_OPERATIONAL, ARCHITECTURE/PROVIDER/IMPLEMENTATION_APPROVED, PRODUCTION_READY, REAL_WORLD_VALIDATED ni generalización fuera del corpus sintético. La representación semántica es una **simulación local provider-neutral, no embeddings reales**. Sin sobre-afirmación.

## Salida final

```
AUTHORIZATION_076_STATUS = CONSUMED_ON_DELIVERY_OF_COMPLETE_EXTERNAL_AUDIT_PACKAGE
EXECUTOR = CLAUDE
SOURCE_HEAD = 7054a1bfc9344065ad3bb9637ce8d7b808562d7a
SOURCE_PENDING = PEND-LAB-021
SOURCE_EXECUTION = FULL-RAG-AUTHORITY-FIRST-FAILURE-DISCRIMINATION-TEST-EXECUTION-002
AUDIT_RESULT = AUDIT_CONFIRMS_EXECUTION_MODIFIES_INTERPRETATION
FILES_AUDITED = 107
RUNS_REVIEWED = 66
REPRODUCTION_RESULT = REPRODUCED_WITH_NON_MATERIAL_DIFFERENCES
FREEZE_INTEGRITY = PASS_WITH_NON_MATERIAL_FINDINGS
ISOLATION_AND_LEAKAGE = PASS_NO_LEAKAGE
CAUSAL_CLAIMS = PRIMARY_CAUSES_CONFIRMED_SOME_ATTRIBUTIONS_QUALIFIED
CANONICAL_MUTATION = NO
COMMIT = NONE
PUSH = NONE
PROVIDER_SELECTED = NO
ARCHITECTURE_SELECTED = NO
IMPLEMENTATION_SELECTED = NO
IMPLEMENTATION_APPROVED = NO
PRODUCT_EFFECT = NONE
RUNTIME_EFFECT = NONE
NEXT_AUTHORIZED_ACTION = NONE_AFTER_DELIVERY
```

La entrega no cierra PEND-LAB-021 ni crea autorización posterior. La reconciliación canónica futura exige autorización separada.
