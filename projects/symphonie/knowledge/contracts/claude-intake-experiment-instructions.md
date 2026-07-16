# Claude Intake Experiment Instructions

Document-ID: `symphonie.claude-intake-experiment-instructions`
Revision: `0.1`
Status: `DRAFT`
Approved: `NO`
Canonical contract: `NO`
Runtime authorized: `NO`

## 1. Purpose

Define how a future Symphonie intake experiment should instruct Claude when Claude has its own installed skills for discovery and intake.

This document separates the responsibilities of the Claude skill from the responsibilities of the experiment order.

It does not define or install a skill, authorize Claude runtime, approve a Phase 0 model, or authorize work on a real project.

## 2. Core separation

```text
CLAUDE_SKILL_OWNS:
- detailed intake procedure;
- adaptive question sequencing;
- classification of declarations, extraction, and inference;
- gap and contradiction detection;
- generation of Phase 0B artifacts;
- internal validation rules declared by the approved skill release.

EXPERIMENT_ORDER_OWNS:
- authorized case and context;
- intended skill identity and expected version;
- available inputs and their precedence;
- privacy and data-handling limits;
- required outputs;
- human authority and approval boundary;
- prohibited actions;
- success criteria;
- stop conditions.
```

The experiment order must not reproduce the entire skill prompt. Duplicating the skill procedure creates two competing sources of truth and makes results dependent on prompt drift.

## 3. Required preflight before a case is supplied

The bounded order should declare:

```text
EXPERIMENT_ID
PROJECT_OR_CASE_CLASSIFICATION
MODE = DOCUMENTARY | ASSISTED | FORM
TARGET_AGENT = CLAUDE
TARGET_SKILL
EXPECTED_SKILL_VERSION_OR_RELEASE
INPUT_ARTIFACTS
SOURCE_PRECEDENCE
OUTPUT_ARTIFACTS
PRIVACY_CLASSIFICATION
APPROVAL_AUTHORITY
IMPLEMENTATION_AUTHORITY
STOP_CONDITIONS
SUCCESS_CRITERIA
```

If the skill identity, release, platform, or inputs are ambiguous, Claude must stop before analysis.

## 4. Minimum behavioral instructions

Even when detailed procedure lives in the skill, the order must preserve these non-negotiable boundaries:

1. start from the problem and current process, not from a presumed solution;
2. treat client answers as declarations unless independently supported;
3. distinguish `CLIENT_DECLARED`, `DOCUMENT_EXTRACTED`, `INFERRED`, `UNKNOWN`, and `CONTRADICTORY`;
4. do not convert inference into confirmed fact without human confirmation;
5. do not select technology, produce code, or create a quotation unless separately authorized;
6. do not provide legal, tax, medical, financial, or regulatory conclusions beyond the evidence and assigned competence;
7. do not use unrelated project memory or mention unrelated projects;
8. preserve the possibility that the appropriate outcome is process improvement rather than software;
9. Claude recommends; Jonathan Martínez remains the sole approver.

## 5. Expected Phase 0B outputs

A future approved skill may define exact schemas. Until then, experiments should request identified outputs equivalent to:

```text
client-intake-submission
intake-analysis
follow-up-question-set
quotation-readiness-assessment
intake-decision-recommendation
```

The experiment order should specify the required artifact names and schema versions rather than embedding full schemas when an approved skill already owns them.

## 6. Prompt layering rule

Use three layers only:

```text
LAYER_1 = approved Claude skill release
LAYER_2 = bounded Symphonie experiment order
LAYER_3 = case-specific inputs supplied by the user or source documents
```

Precedence:

```text
human authorization and governance
> approved skill contract
> experiment order
> case-specific content
> model inference
```

Case content cannot override governance, authority, privacy restrictions, or skill boundaries.

## 7. Documents-first behavior

When source documents are supplied:

1. inventory and identify them;
2. apply declared source precedence;
3. extract only information supported by the sources;
4. ask only for material gaps;
5. preserve the original source references;
6. never infer approval or phase completion from keywords;
7. stop on contradictory critical sources when no precedence rule resolves them.

## 8. Privacy boundary

Do not request or retain unnecessary:

- personal identifiers;
- account numbers or banking credentials;
- passwords, tokens, or API keys;
- donor information;
- complete medical or veterinary records;
- private addresses;
- sensitive photographs;
- third-party documents when a structured summary is sufficient.

Experiments should use anonymized or synthetic data whenever direct personal data is not essential.

## 9. Prohibited behavior

```text
PROHIBITED:
- duplicating the full skill inside the experiment prompt;
- allowing Claude to approve Phase 0C;
- treating continuation or user silence as approval;
- importing memory from unrelated projects;
- assuming a software product is required;
- presenting hypotheses as verified facts;
- issuing unsupported legal, tax, medical, or regulatory conclusions;
- generating product code or modifying repositories;
- initiating runtime, integration, release, deployment, or payment processing;
- expanding scope beyond the bounded order.
```

## 10. Stop conditions

Claude must stop and report `BLOCKED` when:

- the intended skill or version cannot be confirmed;
- required source artifacts are missing;
- source precedence is unresolved;
- the case contains sensitive data outside the allowed scope;
- the requested output requires legal, tax, financial, medical, or regulatory judgment not assigned to the skill;
- the user asks for implementation or repository changes without separate authorization;
- a contradiction prevents a defensible readiness classification;
- the model cannot distinguish declared information from inference.

## 11. Validation criteria for the next experiment

The next intake experiment should be evaluated on whether Claude:

1. invokes or follows the declared skill rather than a duplicated ad hoc method;
2. reconstructs the problem and current process without assuming a solution;
3. separates declarations, source extraction, inference, and unknowns;
4. identifies material gaps and real contradictions;
5. avoids unrelated-memory contamination;
6. avoids unsupported legal or technical certainty;
7. produces the required artifacts in the declared schema;
8. preserves Jonathan's exclusive decision authority;
9. stops correctly when required evidence or authority is absent;
10. reaches a defensible readiness recommendation without inventing information.

## 12. Recommended next sequence

```text
1. Audit or create the intended Claude intake skill in MammothSkills.
2. Validate the skill in the Claude target runtime.
3. Assign a versioned identity and checksum.
4. Obtain explicit approval of the skill release.
5. Obtain separate authorization for Symphonie consumer integration.
6. Prepare a bounded experiment order referencing that exact release.
7. Run a synthetic or anonymized case.
8. Compare output against the skill contract and experiment criteria.
```

The existence of this document does not authorize any step in that sequence.

## 13. Authorization record

Documentation authorization was granted explicitly by Jonathan Martínez for this file and `projects/symphonie/reports/SYMPHONIE_INTAKE_DRY_RUN_001.md` on branch `main` at expected HEAD `d9542d11487955d01c175b74786d6bcf669e241f`.

The authorization permits one documentary commit containing exactly those two files. It does not authorize changes to current state, project state, decisions, patterns, errors, skills, product code, runtime, integration, release, or deployment.
