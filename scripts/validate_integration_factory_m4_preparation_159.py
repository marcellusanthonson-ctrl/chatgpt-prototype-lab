#!/usr/bin/env python3
"""Bounded, read-only validator for authorization 159 stage 2."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "928b9829b48cf4e1411b98e608a3a01c52b1b11e"
OPTIONS = [
    "APPROVE_BOUNDED_M5_CUTOVER",
    "DEFER_M5_RETAIN_STATIC_SELECTOR",
    "REJECT_CUTOVER_CLOSE_MIGRATION",
    "RETURN_FOR_REMEDIATION",
]
EXPECTED_BLOBS = {
    "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/ACCEPTANCE_FIXTURES.json": "db53d11e4a45e8f98a9b6aa540a2c7459723601b",
    "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json": "301ba432907758fc49a9b3c86a83fc762eac4607",
    "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json": "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78",
    "architecture/integrations/migration/M2/module-adapters/EVIDENCE_AND_CLAIMS/ADAPTER.json": "13d692e2aa481516f8411cc7092d1865369030d2",
    "architecture/integrations/migration/M2/module-adapters/DESIGN_CRITERION/ADAPTER.json": "eba37a0e3d9207e269585d92f7b858486a44d9d6",
    "architecture/integrations/migration/M2/module-adapters/WEB_ACCESSIBILITY/ADAPTER.json": "7c360c04703196989322bbc177e7b5877f9e4b3b",
    "architecture/integrations/migration/M2/module-adapters/CONTEXTUAL_VISUAL_PREFERENCE/ADAPTER.json": "fbc7ba41184fe928db8c5c70c636e03a2ede2d78",
}
ARCHIVE_ROOT = "projects/lab/continuity/archive/m4-preparation-stage-2-preexecution-" + BASE
CREATED = {
    "architecture/integrations/migration/M4/README.md",
    "architecture/integrations/migration/M4/CUTOVER_DECISION_PACKAGE.json",
    "architecture/integrations/migration/M4/ROLLBACK_READINESS.json",
    "architecture/integrations/migration/M4/VALIDATION_RESULTS.json",
    "architecture/integrations/migration/M4/CHANGED_FILES.json",
    "scripts/validate_integration_factory_m4_preparation_159.py",
    "errors/ERR-LAB-008.json",
    "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M4-PREPARATION-159.json",
    "projects/lab/pending/PEND-LAB-037.json",
    "projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_160.json",
    "projects/lab/briefs/CODEX_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_001.json",
    *(f"{ARCHIVE_ROOT}/{name}" for name in ("CURRENT_CONTINUITY.json", "CURRENT_CONTINUITY.md", "ATTACHMENT_MANIFEST.json", "START_PROMPT.md")),
}
MODIFIED = {
    "projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M4_HUMAN_CUTOVER_DECISION_PREPARATION_AND_DOCUMENTARY_RECONCILIATION_159.json",
    "projects/lab/pending/PEND-LAB-036.json",
    "projects/lab/PENDING.json",
    "registry/index.json",
    "registry/deltas/integration-factory-m4-preparation-authorization-159.json",
    "projects/lab/ROADMAP.json",
    "CURRENT_STATE.md",
    "projects/lab/PROJECT_STATE.md",
    "projects/lab/continuity/CURRENT_CONTINUITY.json",
    "projects/lab/continuity/CURRENT_CONTINUITY.md",
    "projects/lab/continuity/ATTACHMENT_MANIFEST.json",
    "projects/lab/continuity/START_PROMPT.md",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs_no_duplicates)


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True, encoding="utf-8").strip()


def git_blob(path: str) -> str:
    return git("hash-object", "--path", path, path)


def main() -> int:
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts or ".validation" in path.parts:
            continue
        json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs_no_duplicates)

    decision = load("architecture/integrations/migration/M4/CUTOVER_DECISION_PACKAGE.json")
    assert [item["id"] for item in decision["options"]] == OPTIONS
    assert decision["selected_option"] is None
    assert decision["recommendation"] is None
    assert decision["decision_inferred"] is False

    rollback = load("architecture/integrations/migration/M4/ROLLBACK_READINESS.json")
    assert rollback["classification"] == "DOCUMENTARY_AND_SOURCE_ROLLBACK_READY_OPERATIONAL_ROLLBACK_NOT_EXECUTED"
    assert all(rollback["checks"].values())
    assert rollback["m5_requirement"] == "PRE_ACTIVATION_ROLLBACK_DRILL_REQUIRED"
    assert rollback["operational_rollback_executed"] is False
    assert rollback["production_rollback_verified"] is False
    assert rollback["cutover_approved"] is False

    m3 = load("architecture/integrations/migration/M3/remediation-158/VALIDATION_RESULTS.json")
    assert m3["classification"] == "M3_REMEDIATED_PASS_EXACT_DUAL_EQUIVALENCE"
    assert m3["all_gates_pass"] is True and m3["divergence_count"] == 0
    assert m3["behavioral_digest"] == "9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329"
    for path, expected in EXPECTED_BLOBS.items():
        assert git_blob(path) == expected, f"immutable blob drift: {path}"

    error = load("errors/ERR-LAB-008.json")
    assert error["status"] == "OPEN_CONTAINED_NOT_REPAIRED"
    assert error["repair_authorized"] is False and error["repair_performed"] is False

    auth160 = load("projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_160.json")
    assert auth160["status"] == "PROPOSED"
    assert auth160["approved_by"] is None
    assert auth160["authority_effect"] == "NONE_UNTIL_EXPLICIT_HUMAN_GRANT"
    assert auth160["execution_authorized"] is False
    assert auth160["human_decision_ref"] == "PEND-LAB-037"
    assert auth160["must_require_pre_activation_rollback_drill"] is True
    assert auth160["must_preserve_static_selector_until_post_cutover_human_retirement_decision"] is True
    assert auth160["technical_executor"] == "CODEX"
    brief160 = load("projects/lab/briefs/CODEX_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_001.json")
    assert brief160["execution_authorized"] is False
    assert brief160["brief_complete"] is True and brief160["explicit_human_grant_required"] is True
    assert brief160["authority_effect"] == "NONE_UNTIL_EXPLICIT_HUMAN_GRANT"

    assert load("projects/lab/pending/PEND-LAB-036.json")["status"] == "COMPLETED_M4_PREPARATION_PACKAGE_PUBLISHED"
    pend37 = load("projects/lab/pending/PEND-LAB-037.json")
    assert pend37["status"] == "AWAITING_HUMAN_CUTOVER_DECISION"
    assert pend37["selected_option"] is None and pend37["allowed_options"] == OPTIONS

    for path in ("registry/index.json", "CURRENT_STATE.md", "projects/lab/PROJECT_STATE.md", "projects/lab/PENDING.json", "projects/lab/ROADMAP.json"):
        text = (ROOT / path).read_text(encoding="utf-8-sig")
        assert "CHATGPT-CRITERION-LAYER-001@1.1.0" not in text, f"stale live criterion ref: {path}"

    index = load("registry/index.json")
    assert index["counts"]["errors"] == 9
    assert index["counts"]["authorizations"] == 89
    assert index["counts"]["evidence"] == 67
    assert index["latest"]["decision"] == "DEC-LAB-025"
    assert index["latest"]["error"] == "ERR-LAB-008"
    assert index["latest"]["authorization"] == "AUTHORIZATION_LAB_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_160"
    assert index["latest"]["evidence"] == "EVD-LAB-INTEGRATION-FACTORY-M4-PREPARATION-159"
    assert index["latest"]["pending"] == "PEND-LAB-037"
    assert index["latest"]["chatgpt_criterion_layer"] == "CHATGPT-CRITERION-LAYER-001@1.1.1"

    for name in ("CURRENT_CONTINUITY.json", "CURRENT_CONTINUITY.md", "ATTACHMENT_MANIFEST.json", "START_PROMPT.md"):
        original_blob = git("rev-parse", f"{BASE}:projects/lab/continuity/{name}")
        archived_blob = git_blob(f"{ARCHIVE_ROOT}/{name}")
        assert archived_blob == original_blob, f"archive mismatch: {name}"

    changed = set(filter(None, git("diff", "--name-only", BASE, "--").splitlines()))
    untracked = set(filter(None, git("ls-files", "--others", "--exclude-standard").splitlines()))
    actual = {item.replace("\\", "/") for item in changed | untracked}
    expected = CREATED | MODIFIED
    assert actual == expected, f"changed-path mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}"

    manifest = load("architecture/integrations/migration/M4/CHANGED_FILES.json")
    assert set(manifest["created"]) == CREATED
    assert set(manifest["modified"]) == MODIFIED
    assert manifest["outside_authorized_paths"] == []
    assert manifest["immutable_paths_modified"] == []

    auth159 = load("projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M4_HUMAN_CUTOVER_DECISION_PREPARATION_AND_DOCUMENTARY_RECONCILIATION_159.json")
    assert auth159["technical_executor"] == "CODEX"
    assert auth159["status"] == "CONSUMED"
    assert auth159["stage_2_execution_status"] == "COMPLETED_M4_PREPARATION_AWAITING_HUMAN_CUTOVER_DECISION"
    assert auth159["consumption_publication_boundary"] == "CONSUMPTION_EFFECTIVE_WHEN_STAGE_2_RESULT_COMMIT_IS_PUSHED_AND_REMOTE_HEAD_VERIFIED"
    assert auth159["runtime_effect"] == "NONE" and auth159["integration_effect"] == "NONE"

    results = load("architecture/integrations/migration/M4/VALIDATION_RESULTS.json")
    assert results["all_gates_pass"] is True and all(results["gates"].values())
    print("PASS: M4 preparation 159 bounded validation; 27 authorized paths, no cutover or M5 effect")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
