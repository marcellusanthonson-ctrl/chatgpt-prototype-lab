# A1 Canary Recovery / Break-Glass Runbook

Document-Role: DOCUMENTARY_NON_ACTIVATING_RUNBOOK
Contract: `A1_CANARY_RECOVERY_BREAK_GLASS_DESIGN_001`
Authorization-For-This-Document: `AUTHORIZATION_LAB_A1_RECOVERY_BREAK_GLASS_DESIGN_MATERIALIZATION_214`
Authority-Effect: NONE_BY_ITSELF
Default-State: `DISABLED_NO_STANDING_BYPASS_NO_RESIDUAL_AUTHORITY`

## 1. Purpose

This runbook defines how a future, separately authorized incident-bound recovery could restore the A1 canary governance control plane to its known-good baseline. It does **not** authorize activation, simulation, ruleset mutation, bypass creation, workflow mutation, main-branch changes, or an A1 PASS.

The normal and terminal state is always:

- ruleset `20573868` enforcement `active`;
- one approving review required;
- `LAB Publication Gate` required;
- `LAB Canonical Authority Gate v2` required;
- `bypass_actors: []`;
- `current_user_can_bypass: never`;
- no standing recovery principal;
- no residual recovery authority.

## 2. Activation gate

A recovery procedure may begin only under a **new explicit textual authorization** from Jonathan Martínez created after the incident is observed. Every condition below is mandatory:

1. `VERIFY_LIVE_AT_USE` resolves current `main` and current canary ruleset state.
2. A material canary control-plane divergence or lockout is observed remotely.
3. Ordinary protected PR recovery is demonstrated unavailable or insufficient for the specific incident.
4. The new authorization identifies the incident, operator principal, recovery mode, exact allowed actions, forbidden actions, expiration, restoration target and readback method.
5. The authorization is still current, active and scope-compatible immediately before any mutation.
6. The recovery remains limited to `marcellusanthonson-ctrl/chatgpt-prototype-lab`, branch `lab-governance-canary-210`, ruleset `20573868`.

Convenience, failed checks, missing approval, a desire to merge a blocked PR, or a desire to declare A1 PASS are never valid activation triggers.

## 3. Human authority and separation

Jonathan Martínez remains the sole normative and executive approver. The future recovery authorization must name the operator explicitly.

Approval of emergency recovery does not waive protected-publication review requirements. The author of an affected pull request cannot approve that same pull request. If the required execution/review separation cannot be satisfied, recovery stops fail-closed.

A read-only independent sensor, preferably `LAB Governance Reader`, must verify restoration after the operator finishes. The sensor can observe; it cannot create authority or perform recovery mutations.

## 4. Time and action bounds

A future activation is:

- single-use;
- maximum 15 minutes from activation unless the future authorization specifies a shorter window;
- non-renewable without a new explicit authorization;
- automatically expired at the end of its authorized window if not already consumed;
- limited to canary control-plane recovery only.

No standing break-glass authority exists before or after that window.

## 5. Recovery modes

### R1 — Exact control-plane restore, no bypass

This is mandatory first choice.

Use the minimum administrative mutation necessary to restore ruleset `20573868` to the known-good baseline without creating a bypass actor. No unrelated ruleset field may change.

R1 ends only when direct and independent readbacks both match the known-good baseline.

### R2 — Temporary single-principal bypass, last resort

R2 is forbidden unless all of the following are true:

1. R1 has been attempted or shown technically unavailable and that fact is evidenced.
2. The future authorization explicitly names R2.
3. Exactly one recovery principal is named.
4. The temporary bypass is canary-only and exists only inside the authorized window.
5. The bypass is removed before closeout.

R2 is never a standing repository capability. If GitHub cannot express or remove the temporary bypass safely and deterministically, stop without activation.

## 6. Allowed emergency actions

A future incident authorization may select only the actions it explicitly needs from this bounded set:

- read current canary branch and ruleset state;
- compare current state with the verified known-good baseline;
- restore only ruleset `20573868` fields necessary to match that baseline;
- under explicitly authorized R2 only, add one named temporary recovery bypass principal;
- remove the temporary bypass before closeout;
- perform direct readback;
- trigger or use an already-authorized independent read-only readback mechanism;
- record evidence and close the single-use authorization.

Any action not explicitly named in the future authorization is denied.

## 7. Forbidden actions

Recovery may never be used to:

- modify `main` branch protection, main rulesets or main publication workflows;
- make a failed governance test or failed PR mergeable by policy exception;
- leave either required A1 gate removed;
- leave approving-review count below one;
- leave any bypass actor configured;
- create standing emergency authority;
- create or rotate credentials unless a different explicit authorization governs that distinct action;
- change product, runtime, integration or external repositories;
- bypass authorization semantics;
- reuse a consumed, expired or revoked recovery authorization;
- declare A1 PASS merely because recovery succeeded.

## 8. Known-good restoration target

Before any future mutation, resolve and evidence the canonical/live target. The current design baseline is:

| Field | Required terminal value |
| --- | --- |
| Ruleset | `20573868` |
| Enforcement | `active` |
| Required approvals | `1` |
| Required check 1 | `LAB Publication Gate` |
| Required check 2 | `LAB Canonical Authority Gate v2` |
| Strict required checks | `true` |
| Bypass actors | `[]` |
| Current user can bypass | `never` |
| Non-fast-forward rule | present |
| Deletion rule | present |

A future recovery authorization must reverify this target in live GitHub state. This table is not permission to restore an outdated baseline.

## 9. Mandatory restoration sequence

A future authorized operator follows this exact sequence:

1. Stop all unrelated mutations.
2. Verify live `main`, live canary branch and ruleset state.
3. Verify the future authorization is active, incident-bound, unexpired and scope-compatible.
4. Verify ordinary protected recovery is unavailable or insufficient.
5. Resolve the known-good target from canonical evidence plus live readback.
6. Select R1 unless the future authorization explicitly permits R2 and contains R1-unavailability evidence.
7. Apply only the minimum authorized canary control-plane mutation.
8. If R2 was used, remove the temporary bypass principal immediately after the restorative mutation.
9. Restore ruleset enforcement to `active`.
10. Restore required approvals to `1`.
11. Restore both required checks.
12. Confirm `bypass_actors: []` and `current_user_can_bypass: never`.
13. Perform direct GitHub readback.
14. Perform independent read-only readback.
15. Verify `main` was not changed by the recovery.
16. If any comparison differs, stop as `BLOCKED_RECOVERY_NOT_CLOSED`.
17. Canonically record the evidence and consume or expire the future authorization with residual authority `NONE`.

## 10. Evidence required

### Before activation

- current live `main` HEAD;
- current live canary ruleset readback;
- incident description;
- evidence that ordinary recovery is unavailable or insufficient;
- exact future human authorization source;
- named operator and permitted mode.

### During recovery

- timestamped action log;
- exact ruleset fields changed;
- operator identity;
- recovery mode;
- no secret values.

### After restoration

- direct ruleset readback;
- independent read-only readback;
- approving review count = `1`;
- both required status checks present;
- enforcement = `active`;
- bypass actors = `[]`;
- `current_user_can_bypass = never`;
- `main` unchanged by recovery;
- future authorization terminal state and residual authority `NONE`.

No success claim is valid until the required evidence is canonically recorded.

## 11. Closeout outcomes

`RECOVERY_PASS_CANARY_BASELINE_RESTORED_NO_RESIDUAL_AUTHORITY` requires every terminal condition above.

`BLOCKED_RECOVERY_NOT_CLOSED` applies if restoration or either readback is incomplete or mismatched. A blocked recovery does not create more authority; it returns control to Jonathan Martínez for a new decision or authorization.

A successful recovery is not itself `A1_OPERATIONAL_PASS`. Any A1 conclusion remains governed by the active A1 authorization and its complete test matrix.

## 12. Fail-closed rules

Stop without mutation if any of these is true:

- live baseline cannot be verified;
- incident scope is ambiguous;
- ordinary recovery unavailability is not established;
- the future explicit activation authorization is absent, stale, consumed, revoked, expired or scope-mismatched;
- a proposed recovery would touch `main` or an external repository;
- R2 is proposed without R1-unavailability evidence;
- independent readback is unavailable;
- the post-restoration state does not match the baseline.

This runbook has no authority effect by itself.
