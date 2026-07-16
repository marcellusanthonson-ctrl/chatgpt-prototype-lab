# Symphonie Continuity Protocol — Phase 0 and Claude Skills

Document-ID: `symphonie.continuity.phase0-claude-skills`
Revision: `0.1`
Status: `DRAFT`
Approved: `NO`
Canonical protocol: `NO`
Runtime authorized: `NO`

## 1. Purpose

Provide a bounded handoff for continuing Symphonie work in a new conversation after the 2026-07-15 intake and external-skill experiment.

This protocol is a continuity aid. It does not replace the canonical repository read order, approve any proposal, or authorize repository writes, runtime, integration, migration, release, implementation, or work on a real client case.

## 2. Mandatory opening sequence

Before answering about current state, decisions, authorizations, or the next Symphonie action, read from `marcellusanthonson-ctrl/chatgpt-prototype-lab`, branch `main`, in this order:

1. `LAB_CONTRACT.md`
2. `METHODOLOGY.md`
3. `CURRENT_STATE.json`
4. `CURRENT_STATE.md`
5. `registry/projects.json`
6. `projects/symphonie/PROJECT_STATE.md`
7. decisions in force relevant to Symphonie
8. open errors
9. applicable validated patterns
10. this continuity protocol
11. `projects/symphonie/reports/SYMPHONIE_SESSION_REPORT_2026-07-15_INTAKE_AND_RISK_TIER_1.md`
12. `projects/symphonie/reports/SYMPHONIE_INTAKE_DRY_RUN_001.md`
13. `projects/symphonie/knowledge/contracts/claude-intake-experiment-instructions.md`

`CURRENT_STATE.json` remains the structured source of truth. This protocol must never override a newer state, decision, error, pattern, or project record.

## 3. Identity and authority checkpoint

At the start of the new conversation, confirm:

```text
SOLE_APPROVER = Jonathan Martínez
CHATGPT_ROLE = coordinate, analyze, validate, audit, prepare bounded orders
CLAUDE_ROLE = discovery or definition only when explicitly assigned
CODEX_ROLE = bounded technical executor without autonomous authority
COMMIT_CREATES_AUTHORIZATION = NO
```

If the repository cannot be consulted, state that explicitly and do not claim the current state.

## 4. Current Symphonie baseline to verify, not assume

The last observed state at creation of this draft was:

```text
PROJECT = symphonie
STATUS = KNOWN_AND_SYNCED
PHASE_3A_SKILL = symphonie-ux-ui-architect 0.1.0-alpha.6
PHASE_4A_SKILL = symphonie-ui-implementer 0.1.0-alpha.3
REAL_DESIGN_EXECUTION = NOT_AUTHORIZED
REPEATABILITY_TEST = NOT_AUTHORIZED
SKILL_INSTALLATION = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
NEXT_AUTHORIZED_ACTION = NONE_UNTIL_NEW_EXPLICIT_APPROVAL
```

A new conversation must verify every field against `CURRENT_STATE.json` and `projects/symphonie/PROJECT_STATE.md` before using it.

## 5. Session evidence to reconstruct

The preceding session produced three distinct evidence layers:

### 5.1 Intake dry run

An anonymized animal-shelter fundraising scenario tested a proposed Phase 0B analysis. Result: `PASS_WITH_FINDINGS`.

Important findings:

- intermediary-only information is declared or plausible, not independently verified;
- structural operating-deficit interpretations belong to Discovery as hypotheses;
- legal, tax, payment-provider, and data-protection claims require qualified validation;
- unrelated project memory must not appear;
- Claude recommends, while Jonathan decides.

### 5.2 Claude experiment instructions

A draft contract separates what belongs to the Claude skill from what belongs to a bounded experiment order.

```text
SKILL_OWNS = detailed interview or intake procedure
ORDER_OWNS = case, inputs, privacy limits, outputs, authority, stop conditions, success criteria
```

The experiment order must not duplicate the entire skill because that creates competing sources of truth.

### 5.3 External interview skill runtime test

The external `design-research` plugin and its `interview-script` capability were installed only in an isolated local Claude Code test directory.

Observed result:

```text
FIRST_RUN = PASS_WITH_FINDINGS
CORRECTED_RUN = PASS
CORRECTION_MODEL_TIME = 48_SECONDS
PROPOSED_STATUS = PROVISIONALLY_ADMITTED
DECLARED_USE = INTERVIEW_SCRIPT_GENERATION_ONLY
CANONICAL_APPROVAL = NO
SYMPHONIE_INTEGRATION = NO
```

The command wrote to a temporary Claude scratchpad and offered artifact publication. No workspace write, repository change, or publication occurred.

## 6. Do not conflate these systems

Maintain the following separation:

```text
SYMPHONIE
= workflow consumer and project coordinator

MAMMOTHSKILLS
= possible future canonical producer, adapter, auditor, and publisher of reusable skills

EXTERNAL_CLAUDE_PLUGIN
= upstream third-party capability used in an isolated experiment

LOCAL_CLAUDE_INSTALLATION
= test environment only; not a Symphonie dependency
```

A successful local test does not establish:

- canonical ownership;
- approved release identity;
- supply-chain trust;
- compatibility across future Claude versions;
- Symphonie installation;
- MammothSkills migration;
- authorization for real-client use.

## 7. Proposed Phase 0 model

The session explored:

```text
0A = CAPTURE
0B = ANALYZE_AND_CLASSIFY
0C = HUMAN_DECISION
```

Required boundaries if this proposal is developed further:

- 0A records client declarations and source documents without inferring approval;
- 0B distinguishes `CLIENT_DECLARED`, `DOCUMENT_EXTRACTED`, `INFERRED`, `UNKNOWN`, and `CONTRADICTORY`;
- 0B identifies gaps and recommends readiness but does not approve progression;
- 0C belongs exclusively to Jonathan Martínez;
- Discovery validates material hypotheses and direct-user understanding;
- no phase assumes software is required;
- no phase produces implementation, quotation, or legal conclusions without separate authority and evidence.

Status at continuity handoff:

```text
MODEL_STATUS = PROPOSED_NOT_APPROVED
```

## 8. Proposed risk-tier protocol

Use the following only as an evaluation draft until explicitly approved.

### 8.1 Classify capability before testing

Examples:

```text
DOCUMENT_GENERATION
DOCUMENT_WRITE_LOCAL
REPOSITORY_WRITE
COMMAND_EXECUTION
NETWORK_ACCESS
EXTERNAL_PUBLICATION
CREDENTIAL_ACCESS
HIGH_IMPACT_RECOMMENDATION
```

Classify actual runtime behavior, not only README or `SKILL.md` claims.

### 8.2 Determine tier

```text
RISK_TIER_1
- documentary or advisory output
- isolated workspace
- no persistent project write
- no external effect
- narrow declared use

RISK_TIER_2
- persistent local writes
- multiple output formats
- wider reuse
- moderate decision consequence

RISK_TIER_3
- repository modification
- command execution affecting systems
- network or external publication
- credentials or sensitive data
- high-impact or production use
```

When uncertain, assign the higher tier.

### 8.3 Tier 1 minimum evidence

1. identify source repository and exact commit or release;
2. inspect the relevant skill and command documentation;
3. install only in an isolated local scope;
4. define one bounded representative case;
5. define no more than ten objective controls;
6. execute once;
7. record permissions, writes, publication offers, and other side effects;
8. score the output;
9. issue at most one bounded correction for minor findings;
10. assign a proposed state without creating canonical approval.

### 8.4 Proposed Tier 1 scoring

```text
9–10 controls = candidate for PROVISIONALLY_ADMITTED
7–8 controls = PASS_WITH_FINDINGS
0–6 controls = REJECTED
```

A correction may close minor output defects. It must not conceal capability expansion, unauthorized effects, unsafe data handling, or failure to respect authority.

### 8.5 Escalate to Tier 2 or Tier 3 when

- the skill writes outside a temporary scratchpad;
- it runs shell commands;
- it edits repositories;
- it accesses network resources or credentials;
- it publishes externally;
- it handles personal or sensitive information;
- it makes legal, medical, financial, employment, safety, or other high-impact decisions;
- the intended use expands beyond the tested declaration;
- upstream changes invalidate the tested version;
- a wrapper or adaptation materially changes behavior.

## 9. `interview-script` declared-use boundary

The tested capability may only be described as a provisional candidate under this exact proposed scope:

```text
CAPABILITY = generate a bounded qualitative interview script
DECLARED_USE = interview-script generation for discovery or intake preparation
TARGET_RUNTIME = isolated local Claude Code experiment
DATA = synthetic or anonymized
HUMAN_REVIEW = mandatory
DECISION_AUTHORITY = none
IMPLEMENTATION_AUTHORITY = none
```

Do not claim approval for:

- full intake analysis;
- legal, tax, medical, or financial interviews;
- autonomous participant contact;
- recording, storage, or processing of real interview data;
- publication;
- integration into Symphonie;
- inclusion in MammothSkills;
- general approval of the `design-research` plugin or `designer-skills` collection.

## 10. Standard test controls for the next interview case

Use these controls unless a later approved contract supersedes them:

1. explicit participant and research objective;
2. requested time limit respected;
3. requested maximum question count respected;
4. first substantive question starts from a recent real event;
5. questions remain open and neutral;
6. sensitive topics are marked;
7. current behavior is separated from future wishes;
8. no software or solution assumption;
9. no unsupported professional conclusions;
10. no sensitive-data request or scope expansion.

Record both output quality and runtime behavior.

## 11. Recommended next bounded options

At the opening of the next conversation, present the verified state and ask Jonathan to choose or authorize one bounded direction. Reasonable options include:

### Option A — Phase 0 definition

Prepare a documentary proposal for an approved `0A → 0B → 0C` contract, including schemas, gates, evidence classes, privacy rules, and approval boundaries.

This would require a new explicit documentation authorization before repository writes.

### Option B — Second Tier 1 runtime case

Run `interview-script` against a materially different synthetic or anonymized scenario to test repeatability and declared-use boundaries.

This would require explicit runtime authorization identifying the case, skill version, local workspace, permitted outputs, prohibited effects, and stop conditions.

### Option C — Negative-control test

Test whether the skill resists leading questions, premature solution assumptions, excessive duration, sensitive-data requests, or artifact publication.

This would require a separate bounded runtime authorization.

### Option D — Skill governance design

Define where provisional skill records, versions, checksums, test evidence, suspension, and supersession should live between LAB, Symphonie, and MammothSkills.

This is documentary design and requires explicit authorization before canonical writes.

### Option E — Return to the principal Symphonie roadmap

Plan the real-design architect-to-implementer execution already identified in current state, without treating the interview skill experiment as a prerequisite.

Any runtime or repository-writing step requires its own bounded authorization.

## 12. Opening checklist for a new conversation

```text
[ ] Repository main consulted
[ ] LAB_CONTRACT.md read
[ ] METHODOLOGY.md read
[ ] CURRENT_STATE.json read and treated as source of truth
[ ] CURRENT_STATE.md checked for human-readable alignment
[ ] registry/projects.json read
[ ] projects/symphonie/PROJECT_STATE.md read
[ ] relevant decisions read
[ ] open errors read
[ ] applicable patterns read
[ ] this protocol read
[ ] session report read
[ ] current HEAD recorded
[ ] no authorization inferred from commits or conversation memory
[ ] proposed next action separated from authorized next action
```

## 13. Required structure for any new technical order

Every technical order must state:

```text
RECIPIENT
EXECUTING_AGENT
REPOSITORY
BRANCH
EXPECTED_HEAD
AUTHORIZED_FILES
PERMITTED_ACTIONS
PROHIBITED_ACTIONS
VALIDATIONS
STOP_CONDITIONS
COMMIT_AUTHORIZATION
PUSH_AUTHORIZATION
EXPECTED_RESULT
```

An authorization is consumed when completed and cannot be reused.

## 14. Closing checklist for the next session

Before ending a future session:

```text
[ ] distinguish observed facts from hypotheses and proposals
[ ] record exact skill or repository versions used
[ ] record runtime permissions and side effects
[ ] record PASS, PASS_WITH_FINDINGS, BLOCKED, or REJECTED
[ ] record what remains unapproved
[ ] record whether authorization was consumed
[ ] update canonical state only under explicit authorization
[ ] create a new continuity note only when needed and authorized
[ ] do not preserve full transcripts when event records suffice
```

## 15. Stop conditions

Stop and request clarification or a new authorization when:

- repository HEAD differs from the expected value in an approved order;
- current state contradicts this draft;
- the intended external skill version cannot be confirmed;
- the requested case contains unnecessary sensitive data;
- a local test attempts persistent workspace or repository writes outside scope;
- artifact publication, network access, command execution, or credentials are requested unexpectedly;
- a task shifts from discovery or definition into implementation;
- a third-party skill is being treated as canonically approved without a recorded decision;
- a proposed state is being written as approved state;
- additional files are needed beyond an authorized file list.

## 16. Minimal handoff message for the next conversation

The following message may be pasted into a new conversation, but it does not replace repository verification:

```text
Continue Symphonie from the canonical LAB repository.
Read the mandatory continuity order beginning with LAB_CONTRACT.md and CURRENT_STATE.json, then read:
- projects/symphonie/PROJECT_STATE.md
- projects/symphonie/continuity/SYMPHONIE_CONTINUITY_PROTOCOL_PHASE0_AND_CLAUDE_SKILLS.md
- projects/symphonie/reports/SYMPHONIE_SESSION_REPORT_2026-07-15_INTAKE_AND_RISK_TIER_1.md
- projects/symphonie/reports/SYMPHONIE_INTAKE_DRY_RUN_001.md
- projects/symphonie/knowledge/contracts/claude-intake-experiment-instructions.md

Report the verified current state, distinguish proposals from approvals, list pending decisions, and recommend one bounded next action. Do not execute or write anything without my explicit authorization.
```

## 17. Non-authorization statement

This draft protocol does not approve the risk-tier model, Phase 0, the external skill, a Symphonie installation, a MammothSkills migration, a real-client interview, runtime, repository changes, release, deployment, or implementation.

## 18. Documentation authorization record

Jonathan Martínez explicitly authorized creation of this draft and `projects/symphonie/reports/SYMPHONIE_SESSION_REPORT_2026-07-15_INTAKE_AND_RISK_TIER_1.md` in one documentary commit on `main`, with expected HEAD `6b5b380eae5cc0977cb448758feef34e2e119f9e`.

The authorization permits exactly those two files and prohibits changes to current state, project state, decisions, patterns, errors, skills, MammothSkills, product repositories, runtime, integration, release, migration, and implementation.