#!/usr/bin/env python3
"""Scoped, dependency-free validator for Product Leadership redesign 191.

The validator intentionally reads only the authorized LAB repository and the
Product Leadership records placed in scope by authorization 191. It never
invokes a model or executes a test arm.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARENT = "2e2f97449c9734512ddd0dfe3a3f308c037a8e8c"
AUTH_ID = "AUTHORIZATION_LAB_PRODUCT_LEADERSHIP_TEST003_INSTRUMENT_REDESIGN_191"
CLAIM_BOUNDARY = "INSTRUMENT_REDESIGN_COMPLETE_AWAITING_SEPARATE_FRESH_RETEST_AUTHORIZATION"
EXECUTION_ROOT = "projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-004"
DESIGN_REL = "projects/lab/test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/INSTRUMENT_REDESIGN_191"
DESIGN = ROOT / DESIGN_REL
AUTH_REL = "projects/lab/authorizations/AUTHORIZATION_LAB_PRODUCT_LEADERSHIP_TEST003_INSTRUMENT_REDESIGN_191.json"
BRIEF_REL = "projects/lab/briefs/CODEX_PRODUCT_LEADERSHIP_TEST003_INSTRUMENT_REDESIGN_191_001.json"

ARTIFACTS = [
    "MANIFEST.json",
    "ARM_SYMMETRY_CONTRACT.json",
    "SCORER_ISOLATION_CONTRACT.json",
    "NEGATIVE_CONTROL_CONTRACT.json",
    "FIXTURE_ORACLE_TRACEABILITY.json",
    "INSUFFICIENT_EVIDENCE_CONTRACT.json",
    "STOP_CONDITIONS.json",
    "SCORING_CALIBRATION.json",
    "CHAIN_OF_CUSTODY_CONTRACT.json",
    "FRESH_RETEST_GATES_AND_CLAIM_LIMITS.json",
    "STATIC_CALIBRATION_FIXTURES.json",
    "VALIDATION_RESULTS.json",
]

REQUIRED_BY_ARTIFACT = {
    "INSTRUMENT_REDESIGN_MANIFEST": ["purpose", "scope", "historical_execution", "defect_inventory", "artifact_inventory", "validation_commands", "claim_limits", "model_activity"],
    "ARM_SYMMETRY_CONTRACT": ["canonical_arm_envelope", "arms", "comparisons", "forbidden_asymmetries", "normalization_algorithm", "validator_expectations"],
    "SCORER_ISOLATION_CONTRACT": ["allowed_top_level_fields", "forbidden_fields_recursive", "redaction_rules", "forbidden_value_patterns_case_insensitive", "failure_semantics"],
    "NEGATIVE_CONTROL_CONTRACT": ["architecture", "model_cooperation_required", "controls", "non_refusability_rationale", "validation_rules"],
    "FIXTURE_ORACLE_TRACEABILITY": ["required_input_fields", "fixtures", "coverage"],
    "INSUFFICIENT_EVIDENCE_CONTRACT": ["outcomes", "precedence", "triggers", "propagation_rules", "aggregation_prohibition", "reporting", "recovery_boundary"],
    "STOP_CONDITIONS": ["conditions", "required_stage_coverage", "default_behavior"],
    "SCORING_CALIBRATION": ["rubric_version", "dimensions", "boolean_flags", "individual_score_formula", "aggregation_formula", "thresholds", "boundary_behavior", "calibration_result"],
    "CHAIN_OF_CUSTODY_CONTRACT": ["runner_source_provenance", "frozen_component_categories", "hash_algorithm", "pre_run_verification", "artifact_linkage", "append_only_rules", "custody_failure_behavior"],
    "FRESH_RETEST_GATES_AND_CLAIM_LIMITS": ["preconditions", "execution_gates", "adjudication_gates", "allowed_claims", "forbidden_claims", "separate_authorization_requirements", "current_authority"],
    "STATIC_CALIBRATION_FIXTURES": ["neutrality", "arm_symmetry_cases", "scorer_isolation_cases", "score_vectors", "rubric_calibration_cases", "outcome_propagation_cases"],
    "VALIDATION_RESULTS": ["commands", "timestamps", "tested_contracts", "fixture_counts", "positive_cases", "negative_cases", "historical_hash_verification", "model_activity_verification", "overall_result"],
}

DIMENSIONS = [
    "problem_outcome_clarity", "strategic_choices", "prioritization_order",
    "cost_of_opportunity_recognition", "authorization_proportionality",
    "reversibility_stop_rules", "framework_relevance",
    "evidence_authority_discipline", "uncertainty_calibration",
    "closed_scope_preservation", "actionability", "process_efficiency",
]
BOOLEAN_FLAGS = [
    "authority_confusion", "fabricated_evidence", "closed_scope_reopening",
    "unnecessary_documentation",
]
REQUIRED_INPUTS = [
    "TASK_OBJECTIVE", "TASK_STATE", "AUTHORITY_STATE", "BINDING_OBLIGATIONS",
    "AVAILABLE_EVIDENCE", "PRODUCT_DECISION_SCOPE", "REQUESTED_OUTPUT",
]

FAILURES: list[str] = []
PASSES: list[str] = []


def fail(message: str) -> None:
    FAILURES.append(message)


def passed(message: str) -> None:
    PASSES.append(message)


def duplicate_guard(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    counts = Counter(key for key, _value in pairs)
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError("duplicate JSON keys: " + ", ".join(duplicates))
    return dict(pairs)


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=duplicate_guard)
    except Exception as exc:  # noqa: BLE001 - report every deterministic parse failure
        fail(f"{relative}: {exc}")
        return {}


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.check_output(["git", *args], cwd=ROOT)
    return result if binary else result.decode("utf-8").strip()


def changed_paths() -> set[str]:
    tracked = set(filter(None, str(git("diff", "--name-only", EXPECTED_PARENT, "--")).splitlines()))
    untracked = set(filter(None, str(git("ls-files", "--others", "--exclude-standard")).splitlines()))
    return {path.replace("\\", "/") for path in tracked | untracked}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def delete_path(value: dict[str, Any], dotted: str) -> None:
    parts = dotted.split(".")
    cursor: Any = value
    for part in parts[:-1]:
        if not isinstance(cursor, dict) or part not in cursor:
            return
        cursor = cursor[part]
    if isinstance(cursor, dict):
        cursor.pop(parts[-1], None)


def normalized_arm(value: dict[str, Any], allowed: list[str]) -> str:
    result = deepcopy(value)
    for path in allowed:
        delete_path(result, path)
    return json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def classify_outcome(case: dict[str, Any]) -> str:
    if case.get("integrity_triggers"):
        return "INSUFFICIENT_EVIDENCE"
    if case.get("controls_pass") is not True:
        return "INSUFFICIENT_EVIDENCE"
    if case.get("rubric_calibrated") is not True:
        return "INSUFFICIENT_EVIDENCE"
    if case.get("comparable") is not True:
        return "INSUFFICIENT_EVIDENCE"
    return (
        "PASS_CANDIDATE_FOR_SEPARATE_INTEGRATION_DECISION"
        if all(case.get("substantive_gates", []))
        else "FAIL_REVISE_OR_REJECT"
    )


def historical_blob_manifest() -> dict[str, Any]:
    raw = git("ls-tree", "-r", "-z", EXPECTED_PARENT, EXECUTION_ROOT, binary=True)
    assert isinstance(raw, bytes)
    rows: list[tuple[str, str, int]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, path_bytes = record.split(b"\t", 1)
        _mode, _kind, oid = meta.split(b" ")
        blob = git("cat-file", "blob", oid.decode("ascii"), binary=True)
        assert isinstance(blob, bytes)
        rows.append((path_bytes.decode("utf-8"), hashlib.sha256(blob).hexdigest(), len(blob)))
    rows.sort()
    payload = "".join(f"{path}\t{digest}\n" for path, digest, _size in rows).encode("utf-8")
    return {
        "file_count": len(rows),
        "total_bytes": sum(size for _path, _digest, size in rows),
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
        "git_tree": str(git("rev-parse", f"{EXPECTED_PARENT}:{EXECUTION_ROOT}")),
    }


def validate_authority_and_scope(paths: set[str]) -> None:
    auth = load_json(AUTH_REL)
    brief = load_json(BRIEF_REL)
    if auth.get("authorization_id") != AUTH_ID or auth.get("status") not in {"GRANTED", "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"}:
        fail("authorization 191 is not the exact granted/consumed record")
    if auth.get("approved_by") != "Jonathan Martínez" or auth.get("grant_inferred") is not False:
        fail("authorization 191 approval identity or inference boundary invalid")
    permissions = auth.get("execution_permissions", {})
    for key in ["model_requests_authorized", "retest_authorized", "regeneration_authorized", "rescoring_authorized", "package_change_authorized", "integration_authorized", "runtime_authorized", "product_changes_authorized"]:
        if permissions.get(key) is not False:
            fail(f"authorization permission must remain false: {key}")
    if brief.get("brief_id") != brief.get("task_id") or brief.get("status") not in {
        "READY",
        "EXECUTED_STATIC_VALIDATION_PASS_PUBLICATION_PENDING",
        "CONSUMED",
    }:
        fail("brief identity or lifecycle invalid")
    for key in ["repositories", "authority", "scope", "required_outputs", "acceptance_checks", "stop_conditions", "response_contract"]:
        if key not in brief:
            fail(f"brief missing generic schema field: {key}")
    registry_index = load_json(ROOT / "registry/index.json")
    delta_ref = "registry/deltas/product-leadership-test003-instrument-redesign-191.json"
    for registry_key in ["authorization_deltas", "evidence_deltas", "current_state_deltas", "test_design_deltas"]:
        if registry_index.get("registries", {}).get(registry_key, []).count(delta_ref) != 1:
            fail(f"redesign delta must appear exactly once in {registry_key}")
    if delta_ref in registry_index.get("registries", {}).get("error_deltas", []):
        fail("redesign delta must not be indexed as an error delta")
    prohibited_exact = {
        "projects/lab/integrations/INT-LAB-004.json",
        "projects/lab/reassessments/REA-LAB-010.json",
        "projects/lab/reconciliations/REC-LAB-PL003-EXEC004-AUDIT190-001.json",
        "projects/lab/evidence/EVD-LAB-AUD-008.json",
    }
    prohibited_prefixes = [
        EXECUTION_ROOT + "/",
        "projects/lab/external-audits/AUDIT-CLAUDE-PRODUCT-LEADERSHIP-EXECUTION-004-PHASE3-001/",
        "foundation-library/product-leadership/PRODUCT-LEADERSHIP-CANDIDATE-PACKAGE-001/",
    ]
    violations = sorted(path for path in paths if path in prohibited_exact or any(path.startswith(prefix) for prefix in prohibited_prefixes))
    if violations:
        fail("forbidden historical/package/integration mutation: " + ", ".join(violations))
    else:
        passed("authorized scope and immutable boundaries")


def validate_schema_and_references() -> dict[str, dict[str, Any]]:
    schema = load_json("schemas/product-leadership-instrument-redesign.schema.json")
    core_required = schema.get("required", [])
    artifacts: dict[str, dict[str, Any]] = {}
    for name in ARTIFACTS:
        relative = f"{DESIGN_REL}/{name}"
        if not (ROOT / relative).is_file():
            fail(f"missing required artifact: {relative}")
            continue
        doc = load_json(relative)
        artifacts[name] = doc
        for key in core_required:
            if key not in doc:
                fail(f"{name}: missing schema key {key}")
        if doc.get("redesign_id") != "INSTRUMENT_REDESIGN_191" or doc.get("authorization_ref") != AUTH_ID:
            fail(f"{name}: identity mismatch")
        if doc.get("claim_boundary") != CLAIM_BOUNDARY:
            fail(f"{name}: claim boundary exceeds or differs from authorized maximum")
        historical = doc.get("historical_execution", {})
        if historical.get("mutation_allowed") is not False or historical.get("attempt") != "ATTEMPT-003":
            fail(f"{name}: historical immutability boundary missing")
        for key in REQUIRED_BY_ARTIFACT.get(doc.get("artifact_type", ""), []):
            if key not in doc:
                fail(f"{name}: missing artifact-specific key {key}")
    manifest = artifacts.get("MANIFEST.json", {})
    if sorted(manifest.get("artifact_inventory", [])) != sorted([*ARTIFACTS, "INSTRUMENT_CORE.mjs"]):
        fail("manifest artifact inventory mismatch")
    if not (DESIGN / "INSTRUMENT_CORE.mjs").is_file():
        fail("canonical deterministic instrument core missing")
    passed("scoped JSON, duplicate keys, schema keys and artifact references")
    return artifacts


def validate_historical_immutability(manifest: dict[str, Any], paths: set[str]) -> None:
    actual = historical_blob_manifest()
    baseline = manifest.get("historical_execution", {})
    expected = {
        "file_count": baseline.get("file_count"),
        "total_bytes": baseline.get("total_bytes"),
        "manifest_sha256": baseline.get("sorted_path_sha256_manifest_digest"),
        "git_tree": baseline.get("git_tree_sha1"),
    }
    if actual != expected:
        fail(f"historical baseline mismatch: expected={expected} actual={actual}")
    if any(path == EXECUTION_ROOT or path.startswith(EXECUTION_ROOT + "/") for path in paths):
        fail("Execution 004 working change detected")
    else:
        passed("Execution 004 / ATTEMPT-003 150-file SHA-256 baseline preserved")


def validate_contracts(artifacts: dict[str, dict[str, Any]]) -> None:
    manifest = artifacts["MANIFEST.json"]
    defects = manifest.get("defect_inventory", [])
    if len(defects) != 8 or len({item.get("domain") for item in defects}) != 8:
        fail("eight PEND-LAB-048 defect domains are not one-to-one traceable")

    symmetry = artifacts["ARM_SYMMETRY_CONTRACT.json"]
    comparisons = symmetry.get("comparisons", [])
    if len(symmetry.get("arms", [])) != 4 or len(comparisons) != 2:
        fail("four-arm or comparison contract incomplete")

    static = artifacts["STATIC_CALIBRATION_FIXTURES.json"]
    for case in static.get("arm_symmetry_cases", []):
        arms = [deep_merge(case["base_envelope"], override) for override in case["arm_overrides"].values()]
        normalized = [normalized_arm(arm, case["allowed_delta_paths"]) for arm in arms]
        symmetric = len(set(normalized)) == 1
        if (case["expected"] == "PASS") != symmetric:
            fail(f"arm symmetry oracle mismatch: {case['case_id']}")

    scorer = artifacts["SCORER_ISOLATION_CONTRACT.json"]
    forbidden_fields = {name.casefold() for name in scorer.get("forbidden_fields_recursive", [])}
    patterns = [re.compile(pattern, re.IGNORECASE) for pattern in scorer.get("forbidden_value_patterns_case_insensitive", [])]

    def leaks(value: Any) -> bool:
        if isinstance(value, dict):
            return any(str(key).casefold() in forbidden_fields or leaks(child) for key, child in value.items())
        if isinstance(value, list):
            return any(leaks(child) for child in value)
        return isinstance(value, str) and any(pattern.search(value) for pattern in patterns)

    for case in static.get("scorer_isolation_cases", []):
        leaked = leaks(case["payload"])
        if (case["expected"] == "PASS") == leaked:
            fail(f"scorer isolation oracle mismatch: {case['case_id']}")

    negative = artifacts["NEGATIVE_CONTROL_CONTRACT.json"]
    controls = negative.get("controls", [])
    if negative.get("model_cooperation_required") is not False or len(controls) != 4:
        fail("negative controls are not four fixed non-model artifacts")
    if len({item.get("detected_failure_mode") for item in controls}) != len(controls):
        fail("negative controls do not map to unique primary failure modes")
    for item in controls:
        if not isinstance(item.get("fixed_candidate_output"), dict) or not item.get("required_boolean_flag"):
            fail(f"negative control incomplete: {item.get('control_id')}")

    trace = artifacts["FIXTURE_ORACLE_TRACEABILITY.json"]
    fixtures = trace.get("fixtures", [])
    if trace.get("coverage", {}).get("unmapped_fixture_count") != 0 or trace.get("coverage", {}).get("fixture_count") != len(fixtures):
        fail("fixture traceability coverage mismatch")
    for fixture in fixtures:
        if set(fixture.get("context", {})) != set(REQUIRED_INPUTS):
            fail(f"fixture input contract mismatch: {fixture.get('fixture_id')}")
        for key in ["tested_capability_claim", "permitted_outputs", "prohibited_outputs", "oracle", "scoring_dimensions", "invalidating_conditions", "stop_condition", "permitted_adjudication"]:
            if not fixture.get(key):
                fail(f"fixture {fixture.get('fixture_id')} missing {key}")

    insufficient = artifacts["INSUFFICIENT_EVIDENCE_CONTRACT.json"]
    prohibited = insufficient.get("aggregation_prohibition", {})
    if any(value is not False for value in prohibited.values()):
        fail("INSUFFICIENT_EVIDENCE coercion prohibition incomplete")
    for case in static.get("outcome_propagation_cases", []):
        if classify_outcome(case) != case.get("expected"):
            fail(f"outcome propagation oracle mismatch: {case.get('case_id')}")

    stops = artifacts["STOP_CONDITIONS.json"]
    covered = {item.get("stage") for item in stops.get("conditions", [])}
    if covered != set(stops.get("required_stage_coverage", [])) or stops.get("default_behavior") != "FAIL_CLOSED":
        fail("stop-condition stage coverage incomplete")
    if any(item.get("outcome") != "INSUFFICIENT_EVIDENCE" or not item.get("machine_reason") for item in stops.get("conditions", [])):
        fail("stop condition lacks exact outcome or reason")

    scoring = artifacts["SCORING_CALIBRATION.json"]
    if [item.get("id") for item in scoring.get("dimensions", [])] != DIMENSIONS or scoring.get("boolean_flags") != BOOLEAN_FLAGS:
        fail("exact 12-dimension and 4-boolean rubric mismatch")
    vectors = static.get("score_vectors", {})
    for name, vector in vectors.items():
        if set(vector) != set(DIMENSIONS) or any(not isinstance(value, int) or value < 0 or value > 4 for value in vector.values()):
            fail(f"invalid score vector: {name}")
    required_case_types = {"CLEAR_PASS", "CLEAR_FAIL", "BOUNDARY", "AMBIGUOUS", "CONTRADICTORY", "MISSING", "MALFORMED", "REFUSAL", "SCORER_LEAKAGE", "INVALID_CONTROL", "PARTIAL_EXECUTION"}
    cases = static.get("rubric_calibration_cases", [])
    if {case.get("case_type") for case in cases} != required_case_types:
        fail("static rubric case-type coverage incomplete")
    for case in cases:
        vector_name = case.get("score_vector")
        if vector_name:
            vector = vectors[vector_name]
            raw = sum(vector.values())
            if raw != case.get("expected_raw") or raw / 2 != case.get("expected_normalized"):
                fail(f"calibration arithmetic mismatch: {case.get('case_id')}")
            flags = case.get("boolean_flags", {})
            if set(flags) != set(BOOLEAN_FLAGS) or any(not isinstance(value, bool) for value in flags.values()):
                fail(f"calibration boolean schema mismatch: {case.get('case_id')}")
        elif case.get("expected_outcome") != "INSUFFICIENT_EVIDENCE" or not case.get("triggers"):
            fail(f"non-scorable case not first-class insufficient evidence: {case.get('case_id')}")

    custody = artifacts["CHAIN_OF_CUSTODY_CONTRACT.json"]
    categories = {item.get("category") for item in custody.get("frozen_component_categories", [])}
    required_categories = {"RUNNER_AND_INSTRUMENT_SOURCE", "PROMPT_TEMPLATES", "CONTRACTS", "FIXTURES_AND_ORACLES", "SCHEMAS", "CONFIGURATION", "DEPENDENCY_LOCK_STATE", "ENVIRONMENT_DECLARATION", "GENERATED_REQUEST_MANIFESTS"}
    if categories != required_categories or custody.get("hash_algorithm") != "SHA-256_RAW_BYTES_NO_LINE_ENDING_NORMALIZATION":
        fail("chain-of-custody component or hash contract incomplete")
    if custody.get("custody_failure_behavior", {}).get("outcome") != "INSUFFICIENT_EVIDENCE":
        fail("custody failure does not fail closed")

    fresh = artifacts["FRESH_RETEST_GATES_AND_CLAIM_LIMITS.json"]
    if any(fresh.get("current_authority", {}).values()):
        fail("fresh retest contract grants unauthorized current authority")
    if not all(fresh.get("separate_authorization_requirements", {}).values()):
        fail("separate future authorization boundary incomplete")

    if any(manifest.get("model_activity", {}).values()):
        fail("manifest records prohibited model or retest activity")
    else:
        passed("eight enforceable defect domains, static fixtures and zero model activity")


def main() -> int:
    try:
        current_head = str(git("rev-parse", "HEAD"))
        merge_base = str(git("merge-base", "HEAD", EXPECTED_PARENT))
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: Git preflight failed: {exc}")
        return 1
    if merge_base != EXPECTED_PARENT:
        fail(f"branch is not based on authorized parent: HEAD={current_head} merge_base={merge_base}")
    paths = changed_paths()
    validate_authority_and_scope(paths)
    artifacts = validate_schema_and_references()
    if "MANIFEST.json" in artifacts:
        validate_historical_immutability(artifacts["MANIFEST.json"], paths)
    required_for_contracts = set(ARTIFACTS)
    if required_for_contracts.issubset(artifacts):
        validate_contracts(artifacts)
    if FAILURES:
        for message in FAILURES:
            print("FAIL:", message)
        print(f"Product Leadership instrument redesign 191 validation: FAIL ({len(FAILURES)} failure(s))")
        return 1
    for message in PASSES:
        print("PASS:", message)
    print("Product Leadership instrument redesign 191 validation: PASS")
    print(f"Changed files inspected: {len(paths)}")
    print("Model requests: 0; retests: 0; replays: 0; regenerations: 0; rescoring: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
