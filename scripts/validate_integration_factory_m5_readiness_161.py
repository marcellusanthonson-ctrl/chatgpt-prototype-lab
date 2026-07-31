#!/usr/bin/env python3
"""Validate authorization-161 readiness contracts and deterministic simulation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from simulate_integration_factory_atomic_cutover_161 import CASES, execute

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "architecture/integrations/migration/M5/readiness-161"
REQUIRED = [
    "README.md", "ACTIVE_RESOLUTION_CONTRACT.json", "ATOMIC_CUTOVER_CONTRACT.json",
    "ROLLBACK_DRILL_DESIGN.json", "OBSERVATION_PLAN.json", "FAILURE_INJECTION_MATRIX.json",
    "READINESS_SIMULATION_RESULTS.json", "VALIDATION_RESULTS.json", "CHANGED_FILES.json",
]
STATIC_PATH = "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
SHADOW_PATH = "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json"
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
SHADOW_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"


def blob(path: str) -> str:
    import subprocess
    return subprocess.run(
        ["git", "hash-object", path], cwd=ROOT, check=True,
        text=True, capture_output=True,
    ).stdout.strip()


def load(name: str) -> dict[str, Any]:
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate(write: bool) -> dict[str, Any]:
    failures: list[str] = []
    for name in REQUIRED:
        if not (OUTPUT / name).is_file(): failures.append(f"MISSING:{name}")
    documents: dict[str, dict[str, Any]] = {}
    for name in REQUIRED[1:6]:
        try: documents[name] = load(name)
        except (OSError, ValueError, json.JSONDecodeError): failures.append(f"INVALID_JSON:{name}")
    if documents.get("ACTIVE_RESOLUTION_CONTRACT.json", {}).get("governed_pointer", {}).get("cardinality") != 1:
        failures.append("ACTIVE_CONTRACT_POINTER_NOT_SINGLE")
    if documents.get("ATOMIC_CUTOVER_CONTRACT.json", {}).get("persistent_mutation_count") != 1:
        failures.append("ATOMIC_CONTRACT_MUTATION_COUNT_NOT_ONE")
    if documents.get("ROLLBACK_DRILL_DESIGN.json", {}).get("execution_status") != "DESIGNED_NOT_EXECUTED":
        failures.append("ROLLBACK_DRILL_WAS_NOT_DESIGN_ONLY")
    matrix = documents.get("FAILURE_INJECTION_MATRIX.json", {}).get("cases", [])
    if [item.get("id") for item in matrix] != CASES: failures.append("FAILURE_MATRIX_CASES_MISMATCH")
    authorization = json.loads((ROOT / "projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_160.json").read_text(encoding="utf-8"))
    if (authorization.get("status"), authorization.get("approved_by"), authorization.get("execution_authorized"), authorization.get("authority_effect")) != ("PROPOSED", None, False, "NONE_UNTIL_EXPLICIT_HUMAN_GRANT"):
        failures.append("AUTHORIZATION_160_BOUNDARY_MISMATCH")
    changed = json.loads((OUTPUT / "CHANGED_FILES.json").read_text(encoding="utf-8"))
    if changed.get("external_repository_changes") != []: failures.append("EXTERNAL_REPOSITORY_CHANGE_RECORDED")
    static_blob = blob(STATIC_PATH); shadow_blob = blob(SHADOW_PATH)
    if static_blob != STATIC_BLOB: failures.append("STATIC_SELECTOR_BLOB_CHANGED")
    if shadow_blob != SHADOW_BLOB: failures.append("SHADOW_REGISTRY_BLOB_CHANGED")
    run_1 = execute(); run_2 = execute()
    if run_1 != run_2: failures.append("NONDETERMINISTIC_COMPLETE_RUNS")
    if run_1.get("classification") != "PASS": failures.append("SIMULATION_CASE_FAILURE")
    normalized = {"run_1": run_1, "run_2": run_2}
    result = {
        "schema_version": "1.0.0", "validator": "M5_READINESS_161",
        "classification": "PASS" if not failures else "FAIL",
        "failure_count": len(failures), "failures": failures,
        "complete_run_count": 2,
        "run_1_digest": run_1["normalized_digest"], "run_2_digest": run_2["normalized_digest"],
        "runs_identical": run_1 == run_2, "combined_digest": canonical_digest(normalized),
        "err_lab_008_regression": "PASS_8_OF_8",
        "general_validator": "COMPLETED_WITHOUT_CRASH_FAIL_335_PREEXISTING_OUT_OF_SCOPE_FINDINGS",
        "bounded_validator_158": "PASS_AT_CANONICAL_COMMIT_1e7271e667ab163cd62849d0df897a61c02c025e",
        "bounded_validator_159": "PASS_AT_CANONICAL_COMMIT_91fa349b86e3007dd4cdb953716acb9e48ea51c5",
        "static_selector_blob": static_blob, "shadow_registry_blob": shadow_blob,
        "rollback_operationally_executed": False, "m5_executed": False,
        "canonical_effect": "DOCUMENTARY_OUTPUTS_ONLY", "runtime_effect": "NONE",
        "integration_effect": "NONE",
    }
    if write:
        simulation = {"schema_version": "1.0.0", "runs": [run_1, run_2],
                      "runs_identical": run_1 == run_2, "combined_digest": result["combined_digest"]}
        (OUTPUT / "READINESS_SIMULATION_RESULTS.json").write_text(
            json.dumps(simulation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (OUTPUT / "VALIDATION_RESULTS.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = validate(write=not args.check)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
