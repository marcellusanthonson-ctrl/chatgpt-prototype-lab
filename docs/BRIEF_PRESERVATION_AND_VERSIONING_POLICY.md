# Brief Preservation and Versioning Policy

Document-Role: GOVERNED_BRIEF_POLICY
Approved-By: Jonathan Martínez
Effective-Date: 2026-07-26
Authority-Effect: DOCUMENTATION_RULE_ONLY

## Purpose

Prevent loss of validated intent, constraints, photographic direction, acceptance criteria, evidence, and execution boundaries when creating a new brief or revising an existing one.

## Mandatory rule

Every brief created for LAB, Symphonie, Codex, Claude, MammothSkills, or any governed project must be committed to its canonical repository before it is treated as current, executable, or reusable.

A new brief must improve the accumulated knowledge. It may not silently replace stronger or more complete information with a shorter, weaker, inferred, or generic formulation.

## Preservation contract

Each new brief must declare:

- `brief_id` and version or revision;
- canonical repository and path;
- parent brief or source package;
- complete `source_refs`;
- facts and constraints preserved verbatim or semantically unchanged;
- additions;
- modifications;
- removals;
- rationale and authority for every removal or weakening;
- unresolved gaps;
- digest or SHA-256 when applicable;
- supersession status;
- execution authority, which remains separate from the brief.

## Prohibited behavior

- Rewriting established information into a less precise summary and presenting it as equivalent.
- Omitting previously defined sections because a later brief is shorter.
- Replacing user-authored wording with model-generated wording when the original carries material intent.
- Treating a derived brief as the only source when stronger parent material exists.
- Inventing missing taxonomies, styles, metrics, evidence, or decisions.
- Deleting or deprecating a briefing without an explicit recorded decision.
- Allowing a new brief to inherit authority from an older authorization.

## Cumulative improvement rule

A successor brief is valid only when:

`SUCCESSOR_CONTENT = PRESERVED_PARENT_CONTENT + APPROVED_ADDITIONS + EXPLICITLY_AUTHORIZED_CHANGES`

If the successor intentionally condenses material, the complete parent remains an active required source. The condensed file must be labeled `EXECUTION_SUMMARY`, not a replacement.

## Mandatory delta report

Every successor brief must include or accompany a delta report with these classes:

- `PRESERVED`
- `ADDED`
- `MODIFIED`
- `REMOVED_WITH_AUTHORITY`
- `OMITTED_IN_ERROR`
- `UNRESOLVED`

Any material item classified `OMITTED_IN_ERROR` blocks execution until restored.

## User-authored source preservation

When Jonathan Martínez provides or restores a briefing in conversation, its exact substantive content must be stored as a canonical source artifact before producing a revised derivative. The derivative must reference the preserved source and must not silently normalize its terminology, structure, or level of detail.

## Photographic and visual briefs

For photographic, art-direction, or visual-impact briefs, the following categories are independently preservable and may not be collapsed into one generic section:

- intention and conversion goal;
- emotional qualities and avoid list;
- photographic role;
- photographic requirements;
- photographic avoid list;
- photographic style taxonomy;
- camera language;
- light and color language;
- scale and drama;
- realism and post-processing;
- crop continuity;
- responsive impact;
- visual hierarchy;
- materiality and depth;
- control finish;
- motion;
- rejection conditions;
- self-critique;
- required outputs and gates.

## Storage rule

- Project-specific briefs belong in the project repository.
- Governance rules and cross-project brief policies belong in LAB.
- Historical briefs remain immutable evidence.
- New revisions use new files or explicit versioned updates with preserved history.

## Validation before publication

Before publication, validate:

1. Parent sources exist.
2. No material section disappeared without authority.
3. All user-authored material is traceable.
4. Delta classification is complete.
5. JSON or Markdown syntax passes.
6. Canonical path is registered or discoverable.
7. Remote publication is verified.

## Authority boundary

This policy requires documentation and preservation. It does not authorize code generation, runtime execution, image generation, product modification, dependency installation, deployment, or release.
