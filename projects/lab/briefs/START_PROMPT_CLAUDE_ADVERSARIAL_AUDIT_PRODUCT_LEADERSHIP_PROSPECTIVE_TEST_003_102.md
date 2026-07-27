# Start Prompt — Claude Adversarial Audit of Product Leadership Prospective Test 003

Perform an independent adversarial read-only audit of `PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003` in:

- repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`
- branch: `main`

Canonical authorization:

`projects/lab/authorizations/AUTHORIZATION_LAB_CLAUDE_ADVERSARIAL_AUDIT_PRODUCT_LEADERSHIP_PROSPECTIVE_TEST_003_102.json`

Canonical brief:

`projects/lab/briefs/BRIEF_CLAUDE_ADVERSARIAL_AUDIT_PRODUCT_LEADERSHIP_PROSPECTIVE_TEST_003_102.json`

Audit mode:

`INDEPENDENT_ADVERSARIAL_READ_ONLY`

## Preflight

1. Verify the live remote HEAD of `main` and record it as the audited HEAD.
2. Read `project-sources/chatgpt/START_HERE.md` and follow its required order.
3. Confirm the working tree remains clean.
4. Do not edit, stage, commit, push or otherwise modify the repository.
5. If canonical sources cannot be verified, return `INSUFFICIENT_EVIDENCE` and stop.

## Required sources

Read completely:

- `projects/lab/test-designs/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/PROPOSAL.json`
- `projects/lab/evidence/product-leadership/external-audit-execution-002/AUDIT_REPORT.md`
- `projects/lab/evidence/product-leadership/external-audit-execution-002/AUDIT_FINDINGS.json`
- `projects/lab/reconciliations/REC-LAB-PRODUCT-LEADERSHIP-EXTERNAL-AUDIT-002-002.json`
- `LAB_CONTRACT.md`
- `METHODOLOGY.md`

## Audit objective

Determine whether the prospective contract is ready for execution authorization, ready only after bounded corrections, requires material redesign, or remains insufficiently specified.

Do not repeat the prior audit of execution 002 except where its findings are needed to test whether contract 003 actually prevents recurrence.

## Required analysis

### Statistical design

Assess independently:

- the rationale and adequacy of two independent replications;
- the rationale for 160 paired fixtures per replication;
- whether `+1.0` is a defensible minimum relevant effect;
- the exact one-sided 95% studentized paired rule;
- pooled versus replication-level decision logic;
- heterogeneity between replications;
- missingness, exclusions and invalid pairs;
- treatment of ties;
- multiplicity across rubric dimensions;
- PASS, FAIL and INSUFFICIENT_EVIDENCE boundaries;
- whether a formal power or sensitivity analysis is required before execution.

### Effective blinding

Assess whether the contract specifies an executable protocol for:

- a common neutral response schema;
- common field order, renderer and length envelope;
- removal of arm-specific headings and stylistic fingerprints;
- preservation of substantive content during normalization;
- authority and timing for normalization;
- freezing normalized outputs before evaluation;
- evaluator information boundaries;
- an arm-guess test with a predeclared metric, sample size, chance tolerance, uncertainty rule and failure condition.

### Operational isolation and evidence

Assess whether the contract can prove:

- separate generator, evaluator and oracle-custodian contexts;
- immutable prompts and input manifests;
- tool and file access boundaries;
- session or process isolation;
- oracle and mapping custody;
- pre-unblind checkpoints;
- external or append-only timestamps;
- complete hashes and a declared LF/CRLF policy;
- prevention of unblinding before all scores and rationales are frozen.

### Rubric, controls and taxonomy

Assess:

- whether the existing 0–24 rubric risks ceiling saturation;
- whether fixture difficulty and rubric granularity are adequate;
- whether positive and negative controls can discriminate without overlapping PACKAGE outputs;
- exact precedence between `ACTIVE`, `INACTIVE` and `LIMITED_OR_AMBIGUOUS`;
- full three-class confusion-matrix metrics;
- macro precision and recall thresholds;
- the exact predeclared closed-scope denominator;
- whether the design prevents the ambiguities identified in `PL-CLEAN-028`, `033` and `035`.

### Governance

Confirm that:

- a test PASS would not automatically activate or integrate Product Leadership;
- a test FAIL would not automatically create a rejection decision beyond the declared scope;
- a separate reconciliation and human decision remain required;
- no runtime, product, Symphonie or real-data effect is authorized;
- stop conditions are explicit and fail closed.

## Classification rules

For every material claim return one of:

- `CONFIRMED`
- `MODIFIED`
- `REVERSED`
- `INSUFFICIENT_EVIDENCE`

Return exactly one global classification:

- `READY_FOR_EXECUTION_AUTHORIZATION`
- `READY_AFTER_BOUNDED_CORRECTIONS`
- `REQUIRES_MATERIAL_REDESIGN`
- `INSUFFICIENT_EVIDENCE`

Distinguish clearly between:

- strengths already present;
- missing executable details;
- material design defects;
- recommended corrections;
- authorization and human-decision boundaries.

## Required outputs

Create outside the repository:

1. `CLAUDE_AUDIT_REPORT.md`
2. `CLAUDE_AUDIT_FINDINGS.json`

The report must include:

- audited HEAD;
- scope and methodology;
- strengths;
- material gaps;
- findings for statistics, blinding, operational evidence, rubric/taxonomy and governance;
- exact corrections required before execution;
- global classification;
- one next action.

The JSON must include:

- `audit_id`;
- `audited_head`;
- `audit_mode`;
- `source_files`;
- `statistical_findings`;
- `blinding_findings`;
- `operational_evidence_findings`;
- `rubric_taxonomy_findings`;
- `governance_findings`;
- `required_corrections`;
- `global_classification`;
- `limitations`;
- `recommended_next_action`;
- `authority_effect: NONE`.

Calculate and report SHA-256 hashes for both files.

## Prohibitions

Do not:

- modify the repository;
- execute or simulate test 003;
- generate fixtures, outputs or scores;
- introduce thresholds based on new outcomes;
- authorize execution;
- promote, reject, activate or integrate Product Leadership;
- modify Symphonie or products;
- use real product data;
- create runtime, RAG, embeddings, vector storage, deployment or release effects.

A separate explicit reconciliation authorization is required before either audit output may be committed to the LAB.
