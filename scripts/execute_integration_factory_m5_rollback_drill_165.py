#!/usr/bin/env python3
"""Execute authorization-165's rollback drill in a linked disposable worktree."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "b19e702cbe7afb83b4e209b85f9e7c5dbba40fc1"
STATIC = "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
SHADOW = "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json"
POINTER = "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json"
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
SHADOW_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
CASES = [
    "STATIC_TO_CANDIDATE_SUCCESS", "CANDIDATE_TO_STATIC_SUCCESS",
    "FAIL_BEFORE_PREPARATION", "FAIL_DURING_PREPARATION",
    "FAIL_BEFORE_POINTER_SWITCH", "FAIL_IMMEDIATELY_AFTER_POINTER_SWITCH",
    "INTERRUPTION_DURING_VALIDATION", "IDEMPOTENT_ROLLBACK",
    "DOUBLE_EXECUTION", "INVALID_INITIAL_STATE", "UNEXPECTED_BLOB",
    "LOCK_OCCUPIED", "CLEANUP", "NO_PERSISTENT_PARTIAL_ACTIVATION",
]
EXPECTED = {
    "STATIC_TO_CANDIDATE_SUCCESS": "CANDIDATE_CONFIRMED_THEN_SANDBOX_RESET",
    "CANDIDATE_TO_STATIC_SUCCESS": "STATIC_INTACT",
    "FAIL_BEFORE_PREPARATION": "STATIC_INTACT",
    "FAIL_DURING_PREPARATION": "STATIC_INTACT",
    "FAIL_BEFORE_POINTER_SWITCH": "STATIC_INTACT",
    "FAIL_IMMEDIATELY_AFTER_POINTER_SWITCH": "STATIC_INTACT",
    "INTERRUPTION_DURING_VALIDATION": "STATIC_INTACT",
    "IDEMPOTENT_ROLLBACK": "STATIC_INTACT_AFTER_TWO_CALLS",
    "DOUBLE_EXECUTION": "DETERMINISTIC_IDEMPOTENT_CONFIRMATION",
    "INVALID_INITIAL_STATE": "REVERTED_TO_STATIC",
    "UNEXPECTED_BLOB": "REVERTED_TO_STATIC",
    "LOCK_OCCUPIED": "NO_MUTATION_LOCK_REJECTED",
    "CLEANUP": "NO_TEMP_CANDIDATE_OR_LOCK",
    "NO_PERSISTENT_PARTIAL_ACTIVATION": "UNREFERENCED_PARTIAL_DISCARDED_STATIC_INTACT",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def blob(relative: str) -> str:
    return git("hash-object", relative)


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class Drill:
    def __init__(self) -> None:
        self.active = ROOT / "architecture/integrations/active"
        self.active_preexisted = self.active.exists()
        self.pointer = ROOT / POINTER
        self.pointer_tmp = self.active / ".INTEGRATION_FACTORY_RESOLUTION_POINTER.json.tmp"
        self.candidate_tmp = self.active / ".integration-factory-candidate-165.tmp"
        self.case_lock = self.active / ".rollback-drill-165.case.lock"
        self.drill_lock = self.active / ".rollback-drill-165.lock"
        self.active.mkdir(parents=True, exist_ok=True)

    def atomic_pointer(self, target: str, target_blob: str) -> None:
        payload = {"target": target, "blob": target_blob, "temporary_drill": True}
        with self.pointer_tmp.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.pointer_tmp.replace(self.pointer)

    def acquire_drill_lock(self) -> None:
        with self.drill_lock.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write("AUTHORIZATION_165_EXCLUSIVE_DISPOSABLE_WORKTREE\n")

    def cleanup(self, include_drill_lock: bool = False) -> None:
        for path in (self.pointer_tmp, self.candidate_tmp, self.pointer, self.case_lock):
            path.unlink(missing_ok=True)
        if include_drill_lock:
            self.drill_lock.unlink(missing_ok=True)
        if not self.active_preexisted:
            try:
                self.active.rmdir()
            except OSError:
                pass

    def static_intact(self) -> bool:
        shadow = json.loads((ROOT / SHADOW).read_text(encoding="utf-8"))
        return (
            not self.pointer.exists()
            and blob(STATIC) == STATIC_BLOB
            and blob(SHADOW) == SHADOW_BLOB
            and shadow.get("status") == "SHADOW_ONLY_NOT_ACTIVE"
            and shadow.get("automatic_activation") is False
        )

    def rollback(self) -> None:
        if blob(STATIC) != STATIC_BLOB:
            raise RuntimeError("STATIC_ROLLBACK_BLOB_MISMATCH")
        self.cleanup()

    def activate(self, injection: str | None = None) -> str:
        if self.case_lock.exists():
            return "LOCK_REJECTED_NO_MUTATION"
        if self.pointer.exists():
            current = json.loads(self.pointer.read_text(encoding="utf-8"))
            allowed = [
                {"target": "STATIC", "blob": STATIC_BLOB, "temporary_drill": True},
                {"target": "CANDIDATE", "blob": SHADOW_BLOB, "temporary_drill": True},
            ]
            if current not in allowed:
                self.rollback()
                return "INVALID_INITIAL_STATE_REVERTED"
        if injection == "BEFORE_PREPARATION":
            self.rollback()
            return "INJECTED_FAILURE_REVERTED"
        self.case_lock.write_text("AUTHORIZATION_165_CASE_OWNER\n", encoding="utf-8")
        try:
            self.candidate_tmp.write_text(
                json.dumps({"target": "CANDIDATE", "blob": SHADOW_BLOB}) + "\n",
                encoding="utf-8", newline="\n",
            )
            if injection == "DURING_PREPARATION":
                raise RuntimeError("INJECTED_DURING_PREPARATION")
            candidate = json.loads(self.candidate_tmp.read_text(encoding="utf-8"))
            if candidate.get("blob") != SHADOW_BLOB:
                raise RuntimeError("UNEXPECTED_CANDIDATE_BLOB")
            if injection == "BEFORE_POINTER_SWITCH":
                raise RuntimeError("INJECTED_BEFORE_POINTER_SWITCH")
            self.atomic_pointer("CANDIDATE", SHADOW_BLOB)
            if injection in {"AFTER_POINTER_SWITCH", "DURING_VALIDATION"}:
                raise RuntimeError("INJECTED_POST_SWITCH")
            return "CANDIDATE_CONFIRMED"
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
            self.rollback()
            return "INJECTED_FAILURE_REVERTED"
        finally:
            self.case_lock.unlink(missing_ok=True)


def run_case(name: str, drill: Drill) -> dict[str, Any]:
    drill.rollback()
    outcome = ""
    if name == "STATIC_TO_CANDIDATE_SUCCESS":
        outcome = drill.activate(); passed = outcome == "CANDIDATE_CONFIRMED"
        drill.rollback()
    elif name == "CANDIDATE_TO_STATIC_SUCCESS":
        drill.atomic_pointer("CANDIDATE", SHADOW_BLOB); drill.rollback()
        outcome = "STATIC_INTACT"; passed = drill.static_intact()
    elif name in {"FAIL_BEFORE_PREPARATION", "FAIL_DURING_PREPARATION", "FAIL_BEFORE_POINTER_SWITCH", "FAIL_IMMEDIATELY_AFTER_POINTER_SWITCH", "INTERRUPTION_DURING_VALIDATION"}:
        injection = {
            "FAIL_BEFORE_PREPARATION": "BEFORE_PREPARATION",
            "FAIL_DURING_PREPARATION": "DURING_PREPARATION",
            "FAIL_BEFORE_POINTER_SWITCH": "BEFORE_POINTER_SWITCH",
            "FAIL_IMMEDIATELY_AFTER_POINTER_SWITCH": "AFTER_POINTER_SWITCH",
            "INTERRUPTION_DURING_VALIDATION": "DURING_VALIDATION",
        }[name]
        outcome = drill.activate(injection); passed = drill.static_intact()
    elif name == "IDEMPOTENT_ROLLBACK":
        drill.rollback(); drill.rollback(); outcome = "STATIC_INTACT_AFTER_TWO_CALLS"; passed = drill.static_intact()
    elif name == "DOUBLE_EXECUTION":
        first = drill.activate(); drill.rollback(); second = drill.activate(); drill.rollback()
        outcome = f"{first}+{second}"; passed = first == second == "CANDIDATE_CONFIRMED"
    elif name == "INVALID_INITIAL_STATE":
        drill.atomic_pointer("PARTIAL", "invalid"); outcome = drill.activate(); passed = drill.static_intact()
    elif name == "UNEXPECTED_BLOB":
        drill.atomic_pointer("STATIC", "unexpected"); outcome = drill.activate(); passed = drill.static_intact()
    elif name == "LOCK_OCCUPIED":
        drill.case_lock.write_text("FOREIGN_OWNER\n", encoding="utf-8")
        outcome = drill.activate(); passed = outcome == "LOCK_REJECTED_NO_MUTATION" and not drill.pointer.exists()
        drill.case_lock.unlink(missing_ok=True)
    elif name == "CLEANUP":
        drill.candidate_tmp.write_text("stale\n", encoding="utf-8")
        drill.case_lock.write_text("AUTHORIZATION_165_CASE_OWNER\n", encoding="utf-8")
        drill.rollback(); outcome = "NO_TEMP_CANDIDATE_OR_LOCK"
        passed = drill.static_intact()
    else:
        drill.pointer_tmp.write_text("partial\n", encoding="utf-8")
        drill.candidate_tmp.write_text("partial\n", encoding="utf-8")
        drill.rollback(); outcome = "UNREFERENCED_PARTIAL_DISCARDED_STATIC_INTACT"
        passed = drill.static_intact()
    clean = all(not path.exists() for path in (drill.pointer, drill.pointer_tmp, drill.candidate_tmp, drill.case_lock))
    return {"case": name, "expected": EXPECTED[name], "result": "PASS" if passed and clean else "FAIL",
            "observed": outcome, "final_state": "STATIC_INTACT" if drill.static_intact() else "NOT_STATIC",
            "temporary_cleanup": "PASS" if clean else "FAIL"}


def execute() -> dict[str, Any]:
    if not (ROOT / ".git").is_file() or git("rev-parse", "HEAD") != EXPECTED_HEAD:
        raise RuntimeError("NOT_EXACT_DISPOSABLE_STAGE_1_WORKTREE")
    drill = Drill()
    pre = {"pointer": "ABSENT" if not drill.pointer.exists() else "PRESENT", "static_blob": blob(STATIC), "shadow_blob": blob(SHADOW)}
    drill.acquire_drill_lock()
    try:
        results = [run_case(name, drill) for name in CASES]
    finally:
        drill.cleanup(include_drill_lock=True)
    post = {"pointer": "ABSENT" if not drill.pointer.exists() else "PRESENT", "static_blob": blob(STATIC), "shadow_blob": blob(SHADOW)}
    core = {"schema_version": "1.0.0", "drill_id": "INTEGRATION_FACTORY_M5_OPERATIONAL_ROLLBACK_DRILL_165",
            "authorization": "AUTHORIZATION_LAB_M5_CANONICAL_CORRECTION_AND_CONDITIONAL_OPERATIONAL_ROLLBACK_DRILL_165",
            "verified_stage_1_head": EXPECTED_HEAD, "environment": "DISPOSABLE_TEMPORARY_GIT_WORKTREE_ONLY",
            "case_count": len(results), "cases": results, "pointer_pre_state": pre, "pointer_post_state": post,
            "failure_invariant": "EVERY_INJECTED_FAILURE_ENDS_STATIC_INTACT", "persistent_pointer": False,
            "m5_retry": False, "cutover": False, "runtime_effect": "NONE", "integration_effect": "NONE",
            "aws_effect": "NONE", "terraform_effect": "NONE"}
    passed = len(results) == 14 and all(item["result"] == "PASS" and item["final_state"] == "STATIC_INTACT" for item in results)
    return {**core, "normalized_digest": canonical_digest(core),
            "classification": "M5_OPERATIONAL_ROLLBACK_DRILL_PASS_AWAITING_SEPARATE_M5_RETRY_OR_CUTOVER_DECISION" if passed else "M5_OPERATIONAL_ROLLBACK_DRILL_FAIL_CLOSED_WITH_CLASSIFIED_FAILURES"}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args()
    result = execute(); rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    raise SystemExit(0 if result["classification"].startswith("M5_OPERATIONAL_ROLLBACK_DRILL_PASS") else 1)


if __name__ == "__main__":
    main()
