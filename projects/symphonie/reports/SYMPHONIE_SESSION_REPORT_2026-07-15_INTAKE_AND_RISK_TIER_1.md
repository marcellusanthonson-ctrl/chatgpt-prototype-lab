# Symphonie Session Report — Intake and Risk Tier 1

Document-ID: `symphonie.session-report.2026-07-15.intake-risk-tier-1`
Revision: `0.1`
Status: `RECORDED_SESSION_EVIDENCE`
Date: `2026-07-15`
Approved: `NO`
Canonical decision: `NO`
Runtime authorization created: `NO`
Integration authorization created: `NO`

## 1. Purpose

Record the work completed in the session concerning the proposed Symphonie Phase 0 intake model, the use of Claude for interview-script generation, and a fast risk-tier method for evaluating external skills.

This report records evidence and proposals. It does not approve a new Symphonie phase contract, admit a skill canonically, authorize runtime, modify MammothSkills, or authorize product execution.

## 2. Canonical context at session close

Symphonie remains a known and synchronized eight-phase workflow. The current approved Phase 3A and Phase 4A baselines remain unchanged. Real-design execution, repeatability testing, skill installation, integration, migration, release, product changes, and Codex execution remain separately controlled and are not authorized by this report.

Jonathan Martínez remains the sole approver. ChatGPT coordinates, validates, audits, and prepares bounded orders. Claude participates only when explicitly assigned discovery or definition work. Codex remains a bounded technical executor without autonomous authority.

## 3. Phase 0 model explored

The session reinforced the following experimental separation:

```text
0A = capture client-declared information
0B = Claude analyzes, classifies, detects gaps, and prepares a recommendation
0C = Jonathan Martínez decides, with ChatGPT presenting the evidence
```

This model remains experimental and unapproved. The preceding dry run supported the separation while identifying excess certainty, unsupported legal or financial conclusions, context contamination, and the need to preserve the boundary between intake and discovery.

## 4. External skill candidate

```text
SOURCE_REPOSITORY = Owl-Listener/designer-skills
OBSERVED_COMMIT = acc3e574b36ef2895268a176dbae886e1b845ae0
PLUGIN = design-research
SKILL_PATH = design-research/skills/interview-script/SKILL.md
TESTED_COMMAND = /design-research:interview
INSTALL_SCOPE = LOCAL
WORKSPACE = isolated Claude Code test directory
SYMPHONIE_INSTALLATION = NO
MAMMOTHSKILLS_IMPORT = NO
```

The candidate was selected because it provides interview-script structure, open-question guidance, broad-to-specific sequencing, probes, and non-leading-question safeguards relevant to Phase 0 and Discovery work.

## 5. Risk-tier method defined

A fast evaluation model was defined to reduce the cost of reviewing low-risk skills.

```text
AUDIT_DEPTH = CAPABILITY_RISK × CONSEQUENCE × REUSE_SCOPE
```

Proposed tiers:

- `RISK_TIER_1`: low-risk documentary or advisory capability; static screening plus one isolated runtime test; eligible only for provisional, declared-use admission.
- `RISK_TIER_2`: moderate capability or broader reuse; at least two tests and an explicit output contract.
- `RISK_TIER_3`: repository writes, command execution, external effects, high-impact decisions, or broad reuse; full audit required.

Proposed lifecycle states:

```text
UNREVIEWED
SCREENED
PROVISIONALLY_ADMITTED
VALIDATED_FOR_DECLARED_USE
REJECTED
SUSPENDED
SUPERSEDED
```

These tiers and states are session proposals. They are not yet approved methodology or canonical registry values.

## 6. Runtime environment and behavior observed

Claude Code `2.1.211` was installed and used in an isolated local directory. The `designer-skills` marketplace was added, and `design-research` was installed with local scope.

The command presented a guided wizard. Notable behavior:

1. initial categories were more generic than the supplied case and could erase case-specific context if accepted without customization;
2. predefined durations started at 30 minutes, but a custom 20-minute value was accepted;
3. the command created the draft in Claude's temporary scratchpad rather than in the project workspace;
4. the command offered publication as an artifact, but publication was declined;
5. reading the scratchpad required explicit permission;
6. no workspace file, shared artifact, repository change, or external publication was produced.

Observed effective capability:

```text
PRIMARY_CAPABILITY = DOCUMENT_GENERATION
SECONDARY_CAPABILITY = TEMPORARY_SCRATCHPAD_WRITE
WORKSPACE_WRITE = NO
EXTERNAL_PUBLICATION = OFFERED_BUT_NOT_EXECUTED
OBSERVED_RISK = LOW_WHEN_LOCAL_AND_ISOLATED
```

## 7. Test case and controls

The tested case concerned understanding how a person who informally administers an animal shelter in Chile organizes fundraising for veterinary care.

Required boundaries included:

- understand the current problem and process;
- identify actors, frictions, risks, and needs;
- do not assume software is required;
- do not design a solution;
- do not provide legal or tax conclusions;
- do not request personal, banking, or real-document data;
- produce an interview executable in no more than 20 minutes.

Ten runtime controls were used:

1. maximum 15 questions;
2. maximum 20 minutes;
3. begin from a recent real experience;
4. use open and neutral questions;
5. avoid assuming software;
6. avoid legal claims;
7. avoid sensitive-data requests;
8. separate current behavior from future wishes;
9. provide useful optional probes;
10. remain within scope.

Scoring proposal:

```text
9–10 = PROVISIONALLY_ADMITTED candidate
7–8 = PASS_WITH_FINDINGS
0–6 = REJECTED
```

## 8. First generation result

The first generated script was usable and respected most boundaries. It reconstructed the process, actors, frictions, and needs without assuming a digital solution.

Result:

```text
FIRST_RUN = PASS_WITH_FINDINGS
CONTROLS_PASSED = 8_OF_10
```

Findings:

- 16 numbered questions instead of the requested maximum of 15;
- the recent real experience appeared as question 4 rather than the first substantive question;
- financially sensitive questions were not explicitly marked;
- one question about problems or misunderstandings with collected money began in a partially closed and negatively oriented form.

The consent and follow-up-contact questions were treated separately from research-question quality because explicit consent may legitimately use a yes-or-no form.

## 9. Corrective iteration

A bounded correction prompt requested only:

- no more than 15 numbered questions;
- the first substantive question to concern a recent real fundraising event;
- `[SENSIBLE]` labels for money, payment, debt, accountability, or conflict questions;
- open and neutral wording;
- preservation of the 20-minute, no-solution, no-legal-conclusion boundaries;
- direct display in the conversation without artifact publication.

Claude reported a generation time of `48s`.

Second result:

```text
SECOND_RUN = PASS
NUMBERED_QUESTIONS = 15
FIRST_SUBSTANTIVE_QUESTION = RECENT_REAL_EVENT
SENSITIVE_QUESTIONS_MARKED = YES
MAX_DURATION = 20_MINUTES
SOFTWARE_ASSUMPTION = NO
LEGAL_OR_TAX_CONCLUSIONS = NO
PUBLICATION = NO
```

The correction required approximately two to three minutes end to end, including instruction entry and human review.

## 10. Time findings

The initial session included one-time setup costs: Claude Code installation, path resolution, marketplace addition, plugin installation, trust prompts, and interface familiarization.

Observed estimates:

```text
INITIAL_ENVIRONMENT_SETUP = approximately 26 minutes
FIRST_TEST_AND_REVIEW = approximately 12 minutes
CORRECTIVE_GENERATION = 48 seconds model time
CORRECTIVE_END_TO_END = approximately 2–3 minutes
EXPECTED_FUTURE_TIER_1_CYCLE = approximately 11–18 minutes
```

The principal cost was environment setup, not recurring Tier 1 evaluation.

## 11. Session conclusion

The experiment showed that a low-risk documentary skill can be screened, run once in isolation, corrected if needed, and evaluated in a short cycle without immediately adapting or importing the skill.

Proposed disposition:

```text
SKILL = interview-script
PROPOSED_STATUS = PROVISIONALLY_ADMITTED
DECLARED_USE = INTERVIEW_SCRIPT_GENERATION_ONLY
SCOPE = LOCAL_ISOLATED_CLAUDE_CODE_EXPERIMENTS
CANONICAL_APPROVAL = NOT_GRANTED
SYMPHONIE_INTEGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
```

`PROVISIONALLY_ADMITTED` is only a recommendation derived from this session. A future explicit approval is required before it becomes a canonical state or authorized Symphonie dependency.

## 12. Defined but not approved

The session defined the following proposals:

1. Phase 0 separation `0A → 0B → 0C`;
2. fast risk tiers for external skills;
3. one-test provisional admission for low-risk documentary skills;
4. declared-use scoping rather than collection-wide approval;
5. correction of output before modifying an external skill;
6. runtime behavior, not only `SKILL.md`, must be audited;
7. temporary scratchpad writing must be declared as an effective capability;
8. external publication options must remain disabled unless separately authorized.

None of these proposals modifies `METHODOLOGY.md`, `CURRENT_STATE.json`, decisions, patterns, errors, skill registries, or project authorization state.

## 13. Pending work

### Phase 0 and intake

- decide whether `0A → 0B → 0C` should become an approved Symphonie model;
- define authoritative schemas for intake submission, analysis, gaps, readiness, and decision recommendation;
- define the exact boundary between Intake and Discovery;
- determine when direct-client confirmation is mandatory;
- define privacy classes and source-precedence rules;
- test a direct interview with an actual or anonymized operator rather than an intermediary-only case.

### Skill governance

- decide whether to approve the proposed risk-tier method;
- decide where provisional-skill records should live canonically;
- determine whether `interview-script` should be adapted, wrapped, imported into MammothSkills, or remain external;
- run an additional case before claiming broader validity;
- test failure behavior, including scope-expansion, sensitive-data, and solution-leading prompts;
- verify exact upstream version, checksum, and update policy before any dependency claim;
- define suspension and supersession procedures for changed upstream skills.

### Symphonie roadmap

- plan and explicitly authorize a real-design execution through the approved architect-to-implementer chain;
- separately decide whether historical REG-02 through REG-07 evidence closure should be executed;
- repeat any real-design flow before claiming reproducibility;
- do not consider migration to MammothSkills until consumer need, approved artifact identity, target runtime, and separate authorization are established.

## 14. Explicit non-authorizations

This report does not authorize:

- changes to Symphonie or MammothSkills repositories;
- modification or redistribution of the external skill;
- canonical provisional admission;
- skill installation in Symphonie;
- runtime execution for a real client or product project;
- integration, migration, release, deployment, or product changes;
- legal, tax, financial, medical, or regulatory conclusions;
- creation of a shelter project.

## 15. Documentation authorization record

Jonathan Martínez explicitly authorized creation of this report and `projects/symphonie/continuity/SYMPHONIE_CONTINUITY_PROTOCOL_PHASE0_AND_CLAUDE_SKILLS.md` in one documentary commit on `main`, with expected HEAD `6b5b380eae5cc0977cb448758feef34e2e119f9e`.

The authorization permits exactly those two files and prohibits modifications to state documents, decisions, patterns, errors, skills, MammothSkills, product repositories, runtime, integration, release, migration, and implementation.