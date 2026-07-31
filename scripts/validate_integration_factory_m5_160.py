#!/usr/bin/env python3
"""Validate the fail-closed M5 execution-160 publication."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "architecture/integrations/migration/M5/execution-160"
POINTER = ROOT / "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json"
REQUIRED = [
    "GENERAL_VALIDATOR_BASELINE.json",
    "ROLLBACK_DRILL_RESULTS.json",
    "CUTOVER_RESULTS.json",
    "OBSERVATION_RESULTS.json",
    "VALIDATION_RESULTS.json",
]


def load(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    for name in REQUIRED:
        if not (PACKAGE / name).is_file():
            failures.append(f"MISSING_{name}")
    if failures:
        raise SystemExit("\n".join(failures))
    baseline = load("GENERAL_VALIDATOR_BASELINE.json")
    drill = load("ROLLBACK_DRILL_RESULTS.json")
    cutover = load("CUTOVER_RESULTS.json")
    observation = load("OBSERVATION_RESULTS.json")
    validation = load("VALIDATION_RESULTS.json")
    if baseline.get("actual_finding_count") != 335 or not baseline.get("exact_inventory_frozen"):
        failures.append("GENERAL_VALIDATOR_BASELINE_NOT_EXACT")
    if drill.get("classification") != "FAIL_CLOSED_BEFORE_POINTER_MUTATION":
        failures.append("DRILL_CLASSIFICATION_MISMATCH")
    if cutover.get("pointer_created") or cutover.get("persistent_mutation_count") != 0:
        failures.append("UNEXPECTED_CUTOVER_MUTATION")
    if observation.get("executed_iterations") != 0:
        failures.append("UNEXPECTED_OBSERVATION")
    if POINTER.exists():
        failures.append("ACTIVE_POINTER_MUST_BE_ABSENT")
    expected = "M5_BOUNDED_CUTOVER_ROLLED_BACK_WITH_CLASSIFIED_FAILURES"
    if validation.get("classification") != expected:
        failures.append("FINAL_CLASSIFICATION_MISMATCH")
    print(json.dumps({"classification": "PASS" if not failures else "FAIL", "failures": failures}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
