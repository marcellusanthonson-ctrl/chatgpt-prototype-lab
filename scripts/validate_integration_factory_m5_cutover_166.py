#!/usr/bin/env python3
"""Validate authorization 166 Stage 2 final or rolled-back state."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARENT = "4ced6a5f63f833f1526400b70eb531078f1e771a"
BASE = Path("architecture/integrations/migration/M5/cutover-166")
POINTER = Path("architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json")
LOCK = Path("architecture/integrations/active/.integration-factory-cutover-166.lock")
TEMP = Path("architecture/integrations/active/.INTEGRATION_FACTORY_RESOLUTION_POINTER.166.tmp")
STATIC = Path("project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json")
CANDIDATE = Path("architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json")
CORPUS = Path("architecture/integrations/migration/M3/remediation-158/TEST_CORPUS.json")
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
CANDIDATE_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
CORPUS_BLOB = "009065769f524f17f3ffdf137fb0213ee30fb150"
DIGEST = "9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329"


def load(path: Path) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def blob(path: Path) -> str:
    return git("hash-object", "--", path.as_posix())


def validate(expected: str) -> dict[str, Any]:
    failures: list[str] = []
    required = ["CUTOVER_RESULTS.json", "OBSERVATION_RESULTS.json", "POINTER_STATE_TRANSITIONS.json",
                "AUTOMATIC_ROLLBACK_RESULTS.json", "COMMAND_TRANSCRIPT.json", "LOCK_AND_CLEANUP_RESULTS.json",
                "GENERAL_VALIDATOR_DELTA.json", "VALIDATION_RESULTS.json"]
    missing = [name for name in required if not (ROOT / BASE / name).is_file()]
    if missing:
        failures.append("MISSING_REQUIRED_EXECUTION_OUTPUTS")
    if not (ROOT / POINTER).is_file():
        failures.append("POINTER_ABSENT_AFTER_EXECUTION")
    if failures:
        return {"classification": "BLOCK", "failure_codes": failures, "missing": missing}
    cutover, observation, pointer = load(BASE / "CUTOVER_RESULTS.json"), load(BASE / "OBSERVATION_RESULTS.json"), load(POINTER)
    delta, cleanup, rollback = load(BASE / "GENERAL_VALIDATOR_DELTA.json"), load(BASE / "LOCK_AND_CLEANUP_RESULTS.json"), load(BASE / "AUTOMATIC_ROLLBACK_RESULTS.json")
    success = expected == "PASS"
    expected_classification = ("M5_BOUNDED_CUTOVER_PASS_INTEGRATION_ACTIVE_STATIC_FALLBACK_PRESERVED" if success else
                               "M5_BOUNDED_CUTOVER_ROLLED_BACK_STATIC_FALLBACK_ACTIVE_WITH_CLASSIFIED_FAILURES")
    expected_target, expected_state = ("CANDIDATE", "CANDIDATE_ACTIVE_CONFIRMED") if success else ("STATIC", "FAILED_CLOSED_STATIC")
    checks = {
        "CUTOVER_CLASSIFICATION": cutover.get("classification") == expected_classification,
        "VERIFIED_PARENT": cutover.get("verified_parent_head") == PARENT,
        "POINTER_TARGET": pointer.get("active_target") == expected_target,
        "POINTER_STATE": pointer.get("state") == expected_state,
        "POINTER_FALLBACK": pointer.get("fallback_target") == "STATIC",
        "POINTER_PARENT": pointer.get("verified_activation_parent_head") == PARENT,
        "STATIC_BLOB": blob(STATIC) == STATIC_BLOB,
        "CANDIDATE_BLOB": blob(CANDIDATE) == CANDIDATE_BLOB,
        "CORPUS_BLOB": blob(CORPUS) == CORPUS_BLOB,
        "LOCK_ABSENT": not (ROOT / LOCK).exists(),
        "TEMP_ABSENT": not (ROOT / TEMP).exists(),
        "CLEANUP_PASS": cleanup.get("cleanup") == "PASS" and cleanup.get("lock_removed") is True,
        "GENERAL_329": delta.get("finding_count") == 329 and delta.get("exact_ordered_inventory") is True,
        "GENERAL_ZERO_DELTA": delta.get("added") == delta.get("removed") == delta.get("modified") == [],
        "GLOBAL_PASS_FALSE": delta.get("global_repository_pass") is False,
        "ROLLBACK_POLICY": rollback.get("triggered") is (not success),
    }
    state = load(Path("CURRENT_STATE.json"))
    authorization = load(Path("projects/lab/authorizations/AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166.json"))
    registry = load(Path("registry/authorizations.json"))
    integration = load(Path("architecture/integrations/STANDARDIZED_INTEGRATION_FACTORY_001.json"))
    if success:
        checks["CANONICAL_PHASE"] = state.get("current_phase") == expected_classification
        checks["CANONICAL_AUTHORIZATION"] = state.get("authorization_state", {}).get(
            "integration_factory_m5_bounded_cutover_observation_and_automatic_rollback_166"
        ) == "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"
        checks["AUTHORIZATION_CONSUMED"] = authorization.get("status") == "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"
        checks["STAGE_2_CONSUMED"] = authorization.get("stage_2", {}).get("status") == "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"
        checks["NO_ACTIVE_AUTHORIZATIONS"] = registry.get("active_authorizations") == []
        checks["INTEGRATION_ACTIVE"] = integration.get("status") == "M5_INTEGRATED_ACTIVE_VIA_GOVERNED_POINTER"
        checks["SUCCESSOR_PENDING_CREATED"] = (ROOT / "projects/lab/pending/PEND-LAB-042.json").is_file()
        checks["CUTOVER_EVIDENCE_CREATED"] = (ROOT / "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M5-CUTOVER-166.json").is_file()
    iterations = observation.get("iterations", [])
    checks["TWO_ITERATIONS"] = len(iterations) == 2 if success else len(iterations) < 2
    if success:
        checks["MATCHES"] = all(item.get("exact_matches") == 420 for item in iterations)
        checks["ORACLES"] = all(item.get("static_oracles") == item.get("candidate_oracles") == 13 for item in iterations)
        checks["ZERO_DIVERGENCES"] = all(item.get("behavioral_divergences") == 0 for item in iterations)
        checks["EXACT_DIGEST"] = all(item.get("static_digest") == item.get("candidate_digest") == DIGEST for item in iterations)
        checks["DETERMINISTIC"] = observation.get("deterministic") is True
    failures.extend(name for name, passed in checks.items() if not passed)
    return {"classification": "PASS" if not failures else "BLOCK", "expected_outcome": expected,
            "failure_codes": failures, "checks": checks, "pointer_target": pointer.get("active_target")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-outcome", choices=("PASS", "ROLLBACK"), required=True)
    result = validate(parser.parse_args().expected_outcome)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)
