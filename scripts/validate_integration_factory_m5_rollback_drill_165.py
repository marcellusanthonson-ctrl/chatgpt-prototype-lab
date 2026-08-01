#!/usr/bin/env python3
"""Validate authorization-165 rollback evidence, cleanup, scope, and state."""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from execute_integration_factory_m5_rollback_drill_165 import (
    CASES, EXPECTED, EXPECTED_HEAD, POINTER, ROOT, SHADOW, SHADOW_BLOB,
    STATIC, STATIC_BLOB,
)

RESULTS = "architecture/integrations/migration/M5/rollback-drill-165/ROLLBACK_DRILL_RESULTS.json"
VALIDATION = "architecture/integrations/migration/M5/rollback-drill-165/VALIDATION_RESULTS.json"
PORTABLE = "architecture/integrations/migration/M5/canonical-reconciliation-165/GENERAL_VALIDATOR_PORTABLE_BASELINE.json"
DELTA = "registry/deltas/integration-factory-m5-canonical-correction-and-conditional-rollback-drill-165.json"
AUTH = "projects/lab/authorizations/AUTHORIZATION_LAB_M5_CANONICAL_CORRECTION_AND_CONDITIONAL_OPERATIONAL_ROLLBACK_DRILL_165.json"
EVIDENCE = "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M5-ROLLBACK-DRILL-165.json"
ERR9 = "errors/ERR-LAB-009.json"
PEND41 = "projects/lab/pending/PEND-LAB-041.json"
EXPECTED_CHECKPOINT = "07061091d876e97b0299ff025edd9c59c227e966"


def load(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


def blob(relative: str) -> str:
    return git("hash-object", relative).stdout.strip()


def changed_paths() -> list[str]:
    tracked = git("diff", "--name-only", "HEAD").stdout.splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").stdout.splitlines()
    return sorted(set(path.replace("\\", "/") for path in tracked + untracked))


def allowed(path: str, rules: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, rule) for rule in rules)


def general_findings() -> tuple[int, list[str], list[str]]:
    completed = subprocess.run(
        [sys.executable, "-B", "scripts/validate_repository.py"], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    live = [line[6:].replace("\\", "/") for line in completed.stdout.splitlines() if line.startswith("FAIL: ")]
    portable = [item["normalized_message"] for item in load(PORTABLE)["findings"]]
    removed_stage_1 = load(DELTA)["stage_1"]["general_validator"]["removed_findings"]
    stage_1 = [message for message in portable if message not in removed_stage_1]
    added = [message for message in live if message not in stage_1]
    removed = [message for message in stage_1 if message not in live]
    return len(live), added, removed


def validate() -> dict[str, Any]:
    failures: list[str] = []
    result = load(RESULTS)
    matrix = load("architecture/integrations/migration/M5/readiness-161/FAILURE_INJECTION_MATRIX.json")
    auth = load(AUTH)
    state = load("CURRENT_STATE.json")
    registry = load("registry/authorizations.json")
    shadow = load(SHADOW)
    head = git("rev-parse", "HEAD").stdout.strip()
    parent = git("rev-parse", "HEAD^").stdout.strip()
    if not (ROOT / ".git").is_file() or head != EXPECTED_CHECKPOINT or parent != EXPECTED_HEAD:
        failures.append("NOT_EXACT_DISPOSABLE_STAGE_1_WORKTREE")
    cases = result.get("cases", [])
    if [item.get("case") for item in cases] != CASES or [x.get("id") for x in matrix.get("cases", [])] != CASES:
        failures.append("REQUIRED_CASE_ORDER_MISMATCH")
    if any(item.get("expected") != EXPECTED.get(item.get("case")) for item in cases):
        failures.append("EXPECTED_OUTCOME_CONTRACT_MISMATCH")
    if len(cases) != 14 or any(item.get("result") != "PASS" for item in cases):
        failures.append("NOT_14_OF_14_PASS")
    if any(item.get("final_state") != "STATIC_INTACT" for item in cases):
        failures.append("FAILURE_DID_NOT_END_STATIC_INTACT")
    if any(item.get("temporary_cleanup") != "PASS" for item in cases):
        failures.append("CASE_TEMPORARY_CLEANUP_FAILED")
    if result.get("classification") != "M5_OPERATIONAL_ROLLBACK_DRILL_PASS_AWAITING_SEPARATE_M5_RETRY_OR_CUTOVER_DECISION":
        failures.append("DRILL_CLASSIFICATION_MISMATCH")
    double = next((item for item in cases if item.get("case") == "DOUBLE_EXECUTION"), {})
    if double.get("observed") != "CANDIDATE_CONFIRMED+CANDIDATE_CONFIRMED":
        failures.append("DOUBLE_EXECUTION_NONDETERMINISTIC")
    active = ROOT / "architecture/integrations/active"
    temporary = [
        ROOT / POINTER, active / ".INTEGRATION_FACTORY_RESOLUTION_POINTER.json.tmp",
        active / ".integration-factory-candidate-165.tmp", active / ".rollback-drill-165.case.lock",
        active / ".rollback-drill-165.lock",
    ]
    if any(path.exists() for path in temporary):
        failures.append("TEMPORARY_DRILL_ARTIFACT_REMAINS")
    static_blob, shadow_blob = blob(STATIC), blob(SHADOW)
    if static_blob != STATIC_BLOB:
        failures.append("STATIC_SELECTOR_BLOB_ALTERED")
    if shadow_blob != SHADOW_BLOB or shadow.get("status") != "SHADOW_ONLY_NOT_ACTIVE" or shadow.get("automatic_activation") is not False:
        failures.append("SHADOW_REGISTRY_CHANGED_OR_ACTIVE")
    if result.get("pointer_pre_state", {}).get("pointer") != "ABSENT" or result.get("pointer_post_state", {}).get("pointer") != "ABSENT":
        failures.append("CANONICAL_POINTER_PRE_OR_POST_PRESENT")
    for key in ("m5_retry", "cutover", "persistent_active_pointer", "runtime", "integration"):
        if auth.get("authority", {}).get(key) is not False:
            failures.append(f"UNAUTHORIZED_EFFECT:{key}")
    if auth.get("status") != "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION" or auth.get("stage_2", {}).get("status") != "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION":
        failures.append("AUTHORIZATION_165_NOT_FINAL")
    expected_phase = "M5_OPERATIONAL_ROLLBACK_DRILL_PASS_AWAITING_SEPARATE_M5_RETRY_OR_CUTOVER_DECISION"
    if state.get("status") != expected_phase or state.get("current_phase") != expected_phase or state.get("open_errors") != []:
        failures.append("FINAL_CANONICAL_STATE_MISMATCH")
    if load(ERR9).get("status") != "RESOLVED" or load(ERR9).get("resolution") != "STAGE_AWARE_VALIDATORS_CORRECTED_AND_OPERATIONAL_ROLLBACK_DRILL_PASS":
        failures.append("ERR_LAB_009_NOT_RESOLVED")
    if (ROOT / "errors/ERR-LAB-010.json").exists():
        failures.append("ERR_LAB_010_UNEXPECTEDLY_CREATED")
    if load(PEND41).get("status") != "AWAITING_HUMAN_DECISION_FOR_SEPARATE_M5_RETRY_OR_CUTOVER_AUTHORIZATION":
        failures.append("PEND_LAB_041_STATE_MISMATCH")
    if registry.get("active_authorizations") != []:
        failures.append("ACTIVE_AUTHORIZATION_REMAINS")
    records = [x for x in registry.get("records", []) if x.get("id") == auth.get("authorization_id")]
    if len(records) != 1 or records[0].get("status") != "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION":
        failures.append("AUTHORIZATION_165_CONSUMED_RECORD_MISMATCH")
    canonical = subprocess.run([sys.executable, "-B", "scripts/validate_integration_factory_m5_canonical_state_165.py"], cwd=ROOT, text=True, capture_output=True)
    portable = subprocess.run([sys.executable, "-B", "scripts/validate_repository_portable_baseline_165.py"], cwd=ROOT, text=True, capture_output=True)
    if canonical.returncode or "\"canonical_stage\": \"STAGE_2_FINAL\"" not in canonical.stdout:
        failures.append("REAL_CANONICAL_STATE_VALIDATOR_FAILED")
    if portable.returncode:
        failures.append("PORTABLE_BASELINE_VALIDATOR_FAILED")
    live_count, new_findings, removed_findings = general_findings()
    if new_findings:
        failures.append("NEW_OR_CHANGED_STAGE_2_GENERAL_FINDINGS")
    paths = changed_paths(); bad = [path for path in paths if not allowed(path, auth["stage_2_allowed_paths"])]
    if bad:
        failures.append("STAGE_2_UNAUTHORIZED_PATH_CHANGED")
    immutable = [path for path in paths if allowed(path, auth["immutable_paths"])]
    if immutable:
        failures.append("IMMUTABLE_PATH_CHANGED")
    code_lines = {path: len((ROOT / path).read_text(encoding="utf-8").splitlines()) for path in paths if Path(path).suffix in {".py", ".ps1", ".sh", ".js", ".cjs", ".mjs", ".ts", ".tsx"}}
    if any(count > 280 for count in code_lines.values()):
        failures.append("STAGE_2_CODE_LINE_LIMIT_EXCEEDED")
    if not (ROOT / EVIDENCE).is_file():
        failures.append("ROLLBACK_DRILL_EVIDENCE_MISSING")
    return {
        "schema_version": "1.0.0", "validator": "M5_ROLLBACK_DRILL_165",
        "classification": "PASS" if not failures else "BLOCK", "failure_codes": failures,
        "case_count": len(cases), "passed_cases": sum(item.get("result") == "PASS" for item in cases),
        "static_selector_blob": static_blob, "shadow_registry_blob": shadow_blob,
        "pointer_absent_after_validation": not (ROOT / POINTER).exists(),
        "temporary_cleanup": "PASS" if not any(path.exists() for path in temporary) else "FAIL",
        "double_execution_deterministic": double.get("result") == "PASS", "general_validator_global_pass": False,
        "general_validator_live_findings": live_count, "new_or_changed_stage_2_findings": new_findings,
        "stage_2_removed_findings": removed_findings, "changed_paths": paths,
        "unauthorized_changed_paths": bad, "immutable_changed_paths": immutable, "code_line_counts": code_lines,
        "runtime_effect": "NONE", "integration_effect": "NONE", "aws_effect": "NONE", "terraform_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); args = parser.parse_args()
    result = validate(); rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        target = ROOT / VALIDATION; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end=""); raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
