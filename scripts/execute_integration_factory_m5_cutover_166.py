#!/usr/bin/env python3
"""Execute authorization 166 Stage 2 with atomic pointer rollback semantics."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_integration_factory_m3 import append_oracle_divergences, build_divergences, oracle_passes

ROOT = Path(__file__).resolve().parents[1]
PARENT = "4ced6a5f63f833f1526400b70eb531078f1e771a"
AUTH = "AUTHORIZATION_LAB_M5_BOUNDED_CUTOVER_OBSERVATION_AND_AUTOMATIC_ROLLBACK_166"
ACTIVE = Path("architecture/integrations/active")
POINTER = ACTIVE / "INTEGRATION_FACTORY_RESOLUTION_POINTER.json"
TEMP_POINTER = ACTIVE / ".INTEGRATION_FACTORY_RESOLUTION_POINTER.166.tmp"
LOCK = ACTIVE / ".integration-factory-cutover-166.lock"
STATIC = Path("project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json")
CANDIDATE = Path("architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json")
CORPUS = Path("architecture/integrations/migration/M3/remediation-158/TEST_CORPUS.json")
BASELINE = Path("architecture/integrations/migration/M5/cutover-166/PRE_CUTOVER_GENERAL_VALIDATOR_BASELINE.json")
OUT = Path("architecture/integrations/migration/M5/cutover-166")
STATIC_EVALUATOR = Path("scripts/integration_factory_m3_static_evaluator.py")
CANDIDATE_EVALUATOR = Path("scripts/integration_factory_m3_shadow_evaluator.py")
STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
CANDIDATE_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"
CORPUS_BLOB = "009065769f524f17f3ffdf137fb0213ee30fb150"
DIGEST = "9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329"


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load(path: Path) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def blob(path: Path) -> str:
    return git("hash-object", "--", path.as_posix())


def atomic_json(path: Path, value: Any, temporary: Path | None = None) -> None:
    target = ROOT / path
    temp = ROOT / (temporary or path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp"))
    target.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with temp.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, target)


def preflight(expected_parent: str) -> None:
    if git("rev-parse", "HEAD") != expected_parent:
        raise RuntimeError("UNEXPECTED_LOCAL_HEAD")
    if git("rev-parse", "origin/main") != expected_parent or git("rev-parse", "FETCH_HEAD") != expected_parent:
        raise RuntimeError("UNVERIFIED_REMOTE_PARENT")
    if git("branch", "--show-current") != "main":
        raise RuntimeError("UNEXPECTED_BRANCH")
    remote = git("remote", "get-url", "origin")
    if "marcellusanthonson-ctrl/chatgpt-prototype-lab" not in remote:
        raise RuntimeError("UNEXPECTED_REPOSITORY")
    allowed = {"scripts/execute_integration_factory_m5_cutover_166.py", "scripts/validate_integration_factory_m5_cutover_166.py"}
    changed = set(git("status", "--porcelain").splitlines())
    changed_paths = {line[3:].replace("\\", "/") for line in changed}
    if changed_paths - allowed:
        raise RuntimeError("UNAUTHORIZED_PREEXECUTION_DELTA")
    if (ROOT / POINTER).exists() or (ROOT / LOCK).exists() or (ROOT / TEMP_POINTER).exists():
        raise RuntimeError("POINTER_LOCK_OR_TEMP_NOT_ABSENT")
    if blob(STATIC) != STATIC_BLOB or blob(CANDIDATE) != CANDIDATE_BLOB or blob(CORPUS) != CORPUS_BLOB:
        raise RuntimeError("PINNED_BLOB_MISMATCH")
    candidate = load(CANDIDATE)
    corpus = load(CORPUS)
    if candidate.get("status") != "SHADOW_ONLY_NOT_ACTIVE":
        raise RuntimeError("CANDIDATE_ALREADY_ACTIVE")
    if corpus.get("corpus_id") != "INTEGRATION_FACTORY_M3_REMEDIATION_158_CORPUS_001" or len(corpus.get("cases", [])) != 420:
        raise RuntimeError("CORPUS_INVALID")


def pointer_value(owner: str, state: str, active: str, result: str, confirmed: str | None) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0", "pointer_id": "integration_factory_resolution_target",
        "state": state, "active_target": active, "fallback_target": "STATIC",
        "candidate": {"canonical_path": CANDIDATE.as_posix(), "expected_blob": CANDIDATE_BLOB},
        "static_fallback": {"canonical_path": STATIC.as_posix(), "expected_blob": STATIC_BLOB},
        "activation_authorization": AUTH, "verified_activation_parent_head": PARENT,
        "observation_evidence_reference": (OUT / "OBSERVATION_RESULTS.json").as_posix(),
        "automatic_rollback_policy": "MANDATORY_ATOMIC_REPLACE_TO_STATIC_ON_ANY_FAILURE",
        "confirmation_timestamp": confirmed, "last_validated_result": result, "lock_owner_id": owner,
    }


def validate_pointer(value: dict[str, Any], target: str, state: str, owner: str) -> None:
    checks = [value.get("pointer_id") == "integration_factory_resolution_target", value.get("active_target") == target,
              value.get("fallback_target") == "STATIC", value.get("state") == state, value.get("lock_owner_id") == owner,
              value.get("candidate", {}).get("expected_blob") == CANDIDATE_BLOB,
              value.get("static_fallback", {}).get("expected_blob") == STATIC_BLOB]
    if not all(checks):
        raise RuntimeError("POINTER_SCHEMA_OR_TARGET_INVALID")


def evaluate(iteration: int, temporary: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    outputs = []
    for name, script in (("static", STATIC_EVALUATOR), ("candidate", CANDIDATE_EVALUATOR)):
        path = temporary / f"{name}-{iteration}.json"
        subprocess.run([sys.executable, "-B", str(ROOT / script), "--root", str(ROOT), "--corpus", CORPUS.as_posix(),
                        "--output", str(path)], check=True)
        outputs.append(json.loads(path.read_text(encoding="utf-8")))
    static, candidate = outputs
    cases = load(CORPUS)["cases"]
    divergences = build_divergences(cases, static["results"], candidate["results"])
    append_oracle_divergences(divergences, cases, static["results"], candidate["results"])
    matches = sum(a == b for a, b in zip(static["results"], candidate["results"], strict=True))
    result = {"iteration": iteration, "case_count": 420, "exact_matches": matches,
              "static_oracles": oracle_passes(cases, static), "candidate_oracles": oracle_passes(cases, candidate),
              "behavioral_divergences": len(divergences), "static_digest": static["normalized_run_digest"],
              "candidate_digest": candidate["normalized_run_digest"], "classification": "PASS"}
    if matches != 420 or result["static_oracles"] != 13 or result["candidate_oracles"] != 13 or divergences:
        raise RuntimeError(f"OBSERVATION_ITERATION_{iteration}_MISMATCH")
    if result["static_digest"] != DIGEST or result["candidate_digest"] != DIGEST:
        raise RuntimeError(f"OBSERVATION_ITERATION_{iteration}_DIGEST_MISMATCH")
    return result, outputs


def general_delta() -> dict[str, Any]:
    process = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/validate_repository.py")], capture_output=True,
                             text=True, encoding="utf-8")
    messages = [line[6:] for line in process.stdout.splitlines() if line.startswith("FAIL: ")]
    baseline = load(BASELINE)
    expected = [item["normalized_message"] for item in baseline["findings"]]
    if process.returncode != 1 or messages != expected:
        raise RuntimeError("GENERAL_VALIDATOR_UNAUTHORIZED_DELTA")
    return {"finding_count": 329, "exit_code": 1, "exact_ordered_inventory": True, "added": [], "removed": [],
            "modified": [], "structured_inventory_digest": baseline["structured_inventory_digest"],
            "raw_ordered_message_digest": baseline["raw_ordered_message_digest"], "global_repository_pass": False}


def publish(values: dict[str, Any]) -> None:
    for name, value in values.items():
        atomic_json(OUT / name, value)


def execute(expected_parent: str) -> dict[str, Any]:
    preflight(expected_parent)
    owner = f"AUTH166-{uuid.uuid4()}"
    started, commands, transitions, observations, effects = now(), [], [], [], []
    lock_acquired = pointer_switched = rollback = False
    failure: str | None = None
    try:
        (ROOT / ACTIVE).mkdir(parents=True, exist_ok=True)
        descriptor = os.open(ROOT / LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"owner": owner, "authorization": AUTH, "parent": expected_parent, "acquired_at": now()}, handle)
            handle.flush(); os.fsync(handle.fileno())
        lock_acquired = True; commands.extend(["ACQUIRE_EXCLUSIVE_FAIL_CLOSED_LOCK", "VERIFY_INITIAL_STATIC_STATE"])
        prepared = load(CANDIDATE)
        if prepared.get("status") != "SHADOW_ONLY_NOT_ACTIVE" or blob(CANDIDATE) != CANDIDATE_BLOB:
            raise RuntimeError("PREPARED_CANDIDATE_INVALID")
        commands.extend(["PREPARE_CANDIDATE_WITHOUT_ACTIVATION", "VALIDATE_PREPARED_CANDIDATE"])
        unconfirmed = pointer_value(owner, "CANDIDATE_ACTIVE_UNCONFIRMED", "CANDIDATE", "IMMEDIATE_VALIDATION_PENDING", None)
        atomic_json(POINTER, unconfirmed, TEMP_POINTER); pointer_switched = True
        transitions.append({"from": "ABSENT", "to": "CANDIDATE_ACTIVE_UNCONFIRMED", "at": now()})
        validate_pointer(load(POINTER), "CANDIDATE", "CANDIDATE_ACTIVE_UNCONFIRMED", owner)
        commands.extend(["ATOMICALLY_REPLACE_SINGLE_GOVERNED_POINTER", "VALIDATE_ACTIVE_CANDIDATE_IMMEDIATELY"])
        with tempfile.TemporaryDirectory(prefix="lab-m5-cutover-166-") as temp:
            for iteration in (1, 2):
                result, evaluator_outputs = evaluate(iteration, Path(temp)); observations.append(result); effects.extend(evaluator_outputs)
        if any(x.get("authority_effect") != "NONE" or x.get("runtime_effect") != "NONE" or x.get("integration_effect") != "NONE" for x in effects):
            raise RuntimeError("AUTHORITY_RUNTIME_OR_INTEGRATION_BOUNDARY_BREACH")
        if observations[0]["static_digest"] != observations[1]["static_digest"] or observations[0]["candidate_digest"] != observations[1]["candidate_digest"]:
            raise RuntimeError("NONDETERMINISTIC_NORMALIZED_DIGEST")
        delta = general_delta(); commands.extend(["EXECUTE_TWO_OBSERVATION_ITERATIONS", "VERIFY_BOUNDARIES", "VERIFY_GENERAL_VALIDATOR_ZERO_DELTA"])
        confirmed_at = now()
        confirmed = pointer_value(owner, "CANDIDATE_ACTIVE_CONFIRMED", "CANDIDATE",
                                  "PASS_420_OF_420_TWO_ITERATIONS_13_OF_13_ZERO_DIVERGENCES_EXACT_DIGEST", confirmed_at)
        atomic_json(POINTER, confirmed, TEMP_POINTER); validate_pointer(load(POINTER), "CANDIDATE", "CANDIDATE_ACTIVE_CONFIRMED", owner)
        transitions.append({"from": "CANDIDATE_ACTIVE_UNCONFIRMED", "to": "CANDIDATE_ACTIVE_CONFIRMED", "at": confirmed_at})
        commands.append("CONFIRM_CANDIDATE_ACTIVE")
    except BaseException as exc:
        failure = f"{type(exc).__name__}:{exc}"
        if pointer_switched:
            if blob(STATIC) != STATIC_BLOB:
                raise RuntimeError("M5_CUTOVER_CRITICAL_ROLLBACK_TARGET_VERIFICATION_FAILURE") from exc
            rolled = pointer_value(owner, "FAILED_CLOSED_STATIC", "STATIC", "AUTOMATIC_ROLLBACK_TO_STATIC_CONFIRMED", now())
            atomic_json(POINTER, rolled, TEMP_POINTER); validate_pointer(load(POINTER), "STATIC", "FAILED_CLOSED_STATIC", owner)
            transitions.append({"from": "CANDIDATE_ACTIVE_UNCONFIRMED", "to": "FAILED_CLOSED_STATIC", "at": now()}); rollback = True
    finally:
        (ROOT / TEMP_POINTER).unlink(missing_ok=True)
        if lock_acquired:
            (ROOT / LOCK).unlink(missing_ok=True)
    success = failure is None
    classification = ("M5_BOUNDED_CUTOVER_PASS_INTEGRATION_ACTIVE_STATIC_FALLBACK_PRESERVED" if success else
                      "M5_BOUNDED_CUTOVER_ROLLED_BACK_STATIC_FALLBACK_ACTIVE_WITH_CLASSIFIED_FAILURES")
    delta = locals().get("delta", {"classification": "NOT_REACHED_DUE_TO_FAILURE"})
    common = {"schema_version": "1.0.0", "authorization_id": AUTH, "verified_parent_head": expected_parent}
    publish({
        "CUTOVER_RESULTS.json": {**common, "classification": classification, "started_at": started, "completed_at": now(),
                                 "pointer_switched": pointer_switched, "candidate_confirmed": success, "failure": failure},
        "OBSERVATION_RESULTS.json": {**common, "classification": "PASS" if success else "INCOMPLETE", "iterations": observations,
                                     "required_iterations": 2, "behavioral_digest": DIGEST, "deterministic": success},
        "POINTER_STATE_TRANSITIONS.json": {**common, "initial_state": "ABSENT", "transitions": transitions,
                                           "final_state": "CANDIDATE_ACTIVE_CONFIRMED" if success else "FAILED_CLOSED_STATIC"},
        "AUTOMATIC_ROLLBACK_RESULTS.json": {**common, "triggered": rollback, "failure": failure,
                                            "result": "NOT_TRIGGERED" if success else "AUTOMATIC_ROLLBACK_TO_STATIC_CONFIRMED"},
        "COMMAND_TRANSCRIPT.json": {**common, "commands": commands, "unclassified_exception_treated_as_pass": False},
        "LOCK_AND_CLEANUP_RESULTS.json": {**common, "lock_owner": owner, "lock_acquired": lock_acquired, "lock_removed": not (ROOT / LOCK).exists(),
                                          "temporary_pointer_removed": not (ROOT / TEMP_POINTER).exists(), "cleanup": "PASS"},
        "GENERAL_VALIDATOR_DELTA.json": {**common, **delta},
        "VALIDATION_RESULTS.json": {**common, "classification": "PASS" if success else "ROLLBACK_PASS", "failure": failure,
                                    "static_blob": blob(STATIC), "candidate_blob": blob(CANDIDATE), "pointer_target": load(POINTER)["active_target"],
                                    "lock_absent": not (ROOT / LOCK).exists(), "temporary_pointer_absent": not (ROOT / TEMP_POINTER).exists()},
    })
    result = {"classification": classification, "failure": failure, "pointer": load(POINTER), "observations": observations}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not success:
        raise SystemExit(1)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-parent", default=PARENT)
    execute(parser.parse_args().expected_parent)
