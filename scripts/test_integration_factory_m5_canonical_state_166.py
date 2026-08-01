#!/usr/bin/env python3
"""Positive, negative, and metamorphic tests for the authorization-166 successor."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_integration_factory_m5_canonical_state_166 as validator

ROOT = Path(__file__).resolve().parents[1]
AUTH_STATE_KEY = "integration_factory_m5_bounded_cutover_observation_and_automatic_rollback_166"
AMENDMENT2 = "AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166_AMENDMENT_2_STAGE_AWARE_CANONICAL_STATE_VALIDATOR_SUCCESSOR"
PROFILE_VALUES = {
    "PRE_AMENDMENT_166": (
        "M5_BOUNDED_CUTOVER_166_GRANTED_AWAITING_EXECUTION",
        "GRANTED_STAGE_1_CONSUMED_STAGE_2_GRANTED_NOT_STARTED",
        "EXECUTE_STAGE_2_BOUNDED_M5_CUTOVER_FROM_VERIFIED_STAGE_1_REMOTE_HEAD",
        "GRANTED_NOT_STARTED_AWAITING_VERIFIED_STAGE_1_REMOTE_HEAD",
        "USE_VERIFIED_STAGE_1_REMOTE_MAIN_HEAD", "READY", None, None,
        "scripts/validate_integration_factory_m5_canonical_state_165.py"),
    "STAGE_1_5A_PENDING_REMOTE": (
        "M5_BOUNDED_CUTOVER_166_AMENDMENT_2_STAGE_1_5A_PUBLICATION_PENDING_REMOTE_VERIFICATION",
        "GRANTED_STAGE_1_CONSUMED_STAGE_1_5A_PENDING_REMOTE_VERIFICATION_STAGE_1_5B_GRANTED_NOT_STARTED_STAGE_2_GRANTED_NOT_STARTED",
        "VERIFY_STAGE_1_5A_REMOTE_HEAD_THEN_EXECUTE_STAGE_1_5B_FINALIZATION",
        "GRANTED_NOT_STARTED_AWAITING_VERIFIED_STAGE_1_5B_REMOTE_HEAD",
        "USE_VERIFIED_STAGE_1_5B_REMOTE_MAIN_HEAD", "READY", "STAGE_1_5A_PUBLICATION_PENDING_REMOTE_VERIFICATION",
        "GRANTED_STAGE_1_5A_PUBLICATION_PENDING_REMOTE_VERIFICATION",
        "scripts/validate_integration_factory_m5_canonical_state_165.py"),
    "STAGE_1_5B_FINALIZED": (
        "M5_BOUNDED_CUTOVER_166_STAGE_AWARE_VALIDATOR_SUCCESSOR_PUBLISHED_AWAITING_STAGE_2",
        "GRANTED_STAGE_1_AND_STAGE_1_5_CONSUMED_STAGE_2_GRANTED_NOT_STARTED",
        "EXECUTE_STAGE_2_BOUNDED_M5_CUTOVER_FROM_VERIFIED_STAGE_1_5B_REMOTE_HEAD",
        "GRANTED_NOT_STARTED_AWAITING_VERIFIED_STAGE_1_5B_REMOTE_HEAD",
        "USE_VERIFIED_STAGE_1_5B_REMOTE_MAIN_HEAD", "READY", "READY_FOR_STAGE_2_FROM_VERIFIED_STAGE_1_5B_FINALIZATION_HEAD",
        "CONSUMED_ON_VERIFIED_STAGE_1_5B_REMOTE_PUBLICATION",
        "scripts/validate_integration_factory_m5_canonical_state_166.py"),
}


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fixture(profile: str) -> dict[str, Any]:
    phase, auth_state, next_action, stage2, parent, brief_status, brief_stage, amendment_status, canonical = PROFILE_VALUES[profile]
    state = load("CURRENT_STATE.json")
    project = load("projects/lab/PROJECT_STATE.json")
    expected = load("tests/expected_repository_state.json")
    auth = load(validator.AUTH166)
    registry = load(validator.REGISTRY)
    brief = load(validator.BRIEF166)
    state["status"] = phase
    state["current_phase"] = phase
    state["authorization_state"][AUTH_STATE_KEY] = auth_state
    state["next_authorized_action"] = next_action
    state["canonical_model"]["m5_real_canonical_state_validator"] = canonical
    project["current_phase"] = phase
    expected["current_phase"] = phase
    expected["authorization_state"] = copy.deepcopy(state["authorization_state"])
    expected["open_errors"] = copy.deepcopy(state["open_errors"])
    expected["registry_counts"] = load("registry/index.json")["counts"]
    auth["stage_1"]["status"] = "CONSUMED_ON_VERIFIED_STAGE_1_REMOTE_PUBLICATION"
    auth["stage_2"]["status"] = stage2
    auth["stage_2"]["expected_parent_policy"] = parent
    auth["amendments"] = [item for item in auth.get("amendments", []) if item.get("amendment_id") != AMENDMENT2]
    if amendment_status is not None:
        auth["amendments"].append({
            "amendment_id": AMENDMENT2, "revision": 2, "status": amendment_status,
            "approved_by": "Jonathan Martínez", "grant_inferred": False,
            "stage_1_5a_remote_verified": profile == "STAGE_1_5B_FINALIZED",
        })
    registry["active_authorizations"] = [{
        "id": "AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166",
        "status": auth_state,
    }]
    brief["status"] = brief_status
    if brief_stage is None:
        brief.pop("stage_1_5_status", None)
    else:
        brief["stage_1_5_status"] = brief_stage
    brief["repositories"][0]["stage_2_parent_policy"] = parent
    return {
        "CURRENT_STATE.json": state,
        "projects/lab/PROJECT_STATE.json": project,
        "tests/expected_repository_state.json": expected,
        validator.AUTH166: auth,
        validator.REGISTRY: registry,
        validator.BRIEF166: brief,
    }


def mutate(values: dict[str, Any], path: str, operation: Callable[[Any], None]) -> dict[str, Any]:
    result = copy.deepcopy(values)
    if path not in result:
        result[path] = load(path)
    operation(result[path])
    return result


def expect(profile: str, values: dict[str, Any], code: str, require_git: bool = False) -> dict[str, Any]:
    result = validator.validate(profile, overrides=values, require_git=require_git)
    return {"expected": code, "actual": result.get("failure_code"),
            "pass": result.get("classification") == "BLOCK" and result.get("failure_code") == code}


def execute() -> dict[str, Any]:
    positive = {}
    for profile in PROFILE_VALUES:
        result = validator.validate(profile, overrides=fixture(profile), require_git=False)
        positive[profile] = result.get("classification") == "PASS"

    base = fixture("STAGE_1_5B_FINALIZED")
    negative = {}
    negative["authorization_165_not_consumed"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.AUTH165, lambda value: value.update(status="GRANTED")), "AUTHORIZATION_165_NOT_CONSUMED")
    negative["authorization_166_absent_or_not_unique"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.REGISTRY, lambda value: value.update(active_authorizations=[])), "AUTHORIZATION_166_NOT_SOLE_ACTIVE")
    negative["stage_1_not_consumed"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.AUTH166, lambda value: value["stage_1"].update(status="GRANTED_NOT_STARTED")), "STAGE_1_NOT_CONSUMED")
    negative["stage_2_started_consumed_or_revoked"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.AUTH166, lambda value: value["stage_2"].update(status="EXECUTING")), "STAGE_2_NOT_GRANTED_NOT_STARTED")
    negative["amendment_1_inconsistent"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.AUTH166, lambda value: value["amendments"][0].update(status="REVOKED")), "AMENDMENT_1_INCONSISTENT")
    def break_amendment2(value: dict[str, Any]) -> None:
        next(item for item in value["amendments"] if item.get("amendment_id") == AMENDMENT2)["revision"] = 3
    negative["amendment_2_inconsistent"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.AUTH166, break_amendment2), "AMENDMENT_2_INCONSISTENT")
    bad_validator = (ROOT / validator.VALIDATOR165).read_bytes().replace(b"Validate", b"Invalid!", 1)
    negative["validator_165_blob_altered"] = expect("STAGE_1_5B_FINALIZED", {
        **base, validator.VALIDATOR165: bad_validator}, "HISTORICAL_VALIDATOR_165_BLOB_ALTERED")
    bad_test = (ROOT / validator.TEST165).read_bytes().replace(b"Exact-code", b"Wrong-code", 1)
    negative["test_165_blob_altered"] = expect("STAGE_1_5B_FINALIZED", {
        **base, validator.TEST165: bad_test}, "HISTORICAL_TEST_165_BLOB_ALTERED")
    bad_selector = (ROOT / validator.SELECTOR).read_bytes().replace(b"selector_id", b"selector_ix", 1)
    negative["selector_altered"] = expect("STAGE_1_5B_FINALIZED", {
        **base, validator.SELECTOR: bad_selector}, "STATIC_SELECTOR_BLOB_ALTERED")
    bad_candidate = (ROOT / validator.CANDIDATE).read_bytes().replace(b"SHADOW_ONLY_NOT_ACTIVE", b"SHADOW_ONLY_NOT_ACTIVF", 1)
    negative["candidate_altered"] = expect("STAGE_1_5B_FINALIZED", {
        **base, validator.CANDIDATE: bad_candidate}, "CANDIDATE_BLOB_ALTERED")
    negative["candidate_active"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.CANDIDATE, lambda value: value.update(status="ACTIVE")), "CANDIDATE_ACTIVE")
    negative["pointer_present"] = expect("STAGE_1_5B_FINALIZED", {
        **base, "__pointer_exists__": True}, "POINTER_PRESENT")
    def invalid_portable(value: dict[str, Any]) -> None:
        value["findings"] = value["findings"][:-1]
    negative["baseline_333_invalid"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.PORTABLE, invalid_portable), "PORTABLE_BASELINE_333_INVALID")
    bad_329 = (ROOT / validator.BASELINE329).read_bytes().replace(b'"finding_count": 329', b'"finding_count": 328', 1)
    negative["baseline_329_invalid"] = expect("STAGE_1_5B_FINALIZED", {
        **base, validator.BASELINE329: bad_329}, "PRE_CUTOVER_BASELINE_329_INVALID")
    negative["corpus_invalid"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.CORPUS, lambda value: value.update(corpus_id="WRONG")), "CORPUS_INVALID")
    def invalid_digest(value: dict[str, Any]) -> None:
        value["static_run_digest_1"] = "0" * 64
    negative["behavioral_digest_invalid"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, validator.EQUIVALENCE, invalid_digest), "BEHAVIORAL_DIGEST_INVALID")
    negative["state_project_expected_registry_divergence"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, "projects/lab/PROJECT_STATE.json", lambda value: value.update(current_phase="WRONG")), "CANONICAL_STATE_DIVERGENCE")
    negative["runtime_or_integration_effect"] = expect("STAGE_1_5B_FINALIZED", mutate(
        base, "CURRENT_STATE.json", lambda value: value["authorization_state"].update(runtime_authorized=True)),
        "UNAUTHORIZED_RUNTIME_OR_INTEGRATION_EFFECT")

    metamorphic = {}
    unknown = validator.validate("FUTURE_STATE_166", overrides=base, require_git=False)
    metamorphic["future_unknown_blocks"] = unknown.get("failure_code") == "UNKNOWN_PROFILE"
    old_state = mutate(base, "CURRENT_STATE.json", lambda value: value.update(
        status="M5_OPERATIONAL_ROLLBACK_DRILL_PASS_AWAITING_SEPARATE_M5_RETRY_OR_CUTOVER_DECISION"))
    old_result = validator.validate("STAGE_1_5B_FINALIZED", overrides=old_state, require_git=False)
    metamorphic["state_165_blocks_as_live"] = old_result.get("failure_code") == "AUTHORIZATION_165_STATE_LIVE_UNDER_166"
    metamorphic["historical_165_evidence_readable"] = positive["PRE_AMENDMENT_166"]
    lf = (ROOT / validator.VALIDATOR165).read_bytes().replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    lf_result = validator.validate("STAGE_1_5B_FINALIZED", overrides={**base, validator.VALIDATOR165: lf}, require_git=False)
    crlf_result = validator.validate("STAGE_1_5B_FINALIZED", overrides={**base, validator.VALIDATOR165: crlf}, require_git=False)
    metamorphic["lf_crlf_semantic_equivalence"] = lf_result["classification"] == crlf_result["classification"] == "PASS"
    invalid_state = mutate(base, "CURRENT_STATE.json", lambda value: value.update(current_phase="FUTURE"))
    relaxed = validator.validate("STAGE_1_5B_FINALIZED", overrides=invalid_state, require_git=False)
    metamorphic["require_git_false_does_not_relax_state"] = relaxed.get("failure_code") == "CANONICAL_STATE_DIVERGENCE"
    def unverify(value: dict[str, Any]) -> None:
        next(item for item in value["amendments"] if item.get("amendment_id") == AMENDMENT2)["stage_1_5a_remote_verified"] = False
    unverified = validator.validate("STAGE_1_5B_FINALIZED", overrides=mutate(base, validator.AUTH166, unverify), require_git=False)
    metamorphic["consumption_without_verified_publication_blocks"] = unverified.get("failure_code") == "AMENDMENT_2_CONSUMED_WITHOUT_VERIFIED_PUBLICATION"
    gate_pre = validator.validate_stage_2_gate("PRE_AMENDMENT_166", overrides=fixture("PRE_AMENDMENT_166"), require_git=False)
    gate_pending = validator.validate_stage_2_gate("STAGE_1_5A_PENDING_REMOTE", overrides=fixture("STAGE_1_5A_PENDING_REMOTE"), require_git=False)
    gate_final = validator.validate_stage_2_gate("STAGE_1_5B_FINALIZED", overrides=base, require_git=False)
    metamorphic["stage_2_gate_only_finalized"] = (
        gate_pre.get("failure_code") == "STAGE_2_GATE_PROFILE_NOT_FINALIZED"
        and gate_pending.get("failure_code") == "STAGE_2_GATE_PROFILE_NOT_FINALIZED"
        and gate_final.get("classification") == "PASS")
    negative_pass = sum(item["pass"] for item in negative.values())
    all_pass = all(positive.values()) and negative_pass == len(negative) and all(metamorphic.values())
    return {"classification": "PASS" if all_pass else "BLOCK", "positive": positive,
            "negative": negative, "negative_passed": negative_pass, "negative_required": len(negative),
            "metamorphic": metamorphic, "metamorphic_passed": sum(metamorphic.values()),
            "metamorphic_required": len(metamorphic)}


def main() -> None:
    result = execute()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
