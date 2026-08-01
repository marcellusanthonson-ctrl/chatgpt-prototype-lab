#!/usr/bin/env python3
"""Validate the three explicitly governed authorization-166 canonical profiles."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTH165 = "projects/lab/authorizations/AUTHORIZATION_LAB_M5_CANONICAL_CORRECTION_AND_CONDITIONAL_OPERATIONAL_ROLLBACK_DRILL_165.json"
AUTH166 = "projects/lab/authorizations/AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166.json"
BRIEF166 = "projects/lab/briefs/CODEX_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_001.json"
REGISTRY = "registry/authorizations.json"
SELECTOR = "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
CANDIDATE = "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json"
POINTER = "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json"
VALIDATOR165 = "scripts/validate_integration_factory_m5_canonical_state_165.py"
TEST165 = "scripts/test_integration_factory_m5_canonical_state_165.py"
PORTABLE = "architecture/integrations/migration/M5/canonical-reconciliation-165/GENERAL_VALIDATOR_PORTABLE_BASELINE.json"
SOURCE333 = "architecture/integrations/migration/M5/documentary-reconciliation-163/GENERAL_VALIDATOR_SUCCESSOR_BASELINE.json"
BASELINE329 = "architecture/integrations/migration/M5/cutover-166/PRE_CUTOVER_GENERAL_VALIDATOR_BASELINE.json"
CORPUS = "architecture/integrations/migration/M3/remediation-158/TEST_CORPUS.json"
EQUIVALENCE = "architecture/integrations/migration/M3/remediation-158/EQUIVALENCE_RESULTS.json"
AMENDMENT1 = "AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166_AMENDMENT_1_CANONICAL_M3_CORPUS_REFERENCE_CORRECTION"
AMENDMENT2 = "AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166_AMENDMENT_2_STAGE_AWARE_CANONICAL_STATE_VALIDATOR_SUCCESSOR"
AUTH166_ID = "AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166"
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
CANDIDATE_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
VALIDATOR165_BLOB = "7a2eb2d87ef0db8220d2ac8090b460684acc342d"
TEST165_BLOB = "4cb2ef2f6f525b6dbd9c2a929ff4fbcf0386aaa0"
BASELINE329_BLOB = "af6dfd23d615699b3aa7406d1af1847d406554ef"
CORPUS_BLOB = "009065769f524f17f3ffdf137fb0213ee30fb150"
DIGEST = "9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329"
PROFILES = {
    "PRE_AMENDMENT_166": {
        "phase": "M5_BOUNDED_CUTOVER_166_GRANTED_AWAITING_EXECUTION",
        "auth_state": "GRANTED_STAGE_1_CONSUMED_STAGE_2_GRANTED_NOT_STARTED",
        "amendment2": None,
        "next": "EXECUTE_STAGE_2_BOUNDED_M5_CUTOVER_FROM_VERIFIED_STAGE_1_REMOTE_HEAD",
        "stage2": "GRANTED_NOT_STARTED_AWAITING_VERIFIED_STAGE_1_REMOTE_HEAD",
        "parent": "USE_VERIFIED_STAGE_1_REMOTE_MAIN_HEAD",
        "brief": "READY",
        "brief_stage": None,
        "validator": VALIDATOR165,
    },
    "STAGE_1_5A_PENDING_REMOTE": {
        "phase": "M5_BOUNDED_CUTOVER_166_AMENDMENT_2_STAGE_1_5A_PUBLICATION_PENDING_REMOTE_VERIFICATION",
        "auth_state": "GRANTED_STAGE_1_CONSUMED_STAGE_1_5A_PENDING_REMOTE_VERIFICATION_STAGE_1_5B_GRANTED_NOT_STARTED_STAGE_2_GRANTED_NOT_STARTED",
        "amendment2": "GRANTED_STAGE_1_5A_PUBLICATION_PENDING_REMOTE_VERIFICATION",
        "next": "VERIFY_STAGE_1_5A_REMOTE_HEAD_THEN_EXECUTE_STAGE_1_5B_FINALIZATION",
        "stage2": "GRANTED_NOT_STARTED_AWAITING_VERIFIED_STAGE_1_5B_REMOTE_HEAD",
        "parent": "USE_VERIFIED_STAGE_1_5B_REMOTE_MAIN_HEAD",
        "brief": "READY",
        "brief_stage": "STAGE_1_5A_PUBLICATION_PENDING_REMOTE_VERIFICATION",
        "validator": VALIDATOR165,
    },
    "STAGE_1_5B_FINALIZED": {
        "phase": "M5_BOUNDED_CUTOVER_166_STAGE_AWARE_VALIDATOR_SUCCESSOR_PUBLISHED_AWAITING_STAGE_2",
        "auth_state": "GRANTED_STAGE_1_AND_STAGE_1_5_CONSUMED_STAGE_2_GRANTED_NOT_STARTED",
        "amendment2": "CONSUMED_ON_VERIFIED_STAGE_1_5B_REMOTE_PUBLICATION",
        "next": "EXECUTE_STAGE_2_BOUNDED_M5_CUTOVER_FROM_VERIFIED_STAGE_1_5B_REMOTE_HEAD",
        "stage2": "GRANTED_NOT_STARTED_AWAITING_VERIFIED_STAGE_1_5B_REMOTE_HEAD",
        "parent": "USE_VERIFIED_STAGE_1_5B_REMOTE_MAIN_HEAD",
        "brief": "READY",
        "brief_stage": "READY_FOR_STAGE_2_FROM_VERIFIED_STAGE_1_5B_FINALIZATION_HEAD",
        "validator": "scripts/validate_integration_factory_m5_canonical_state_166.py",
    },
}


class GateFailure(RuntimeError):
    pass


def fail(code: str) -> None:
    raise GateFailure(code)


def read_json(root: Path, path: str, values: dict[str, Any]) -> Any:
    if path in values and not isinstance(values[path], bytes):
        return copy.deepcopy(values[path])
    return json.loads((root / path).read_text(encoding="utf-8"))


def read_bytes(root: Path, path: str, values: dict[str, Any]) -> bytes:
    value = values.get(path)
    return value if isinstance(value, bytes) else (root / path).read_bytes()


def normalized_blob(root: Path, path: str, values: dict[str, Any]) -> str:
    data = read_bytes(root, path, values).replace(b"\r\n", b"\n")
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def head_blob(root: Path, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=root, text=True).strip()


def require_blob(root: Path, path: str, expected: str, code: str,
                 values: dict[str, Any], require_git: bool) -> None:
    if normalized_blob(root, path, values) != expected:
        fail(code)
    if require_git and head_blob(root, path) != expected:
        fail(code)


def amendment(auth: dict[str, Any], amendment_id: str) -> dict[str, Any] | None:
    return next((item for item in auth.get("amendments", []) if item.get("amendment_id") == amendment_id), None)


def validate_baselines(root: Path, values: dict[str, Any], require_git: bool) -> None:
    require_blob(root, BASELINE329, BASELINE329_BLOB, "PRE_CUTOVER_BASELINE_329_INVALID", values, require_git)
    portable = read_json(root, PORTABLE, values)
    source = read_json(root, SOURCE333, values)
    findings = portable.get("findings", [])
    stable_ids = [item.get("stable_id") for item in findings]
    source_ids = [item.get("stable_id") for item in source.get("findings", [])]
    structured = hashlib.sha256(json.dumps(findings, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    raw = hashlib.sha256("\n".join(item.get("normalized_message", "") for item in findings).encode()).hexdigest()
    if len(findings) != 333 or stable_ids != source_ids:
        fail("PORTABLE_BASELINE_333_INVALID")
    if portable.get("structured_inventory_digest") != structured or portable.get("raw_ordered_message_digest") != raw:
        fail("PORTABLE_BASELINE_333_INVALID")
    if portable.get("global_repository_pass") is not False:
        fail("PORTABLE_BASELINE_333_INVALID")
    baseline = read_json(root, BASELINE329, values)
    if baseline.get("finding_count") != 329 or len(baseline.get("findings", [])) != 329:
        fail("PRE_CUTOVER_BASELINE_329_INVALID")
    if baseline.get("structured_inventory_digest") != "7014f40da42487c7de502c6e209e10b751b8f1718e4c148663c2511ba2bc705b":
        fail("PRE_CUTOVER_BASELINE_329_INVALID")
    if baseline.get("raw_ordered_message_digest") != "3b724dbb28e9922e1e658bb07d9c5cdbbbe33167553e62398b43c88056af258d":
        fail("PRE_CUTOVER_BASELINE_329_INVALID")


def validate_corpus(root: Path, values: dict[str, Any], require_git: bool) -> None:
    require_blob(root, CORPUS, CORPUS_BLOB, "CORPUS_INVALID", values, require_git)
    corpus = read_json(root, CORPUS, values)
    if corpus.get("corpus_id") != "INTEGRATION_FACTORY_M3_REMEDIATION_158_CORPUS_001":
        fail("CORPUS_INVALID")
    if len(corpus.get("cases", [])) != 420:
        fail("CORPUS_INVALID")
    evidence = read_json(root, EQUIVALENCE, values)
    digest_fields = ("static_run_digest_1", "static_run_digest_2", "shadow_run_digest_1", "shadow_run_digest_2")
    if any(evidence.get(key) != DIGEST for key in digest_fields):
        fail("BEHAVIORAL_DIGEST_INVALID")
    if evidence.get("exact_match_count") != 420 or evidence.get("behavioral_divergence_count") != 0:
        fail("BEHAVIORAL_DIGEST_INVALID")


def validate(profile: str, root: Path = ROOT, overrides: dict[str, Any] | None = None,
             require_git: bool = True) -> dict[str, Any]:
    values = overrides or {}
    try:
        if profile not in PROFILES:
            fail("UNKNOWN_PROFILE")
        spec = PROFILES[profile]
        auth165 = read_json(root, AUTH165, values)
        auth166 = read_json(root, AUTH166, values)
        registry = read_json(root, REGISTRY, values)
        state = read_json(root, "CURRENT_STATE.json", values)
        project = read_json(root, "projects/lab/PROJECT_STATE.json", values)
        expected = read_json(root, "tests/expected_repository_state.json", values)
        index = read_json(root, "registry/index.json", values)
        brief = read_json(root, BRIEF166, values)
        candidate = read_json(root, CANDIDATE, values)
        if state.get("status") == "M5_OPERATIONAL_ROLLBACK_DRILL_PASS_AWAITING_SEPARATE_M5_RETRY_OR_CUTOVER_DECISION":
            fail("AUTHORIZATION_165_STATE_LIVE_UNDER_166")
        if auth165.get("status") != "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION":
            fail("AUTHORIZATION_165_NOT_CONSUMED")
        active = registry.get("active_authorizations", [])
        if len(active) != 1 or active[0].get("id") != AUTH166_ID:
            fail("AUTHORIZATION_166_NOT_SOLE_ACTIVE")
        if auth166.get("stage_1", {}).get("status") != "CONSUMED_ON_VERIFIED_STAGE_1_REMOTE_PUBLICATION":
            fail("STAGE_1_NOT_CONSUMED")
        if auth166.get("stage_2", {}).get("status") != spec["stage2"]:
            fail("STAGE_2_NOT_GRANTED_NOT_STARTED")
        first = amendment(auth166, AMENDMENT1)
        if not first or first.get("status") != "GRANTED_NOT_CONSUMED_WITH_PARENT_AUTHORIZATION_166":
            fail("AMENDMENT_1_INCONSISTENT")
        second = amendment(auth166, AMENDMENT2)
        if spec["amendment2"] is None and second is not None:
            fail("AMENDMENT_2_INCONSISTENT")
        if spec["amendment2"] is not None:
            exact = second and second.get("revision") == 2 and second.get("status") == spec["amendment2"]
            approval = second and second.get("approved_by") == "Jonathan Martínez" and second.get("grant_inferred") is False
            if not exact or not approval:
                fail("AMENDMENT_2_INCONSISTENT")
        if profile == "STAGE_1_5B_FINALIZED" and not second.get("stage_1_5a_remote_verified"):
            fail("AMENDMENT_2_CONSUMED_WITHOUT_VERIFIED_PUBLICATION")
        require_blob(root, VALIDATOR165, VALIDATOR165_BLOB, "HISTORICAL_VALIDATOR_165_BLOB_ALTERED", values, require_git)
        require_blob(root, TEST165, TEST165_BLOB, "HISTORICAL_TEST_165_BLOB_ALTERED", values, require_git)
        require_blob(root, SELECTOR, STATIC_BLOB, "STATIC_SELECTOR_BLOB_ALTERED", values, require_git)
        require_blob(root, CANDIDATE, CANDIDATE_BLOB, "CANDIDATE_BLOB_ALTERED", values, require_git)
        if candidate.get("status") != "SHADOW_ONLY_NOT_ACTIVE" or candidate.get("automatic_activation") is not False:
            fail("CANDIDATE_ACTIVE")
        if values.get("__pointer_exists__", (root / POINTER).exists()):
            fail("POINTER_PRESENT")
        validate_baselines(root, values, require_git)
        validate_corpus(root, values, require_git)
        if state.get("authorization_state", {}).get("runtime_authorized") is not False:
            fail("UNAUTHORIZED_RUNTIME_OR_INTEGRATION_EFFECT")
        if state.get("authorization_state", {}).get("integration_authorized") is not False:
            fail("UNAUTHORIZED_RUNTIME_OR_INTEGRATION_EFFECT")
        auth_state = state.get("authorization_state", {}).get("integration_factory_m5_bounded_cutover_observation_and_automatic_rollback_166")
        phase_ok = state.get("status") == spec["phase"] and state.get("current_phase") == spec["phase"]
        if not phase_ok or auth_state != spec["auth_state"] or state.get("next_authorized_action") != spec["next"]:
            fail("CANONICAL_STATE_DIVERGENCE")
        if project.get("current_phase") != spec["phase"] or expected.get("current_phase") != spec["phase"]:
            fail("CANONICAL_STATE_DIVERGENCE")
        if expected.get("authorization_state") != state.get("authorization_state"):
            fail("CANONICAL_STATE_DIVERGENCE")
        if expected.get("open_errors") != state.get("open_errors") or expected.get("registry_counts") != index.get("counts"):
            fail("CANONICAL_STATE_DIVERGENCE")
        if auth166.get("stage_2", {}).get("expected_parent_policy") != spec["parent"]:
            fail("CANONICAL_STATE_DIVERGENCE")
        if brief.get("status") != spec["brief"] or brief.get("repositories", [{}])[0].get("stage_2_parent_policy") != spec["parent"]:
            fail("CANONICAL_STATE_DIVERGENCE")
        if spec["brief_stage"] is not None and brief.get("stage_1_5_status") != spec["brief_stage"]:
            fail("CANONICAL_STATE_DIVERGENCE")
        if state.get("canonical_model", {}).get("m5_real_canonical_state_validator") != spec["validator"]:
            fail("CANONICAL_STATE_DIVERGENCE")
        drill = read_json(root, "architecture/integrations/migration/M5/rollback-drill-165/ROLLBACK_DRILL_RESULTS.json", values)
        if len(drill.get("cases", [])) != 14:
            fail("HISTORICAL_EVIDENCE_165_UNREADABLE")
        return {"classification": "PASS", "failure_code": None, "profile": profile,
                "portable_finding_count": 333, "pre_cutover_finding_count": 329}
    except GateFailure as exc:
        return {"classification": "BLOCK", "failure_code": str(exc), "profile": profile}
    except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        return {"classification": "BLOCK", "failure_code": "CANONICAL_STRUCTURE_INVALID",
                "profile": profile, "detail": type(exc).__name__}


def validate_stage_2_gate(profile: str, **kwargs: Any) -> dict[str, Any]:
    if profile != "STAGE_1_5B_FINALIZED":
        return {"classification": "BLOCK", "failure_code": "STAGE_2_GATE_PROFILE_NOT_FINALIZED", "profile": profile}
    return validate(profile, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=tuple(PROFILES))
    args = parser.parse_args()
    result = validate(args.profile)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
