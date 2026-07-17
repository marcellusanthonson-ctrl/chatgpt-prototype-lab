# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-07-16`
Repository: `marcellusanthonson-ctrl/symphonie`

## Role

Symphonie is an eight-phase workflow that creates and develops applications and websites from beginning to end. It coordinates project-specific work across ChatGPT, Claude, and Codex. Skills are instruments used by particular phases; Symphonie is not the canonical producer of reusable skills.

## Operating model

- Jonathan Martínez approves.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs explicitly assigned discovery and definition phases.
- Codex performs bounded technical execution without autonomous authority.

## Structural relationship with MammothSkills

Symphonie and MammothSkills remain independent projects. Symphonie may provide requirements and consumer feedback; MammothSkills may later provide identified approved skill artifacts or releases. Release, installation, migration, consumer fit, runtime compatibility, and integration remain separate validations and permissions.

Canonical decisions: `DEC-LAB-005`, `DEC-LAB-006`.

## Dedicated repository architecture

`DEC-LAB-010` aprobó la arquitectura, `DEC-LAB-012` registró el repositorio privado y las órdenes documentales posteriores completaron y reconciliaron el baseline:

```text
TARGET_REPOSITORY = marcellusanthonson-ctrl/symphonie
VISIBILITY = PRIVATE
CANONICAL_BRANCH = main
ARCHITECTURE = APPROVED
REPOSITORY_CREATED = YES
CREATION_VERIFIED = YES
REPOSITORY_EMPTY = NO
FILESET = 40
HEAD = 8692a539bc339ea7b4258d78b3ce9f5f5635f407
REPOSITORY_CREATION = COMPLETED_VERIFIED_AUTHORIZATION_CONSUMED
BOOTSTRAP_003 = CONSUMED
CORRECTION_004 = CONSUMED_WITH_FAILED_RESULT
REPAIR_005 = CONSUMED_COMPLETED_VERIFIED
RECONCILIATION_006 = CONSUMED_COMPLETED_VERIFIED
EIGHT_PHASE_CANONICALIZATION_007 = CONSUMED_COMPLETED_VERIFIED
LAB_STATE_RECONCILIATION_008 = CONSUMED_COMPLETED_VERIFIED
PHASE_0_ALIGNMENT = ALIGNED_TO_DEC_LAB_011
CANONICAL_LANGUAGE = ESPAÑOL
```

`marcellusanthonson-ctrl/symphonie-codex-lab` se conserva como repositorio de evidencia histórica de Symphonie Codex y no debe eliminarse ni transformarse silenciosamente.

Responsibility separation:

```text
chatgpt-prototype-lab = governance, decisions, errors, patterns, registry, continuity
symphonie repository = canonical workflow, phase contracts, gates, schemas, identified integrations
MammothSkills = reusable skill production, adaptation, audit, versioning, releases
symphonie-codex-lab = historical Codex skill evidence and temporary laboratory
```

Los archivos de gobierno locales en el repositorio Symphonie se vincularán o reflejarán la autoridad del LAB; no crearán autoridad de aprobación independiente. `CURRENT_STATE.json` será la fuente estructurada local y `CURRENT_STATE.md` su vista legible.

## Arquitectura de memoria gobernada

`DEC-LAB-012` aprueba la arquitectura documental `CONTEXTO_NO_AUTORIZACION`: memoria curada, no espejo de repositorios. La `UNIDAD_DE_CONOCIMIENTO` es la unidad mínima; Git versionado es el registry canónico y el índice es derivado y reconstruible. Los filtros de privacidad se aplican antes de similitud y las contradicciones no se resuelven por ranking.

El fileset documental de 40 archivos está publicado y reconciliado. Incluye el mapa de ocho fases, contratos para Phase 0–7, registro de gates y modelos transversales de fase, gate, artefacto, handoff y autoridad. Sus autorizaciones de escritura están consumidas. El roadmap documental comprende `RAG_0_ARQUITECTURA_DOCUMENTAL`, `RAG_1_CORPUS_SEMILLA_CURADO_MANUAL`, `RAG_2_RECUPERACION_NO_VECTORIAL`, `RAG_3_EVALUACION_SINTETICA`, `RAG_4_PILOTO_VECTORIAL_LOCAL`, `RAG_5_SELECCION_TECNOLOGICA`, `RAG_6_AMPLIACION_AUTORIZADA_DE_FUENTES`, `RAG_7_PILOTO_CONTROLADO_CON_PROYECTOS_REALES` y `RAG_8_DECISION_DE_ESTABILIDAD`; no afirma runtime ni ingesta implementados.

| Fase | Acceso a memoria |
| --- | --- |
| 0A | Prohibido |
| 0B | Opcional restringido |
| 0C | Opcional, con autoridad humana |

Runtime, ingesta, embeddings, acceso automático a repositorios, integración, migración, cambios de producto y datos de proyectos reales continúan no autorizados.

## Baseline documental canónica de ocho fases

```text
PHASE_0 = APPROVED_EXPERIMENTAL_BASELINE_NOT_RUNTIME_VALIDATED
PHASE_1 = DEFINED_NOT_TESTED
PHASE_2 = DEFINED_NOT_TESTED
PHASE_3 = PARTIALLY_VALIDATED_WITH_FINDINGS
PHASE_4 = PARTIALLY_RUNTIME_VALIDATED
PHASE_5 = DEFINED_NOT_TESTED
PHASE_6 = DEFINED_NOT_TESTED
PHASE_7 = DEFINED_NOT_TESTED
FULL_WORKFLOW_0_TO_7 = NOT_VALIDATED
RUNTIME = NOT_AUTHORIZED
```

Los contratos canónicos distinguen definición, prueba, aprobación y autorización. Phase 3A y Phase 4A conservan evidencia concreta; no se extrapola esa evidencia a la fase completa. Las fases 1, 2, 5, 6 y 7 permanecen definidas pero no probadas.

## Phase 0 experimental baseline

`DEC-LAB-011` approves Phase 0 v0.1 as an experimental baseline:

```text
MODEL = 0A_CAPTURE -> 0B_ANALYZE_AND_CLASSIFY -> 0C_HUMAN_DECISION
STATUS = APPROVED_EXPERIMENTAL_BASELINE
STABLE_CONTRACT = NO
RUNTIME_VALIDATED = NO
REAL_CLIENT_USE = NOT_AUTHORIZED
```

### 0A — Capture

Records declarations, supplied documents, participants, provenance, privacy classification, and source conflicts. It does not interpret viability or approve progression.

Expected outputs:

- `client-intake-submission.json`
- `source-register.json`
- `privacy-screening.json`

### 0B — Analyze and classify

May be assigned to Claude only under an explicit bounded order. It analyzes already supplied sources, separates `CLIENT_DECLARED`, `DOCUMENT_EXTRACTED`, `INFERRED`, `UNKNOWN`, and `CONTRADICTORY`, identifies gaps and risks, and recommends without approving.

Expected outputs:

- `intake-analysis.json`
- `follow-up-question-set.json`
- `quotation-readiness-assessment.json`
- `intake-decision-recommendation.json`

It must not assume software, select a stack, design a solution, produce code or a quotation, estimate price or effort, import unrelated context, or issue unsupported professional conclusions.

### 0C — Human decision

Jonathan Martínez is the exclusive approver. Agents have no approval authority.

Allowed decisions:

- `APPROVE_DISCOVERY`
- `RETURN_FOR_CLARIFICATION`
- `REJECT_OR_ARCHIVE`
- `REFER_TO_QUALIFIED_REVIEW`
- `CLASSIFY_AS_NON_SOFTWARE_INTERVENTION`

Expected output: `phase-0-decision-record.json`.

Intake analyzes declarations and sources already supplied. Discovery creates new evidence through direct-user interaction, observation, research, and hypothesis validation. Intake cannot claim that the problem is validated or justify a quotation.

Privacy defaults to synthetic or anonymized data. `SENSITIVE_RESTRICTED` processing is blocked by default. Runtime, real-client data, Discovery, quotation, implementation, and integration remain not authorized.

## Current Phase 3A architect baseline

```text
SKILL = symphonie-ux-ui-architect
VERSION = 0.1.0-alpha.6
PHASE = 3A
CAPABILITY = DOCUMENT_WRITE
STATUS = APPROVED_BASELINE_WITH_RECORDED_HISTORICAL_EVIDENCE_LIMITATION
BRANCH = feature/design-migration-handoff-alpha6
IMPLEMENTATION_COMMIT = 22d63a901ec30221e7e8e7e944203eb2239598bd
RUNTIME_EVIDENCE_COMMIT = 385f85b85560d8f5a12512c9f36e2bdd140f1d7b
APPROVAL_DECISION = DEC-LAB-009
APPROVED_BY = Jonathan Martínez
APPROVED_AT = 2026-07-14
```

Direct evidence:

```text
STATIC_VALIDATION = PASS
REG-08 = PASS
REG-09 = BLOCKED_AS_EXPECTED
REG-09_REASON = MIGRATION_TARGET_UNCONFIRMED
UNAUTHORIZED_WRITES = ZERO
NORMAL_EIGHT_OUTPUT_FLOW = PRESERVED
```

Alpha.6 conditionally adds `.project/phase-3/migration-handoff.json` when an authorized instruction declares a migration or another applicable fidelity condition. It preserves source identity, formulas, sensitive fidelity zones, runtime risks, navigation, asset provenance, observable acceptance criteria, and reference images.

### Accepted historical evidence limitation

```text
FULL_HISTORICAL_REGRESSION_PACK = NOT_REVALIDATED_IN_ALPHA6_EXECUTION
MISSING_RETAINED_ACTUAL_EVIDENCE = REG-02 THROUGH REG-07
LIMITATION = ACCEPTED_NON_BLOCKING_FOR_PROMOTION
```

The limitation does not invalidate REG-08 or REG-09 and does not block baseline approval. It prevents claiming that the complete historical pack was revalidated during the Alpha.6 run.

Required future tests are recorded in:

`projects/symphonie/reports/ALPHA6_HISTORICAL_EVIDENCE_TEST_PLAN.md`

The future evidence plan is `PLANNED_NOT_AUTHORIZED`.

## Historical Phase 3A baseline

```text
VERSION = 0.1.0-alpha.5
STATUS = HISTORICAL_APPROVED_BASELINE_CLOSED_IMMUTABLE
```

Alpha.5 remains preserved as immutable historical evidence.

## Current Phase 4A implementer baseline

```text
SKILL = symphonie-ui-implementer
VERSION = 0.1.0-alpha.3
PHASE = 4A
CAPABILITY = SOURCE_WRITE
STATUS = APPROVED_BASELINE_CLOSED_IMMUTABLE
STATIC_VALIDATION = PASS
RUNTIME_VALIDATION = PASS
RUNTIME_SUITE = IMP-REG-01 THROUGH IMP-REG-12
BASELINE_HEAD = c2f3159e754d356f23b6855f2aecf1a663209835
```

Its approval does not authorize release, installation, migration, or integration.

## Validated synthetic architect-to-implementer handoff

Project: `handoff-controlled-017`

```text
RESULT = PASS_WITH_FINDINGS
HANDOFF_COMPATIBILITY = PASS
CODEX_DISCOVERY_AND_INTERPRETATION_AS_CHAIN = PASS
VALIDATED_CHAIN = architect -> human gate -> implementer -> build -> manual browser validation
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

The synthetic exercise validated Phase 3A contract generation, preservation of the human design gate, Phase 4A consumption of canonical JSON contracts, bounded application-source changes, successful build, browser rendering, responsive behavior, keyboard and focus behavior, accessibility basics, action preservation, and boundary checks.

It does not establish execution on a real design, reproducibility, production readiness, release, migration, or integration.

## Canonical minimal handoff knowledge

The LAB records three verified generic controls:

- `knowledge/contracts/phase3-minimum-assertions.json`;
- `knowledge/contracts/action-preservation.json`;
- `knowledge/regressions/imp-reg-11.json`.

They provide minimum Phase 3A exit assertions, UI-action preservation, and fail-closed authorization checks before observable effects.

## Current operational sequence

```text
1. DEC-LAB-010 aprobó la arquitectura del repositorio dedicado.
2. DEC-LAB-011 aprobó Phase 0 v0.1 como baseline experimental sin runtime.
3. DEC-LAB-012 registró el repositorio privado y la arquitectura de memoria gobernada.
4. Bootstrap-003, Repair-005, Reconciliation-006 y Canonicalization-007 están consumidas; el HEAD canónico es `8692a539bc339ea7b4258d78b3ce9f5f5635f407`.
5. El LAB fue reconciliado con la baseline documental de ocho fases mediante State-Reconciliation-008.
6. La siguiente transición recomendada es revisar la estructura del LAB y priorizar schemas de las fases aún no probadas.
7. Runtime, ingesta, embeddings, acceso automático, datos reales, diseño real, repetibilidad, evidencia histórica y migración requieren autorizaciones independientes.
```

## Authorization state

```text
DEC_LAB_010_011_DOCUMENTATION = APPROVED_RECORDED_AUTHORIZATION_CONSUMED
DEC_LAB_012_DOCUMENTATION = APPROVED_RECORDED_AUTHORIZATION_CONSUMED
SYMPHONIE_REPOSITORY_CREATION = COMPLETED_VERIFIED_AUTHORIZATION_CONSUMED
SYMPHONIE_BOOTSTRAP = COMPLETED_VERIFIED_AUTHORIZATION_CONSUMED
SYMPHONIE_DOCUMENTARY_REPAIR_005 = CONSUMED_COMPLETED_VERIFIED
SYMPHONIE_PHASE0_RECONCILIATION_006 = CONSUMED_COMPLETED_VERIFIED
SYMPHONIE_EIGHT_PHASE_CANONICALIZATION_007 = CONSUMED_COMPLETED_VERIFIED
LAB_SYMPHONIE_STATE_RECONCILIATION_008 = CONSUMED_COMPLETED_VERIFIED
PHASE_0_RUNTIME = NOT_AUTHORIZED
PHASE_0_REAL_CLIENT_USE = NOT_AUTHORIZED
HISTORICAL_EVIDENCE_EXECUTION = NOT_AUTHORIZED
PRODUCT_CHANGE = NOT_AUTHORIZED
REAL_DESIGN_EXECUTION = NOT_AUTHORIZED
REPEATABILITY_TEST = NOT_AUTHORIZED
SKILL_MERGE = NOT_AUTHORIZED
SKILL_RELEASE = NOT_AUTHORIZED
SKILL_INSTALLATION = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
RAG_RUNTIME = NOT_AUTHORIZED
RAG_INGESTION = NOT_AUTHORIZED
RAG_EMBEDDINGS = NOT_AUTHORIZED
RAG_AUTOMATIC_REPOSITORY_ACCESS = NOT_AUTHORIZED
RAG_REAL_PROJECT_DATA = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
```

## Next action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended transition:

`REVIEW_LAB_REPOSITORY_STRUCTURE_THEN_PRIORITIZE_UNTESTED_PHASE_CONTRACT_SCHEMAS`
