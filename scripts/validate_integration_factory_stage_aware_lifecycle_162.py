#!/usr/bin/env python3
"""Stage-aware authorization lifecycle validator for ATTEMPT-003."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "architecture/integrations/migration/M5/validator-remediation-162"
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
CANDIDATE_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
PARENT_POLICY = "USE_VERIFIED_REMOTE_HEAD_AFTER_AUTHORIZATION_164_PUBLICATION"
DECISION = "decisions/DEC-LAB-028.json"
STATES = ["PRE_GRANT", "GRANTED_NOT_STARTED", "EXECUTING", "CONSUMED_PASS", "CONSUMED_FAIL_CLOSED"]


def common(state: str) -> dict[str, Any]:
    return {
        "lifecycle_state": state,
        "decision_ref": DECISION,
        "approved_by": None if state == "PRE_GRANT" else "Jonathan Martínez",
        "parent_head_policy": PARENT_POLICY,
        "canonical_refs": ["registry/authorizations.json", "CURRENT_STATE.json"],
        "authority_limits": {
            "operational_rollback_drill": False,
            "m5_retry": False,
            "cutover": False,
            "active_pointer": False,
            "runtime": False,
            "integration": False,
        },
        "static_blob": STATIC_BLOB,
        "candidate_blob": CANDIDATE_BLOB,
        "active_pointer_present": False,
        "lock_state": "NONE",
    }


def fixtures() -> list[dict[str, Any]]:
    proposed = common("PRE_GRANT") | {
        "authorization_status": "PROPOSED",
        "active": False, "consumed": False, "reusable": False,
    }
    granted = common("GRANTED_NOT_STARTED") | {
        "authorization_status": "GRANTED", "active": True,
        "consumed": False, "reusable": True,
    }
    executing = common("EXECUTING") | {
        "authorization_status": "EXECUTING", "active": True,
        "consumed": False, "reusable": False, "lock_state": "HELD_UNAMBIGUOUS",
    }
    passed = common("CONSUMED_PASS") | {
        "authorization_status": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
        "active": False, "consumed": True, "reusable": False,
        "result": "PASS", "remote_publication_verified": True,
    }
    failed = common("CONSUMED_FAIL_CLOSED") | {
        "authorization_id": "AUTHORIZATION_LAB_INTEGRATION_FACTORY_M5_BOUNDED_CUTOVER_AND_OBSERVATION_160",
        "authorization_status": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
        "active": False, "consumed": True, "reusable": False,
        "result": "FAIL_CLOSED", "remote_publication_verified": True,
    }
    return [proposed, granted, executing, passed, failed]


def validate_snapshot(item: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    state = item.get("lifecycle_state")
    expected_status = {
        "PRE_GRANT": "PROPOSED",
        "GRANTED_NOT_STARTED": "GRANTED",
        "EXECUTING": "EXECUTING",
        "CONSUMED_PASS": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
        "CONSUMED_FAIL_CLOSED": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
    }.get(state)
    if state not in STATES: failures.append("UNKNOWN_LIFECYCLE_STATE")
    if item.get("decision_ref") != DECISION: failures.append("DECISION_REF_INCORRECT")
    if item.get("authorization_status") != expected_status: failures.append("AUTHORIZATION_STATUS_INCORRECT")
    if item.get("approved_by") != (None if state == "PRE_GRANT" else "Jonathan Martínez"):
        failures.append("APPROVED_BY_INCORRECT")
    if item.get("parent_head_policy") != PARENT_POLICY: failures.append("PARENT_HEAD_POLICY_INCORRECT")
    if item.get("canonical_refs") != ["registry/authorizations.json", "CURRENT_STATE.json"]:
        failures.append("CANONICAL_REFS_INCORRECT")
    limits = item.get("authority_limits", {})
    if set(limits) != {"operational_rollback_drill", "m5_retry", "cutover", "active_pointer", "runtime", "integration"}:
        failures.append("AUTHORITY_LIMITS_INCOMPLETE")
    elif any(limits.values()): failures.append("AUTHORITY_LIMIT_EXCEEDED")
    if item.get("static_blob") != STATIC_BLOB: failures.append("STATIC_BLOB_ALTERED")
    if item.get("candidate_blob") != CANDIDATE_BLOB: failures.append("CANDIDATE_BLOB_ALTERED")
    if item.get("active_pointer_present") is not False: failures.append("UNAUTHORIZED_ACTIVE_POINTER_PRESENT")
    if state == "EXECUTING" and item.get("lock_state") != "HELD_UNAMBIGUOUS":
        failures.append("PARTIAL_STATE_OR_AMBIGUOUS_LOCK")
    if state == "PRE_GRANT" and (item.get("active") or item.get("reusable")):
        failures.append("PROPOSED_AUTHORIZATION_TREATED_AS_GRANTED")
    if state in {"CONSUMED_PASS", "CONSUMED_FAIL_CLOSED"}:
        if not item.get("consumed") or item.get("active") or item.get("reusable"):
            failures.append("CONSUMED_AUTHORIZATION_TREATED_AS_REUSABLE")
        if not item.get("remote_publication_verified"): failures.append("CONSUMPTION_WITHOUT_PUBLICATION")
    if state == "CONSUMED_FAIL_CLOSED" and item.get("result") != "FAIL_CLOSED":
        failures.append("AUTHORIZATION_160_NOT_FAIL_CLOSED")
    return failures


def execute() -> dict[str, Any]:
    results = [{"state": item["lifecycle_state"], "failures": validate_snapshot(item)} for item in fixtures()]
    passed = all(not item["failures"] for item in results)
    return {
        "schema_version": "1.0.0", "validator": "STAGE_AWARE_LIFECYCLE_162",
        "attempt_id": "ATTEMPT-003", "classification": "PASS" if passed else "BLOCK",
        "states_required": STATES, "states_validated": len(results), "results": results,
        "authorization_160_consumed_fail_closed_accepted": not results[-1]["failures"],
        "authorization_160_reusable": False, "active_pointer_created": False,
        "runtime_effect": "NONE", "integration_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = execute()
    if args.write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "LIFECYCLE_VALIDATION_RESULTS.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
