# Project Foundation Contract — Architecture v0.1.0

Document-Role: TRANSVERSAL_DOCUMENTARY_CAPABILITY
Authority-Effect: NONE
Runtime-Effect: NONE
Integration-Status: NOT_INTEGRATED

## Purpose

The Project Foundation Contract defines what must be true for a project to be considered sufficiently specified, architecturally coherent, testable, observable and recoverable. It is inspired by specification-driven development but remains risk-proportional and evidence-aware.

The contract is not an execution authorization, does not select a stack and does not replace the project repository.

## Operating model

1. Jonathan provides an idea, constraint set or project intent.
2. The LAB resolves applicable canonical knowledge, rules, patterns, rejected patterns and evidence.
3. A project-specific `PROJECT_FOUNDATION_CONTRACT` is produced or updated in the project repository.
4. The LAB emits a `LAB_TO_SYMPHONIE_BRIEF` containing findings, unresolved assumptions, mandatory gates and source references.
5. Symphonie parses the brief into phase specifications and bounded execution briefs.
6. The project implementation produces tests and evidence derived from the contract.
7. Results may generate candidate transversal learnings, but no project result becomes a global rule without separate evaluation and approval.

## Ownership

### LAB

Owns schemas, rule semantics, quality classes, evidence requirements, failure-mode taxonomy and reusable patterns.

### Symphonie

Owns parsing, contextual phase planning, brief generation, agent assignment, gate orchestration and evidence reconciliation.

### Project repository

Owns the concrete contract instance, product architecture, implementation, tests, runtime evidence, operational state and project continuity.

## Rule classes

- `INVARIANT`: cannot be violated within the current project contract.
- `GUARDRAIL`: deviation requires an explicit project decision.
- `RECOMMENDED_PATTERN`: preferred when applicability conditions hold.
- `REJECTED_PATTERN`: known unsafe or repeatedly defective pattern.
- `HYPOTHESIS`: requires evidence before promotion.
- `CONTEXTUAL_CONSTRAINT`: applies only to the stated project context.

## Evaluation outcomes

- `COMPLIANT`
- `COMPLIANT_WITH_REQUIRED_MODIFICATIONS`
- `INSUFFICIENT_SPECIFICATION`
- `ARCHITECTURALLY_UNSAFE`
- `CONTRADICTS_PROJECT_INVARIANT`
- `UNPROVEN_HIGH_RISK_ASSUMPTION`

A result must include source references, favorable and contrary evidence, uncertainty and the consequence for the next phase.

## Three-state verification rule

The contract distinguishes:

1. `CONFIGURED`: the intended configuration or artifact is stored.
2. `EFFECTIVE`: the configuration is available to the relevant runtime or control plane.
3. `BEHAVIOR_VERIFIED`: the observable system behavior satisfies the expected result.

No state implies the next. This rule generalizes the PL003 learning that stored IAM policy, effective API authorization and simulated decision are separate facts.

## Minimum gates

1. Context and canonical-source gate.
2. Product intent and user-flow gate.
3. Invariant and risk gate.
4. Architecture and failure-mode gate.
5. Visual and interaction quality gate when applicable.
6. Implementation-contract gate.
7. Observability and evidence gate.
8. Atomic real-system validation gate when runtime testing is authorized.
9. Rollback and final-state reconciliation gate.

## Symphonie exchange boundary

The `LAB_TO_SYMPHONIE_BRIEF` is a structured handoff, not an authorization. Symphonie may decompose only the approved contract scope. Any runtime, integration, infrastructure or product mutation still requires a separate explicit authorization.

## Promotion boundary

This package is documentary and not integrated. A future pilot must separately select one project, instantiate the contract, define acceptance criteria and authorize Symphonie consumption. Successful pilot evidence does not automatically make the contract mandatory for every project.
