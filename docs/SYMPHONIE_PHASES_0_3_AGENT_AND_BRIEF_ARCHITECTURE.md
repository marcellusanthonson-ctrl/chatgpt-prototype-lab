# Symphonie phases 0–3: agent responsibility and brief architecture

Decision: `DEC-LAB-022`

## Governing model

Jonathan Martínez owns all normative, product, architecture and visual approval gates.

ChatGPT owns process coordination, evidence reconciliation, canonical brief synthesis, validation and bounded execution orders.

Claude performs Discovery, definition, research or independent critique only when explicitly assigned. Claude output is evidence or a proposal to reconcile; it is not an automatic order to Codex.

Codex produces prototypes, documentation or implementation only from a bounded execution brief. Codex has no autonomous product, architecture or visual approval authority.

## Phase responsibilities

### Phase 0

- `0A_CAPTURE`: ChatGPT by default; Claude optional.
- `0B_ANALYZE_AND_CLASSIFY`: ChatGPT coordinates and validates; Claude may perform the assigned analysis.
- `0C_HUMAN_DECISION`: Jonathan Martínez only.

### Phase 1

ChatGPT owns the process and final canonical `PRODUCT_BRIEF`. Claude may conduct interviews, research, problem reconstruction, hypothesis analysis and contradiction detection when assigned. Jonathan approves the exact brief revision.

### Phase 2

ChatGPT owns cross-phase coherence and the final `ARCHITECTURE_SCOPE_PACKAGE`. Claude may propose alternatives, trade-offs and critiques. Codex may produce bounded technical feasibility evidence. Jonathan approves scope and architecture.

### Phase 3

ChatGPT owns UX/UI synthesis, direction, change-budget classification and the final `UX_UI_DESIGN_BRIEF`. Claude may research or independently critique. Codex creates the authorized prototype or implementation. Jonathan performs the visual gate.

## Canonical brief chain

1. `PRODUCT_BRIEF`
   - Business type, problem, users, value proposition, product objectives, features, scope, exclusions, constraints, success criteria and approved product decisions.

2. `ARCHITECTURE_SCOPE_PACKAGE`
   - Information architecture, navigation, journeys, functional domains, surfaces, integrations, technical architecture, non-functional requirements and Phase 3 entry criteria.

3. `UX_UI_DESIGN_BRIEF`
   - Experience objectives, task hierarchy, interaction states, accessibility intent, visual concept, composition, typography, color, photography, materiality, controls, motion, responsive rules and prohibited patterns.

4. `CODEX_EXECUTION_BRIEF`
   - Exact task mode, parent artifact, artifact roles, allowed difference, locked surfaces, outputs, validation commands, stop conditions, commit/push authority and response contract.

## Reference and digest policy

Each brief references the exact parent revision and digest. Lower-level briefs do not copy or silently replace the canonical content of higher-level briefs.

`SUCCESSOR = PRESERVED_PARENT + APPROVED_ADDITIONS + EXPLICIT_CHANGES`

A lower-level brief cannot change a product, scope, architecture or visual decision without reopening the owning phase and obtaining the applicable human gate.

## Invalidation rules

- Product or business change invalidates affected Phase 2 and Phase 3 outputs.
- Architecture, navigation or scope change invalidates affected Phase 3 outputs.
- Visual-direction change updates Phase 3 but cannot silently alter product or architecture.
- A localized correction may use only a new `CODEX_EXECUTION_BRIEF` when all higher-level decisions remain unchanged.

## Execution modes

- `OPEN_EXPLORATION`: proposals only; human selection required.
- `BOUNDED_EXPLORATION`: only declared variables may vary.
- `DERIVATIVE_REVISION`: exact parent plus a declared change budget.
- `SURGICAL_PATCH`: creative autonomy none; unmentioned elements locked.
- `EXACT_REPRODUCTION`: no intentional visual or behavioral difference.

## Required gates

Codex may not begin a Phase 3 implementation until:

- product brief revision is approved;
- architecture and scope revision is approved;
- UX/UI direction or bounded exploration is approved;
- artifact roles and change budget are defined;
- validation oracles and the human gate are defined;
- an explicit execution authorization exists.

A technical pass does not create product, architecture, accessibility or visual approval.

## Authority effect

This document defines governance and documentary contracts only. It does not authorize runtime, product changes, image or HTML generation, skill integration, deployment or release.
