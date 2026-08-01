#!/usr/bin/env python3
"""Validate authorization-165 canonical state from repository files and Git blobs."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTH162 = "projects/lab/authorizations/AUTHORIZATION_LAB_M5_STAGE_AWARE_VALIDATOR_REMEDIATION_162.json"
AUTH165 = "projects/lab/authorizations/AUTHORIZATION_LAB_M5_CANONICAL_CORRECTION_AND_CONDITIONAL_OPERATIONAL_ROLLBACK_DRILL_165.json"
BRIEF162 = "projects/lab/briefs/CODEX_M5_STAGE_AWARE_VALIDATOR_REMEDIATION_001.json"
BRIEF165 = "projects/lab/briefs/CODEX_M5_CANONICAL_CORRECTION_AND_CONDITIONAL_ROLLBACK_DRILL_001.json"
REGISTRY = "registry/authorizations.json"
SELECTOR = "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
SHADOW = "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json"
POINTER = "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json"
PORTABLE = "architecture/integrations/migration/M5/canonical-reconciliation-165/GENERAL_VALIDATOR_PORTABLE_BASELINE.json"
SOURCE_BASELINE = "architecture/integrations/migration/M5/documentary-reconciliation-163/GENERAL_VALIDATOR_SUCCESSOR_BASELINE.json"
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
SHADOW_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
APPROVER = "Jonathan Martínez"
CONSUMED162 = "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"
MOJIBAKE = re.compile("[\u00c2\u00c3]|\u00e2[\u0080-\u00bf]")
ABSOLUTE = re.compile(r"(?:[A-Za-z]:[/\\]|(?:^|[/\\])Users[/\\]|(?:^|[/\\])home[/\\]|JF Martin|AppData|temporary_directory)", re.I)


class GateFailure(RuntimeError):
    pass


def fail(code: str) -> None:
    raise GateFailure(code)


def read_json(root: Path, relative: str, overrides: dict[str, Any]) -> Any:
    if relative in overrides:
        return copy.deepcopy(overrides[relative])
    return json.loads((root / relative).read_text(encoding="utf-8"))


def read_bytes(root: Path, relative: str, overrides: dict[str, Any]) -> bytes:
    if relative in overrides and isinstance(overrides[relative], bytes):
        return overrides[relative]
    return (root / relative).read_bytes()


def worktree_blob(root: Path, relative: str, overrides: dict[str, Any]) -> str:
    data = read_bytes(root, relative, overrides).replace(b"\r\n", b"\n")
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def head_blob(root: Path, relative: str, require_git: bool) -> str:
    if not require_git:
        return ""
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"], cwd=root, text=True,
    ).strip()


def string_values(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from string_values(child)


def validate_portable(root: Path, overrides: dict[str, Any]) -> None:
    portable = read_json(root, PORTABLE, overrides)
    source = read_json(root, SOURCE_BASELINE, overrides)
    findings = portable.get("findings", [])
    if len(findings) != 333:
        fail("PORTABLE_BASELINE_FINDING_COUNT_NOT_333")
    if [x.get("stable_id") for x in findings] != [x.get("stable_id") for x in source["findings"]]:
        fail("PORTABLE_BASELINE_STABLE_ID_DRIFT")
    if any(ABSOLUTE.search(value) for value in string_values(portable)):
        fail("PORTABLE_BASELINE_CONTAINS_ABSOLUTE_PATH")
    structured = hashlib.sha256(json.dumps(
        findings, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    raw = hashlib.sha256("\n".join(x["normalized_message"] for x in findings).encode()).hexdigest()
    if portable.get("structured_inventory_digest") != structured or portable.get("raw_ordered_message_digest") != raw:
        fail("PORTABLE_BASELINE_DIGEST_MISMATCH")
    if portable.get("global_repository_pass") is not False:
        fail("UNAUTHORIZED_GLOBAL_REPOSITORY_PASS_CLAIM")


def validate(root: Path = ROOT, overrides: dict[str, Any] | None = None, require_git: bool = True) -> dict[str, Any]:
    values = overrides or {}
    try:
        auth162 = read_json(root, AUTH162, values)
        auth165 = read_json(root, AUTH165, values)
        registry = read_json(root, REGISTRY, values)
        state = read_json(root, "CURRENT_STATE.json", values)
        brief162 = read_json(root, BRIEF162, values)
        brief165 = read_json(root, BRIEF165, values)
        pend39 = read_json(root, "projects/lab/pending/PEND-LAB-039.json", values)
        evidence162 = read_json(root, "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M5-STAGE-AWARE-VALIDATOR-REMEDIATION-162.json", values)
        decision = read_json(root, "decisions/DEC-LAB-028.json", values)
        shadow = read_json(root, SHADOW, values)

        stage1 = auth165["stage_1"].get("status", "")
        stage2 = auth165["stage_2"].get("status", "")
        if "EXECUT" in stage2 and stage1 != "CONSUMED_ON_VERIFIED_STAGE_1_REMOTE_PUBLICATION":
            fail("STAGE_2_STARTED_WITHOUT_VERIFIED_STAGE_1_REMOTE_PUBLICATION")
        if auth162.get("status") != CONSUMED162:
            fail("AUTHORIZATION_162_NOT_CONSUMED")
        amendment = next(x for x in auth162.get("amendments", []) if x.get("amendment_id", "").endswith("ATTEMPT_003_CANONICAL_EXECUTION_AND_CLOSURE"))
        if amendment.get("status") != "CONSUMED_WITH_AUTHORIZATION_162_ON_VERIFIED_REMOTE_PUBLICATION":
            fail("AMENDMENT_3_NOT_CONSUMED")
        if amendment.get("approved_by") != APPROVER:
            fail("MOJIBAKE_IN_APPROVED_BY")
        active162 = [x for x in registry.get("active_authorizations", []) if x.get("id") == auth162["authorization_id"]]
        if active162:
            fail("AUTHORIZATION_162_REMAINS_ACTIVE_AFTER_CONSUMPTION")
        records162 = [x for x in registry.get("records", []) if x.get("id") == auth162["authorization_id"]]
        if len(records162) > 1:
            fail("DUPLICATE_CONSUMED_AUTHORIZATION_162_RECORD")
        if not records162:
            fail("MISSING_CONSUMED_AUTHORIZATION_162_RECORD")
        if records162[0].get("approved_by") != APPROVER:
            fail("MOJIBAKE_IN_APPROVED_BY")
        if state.get("authorization_state", {}).get("integration_factory_m5_stage_aware_validator_remediation_162") != CONSUMED162:
            fail("MISSING_CURRENT_STATE_AUTHORIZATION_TRANSITION")
        if brief162.get("status") == "READY":
            fail("BRIEF_162_STILL_READY")
        if brief162.get("authority", {}).get("authorization_status") == "GRANTED":
            fail("BRIEF_162_STILL_GRANTED")
        if brief162.get("current_execution_id") is not None or brief162.get("scope", {}).get("next_attempt_id") is not None:
            fail("BRIEF_162_NEXT_ATTEMPT_NON_NULL")
        if brief162.get("authorization_reusable") is not False or auth162.get("stage_2", {}).get("next_attempt_id") is not None:
            fail("AUTHORIZATION_162_TREATED_AS_REUSABLE")
        if pend39.get("current_authority") != "NONE_AFTER_AUTHORIZATION_162_CONSUMPTION":
            fail("PEND_LAB_039_RETAINS_ACTIVE_AUTHORITY")
        if evidence162.get("publication_commit") != "4fba07c03faa1c4e5d9419476064c2945f06734f" or evidence162.get("verified_final_remote_head") != "4fba07c03faa1c4e5d9419476064c2945f06734f":
            fail("EVIDENCE_162_PUBLICATION_COMMIT_PLACEHOLDER_REMAINS")
        if decision.get("status") != "APPROVED" or decision.get("approved_by") != APPROVER:
            fail("DEC_LAB_028_NOT_APPROVED")
        if worktree_blob(root, SELECTOR, values) != STATIC_BLOB or (require_git and head_blob(root, SELECTOR, True) != STATIC_BLOB):
            fail("STATIC_SELECTOR_BLOB_ALTERED")
        if worktree_blob(root, SHADOW, values) != SHADOW_BLOB or (require_git and head_blob(root, SHADOW, True) != SHADOW_BLOB):
            fail("SHADOW_REGISTRY_BLOB_ALTERED")
        if shadow.get("status") != "SHADOW_ONLY_NOT_ACTIVE" or shadow.get("automatic_activation") is not False:
            fail("SHADOW_REGISTRY_TREATED_AS_ACTIVE")
        pointer_exists = values.get("__pointer_exists__", (root / POINTER).exists())
        if pointer_exists:
            fail("UNAUTHORIZED_CANONICAL_ACTIVE_POINTER_PRESENT")
        if auth165.get("approved_by") != APPROVER or auth165.get("grant_inferred") is not False:
            fail("AUTHORIZATION_165_APPROVAL_NOT_EXACT")
        for key, code in [("m5_retry", "M5_RETRY_AUTHORIZED"), ("cutover", "CUTOVER_AUTHORIZED"), ("persistent_active_pointer", "PERSISTENT_ACTIVE_POINTER_AUTHORIZED"), ("runtime", "RUNTIME_AUTHORIZED"), ("integration", "INTEGRATION_AUTHORIZED")]:
            if auth165.get("authority", {}).get(key) is not False:
                fail(code)
        validate_portable(root, values)
        scan_paths = [AUTH162, BRIEF162, BRIEF165, "CURRENT_STATE.json", "projects/lab/PROJECT_STATE.json", "projects/lab/pending/PEND-LAB-039.json", "projects/lab/pending/PEND-LAB-040.json"]
        if any(MOJIBAKE.search((root / path).read_text(encoding="utf-8")) for path in scan_paths if path not in values):
            fail("NEW_MOJIBAKE_DETECTED")

        final = auth165.get("status") == "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"
        expected_phase = "M5_OPERATIONAL_ROLLBACK_DRILL_PASS_AWAITING_SEPARATE_M5_RETRY_OR_CUTOVER_DECISION" if final else "M5_CANONICAL_CORRECTION_PASS_ROLLBACK_DRILL_165_AUTHORIZED_AWAITING_STAGE_2"
        expected_auth = "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION" if final else "GRANTED_STAGE_1_CONSUMED_STAGE_2_GRANTED_NOT_STARTED"
        if state.get("status") != expected_phase or state.get("current_phase") != expected_phase or state.get("authorization_state", {}).get("integration_factory_m5_canonical_correction_and_conditional_rollback_drill_165") != expected_auth:
            fail("CURRENT_STATE_TRANSITION_MISMATCH")
        project = read_json(root, "projects/lab/PROJECT_STATE.json", values)
        expected = read_json(root, "tests/expected_repository_state.json", values)
        index = read_json(root, "registry/index.json", values)
        if project.get("current_phase") != state.get("current_phase") or expected.get("current_phase") != state.get("current_phase") or expected.get("open_errors") != state.get("open_errors") or expected.get("registry_counts") != index.get("counts") or expected.get("authorization_state") != state.get("authorization_state"):
            fail("JSON_SCHEMAS_REGISTRIES_AND_STATE_DO_NOT_CORRESPOND")
        if brief165.get("status") != ("CONSUMED" if final else "READY"):
            fail("BRIEF_165_STATE_MISMATCH")
        return {"classification": "PASS", "failure_code": None, "canonical_stage": "STAGE_2_FINAL" if final else "STAGE_1_PUBLISHED_STATE", "portable_finding_count": 333}
    except GateFailure as exc:
        return {"classification": "BLOCK", "failure_code": str(exc)}
    except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {"classification": "BLOCK", "failure_code": "CANONICAL_STRUCTURE_INVALID", "detail": type(exc).__name__}


def main() -> None:
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
