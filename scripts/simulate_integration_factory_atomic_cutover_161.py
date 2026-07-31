#!/usr/bin/env python3
"""Deterministic, filesystem-only M5 readiness simulation for authorization 161."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
CANDIDATE_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
CASES = [
    "STATIC_TO_CANDIDATE_SUCCESS", "CANDIDATE_TO_STATIC_SUCCESS",
    "FAIL_BEFORE_PREPARATION", "FAIL_DURING_PREPARATION",
    "FAIL_BEFORE_POINTER_SWITCH", "FAIL_IMMEDIATELY_AFTER_POINTER_SWITCH",
    "INTERRUPTION_DURING_VALIDATION", "IDEMPOTENT_ROLLBACK",
    "DOUBLE_EXECUTION", "INVALID_INITIAL_STATE", "UNEXPECTED_BLOB",
    "LOCK_OCCUPIED", "CLEANUP", "NO_PERSISTENT_PARTIAL_ACTIVATION",
]


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class Sandbox:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.pointer = root / "governed-pointer.json"
        self.candidate = root / "prepared-candidate.json"
        self.lock = root / "cutover.lock"

    def set_pointer(self, target: str, blob: str) -> None:
        temporary = self.pointer.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"target": target, "blob": blob}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.pointer)

    def read_pointer(self) -> dict[str, str]:
        return json.loads(self.pointer.read_text(encoding="utf-8"))

    def reset_static(self) -> None:
        self.set_pointer("STATIC", STATIC_BLOB)
        self.candidate.unlink(missing_ok=True)
        self.lock.unlink(missing_ok=True)

    def intact_static(self) -> bool:
        return self.read_pointer() == {"target": "STATIC", "blob": STATIC_BLOB}


def activate_candidate(box: Sandbox, inject: str | None = None) -> str:
    if box.lock.exists():
        return "LOCK_REJECTED"
    current = box.read_pointer()
    if current not in (
        {"target": "STATIC", "blob": STATIC_BLOB},
        {"target": "CANDIDATE", "blob": CANDIDATE_BLOB},
    ):
        box.reset_static()
        return "INVALID_INITIAL_STATE_REVERTED"
    if inject == "BEFORE_PREPARATION":
        box.reset_static()
        return "INJECTED_FAILURE_REVERTED"
    box.lock.write_text("authorization-161-sandbox\n", encoding="utf-8")
    try:
        box.candidate.write_text(
            json.dumps({"target": "CANDIDATE", "blob": CANDIDATE_BLOB}) + "\n",
            encoding="utf-8",
        )
        if inject == "DURING_PREPARATION":
            raise RuntimeError("injected during preparation")
        prepared = json.loads(box.candidate.read_text(encoding="utf-8"))
        if prepared.get("blob") != CANDIDATE_BLOB:
            raise RuntimeError("unexpected candidate blob")
        if inject == "BEFORE_POINTER_SWITCH":
            raise RuntimeError("injected before pointer switch")
        box.set_pointer("CANDIDATE", CANDIDATE_BLOB)
        if inject in {"AFTER_POINTER_SWITCH", "DURING_VALIDATION"}:
            raise RuntimeError("injected after pointer switch")
        if box.read_pointer() != {"target": "CANDIDATE", "blob": CANDIDATE_BLOB}:
            raise RuntimeError("candidate validation failed")
        return "CANDIDATE_CONFIRMED"
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
        box.reset_static()
        return "INJECTED_FAILURE_REVERTED"
    finally:
        box.lock.unlink(missing_ok=True)


def run_case(case: str, root: Path) -> dict[str, Any]:
    box = Sandbox(root / case.lower())
    box.root.mkdir(parents=True)
    box.reset_static()
    outcome = "PASS"
    if case == "STATIC_TO_CANDIDATE_SUCCESS":
        outcome = activate_candidate(box)
        passed = outcome == "CANDIDATE_CONFIRMED"
        box.reset_static()
    elif case == "CANDIDATE_TO_STATIC_SUCCESS":
        box.set_pointer("CANDIDATE", CANDIDATE_BLOB)
        box.reset_static(); passed = box.intact_static()
    elif case.startswith("FAIL_") or case == "INTERRUPTION_DURING_VALIDATION":
        injection = {
            "FAIL_BEFORE_PREPARATION": "BEFORE_PREPARATION",
            "FAIL_DURING_PREPARATION": "DURING_PREPARATION",
            "FAIL_BEFORE_POINTER_SWITCH": "BEFORE_POINTER_SWITCH",
            "FAIL_IMMEDIATELY_AFTER_POINTER_SWITCH": "AFTER_POINTER_SWITCH",
            "INTERRUPTION_DURING_VALIDATION": "DURING_VALIDATION",
        }[case]
        outcome = activate_candidate(box, injection); passed = box.intact_static()
    elif case == "IDEMPOTENT_ROLLBACK":
        box.reset_static(); box.reset_static(); outcome = "STATIC_TWICE"; passed = box.intact_static()
    elif case == "DOUBLE_EXECUTION":
        first = activate_candidate(box); second = activate_candidate(box)
        outcome = f"{first}+{second}"; passed = first == second == "CANDIDATE_CONFIRMED"
        box.reset_static()
    elif case == "INVALID_INITIAL_STATE":
        box.set_pointer("PARTIAL", "invalid"); outcome = activate_candidate(box); passed = box.intact_static()
    elif case == "UNEXPECTED_BLOB":
        box.set_pointer("STATIC", "unexpected"); outcome = activate_candidate(box); passed = box.intact_static()
    elif case == "LOCK_OCCUPIED":
        box.lock.write_text("other-owner\n", encoding="utf-8")
        outcome = activate_candidate(box); passed = outcome == "LOCK_REJECTED" and box.intact_static()
        box.lock.unlink(missing_ok=True)
    elif case == "CLEANUP":
        box.candidate.write_text("stale\n", encoding="utf-8"); box.reset_static()
        outcome = "CLEAN"; passed = box.intact_static() and not box.candidate.exists() and not box.lock.exists()
    else:
        box.pointer.with_suffix(".tmp").write_text("partial", encoding="utf-8")
        box.reset_static(); outcome = "PARTIAL_DISCARDED"; passed = box.intact_static()
    return {"case": case, "result": "PASS" if passed else "FAIL", "outcome": outcome,
            "final_state": "STATIC_INTACT" if box.intact_static() else "NOT_STATIC"}


def execute() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="lab-m5-readiness-161-") as temporary:
        results = [run_case(case, Path(temporary)) for case in CASES]
    normalized = {"schema_version": "1.0.0", "case_count": len(results), "cases": results}
    digest = canonical_digest(normalized)
    return {**normalized, "normalized_digest": digest,
            "classification": "PASS" if all(x["result"] == "PASS" for x in results) else "FAIL",
            "canonical_effect": "NONE", "runtime_effect": "NONE", "integration_effect": "NONE"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = execute()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
