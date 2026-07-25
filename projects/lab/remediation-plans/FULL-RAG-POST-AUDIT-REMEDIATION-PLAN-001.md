# Plan documental de remediación posterior a la auditoría full RAG

La fuente estructurada es `FULL-RAG-POST-AUDIT-REMEDIATION-PLAN-001.json`.

Estado: `DOCUMENTARY_PLAN_APPROVED_NOT_EXECUTED`.

Decisión: `DEC-LAB-021`.

Autorización fuente: `AUTHORIZATION_LAB_FULL_RAG_POST_AUDIT_DECISION_AND_REMEDIATION_PLANNING_078_REVISION_2`.

## Alcance

El plan resuelve documentalmente `PEND-LAB-022`. Define remediación prospectiva de trazabilidad, diseños futuros y gates. No modifica el diseño 002, la ejecución 002 ni sus resultados; tampoco ejecuta pruebas, genera corpus, selecciona proveedor o arquitectura, aprueba implementación, cambia producto o runtime ni despliega.

La ejecución 002 conserva `TEST_VALID_DISCRIMINATING_RESULTS_PUBLISHED`. Su interpretación sigue siendo `VALID_DISCRIMINATING_SYNTHETIC_RESULTS_WITH_QUALIFIED_CAUSAL_ATTRIBUTIONS`.

## Decisiones

1. `REMEDIATE_DESIGN_SOURCE_TRACEABILITY` — `REMEDIATION_REQUIRED`, prioridad `HIGH`.
2. `DESIGN_ISOLATED_C_RANK_CONTRAST` — `NEW_ISOLATED_CONTRAST_REQUIRED`, prioridad `HIGH`.
3. `REPLACE_FIVE_QUALIFIED_HYPOTHESES_WITH_FRESH_CONTRASTS` — `FRESH_CONTRASTS_REQUIRED_BEFORE_STRONG_CAUSAL_CLAIMS`, prioridad `MEDIUM_HIGH`.
4. `DEFINE_ARCHITECTURE_DECISION_EVIDENCE_GATE` — `NOT_READY`.

## Trazabilidad prospectiva

Una remediación futura deberá producir inventario completo de fuentes, SHA-256 individual, digest ordenado, paths canónicos y una relación verificable entre diseño, freeze y ejecución. Cualquier fuente ausente, no hasheada, sin path canónico o no vinculada bloqueará el freeze.

La remediación será prospectiva. El diseño 002 y la ejecución 002 permanecen históricos e inmutables.

## C-RANK aislado

El futuro contraste variará solamente ranking. Mantendrá constantes representación, corpus, k, filtros, scoring, conjunto candidato y política de safe refusal. Incluirá controles positivo y negativo, gate de identificabilidad, evidencia favorable y contraria, y criterio explícito de no conclusión.

Si cambia otra variable material o los controles no discriminan, el resultado será `INSUFFICIENT_EVIDENCE`; no podrá afirmarse que ranking fue causalmente refutado.

## Cinco hipótesis calificadas

Las cinco hipótesis identificadas por la auditoría son:

- `H-DECLARED-DECOYS` — procedencia `HISTORICAL`; requiere un toggle aislado de decoys declarados.
- `H-SYNONYM-EXPANSION` — procedencia `HISTORICAL`; requiere aislar expansión léxica de representación semántica.
- `H-AUTHORITY-FILTERING` — procedencia `HARDCODED`; requiere un control sintético de mutación de filtros.
- `H-PREDOMINANTLY-LEXICAL` — procedencia `COMPOUND`; requiere variar sólo representación con estratos de colisión constantes.
- `H-CROSS-FIXTURE-DISTRACTORS` — procedencia `COMPOUND`; requiere variar sólo las colisiones cross-fixture.

Cada diseño futuro deberá declarar variable, control, métricas, gate, evidencia favorable y contraria, evidencia faltante, criterio de cierre y límite del claim. Ningún resultado podrá generalizarse más allá del corpus sintético autorizado.

## Orden de remediación

### PHASE_A — DESIGN_TRACEABILITY_REMEDIATION

Define inventario, hashes, digest, paths y matriz diseño-freeze-ejecución. Depende de autorización separada y termina únicamente cuando la trazabilidad prospectiva está completa y el chequeo negativo falla cerrado.

### PHASE_B — ISOLATED_C_RANK_TEST_DESIGN

Diseña el contraste ranking-only después de aprobar Phase A. Termina cuando ranking es la única variable material y todos los controles, métricas, gates y límites están predeclarados. No ejecuta el contraste.

### PHASE_C — FIVE_FRESH_HYPOTHESIS_TEST_DESIGN

Diseña exactamente cinco contrastes frescos. Termina cuando cada hipótesis tiene contrato completo y ninguna evidencia histórica se presenta como fresca. No genera corpus ni ejecuta pruebas.

### PHASE_D — BOUNDED_EXECUTION_PROPOSAL

Prepara un brief delimitado, matriz de runs, costes, stop conditions y auditoría requerida. La propuesta no concede autoridad; cualquier ejecución futura necesita autorización separada.

### PHASE_E — POST_EXECUTION_EXTERNAL_AUDIT

Después de una ejecución futura separadamente autorizada, una auditoría read-only comprobará hashes, reproducción, identificabilidad, controles, claims y limitaciones. Requiere su propia autorización.

### PHASE_F — ARCHITECTURE_DECISION_READINESS_REASSESSMENT

Reevalúa readiness después de la auditoría. Puede declarar `READY` o `NOT_READY`, pero no selecciona arquitectura ni implementación.

## Gate previo a arquitectura

`ARCHITECTURE_DECISION_GATE = NOT_READY`.

Requiere trazabilidad remediada, resultado C-RANK aislado, cinco resultados frescos, reproducción aprobada, aislamiento sin leakage, límites de claims aprobados y auditoría externa posterior. Una comparación con proveedores reales necesita autorización futura separada.

La selección de proveedor, arquitectura o implementación sigue no autorizada.

## Preservación y sucesor

Los históricos designados por 078 revisión 2 permanecen intactos. Una fase futura fallida conservará su evidencia y registrará el stop condition; ningún resultado nulo o contrario será eliminado o relabelado.

El único sucesor es `PEND-LAB-023`, que propone trazabilidad prospectiva y diseños frescos sin autorizar su ejecución.
