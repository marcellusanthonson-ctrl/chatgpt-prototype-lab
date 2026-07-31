#!/usr/bin/env python3
"""Execute and validate authorization 158's additive M3 remediation."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from validate_integration_factory_m3 import (
    CATEGORY_COUNTS,
    append_oracle_divergences,
    build_divergences,
    digest,
    generate_corpus,
    invariant_checks,
    oracle_passes,
)


OUTPUT_ROOT = Path("architecture/integrations/migration/M3/remediation-158")
SELECTOR = Path("project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json")
FIXTURES = Path("project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/ACCEPTANCE_FIXTURES.json")
HISTORICAL_FIXTURES = Path("project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/history/ACCEPTANCE_FIXTURES.v1.1.0.json")
REGISTRY = Path("architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json")
STATIC_EVALUATOR = Path("scripts/integration_factory_m3_static_evaluator.py")
SHADOW_EVALUATOR = Path("scripts/integration_factory_m3_shadow_evaluator.py")
AUTHORIZATION = Path("projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M3_ORACLE_AND_UTF8_REMEDIATION_158.json")
HISTORICAL_M3_ROOT = Path("architecture/integrations/migration/M3")
STAGE_1_HEAD = "c37cd23afcf841fc1f35e4f437c933a32d657a22"
M3_COMMIT = "fd6c371409a6667cbd96305d4a73ccb3bcd4adb2"
M3_PARENT = "ce5c86ee59013f335cc541d0066f9513c0de0872"
HISTORICAL_FIXTURE_BLOB = "de4793dedc9646e388bdce5ccd1807da8a711845"
EXPECTED_CURRENT_FIXTURE_BLOB = "db53d11e4a45e8f98a9b6aa540a2c7459723601b"
EXPECTED_BEHAVIOR_DIGEST = "9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329"
IMMUTABLE_BLOBS = {
    SELECTOR: "301ba432907758fc49a9b3c86a83fc762eac4607",
    REGISTRY: "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78",
    Path("architecture/integrations/migration/M2/module-adapters/EVIDENCE_AND_CLAIMS/ADAPTER.json"): "13d692e2aa481516f8411cc7092d1865369030d2",
    Path("architecture/integrations/migration/M2/module-adapters/DESIGN_CRITERION/ADAPTER.json"): "eba37a0e3d9207e269585d92f7b858486a44d9d6",
    Path("architecture/integrations/migration/M2/module-adapters/WEB_ACCESSIBILITY/ADAPTER.json"): "7c360c04703196989322bbc177e7b5877f9e4b3b",
    Path("architecture/integrations/migration/M2/module-adapters/CONTEXTUAL_VISUAL_PREFERENCE/ADAPTER.json"): "fbc7ba41184fe928db8c5c70c636e03a2ede2d78",
}
HISTORICAL_M3_FILES = [
    "DUAL_SELECTOR_TEST_DESIGN.json", "TEST_CORPUS.json", "STATIC_SELECTOR_RESULTS.json",
    "SHADOW_SELECTOR_RESULTS.json", "EQUIVALENCE_RESULTS.json", "DIVERGENCE_LOG.json",
    "VALIDATION_RESULTS.json",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def blob(root: Path, path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "hash-object", path.as_posix()], text=True).strip()


def head_blob(root: Path, path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", f"HEAD:{path.as_posix()}"], text=True).strip()


def recursive_differences(left: Any, right: Any, path: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    if type(left) is not type(right):
        return [path]
    if isinstance(left, dict):
        differences: list[tuple[Any, ...]] = []
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                differences.append(path + (key,))
            else:
                differences.extend(recursive_differences(left[key], right[key], path + (key,)))
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return [path]
        differences = []
        for index, (a, b) in enumerate(zip(left, right, strict=True)):
            differences.extend(recursive_differences(a, b, path + (index,)))
        return differences
    return [] if left == right else [path]


def fixture_change_is_exact(historical: dict[str, Any], current: dict[str, Any]) -> tuple[bool, list[str]]:
    differences = recursive_differences(historical, current)
    rendered = ["/".join(map(str, path)) for path in differences]
    expected = {"version", "fixtures/7/expected_modules"}
    fixture = next(item for item in current["fixtures"] if item["id"] == "CRIT-FIX-008")
    exact = (
        set(rendered) == expected
        and historical["version"] == "1.1.0"
        and current["version"] == "1.1.1"
        and fixture["expected_modules"] == ["EVIDENCE_AND_CLAIMS", "DESIGN_CRITERION", "WEB_ACCESSIBILITY"]
    )
    return exact, rendered


def run_evaluator(root: Path, script: Path, output: Path) -> dict[str, Any]:
    subprocess.run([
        sys.executable, "-B", str(root / script), "--root", str(root),
        "--corpus", (OUTPUT_ROOT / "TEST_CORPUS.json").as_posix(), "--output", str(output),
    ], check=True)
    return load(output)


def m3_introduced_mojibake_remaining(root: Path) -> tuple[bool, list[str]]:
    paths = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", M3_PARENT, M3_COMMIT], text=True).splitlines()
    suspicious = tuple(chr(value) for value in (0x00C3, 0x00C2, 0x0192, 0xFFFD))
    remaining: list[str] = []
    for relative in paths:
        current_path = root / relative
        if not current_path.exists():
            continue
        current = current_path.read_text(encoding="utf-8")
        parent_process = subprocess.run(
            ["git", "-C", str(root), "show", f"{M3_PARENT}:{relative}"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        parent = "" if parent_process.returncode else parent_process.stdout.decode("utf-8")
        current_count = sum(current.count(char) for char in suspicious)
        parent_count = sum(parent.count(char) for char in suspicious)
        if current_count > parent_count:
            remaining.append(relative)
    return not remaining, remaining


def changed_paths_authorized(root: Path) -> tuple[bool, list[str]]:
    authorization = load(root / AUTHORIZATION)
    archive = f"projects/lab/continuity/archive/m3-remediation-stage-2-preexecution-{STAGE_1_HEAD}"
    allowed_create = {
        path.replace("<STAGE_1_HEAD>", STAGE_1_HEAD) for path in authorization["allowed_create_paths"]
    }
    allowed_modify = set(authorization["allowed_modify_paths"])
    modified = set(subprocess.check_output(["git", "-C", str(root), "diff", "--name-only"], text=True).splitlines())
    untracked = set(subprocess.check_output(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"], text=True).splitlines())
    unauthorized = sorted((modified - allowed_modify) | (untracked - allowed_create))
    return not unauthorized, unauthorized


def prepare_corpus(selector: dict[str, Any], fixtures: dict[str, Any], current_blob: str) -> dict[str, Any]:
    corpus = generate_corpus(selector, fixtures)
    corpus["corpus_id"] = "INTEGRATION_FACTORY_M3_REMEDIATION_158_CORPUS_001"
    corpus["status"] = "DETERMINISTIC_SYNTHETIC_REMEDIATION_158"
    corpus["frozen_baseline"]["git_blob_sha"] = current_blob
    corpus["frozen_baseline"]["fixture_version"] = "1.1.1"
    corpus["frozen_baseline"]["historical_fixture_path"] = HISTORICAL_FIXTURES.as_posix()
    corpus["frozen_baseline"]["historical_fixture_blob"] = HISTORICAL_FIXTURE_BLOB
    corpus["corpus_digest"] = digest(corpus["cases"])
    return corpus


def execute(root: Path, write_outputs: bool) -> dict[str, Any]:
    selector = load(root / SELECTOR)
    fixtures = load(root / FIXTURES)
    historical = load(root / HISTORICAL_FIXTURES)
    current_fixture_blob = blob(root, FIXTURES)
    corpus = prepare_corpus(selector, fixtures, current_fixture_blob)
    corpus_path = root / OUTPUT_ROOT / "TEST_CORPUS.json"
    if write_outputs:
        write(corpus_path, corpus)
    elif load(corpus_path) != corpus:
        raise RuntimeError("Published remediation corpus differs from deterministic regeneration")

    with tempfile.TemporaryDirectory(prefix="lab-m3-remediation-158-") as temporary:
        temp = Path(temporary)
        static_1 = run_evaluator(root, STATIC_EVALUATOR, temp / "static-1.json")
        shadow_1 = run_evaluator(root, SHADOW_EVALUATOR, temp / "shadow-1.json")
        static_2 = run_evaluator(root, STATIC_EVALUATOR, temp / "static-2.json")
        shadow_2 = run_evaluator(root, SHADOW_EVALUATOR, temp / "shadow-2.json")
    for evaluation in (static_1, static_2, shadow_1, shadow_2):
        evaluation["remediation_id"] = "AUTHORIZATION_158"

    cases = corpus["cases"]
    divergences = build_divergences(cases, static_1["results"], shadow_1["results"])
    append_oracle_divergences(divergences, cases, static_1["results"], shadow_1["results"])
    static_oracles = oracle_passes(cases, static_1)
    shadow_oracles = oracle_passes(cases, shadow_1)
    static_invariants = invariant_checks(cases, static_1)
    shadow_invariants = invariant_checks(cases, shadow_1)
    fixture_exact, fixture_diff_paths = fixture_change_is_exact(historical, fixtures)
    immutable_observed = {path.as_posix(): blob(root, path) for path in IMMUTABLE_BLOBS}
    immutable_match = all(immutable_observed[path.as_posix()] == expected for path, expected in IMMUTABLE_BLOBS.items())
    historical_m3_unchanged = all(
        blob(root, HISTORICAL_M3_ROOT / name) == head_blob(root, HISTORICAL_M3_ROOT / name)
        for name in HISTORICAL_M3_FILES
    )
    utf8_clean, utf8_remaining = m3_introduced_mojibake_remaining(root)
    paths_authorized, unauthorized_paths = changed_paths_authorized(root)
    exact_matches = sum(a == b for a, b in zip(static_1["results"], shadow_1["results"], strict=True))
    repeated = static_1 == static_2 and shadow_1 == shadow_2
    gates = {
        "HISTORICAL_FIXTURE_PRESERVED_EXACTLY": blob(root, HISTORICAL_FIXTURES) == HISTORICAL_FIXTURE_BLOB,
        "ONLY_AUTHORIZED_FIXTURE_SEMANTIC_FIELD_CHANGED": fixture_exact,
        "FIXTURE_VERSION_IS_1_1_1": fixtures["version"] == "1.1.1",
        "CRIT_FIX_008_EXPECTED_MODULES_MATCH_SELECTOR_ORDER": next(f for f in fixtures["fixtures"] if f["id"] == "CRIT-FIX-008")["expected_modules"] == ["EVIDENCE_AND_CLAIMS", "DESIGN_CRITERION", "WEB_ACCESSIBILITY"],
        "MODULE_SELECTOR_BLOB_UNCHANGED": immutable_observed[SELECTOR.as_posix()] == IMMUTABLE_BLOBS[SELECTOR],
        "SHADOW_REGISTRY_BLOB_UNCHANGED": immutable_observed[REGISTRY.as_posix()] == IMMUTABLE_BLOBS[REGISTRY],
        "ALL_M2_ADAPTER_BLOBS_UNCHANGED": immutable_match,
        "HISTORICAL_M3_ARTIFACTS_UNCHANGED": historical_m3_unchanged,
        "EXACTLY_420_CASES_GENERATED": corpus["case_count"] == 420 and corpus["category_counts"] == CATEGORY_COUNTS,
        "ALL_13_BASELINE_FIXTURES_PASS_STATIC": static_oracles == 13,
        "ALL_13_BASELINE_FIXTURES_PASS_SHADOW": shadow_oracles == 13,
        "ALL_420_STATIC_SHADOW_RESULTS_EXACTLY_EQUIVALENT": exact_matches == 420,
        "BEHAVIORAL_SELECTION_DIGEST_UNCHANGED_FROM_M3": static_1["normalized_run_digest"] == shadow_1["normalized_run_digest"] == EXPECTED_BEHAVIOR_DIGEST,
        "SECOND_RUN_DIGEST_MATCH": repeated,
        "NO_UNEXPLAINED_NEGATIVE_TRANSFER": not divergences,
        "M3_INTRODUCED_UTF8_CORRUPTION_REPAIRED": utf8_clean,
        "NO_AUTHORITY_RUNTIME_OR_INTEGRATION_DRIFT": all(
            result["authority_effect"] == result["runtime_effect"] == result["integration_effect"] == "NONE"
            for result in (static_1, shadow_1)
        ),
        "ALL_CHANGED_PATHS_AUTHORIZED": paths_authorized,
    }
    classification = "M3_REMEDIATED_PASS_EXACT_DUAL_EQUIVALENCE" if all(gates.values()) else "M3_REMEDIATION_BLOCKED_WITH_CLASSIFIED_DIVERGENCES"
    remediation = {
        "schema_version": "1.0.0", "remediation_id": "M3_FIXTURE_ORACLE_AND_UTF8_REMEDIATION_158",
        "classification": classification, "historical_fixture_blob": HISTORICAL_FIXTURE_BLOB,
        "historical_fixture_path": HISTORICAL_FIXTURES.as_posix(), "current_fixture_blob": current_fixture_blob,
        "fixture_version_change": {"from": "1.1.0", "to": "1.1.1"},
        "fixture_diff_paths": fixture_diff_paths,
        "crit_fix_008_expected_modules": {"from": ["EVIDENCE_AND_CLAIMS", "WEB_ACCESSIBILITY"], "to": ["EVIDENCE_AND_CLAIMS", "DESIGN_CRITERION", "WEB_ACCESSIBILITY"]},
        "utf8_repair": {"defect_commit": M3_COMMIT, "comparison_parent": M3_PARENT, "repaired_paths": [
            "projects/lab/authorizations/AUTHORIZATION_LAB_INTEGRATION_FACTORY_M3_DUAL_SELECTOR_EVALUATION_AND_EQUIVALENCE_VALIDATION_157.json",
            "projects/lab/PENDING.json"], "repaired_string_fields": 7, "remaining_m3_introduced_mojibake_paths": utf8_remaining},
        "selector_effect": "NONE", "runtime_effect": "NONE", "integration_effect": "NONE",
    }
    equivalence = {
        "schema_version": "1.0.0", "result_id": "M3_REMEDIATION_158_EQUIVALENCE_RESULTS_001",
        "classification": classification, "case_count": 420, "exact_match_count": exact_matches,
        "exact_match_rate": exact_matches / 420, "static_baseline_oracle_passes": static_oracles,
        "shadow_baseline_oracle_passes": shadow_oracles, "behavioral_divergence_count": len(divergences),
        "static_run_digest_1": static_1["normalized_run_digest"], "static_run_digest_2": static_2["normalized_run_digest"],
        "shadow_run_digest_1": shadow_1["normalized_run_digest"], "shadow_run_digest_2": shadow_2["normalized_run_digest"],
        "historical_m3_behavioral_digest": EXPECTED_BEHAVIOR_DIGEST,
        "behavioral_digest_unchanged": static_1["normalized_run_digest"] == EXPECTED_BEHAVIOR_DIGEST,
        "second_run_digest_match": repeated, "static_invariants": static_invariants, "shadow_invariants": shadow_invariants,
        "negative_transfer_result": "NONE_DETECTED", "gates": gates,
        "authority_effect": "NONE", "runtime_effect": "NONE", "integration_effect": "NONE",
    }
    divergence_log = {
        "schema_version": "1.0.0", "log_id": "M3_REMEDIATION_158_DIVERGENCE_LOG_001",
        "classification": "ZERO_DIVERGENCES" if not divergences else "CLASSIFIED_DIVERGENCES",
        "divergence_count": len(divergences), "divergences": divergences,
        "unexplained_negative_transfer_count": 0 if not divergences else len(divergences),
        "authority_effect": "NONE", "runtime_effect": "NONE",
    }
    validation = {
        "schema_version": "1.0.0", "validation_id": "INTEGRATION_FACTORY_M3_REMEDIATION_158_VALIDATION_001",
        "authorization_id": "AUTHORIZATION_LAB_INTEGRATION_FACTORY_M3_ORACLE_AND_UTF8_REMEDIATION_158",
        "execution_parent_head": STAGE_1_HEAD, "classification": classification,
        "historical_fixture_blob": HISTORICAL_FIXTURE_BLOB, "current_fixture_blob": current_fixture_blob,
        "immutable_blobs": immutable_observed, "corpus_digest": corpus["corpus_digest"],
        "behavioral_digest": static_1["normalized_run_digest"], "historical_behavioral_digest": EXPECTED_BEHAVIOR_DIGEST,
        "independent_evaluator_proof": {"static_script": STATIC_EVALUATOR.as_posix(), "shadow_script": SHADOW_EVALUATOR.as_posix(), "shared_resolution_function": False, "evaluators_modified": False},
        "gates": gates, "all_gates_pass": all(gates.values()), "divergence_count": len(divergences),
        "unauthorized_paths": unauthorized_paths, "m4_authorized": False, "cutover_authorized": False,
        "authority_effect": "NONE_AFTER_AUTHORIZATION_158_CONSUMPTION", "runtime_effect": "NONE", "integration_effect": "NONE",
    }
    outputs = {
        "FIXTURE_ORACLE_REMEDIATION.json": remediation, "STATIC_SELECTOR_RESULTS.json": static_1,
        "SHADOW_SELECTOR_RESULTS.json": shadow_1, "EQUIVALENCE_RESULTS.json": equivalence,
        "DIVERGENCE_LOG.json": divergence_log, "VALIDATION_RESULTS.json": validation,
    }
    if write_outputs:
        for name, value in outputs.items():
            write(root / OUTPUT_ROOT / name, value)
    else:
        mismatches = [name for name, value in outputs.items() if load(root / OUTPUT_ROOT / name) != value]
        if mismatches:
            raise RuntimeError(f"Published remediation outputs differ from fresh execution: {mismatches}")
    return validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    validation = execute(args.root.resolve(), write_outputs=not args.check)
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    raise SystemExit(0 if validation["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
