#!/usr/bin/env python3
"""Exact-code negative tests for the authorization-165 canonical validator."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_integration_factory_m5_canonical_state_165 as validator

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def changed(relative: str, mutate: Callable[[Any], None]) -> dict[str, Any]:
    value = load(relative)
    mutate(value)
    return {relative: value}


def expect(case: str, overrides: dict[str, Any], code: str) -> dict[str, Any]:
    result = validator.validate(overrides=overrides)
    actual = result.get("failure_code")
    return {
        "case": case,
        "expected_failure_code": code,
        "actual_failure_code": actual,
        "pass": result.get("classification") == "BLOCK" and actual == code,
    }


def execute() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def mojibake(value: dict[str, Any]) -> None:
        value["amendments"][1]["approved_by"] = "Jonathan Mart\u00c3\u00adnez"
    cases.append(expect("MOJIBAKE_IN_APPROVED_BY", changed(validator.AUTH162, mojibake), "MOJIBAKE_IN_APPROVED_BY"))

    def active162(value: dict[str, Any]) -> None:
        value["active_authorizations"].append({"id": "AUTHORIZATION_LAB_M5_STAGE_AWARE_VALIDATOR_REMEDIATION_162"})
    cases.append(expect("AUTHORIZATION_162_REMAINS_ACTIVE_AFTER_CONSUMPTION", changed(validator.REGISTRY, active162), "AUTHORIZATION_162_REMAINS_ACTIVE_AFTER_CONSUMPTION"))

    def duplicate162(value: dict[str, Any]) -> None:
        record = next(x for x in value["records"] if x["id"] == "AUTHORIZATION_LAB_M5_STAGE_AWARE_VALIDATOR_REMEDIATION_162")
        value["records"].append(copy.deepcopy(record))
    cases.append(expect("DUPLICATE_CONSUMED_AUTHORIZATION_162_RECORD", changed(validator.REGISTRY, duplicate162), "DUPLICATE_CONSUMED_AUTHORIZATION_162_RECORD"))

    def remove162(value: dict[str, Any]) -> None:
        value["records"] = [x for x in value["records"] if x["id"] != "AUTHORIZATION_LAB_M5_STAGE_AWARE_VALIDATOR_REMEDIATION_162"]
    cases.append(expect("MISSING_CONSUMED_AUTHORIZATION_162_RECORD", changed(validator.REGISTRY, remove162), "MISSING_CONSUMED_AUTHORIZATION_162_RECORD"))

    def missing_transition(value: dict[str, Any]) -> None:
        value["authorization_state"].pop("integration_factory_m5_stage_aware_validator_remediation_162")
    cases.append(expect("MISSING_CURRENT_STATE_AUTHORIZATION_TRANSITION", changed("CURRENT_STATE.json", missing_transition), "MISSING_CURRENT_STATE_AUTHORIZATION_TRANSITION"))

    cases.append(expect("BRIEF_162_STILL_READY", changed(validator.BRIEF162, lambda value: value.update(status="READY")), "BRIEF_162_STILL_READY"))

    def granted(value: dict[str, Any]) -> None:
        value["authority"]["authorization_status"] = "GRANTED"
    cases.append(expect("BRIEF_162_STILL_GRANTED", changed(validator.BRIEF162, granted), "BRIEF_162_STILL_GRANTED"))

    def next_attempt(value: dict[str, Any]) -> None:
        value["current_execution_id"] = "ATTEMPT-004"
    cases.append(expect("BRIEF_162_NEXT_ATTEMPT_NON_NULL", changed(validator.BRIEF162, next_attempt), "BRIEF_162_NEXT_ATTEMPT_NON_NULL"))

    def active_authority(value: dict[str, Any]) -> None:
        value["current_authority"] = "AUTHORIZATION_162_STAGE_2_VALIDATOR_REMEDIATION_ONLY"
    cases.append(expect("PEND_LAB_039_RETAINS_ACTIVE_AUTHORITY", changed("projects/lab/pending/PEND-LAB-039.json", active_authority), "PEND_LAB_039_RETAINS_ACTIVE_AUTHORITY"))

    def placeholder(value: dict[str, Any]) -> None:
        value["publication_commit"] = "THIS_ATTEMPT_003_PUBLICATION_COMMIT"
    evidence = "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M5-STAGE-AWARE-VALIDATOR-REMEDIATION-162.json"
    cases.append(expect("EVIDENCE_162_PUBLICATION_COMMIT_PLACEHOLDER_REMAINS", changed(evidence, placeholder), "EVIDENCE_162_PUBLICATION_COMMIT_PLACEHOLDER_REMAINS"))

    selector = (ROOT / validator.SELECTOR).read_bytes().replace(b'"selector_id"', b'"selector_ix"', 1)
    cases.append(expect("STATIC_SELECTOR_BLOB_ALTERED", {validator.SELECTOR: selector}, "STATIC_SELECTOR_BLOB_ALTERED"))
    shadow_bytes = (ROOT / validator.SHADOW).read_bytes().replace(b'"SHADOW_ONLY_NOT_ACTIVE"', b'"SHADOW_ONLY_NOT_ACTIVF"')
    cases.append(expect("SHADOW_REGISTRY_BLOB_ALTERED", {validator.SHADOW: shadow_bytes}, "SHADOW_REGISTRY_BLOB_ALTERED"))

    def activate_shadow(value: dict[str, Any]) -> None:
        value["status"] = "ACTIVE"
    cases.append(expect("SHADOW_REGISTRY_TREATED_AS_ACTIVE", changed(validator.SHADOW, activate_shadow), "SHADOW_REGISTRY_TREATED_AS_ACTIVE"))
    cases.append(expect("UNAUTHORIZED_CANONICAL_ACTIVE_POINTER_PRESENT", {"__pointer_exists__": True}, "UNAUTHORIZED_CANONICAL_ACTIVE_POINTER_PRESENT"))

    def absolute(value: dict[str, Any]) -> None:
        value["findings"][0]["normalized_message"] = "C:/Users/example/chatgpt-prototype-lab/" + value["findings"][0]["normalized_message"]
    cases.append(expect("PORTABLE_BASELINE_CONTAINS_ABSOLUTE_PATH", changed(validator.PORTABLE, absolute), "PORTABLE_BASELINE_CONTAINS_ABSOLUTE_PATH"))

    def drift(value: dict[str, Any]) -> None:
        value["findings"][0]["stable_id"] = "GVF-0000000000000000"
    cases.append(expect("PORTABLE_BASELINE_STABLE_ID_DRIFT", changed(validator.PORTABLE, drift), "PORTABLE_BASELINE_STABLE_ID_DRIFT"))

    def reusable(value: dict[str, Any]) -> None:
        value["authorization_reusable"] = True
    cases.append(expect("AUTHORIZATION_162_TREATED_AS_REUSABLE", changed(validator.BRIEF162, reusable), "AUTHORIZATION_162_TREATED_AS_REUSABLE"))

    def premature(value: dict[str, Any]) -> None:
        value["stage_1"]["status"] = "GRANTED_NOT_STARTED"
        value["stage_2"]["status"] = "EXECUTING"
    cases.append(expect("STAGE_2_STARTED_WITHOUT_VERIFIED_STAGE_1_REMOTE_PUBLICATION", changed(validator.AUTH165, premature), "STAGE_2_STARTED_WITHOUT_VERIFIED_STAGE_1_REMOTE_PUBLICATION"))

    passed = sum(item["pass"] for item in cases)
    return {"classification": "PASS" if passed == 18 else "BLOCK", "passed": passed, "required": 18, "cases": cases}


def main() -> None:
    result = execute()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
