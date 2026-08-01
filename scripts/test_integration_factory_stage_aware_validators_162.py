#!/usr/bin/env python3
"""Positive and negative sandbox tests for authorization 162 ATTEMPT-003."""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import validate_integration_factory_m3_semantic_replay_162 as semantic
import validate_integration_factory_stage_aware_lifecycle_162 as lifecycle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "architecture/integrations/migration/M5/validator-remediation-162"
BASELINE = ROOT / "architecture/integrations/migration/M5/documentary-reconciliation-163/GENERAL_VALIDATOR_SUCCESSOR_BASELINE.json"


def semantic_failures(summary: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if summary.get("case_count") != 420: failures.append("CASE_COUNT_INCORRECT")
    if summary.get("exact_match_count") != 420: failures.append("SEMANTIC_DIVERGENCE")
    if summary.get("static_oracles") != 13 or summary.get("shadow_oracles") != 13:
        failures.append("ORACLE_ALTERED")
    if summary.get("behavioral_digest") != semantic.EXPECTED_DIGEST:
        failures.append("BEHAVIORAL_DIGEST_INCORRECT")
    if summary.get("semantic_divergence_count") != 0: failures.append("SEMANTIC_DIVERGENCE")
    return failures


def general_validator_exact() -> tuple[bool, dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, "-B", "scripts/validate_repository.py"], cwd=ROOT,
        text=True, capture_output=True,
    )
    messages = [
        line.removeprefix("FAIL: ").replace("\\", "/")
        for line in process.stdout.splitlines() if line.startswith("FAIL: ")
    ]
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    expected = [item["normalized_message"] for item in baseline["findings"]]
    exact = process.returncode == 1 and messages == expected
    return exact, {
        "finding_count": len(messages), "exit_code": process.returncode,
        "structured_inventory_digest": baseline["structured_inventory_digest"],
        "raw_ordered_message_digest": baseline["raw_ordered_message_digest"],
        "added_findings": sorted(set(messages) - set(expected)),
        "removed_findings": sorted(set(expected) - set(messages)),
    }


def mutated(value: dict[str, Any], **changes: Any) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result.update(changes)
    return result


def blocked(check: Callable[[], bool]) -> bool:
    try:
        return bool(check())
    except (KeyError, TypeError, ValueError):
        return True


def execute() -> dict[str, Any]:
    replay = semantic.execute()
    lifecycle_result = lifecycle.execute()
    fixtures = {item["lifecycle_state"]: item for item in lifecycle.fixtures()}
    exact_general, general = general_validator_exact()

    old_envelope = {"value": 7, "execution_metadata": {
        "generated_at": "2026-07-31T00:00:00Z", "temporary_directory": "A", "run_id": "1"}}
    new_envelope = {"value": 7, "execution_metadata": {
        "generated_at": "2026-07-31T01:00:00Z", "temporary_directory": "B", "run_id": "2"}}
    volatile_diffs = semantic.compare_documents(old_envelope, new_envelope)
    ordering_diffs = semantic.compare_documents(
        {"items": [{"id": "A"}, {"id": "B"}]}, {"items": [{"id": "B"}, {"id": "A"}]}
    )
    positive = {
        "EXPLICITLY_ALLOWED_VOLATILE_METADATA_DIFFERENCE_ACCEPTED":
            bool(volatile_diffs) and all(item["classification"] == "VOLATILE_METADATA" for item in volatile_diffs),
        "ORDERING_ONLY_DIFFERENCE_NORMALIZED_WITH_STABLE_SEMANTIC_DIGEST":
            ordering_diffs == [{"path": "$.items", "classification": "ORDERING_ONLY"}],
        "CURRENT_AUTHORIZATION_160_CONSUMED_FAIL_CLOSED_STATE_ACCEPTED":
            lifecycle.validate_snapshot(fixtures["CONSUMED_FAIL_CLOSED"]) == [],
        "EXACT_333_SUCCESSOR_GENERAL_VALIDATOR_BASELINE_REPRODUCED_WITH_ONLY_THE_TWO_AUTHORIZED_REMOVALS":
            exact_general,
    }

    one_diverges = mutated(replay, exact_match_count=419, semantic_divergence_count=1)
    oracle_altered = mutated(replay, static_oracles=12)
    digest_wrong = mutated(replay, behavioral_digest="0" * 64)
    proposed_as_granted = mutated(fixtures["PRE_GRANT"], authorization_status="GRANTED", active=True, reusable=True)
    consumed_reused = mutated(fixtures["CONSUMED_PASS"], active=True, reusable=True)
    decision_wrong = mutated(fixtures["GRANTED_NOT_STARTED"], decision_ref="decisions/DEC-LAB-000.json")
    parent_wrong = mutated(fixtures["GRANTED_NOT_STARTED"], parent_head_policy="STALE_PARENT")
    pointer_present = mutated(fixtures["EXECUTING"], active_pointer_present=True)
    partial_lock = mutated(fixtures["EXECUTING"], lock_state="AMBIGUOUS")
    undeclared = semantic.compare_documents(
        {"execution_metadata": {"host": "A"}}, {"execution_metadata": {"host": "B"}}
    )
    static_altered = mutated(fixtures["EXECUTING"], static_blob="0" * 40)
    candidate_altered = mutated(fixtures["EXECUTING"], candidate_blob="0" * 40)
    negative = {
        "ONE_OF_420_CASES_DIVERGES": blocked(lambda: bool(semantic_failures(one_diverges))),
        "ORACLE_ALTERED": blocked(lambda: bool(semantic_failures(oracle_altered))),
        "BEHAVIORAL_DIGEST_INCORRECT": blocked(lambda: bool(semantic_failures(digest_wrong))),
        "STATIC_BLOB_ALTERED": blocked(lambda: "STATIC_BLOB_ALTERED" in lifecycle.validate_snapshot(static_altered)),
        "CANDIDATE_BLOB_ALTERED": blocked(lambda: "CANDIDATE_BLOB_ALTERED" in lifecycle.validate_snapshot(candidate_altered)),
        "PROPOSED_AUTHORIZATION_TREATED_AS_GRANTED": blocked(
            lambda: "PROPOSED_AUTHORIZATION_TREATED_AS_GRANTED" in lifecycle.validate_snapshot(proposed_as_granted)
        ),
        "CONSUMED_AUTHORIZATION_TREATED_AS_REUSABLE": blocked(
            lambda: "CONSUMED_AUTHORIZATION_TREATED_AS_REUSABLE" in lifecycle.validate_snapshot(consumed_reused)
        ),
        "DECISION_REF_INCORRECT": blocked(lambda: "DECISION_REF_INCORRECT" in lifecycle.validate_snapshot(decision_wrong)),
        "PARENT_HEAD_INCORRECT": blocked(lambda: "PARENT_HEAD_POLICY_INCORRECT" in lifecycle.validate_snapshot(parent_wrong)),
        "UNAUTHORIZED_ACTIVE_POINTER_PRESENT": blocked(
            lambda: "UNAUTHORIZED_ACTIVE_POINTER_PRESENT" in lifecycle.validate_snapshot(pointer_present)
        ),
        "UNDECLARED_METADATA_OMITTED": blocked(
            lambda: any(item["classification"] == "SEMANTIC_DIVERGENCE" for item in undeclared)
        ),
        "PARTIAL_STATE_OR_AMBIGUOUS_LOCK": blocked(
            lambda: "PARTIAL_STATE_OR_AMBIGUOUS_LOCK" in lifecycle.validate_snapshot(partial_lock)
        ),
    }
    all_pass = (
        replay["classification"] == "PASS" and lifecycle_result["classification"] == "PASS"
        and all(positive.values()) and all(negative.values()) and exact_general
    )
    return {
        "semantic_replay": replay,
        "lifecycle_validation": lifecycle_result,
        "tests": {
            "positive": positive, "positive_pass_count": sum(positive.values()),
            "negative": negative, "negative_pass_count": sum(negative.values()),
        },
        "general_validator": general,
        "classification": "PASS" if all_pass else "BLOCK",
    }


def write_outputs(result: dict[str, Any]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    documents = {
        "SEMANTIC_REPLAY_RESULTS.json": result["semantic_replay"],
        "LIFECYCLE_VALIDATION_RESULTS.json": result["lifecycle_validation"],
        "NEGATIVE_TEST_RESULTS.json": {
            "schema_version": "1.0.0", "attempt_id": "ATTEMPT-003",
            **result["tests"], "classification": result["classification"],
        },
        "VALIDATION_RESULTS.json": {
            "schema_version": "1.0.0", "attempt_id": "ATTEMPT-003",
            "classification": result["classification"],
            "semantic_replay": result["semantic_replay"]["classification"],
            "lifecycle_validation": result["lifecycle_validation"]["classification"],
            "positive_tests": f"{result['tests']['positive_pass_count']}/4",
            "negative_tests": f"{result['tests']['negative_pass_count']}/12",
            "general_validator": result["general_validator"],
            "operational_rollback_drill_executed": False, "m5_retry_executed": False,
            "cutover_executed": False, "active_pointer_created": False,
            "runtime_effect": "NONE", "integration_effect": "NONE",
        },
    }
    for name, value in documents.items():
        (OUTPUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = execute()
    if args.write: write_outputs(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
