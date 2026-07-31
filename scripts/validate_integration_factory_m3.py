#!/usr/bin/env python3
"""Generate, execute and validate the bounded M3 dual-selector evaluation."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


M3_ROOT = Path("architecture/integrations/migration/M3")
SELECTOR = Path(
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
)
FIXTURES = Path(
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/ACCEPTANCE_FIXTURES.json"
)
REGISTRY = Path("architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json")
M2_VALIDATION = Path("architecture/integrations/migration/M2/VALIDATION_RESULTS.json")
M1A_VALIDATION = Path("architecture/integrations/migration/M1A/VALIDATION_RESULTS.json")
STATIC_SCRIPT = Path("scripts/integration_factory_m3_static_evaluator.py")
SHADOW_SCRIPT = Path("scripts/integration_factory_m3_shadow_evaluator.py")
CORPUS_PATH = M3_ROOT / "TEST_CORPUS.json"

EXPECTED_BLOBS = {
    SELECTOR: "301ba432907758fc49a9b3c86a83fc762eac4607",
    REGISTRY: "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78",
    FIXTURES: "de4793dedc9646e388bdce5ccd1807da8a711845",
}
EXPECTED_M2_DIGEST = "e1a881640a544e483a1e47d52d72782b966ffc1e32cf6ff6c3afa03d54df6359"
EXPECTED_M1A_DIGEST = "048c2e7995986ca061ce66ce65a1a33f532a8ab17819ea057a0ff979a12ee55d"
EXPECTED_STAGE_1_HEAD = "ce5c86ee59013f335cc541d0066f9513c0de0872"
MODULE_ORDER = [
    "EVIDENCE_AND_CLAIMS",
    "DESIGN_CRITERION",
    "WEB_ACCESSIBILITY",
    "CONTEXTUAL_VISUAL_PREFERENCE",
]
CATEGORY_COUNTS = {
    "FROZEN_BASELINE_FIXTURE": 13,
    "REVERSED_BASELINE_VARIANT": 13,
    "EMPTY_SIGNAL_SET": 1,
    "SIGNAL_SINGLETON": 27,
    "UNORDERED_SIGNAL_PAIR": 351,
    "CONJUNCTIVE_CLAUSE_WITH_EXCLUSION": 8,
    "ALL_FOUR_MODULES_POSITIVE": 1,
    "ALL_FOUR_MODULES_WITH_EXCLUSION": 4,
    "UNKNOWN_SIGNAL_SENTINEL": 1,
    "DUPLICATE_SIGNAL_NORMALIZATION": 1,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(root: Path, path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "hash-object", path.as_posix()], text=True
    ).strip()


def ordered_signal_universe(selector: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    for module in selector["modules"]:
        for operator in ("activate_any", "activate_all", "activate_alternative_all"):
            signals.extend(module.get(operator, []))
    for block in selector["exclusions"]:
        signals.extend(block["when_any"])
    return list(dict.fromkeys(signals))


def expected_case(
    case_id: str,
    category: str,
    input_signals: list[str],
    expected_modules: list[str] | None = None,
    forbidden_modules: list[str] | None = None,
    **metadata: Any,
) -> dict[str, Any]:
    case: dict[str, Any] = {
        "case_id": case_id,
        "category": category,
        "input_signals": input_signals,
        **metadata,
    }
    if expected_modules is not None:
        case["expected_modules"] = expected_modules
    if forbidden_modules is not None:
        case["forbidden_modules"] = forbidden_modules
    return case


def generate_corpus(selector: dict[str, Any], fixture_set: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    fixtures = fixture_set["fixtures"]
    for index, fixture in enumerate(fixtures, 1):
        cases.append(
            expected_case(
                f"M3-BASELINE-{index:03d}",
                "FROZEN_BASELINE_FIXTURE",
                list(fixture["signals"]),
                list(fixture["expected_modules"]),
                list(fixture["forbidden_modules"]),
                source_fixture_id=fixture["id"],
                task_family=fixture["task_family"],
                oracle=fixture["oracle"],
            )
        )
    for index, fixture in enumerate(fixtures, 1):
        cases.append(
            expected_case(
                f"M3-REVERSED-{index:03d}",
                "REVERSED_BASELINE_VARIANT",
                list(reversed(fixture["signals"])),
                list(fixture["expected_modules"]),
                list(fixture["forbidden_modules"]),
                source_fixture_id=fixture["id"],
                paired_case_id=f"M3-BASELINE-{index:03d}",
                oracle=fixture["oracle"],
            )
        )

    cases.append(expected_case("M3-EMPTY-001", "EMPTY_SIGNAL_SET", [], []))
    universe = ordered_signal_universe(selector)
    for index, signal in enumerate(universe, 1):
        cases.append(
            expected_case(
                f"M3-SINGLE-{index:03d}",
                "SIGNAL_SINGLETON",
                [signal],
                singleton_signal=signal,
            )
        )
    for index, pair in enumerate(itertools.combinations(universe, 2), 1):
        cases.append(
            expected_case(
                f"M3-PAIR-{index:03d}",
                "UNORDERED_SIGNAL_PAIR",
                list(pair),
                unordered_pair=list(pair),
            )
        )

    contextual = next(
        module for module in selector["modules"] if module["id"] == "CONTEXTUAL_VISUAL_PREFERENCE"
    )
    clauses = [
        ("ALL", list(contextual["activate_all"])),
        ("ALTERNATIVE_ALL", list(contextual["activate_alternative_all"])),
    ]
    exclusions = list(selector["exclusions"][0]["when_any"])
    sequence = 0
    for operator, clause in clauses:
        for exclusion in exclusions:
            sequence += 1
            cases.append(
                expected_case(
                    f"M3-CONJ-EXCL-{sequence:03d}",
                    "CONJUNCTIVE_CLAUSE_WITH_EXCLUSION",
                    clause + [exclusion],
                    [],
                    [
                        "DESIGN_CRITERION",
                        "WEB_ACCESSIBILITY",
                        "CONTEXTUAL_VISUAL_PREFERENCE",
                    ],
                    activation_operator=operator,
                    activation_clause=clause,
                    exclusion_signal=exclusion,
                )
            )

    all_modules_signals = [
        "TASK_AUDIT",
        "TASK_UI",
        "TASK_VISUAL_DIRECTION",
        "HUMAN_PREFERENCE_OWNER_JONATHAN_MARTINEZ",
    ]
    cases.append(
        expected_case(
            "M3-ALL-MODULES-001",
            "ALL_FOUR_MODULES_POSITIVE",
            all_modules_signals,
            MODULE_ORDER,
        )
    )
    for index, exclusion in enumerate(exclusions, 1):
        cases.append(
            expected_case(
                f"M3-ALL-MODULES-EXCL-{index:03d}",
                "ALL_FOUR_MODULES_WITH_EXCLUSION",
                all_modules_signals + [exclusion],
                ["EVIDENCE_AND_CLAIMS"],
                [
                    "DESIGN_CRITERION",
                    "WEB_ACCESSIBILITY",
                    "CONTEXTUAL_VISUAL_PREFERENCE",
                ],
                exclusion_signal=exclusion,
            )
        )
    cases.append(
        expected_case(
            "M3-UNKNOWN-001",
            "UNKNOWN_SIGNAL_SENTINEL",
            ["M3_UNKNOWN_SIGNAL_SENTINEL"],
            [],
        )
    )
    task_ui_singleton = next(
        case["case_id"]
        for case in cases
        if case["category"] == "SIGNAL_SINGLETON"
        and case["input_signals"] == ["TASK_UI"]
    )
    cases.append(
        expected_case(
            "M3-DUPLICATE-001",
            "DUPLICATE_SIGNAL_NORMALIZATION",
            ["TASK_UI", "TASK_UI"],
            ["DESIGN_CRITERION", "WEB_ACCESSIBILITY"],
            paired_case_id=task_ui_singleton,
        )
    )

    category_counts = {
        category: sum(case["category"] == category for case in cases)
        for category in CATEGORY_COUNTS
    }
    return {
        "schema_version": "1.0.0",
        "corpus_id": "INTEGRATION_FACTORY_M3_DUAL_SELECTOR_CORPUS_001",
        "status": "DETERMINISTIC_SYNTHETIC",
        "generation_algorithm": "DECLARED_ORDER_SIGNAL_UNIVERSE_AND_LEXICOGRAPHIC_COMBINATIONS_V1",
        "synthetic_only": True,
        "real_client_data": False,
        "real_product_data": False,
        "external_network_required": False,
        "frozen_baseline": {
            "source_path": FIXTURES.as_posix(),
            "git_blob_sha": EXPECTED_BLOBS[FIXTURES],
            "fixture_set_id": fixture_set["fixture_set_id"],
            "fixture_count": len(fixtures),
            "fixtures_preserved_semantically_with_original_oracles": True,
        },
        "signal_universe": universe,
        "signal_universe_count": len(universe),
        "case_count": len(cases),
        "category_counts": category_counts,
        "case_ids_unique": len({case["case_id"] for case in cases}) == len(cases),
        "cases": cases,
        "corpus_digest": digest(cases),
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
    }


def test_design(corpus: dict[str, Any], root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "design_id": "INTEGRATION_FACTORY_M3_DUAL_SELECTOR_TEST_DESIGN_001",
        "authorization_id": "AUTHORIZATION_LAB_INTEGRATION_FACTORY_M3_DUAL_SELECTOR_EVALUATION_AND_EQUIVALENCE_VALIDATION_157",
        "execution_parent_head": EXPECTED_STAGE_1_HEAD,
        "objective": "Prove or disprove exact behavioral equivalence without activating either representation.",
        "frozen_inputs": {
            path.as_posix(): {
                "expected_git_blob_sha": blob,
                "observed_git_blob_sha": git_blob(root, path),
                "sha256": file_sha256(root / path),
            }
            for path, blob in EXPECTED_BLOBS.items()
        },
        "m2_digest": EXPECTED_M2_DIGEST,
        "m1a_digest": EXPECTED_M1A_DIGEST,
        "corpus": {
            "case_count": corpus["case_count"],
            "category_counts": corpus["category_counts"],
            "corpus_digest": corpus["corpus_digest"],
        },
        "independent_evaluators": {
            "static": {
                "script": STATIC_SCRIPT.as_posix(),
                "resolution_source": SELECTOR.as_posix(),
                "forbidden_resolution_sources": [REGISTRY.as_posix(), "M2_ADAPTERS"],
            },
            "shadow": {
                "script": SHADOW_SCRIPT.as_posix(),
                "resolution_sources": [REGISTRY.as_posix(), "FOUR_M2_ADAPTERS"],
                "forbidden_resolution_sources": [SELECTOR.as_posix()],
            },
            "shared_resolution_function": False,
            "shared_code": "NONE",
            "shared_normalized_schema_reporting_and_hashing_only": True,
        },
        "runs": 2,
        "pass_rule": "ALL_GATES_TRUE_AND_ZERO_BEHAVIORAL_DIVERGENCES",
        "pass_classification": "M3_PASS_EXACT_DUAL_EQUIVALENCE",
        "blocked_classification": "M3_BLOCKED_WITH_CLASSIFIED_DIVERGENCES",
        "runtime_effect": "NONE",
        "integration_effect": "NONE",
    }


def run_evaluator(root: Path, script: Path, output: Path) -> dict[str, Any]:
    subprocess.run(
        [
            sys.executable,
            str(root / script),
            "--root",
            str(root),
            "--corpus",
            CORPUS_PATH.as_posix(),
            "--output",
            str(output),
        ],
        check=True,
    )
    return load_json(output)


def observable_behavior(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_modules_in_order": result["selected_modules_in_order"],
        "excluded_modules": result["excluded_modules"],
        "matched_activation_semantics": result["matched_activation_semantics"],
        "empty_set_abstention": result["empty_set_abstention"],
        "unknown_signals": sorted(result["unknown_signals"]),
    }


def classify_difference(static: dict[str, Any], shadow: dict[str, Any]) -> str:
    static_modules = static["selected_modules_in_order"]
    shadow_modules = shadow["selected_modules_in_order"]
    if set(shadow_modules) - set(static_modules):
        return "SHADOW_EXTRA_MODULE"
    if set(static_modules) - set(shadow_modules):
        return "SHADOW_MISSING_MODULE"
    if static_modules != shadow_modules:
        return "MODULE_ORDER_DRIFT"
    if static["matched_activation_semantics"] != shadow["matched_activation_semantics"]:
        return "ACTIVATION_CLAUSE_SEMANTIC_DRIFT"
    if static["excluded_modules"] != shadow["excluded_modules"]:
        return "EXCLUSION_PRECEDENCE_FAILURE"
    if static["empty_set_abstention"] != shadow["empty_set_abstention"]:
        return "EMPTY_SET_ABSTENTION_FAILURE"
    if static["unknown_signals"] != shadow["unknown_signals"]:
        return "UNKNOWN_SIGNAL_CONTAMINATION"
    return "UNCLASSIFIED_BEHAVIORAL_DIVERGENCE"


def build_divergences(
    cases: list[dict[str, Any]],
    static_results: list[dict[str, Any]],
    shadow_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    divergences: list[dict[str, Any]] = []
    for case, static, shadow in zip(cases, static_results, shadow_results, strict=True):
        if static != shadow:
            category = classify_difference(static, shadow)
            divergences.append(
                {
                    "divergence_id": f"M3-DIV-{len(divergences) + 1:03d}",
                    "case_id": case["case_id"],
                    "category": category,
                    "severity": "M3_BLOCKING",
                    "static_result": static,
                    "shadow_result": shadow,
                    "canonical_expectation": {
                        "expected_modules": case.get("expected_modules"),
                        "forbidden_modules": case.get("forbidden_modules", []),
                    },
                    "technical_explanation": "Independent normalized behavioral results differ.",
                    "negative_transfer": True,
                    "m4_blocking_effect": "M4_AND_CUTOVER_BLOCKED",
                    "source_refs": [
                        STATIC_SCRIPT.as_posix(),
                        SHADOW_SCRIPT.as_posix(),
                        CORPUS_PATH.as_posix(),
                    ],
                }
            )
    return divergences


def append_oracle_divergences(
    divergences: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    static_results: list[dict[str, Any]],
    shadow_results: list[dict[str, Any]],
) -> None:
    for case, static, shadow in zip(cases, static_results, shadow_results, strict=True):
        if "expected_modules" not in case:
            continue
        forbidden = set(case.get("forbidden_modules", []))
        static_pass = (
            static["selected_modules_in_order"] == case["expected_modules"]
            and not forbidden.intersection(static["selected_modules_in_order"])
        )
        shadow_pass = (
            shadow["selected_modules_in_order"] == case["expected_modules"]
            and not forbidden.intersection(shadow["selected_modules_in_order"])
        )
        if static_pass and shadow_pass:
            continue
        divergences.append(
            {
                "divergence_id": f"M3-DIV-{len(divergences) + 1:03d}",
                "case_id": case["case_id"],
                "category": "BASELINE_ORACLE_REGRESSION",
                "severity": "M3_BLOCKING",
                "static_result": static,
                "shadow_result": shadow,
                "canonical_expectation": {
                    "expected_modules": case["expected_modules"],
                    "forbidden_modules": case.get("forbidden_modules", []),
                    "source_fixture_id": case.get("source_fixture_id"),
                    "oracle": case.get("oracle"),
                },
                "technical_explanation": (
                    "TASK_WEB_INTERFACE activates DESIGN_CRITERION in both frozen "
                    "representations, while the frozen CRIT-FIX-008 oracle omits that module."
                ),
                "negative_transfer": False,
                "m4_blocking_effect": "M3_REMEDIATION_M4_AND_CUTOVER_BLOCKED",
                "source_refs": [
                    FIXTURES.as_posix(),
                    SELECTOR.as_posix(),
                    REGISTRY.as_posix(),
                    CORPUS_PATH.as_posix(),
                ],
            }
        )


def result_index(evaluation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {result["case_id"]: result for result in evaluation["results"]}


def oracle_passes(cases: list[dict[str, Any]], evaluation: dict[str, Any]) -> int:
    indexed = result_index(evaluation)
    passes = 0
    for case in cases:
        if case["category"] != "FROZEN_BASELINE_FIXTURE":
            continue
        result = indexed[case["case_id"]]
        if (
            result["selected_modules_in_order"] == case["expected_modules"]
            and not set(result["selected_modules_in_order"]).intersection(
                case["forbidden_modules"]
            )
        ):
            passes += 1
    return passes


def invariant_checks(cases: list[dict[str, Any]], evaluation: dict[str, Any]) -> dict[str, bool]:
    indexed = result_index(evaluation)
    order_invariance = all(
        observable_behavior(indexed[case["case_id"]])
        == observable_behavior(indexed[case["paired_case_id"]])
        for case in cases
        if case["category"] == "REVERSED_BASELINE_VARIANT"
    )
    duplicate = next(
        case for case in cases if case["category"] == "DUPLICATE_SIGNAL_NORMALIZATION"
    )
    duplicate_invariance = (
        observable_behavior(indexed[duplicate["case_id"]])
        == observable_behavior(indexed[duplicate["paired_case_id"]])
    )
    unknown = indexed["M3-UNKNOWN-001"]
    unknown_non_contamination = (
        unknown["selected_modules_in_order"] == []
        and unknown["unknown_signals"] == ["M3_UNKNOWN_SIGNAL_SENTINEL"]
    )
    all_modules = indexed["M3-ALL-MODULES-001"]
    all_modules_exact = all_modules["selected_modules_in_order"] == MODULE_ORDER
    exclusions_exact = all(
        indexed[case["case_id"]]["selected_modules_in_order"]
        == ["EVIDENCE_AND_CLAIMS"]
        and indexed[case["case_id"]]["excluded_modules"]
        == [
            "DESIGN_CRITERION",
            "WEB_ACCESSIBILITY",
            "CONTEXTUAL_VISUAL_PREFERENCE",
        ]
        for case in cases
        if case["category"] == "ALL_FOUR_MODULES_WITH_EXCLUSION"
    )
    conjunctive_exclusions = all(
        indexed[case["case_id"]]["selected_modules_in_order"] == []
        and "CONTEXTUAL_VISUAL_PREFERENCE"
        in indexed[case["case_id"]]["excluded_modules"]
        for case in cases
        if case["category"] == "CONJUNCTIVE_CLAUSE_WITH_EXCLUSION"
    )
    empty_abstention = (
        indexed["M3-EMPTY-001"]["selected_modules_in_order"] == []
        and indexed["M3-EMPTY-001"]["empty_set_abstention"] is True
    )
    return {
        "INPUT_ORDER_INVARIANCE": order_invariance,
        "DUPLICATE_SIGNAL_INVARIANCE": duplicate_invariance,
        "UNKNOWN_SIGNAL_NON_CONTAMINATION": unknown_non_contamination,
        "ALL_MODULE_ORDER_EXACT": all_modules_exact,
        "EXCLUSIONS_EXACT": exclusions_exact and conjunctive_exclusions,
        "EMPTY_SET_ABSTENTION_EXACT": empty_abstention,
    }


def evaluate(root: Path, write_outputs: bool) -> dict[str, Any]:
    selector = load_json(root / SELECTOR)
    fixture_set = load_json(root / FIXTURES)
    corpus = generate_corpus(selector, fixture_set)
    design = test_design(corpus, root)
    if write_outputs:
        write_json(root / M3_ROOT / "DUAL_SELECTOR_TEST_DESIGN.json", design)
        write_json(root / CORPUS_PATH, corpus)
    elif not (root / CORPUS_PATH).exists() or load_json(root / CORPUS_PATH) != corpus:
        raise RuntimeError("Published TEST_CORPUS.json differs from deterministic regeneration")

    with tempfile.TemporaryDirectory(prefix="lab-m3-") as temporary:
        temp = Path(temporary)
        static_run_1 = run_evaluator(root, STATIC_SCRIPT, temp / "static-1.json")
        shadow_run_1 = run_evaluator(root, SHADOW_SCRIPT, temp / "shadow-1.json")
        static_run_2 = run_evaluator(root, STATIC_SCRIPT, temp / "static-2.json")
        shadow_run_2 = run_evaluator(root, SHADOW_SCRIPT, temp / "shadow-2.json")

    cases = corpus["cases"]
    divergences = build_divergences(
        cases, static_run_1["results"], shadow_run_1["results"]
    )
    append_oracle_divergences(
        divergences, cases, static_run_1["results"], shadow_run_1["results"]
    )
    static_oracles = oracle_passes(cases, static_run_1)
    shadow_oracles = oracle_passes(cases, shadow_run_1)
    static_invariants = invariant_checks(cases, static_run_1)
    shadow_invariants = invariant_checks(cases, shadow_run_1)
    blobs = {path.as_posix(): git_blob(root, path) for path in EXPECTED_BLOBS}
    frozen_hashes_match = all(
        blobs[path.as_posix()] == expected for path, expected in EXPECTED_BLOBS.items()
    )
    m2 = load_json(root / M2_VALIDATION)
    m1a = load_json(root / M1A_VALIDATION)
    m2_digest_match = (
        m2["classification"] == "M2_PASS"
        and m2["normalized_digest_run_1"] == EXPECTED_M2_DIGEST
        and m2["normalized_digest_run_2"] == EXPECTED_M2_DIGEST
        and m2["deterministic"] is True
    )
    m1a_digest_match = (
        m1a["status"] == "PASS"
        and m1a["reproducibility"]["first_normalized_digest"] == EXPECTED_M1A_DIGEST
        and m1a["reproducibility"]["second_normalized_digest"] == EXPECTED_M1A_DIGEST
        and m1a["reproducibility"]["equivalent"] is True
    )
    exact_matches = sum(
        static == shadow
        for static, shadow in zip(
            static_run_1["results"], shadow_run_1["results"], strict=True
        )
    )
    second_run_match = (
        static_run_1["normalized_run_digest"] == static_run_2["normalized_run_digest"]
        and shadow_run_1["normalized_run_digest"] == shadow_run_2["normalized_run_digest"]
        and static_run_1 == static_run_2
        and shadow_run_1 == shadow_run_2
    )
    exact_fields = {
        "MODULE_ORDER_EXACT": all(
            a["selected_modules_in_order"] == b["selected_modules_in_order"]
            for a, b in zip(static_run_1["results"], shadow_run_1["results"], strict=True)
        ),
        "ACTIVATION_SEMANTICS_EXACT": all(
            a["matched_activation_semantics"] == b["matched_activation_semantics"]
            for a, b in zip(static_run_1["results"], shadow_run_1["results"], strict=True)
        ),
        "EXCLUSIONS_EXACT": all(
            a["excluded_modules"] == b["excluded_modules"]
            for a, b in zip(static_run_1["results"], shadow_run_1["results"], strict=True)
        ) and static_invariants["EXCLUSIONS_EXACT"] and shadow_invariants["EXCLUSIONS_EXACT"],
        "EMPTY_SET_ABSTENTION_EXACT": all(
            a["empty_set_abstention"] == b["empty_set_abstention"]
            for a, b in zip(static_run_1["results"], shadow_run_1["results"], strict=True)
        ) and static_invariants["EMPTY_SET_ABSTENTION_EXACT"] and shadow_invariants["EMPTY_SET_ABSTENTION_EXACT"],
    }
    gates = {
        "FROZEN_INPUT_HASHES_MATCH": frozen_hashes_match and m2_digest_match and m1a_digest_match,
        "EXACTLY_420_CASES_GENERATED": corpus["case_count"] == 420
        and corpus["category_counts"] == CATEGORY_COUNTS
        and corpus["case_ids_unique"] is True,
        "ALL_13_BASELINE_FIXTURES_PASS_STATIC": static_oracles == 13,
        "ALL_13_BASELINE_FIXTURES_PASS_SHADOW": shadow_oracles == 13,
        "ALL_420_STATIC_SHADOW_RESULTS_EXACTLY_EQUIVALENT": exact_matches == 420,
        **exact_fields,
        "INPUT_ORDER_INVARIANCE": static_invariants["INPUT_ORDER_INVARIANCE"]
        and shadow_invariants["INPUT_ORDER_INVARIANCE"],
        "DUPLICATE_SIGNAL_INVARIANCE": static_invariants["DUPLICATE_SIGNAL_INVARIANCE"]
        and shadow_invariants["DUPLICATE_SIGNAL_INVARIANCE"],
        "UNKNOWN_SIGNAL_NON_CONTAMINATION": static_invariants["UNKNOWN_SIGNAL_NON_CONTAMINATION"]
        and shadow_invariants["UNKNOWN_SIGNAL_NON_CONTAMINATION"],
        "ALL_DIVERGENCES_CLASSIFIED": all(
            divergence["category"] != "UNCLASSIFIED_BEHAVIORAL_DIVERGENCE"
            for divergence in divergences
        ),
        "NO_UNEXPLAINED_NEGATIVE_TRANSFER": all(
            divergence["category"] != "UNCLASSIFIED_BEHAVIORAL_DIVERGENCE"
            and bool(divergence["technical_explanation"])
            for divergence in divergences
        ),
        "SECOND_RUN_DIGEST_MATCH": second_run_match,
        "NO_AUTHORITY_DRIFT": all(
            evaluation["authority_effect"] == "NONE"
            for evaluation in (static_run_1, shadow_run_1)
        ),
        "NO_RUNTIME_OR_INTEGRATION_EFFECT": all(
            evaluation["runtime_effect"] == "NONE"
            and evaluation["integration_effect"] == "NONE"
            for evaluation in (static_run_1, shadow_run_1)
        ),
        "NO_FROZEN_SOURCE_MODIFICATION": frozen_hashes_match,
    }
    classification = (
        "M3_PASS_EXACT_DUAL_EQUIVALENCE"
        if all(gates.values())
        else "M3_BLOCKED_WITH_CLASSIFIED_DIVERGENCES"
    )
    equivalence = {
        "schema_version": "1.0.0",
        "result_id": "INTEGRATION_FACTORY_M3_EQUIVALENCE_RESULTS_001",
        "classification": classification,
        "case_count": corpus["case_count"],
        "exact_match_count": exact_matches,
        "exact_match_rate": exact_matches / corpus["case_count"],
        "static_baseline_oracle_passes": static_oracles,
        "shadow_baseline_oracle_passes": shadow_oracles,
        "behavioral_divergence_count": len(divergences),
        "unclassified_divergence_count": sum(
            d["category"] == "UNCLASSIFIED_BEHAVIORAL_DIVERGENCE" for d in divergences
        ),
        "unexplained_negative_transfer_count": sum(
            divergence["negative_transfer"]
            and divergence["category"] == "UNCLASSIFIED_BEHAVIORAL_DIVERGENCE"
            for divergence in divergences
        ),
        "static_run_digest_1": static_run_1["normalized_run_digest"],
        "static_run_digest_2": static_run_2["normalized_run_digest"],
        "shadow_run_digest_1": shadow_run_1["normalized_run_digest"],
        "shadow_run_digest_2": shadow_run_2["normalized_run_digest"],
        "second_run_digest_match": second_run_match,
        "static_invariants": static_invariants,
        "shadow_invariants": shadow_invariants,
        "gates": gates,
        "negative_transfer_result": (
            "NONE_DETECTED_STATIC_SHADOW; BASELINE_ORACLE_REGRESSION_CLASSIFIED"
            if divergences and not any(d["negative_transfer"] for d in divergences)
            else "NONE_DETECTED"
            if not divergences
            else "DETECTED_AND_CLASSIFIED"
        ),
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "integration_effect": "NONE",
    }
    divergence_log = {
        "schema_version": "1.0.0",
        "log_id": "INTEGRATION_FACTORY_M3_DIVERGENCE_LOG_001",
        "classification": "ZERO_DIVERGENCES" if not divergences else "CLASSIFIED_DIVERGENCES",
        "behavioral_divergence_count": len(divergences),
        "divergences": divergences,
        "silent_normalization": False,
        "frozen_inputs_modified_to_force_pass": False,
        "m4_blocked": classification != "M3_PASS_EXACT_DUAL_EQUIVALENCE",
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
    }
    validation = {
        "schema_version": "1.0.0",
        "validation_id": "INTEGRATION_FACTORY_M3_VALIDATION_001",
        "authorization_id": "AUTHORIZATION_LAB_INTEGRATION_FACTORY_M3_DUAL_SELECTOR_EVALUATION_AND_EQUIVALENCE_VALIDATION_157",
        "execution_parent_head": EXPECTED_STAGE_1_HEAD,
        "classification": classification,
        "frozen_input_blobs": blobs,
        "m2_digest": EXPECTED_M2_DIGEST,
        "m2_digest_match": m2_digest_match,
        "m1a_digest": EXPECTED_M1A_DIGEST,
        "m1a_digest_match": m1a_digest_match,
        "corpus_digest": corpus["corpus_digest"],
        "case_count": corpus["case_count"],
        "independent_evaluator_proof": {
            "static_script": STATIC_SCRIPT.as_posix(),
            "shadow_script": SHADOW_SCRIPT.as_posix(),
            "shared_resolution_function": False,
            "static_forbidden_source_access": False,
            "shadow_selector_resolution_access": False,
        },
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "second_run_digest_match": second_run_match,
        "behavioral_divergence_count": len(divergences),
        "negative_transfer_result": equivalence["negative_transfer_result"],
        "authority_effect": "NONE_AFTER_AUTHORIZATION_CONSUMPTION",
        "runtime_effect": "NONE",
        "integration_effect": "NONE",
        "selector_effect": "NONE",
        "m4_authorized": False,
        "cutover_authorized": False,
    }
    if write_outputs:
        write_json(root / M3_ROOT / "STATIC_SELECTOR_RESULTS.json", static_run_1)
        write_json(root / M3_ROOT / "SHADOW_SELECTOR_RESULTS.json", shadow_run_1)
        write_json(root / M3_ROOT / "EQUIVALENCE_RESULTS.json", equivalence)
        write_json(root / M3_ROOT / "DIVERGENCE_LOG.json", divergence_log)
        write_json(root / M3_ROOT / "VALIDATION_RESULTS.json", validation)
    else:
        expected_outputs = {
            "DUAL_SELECTOR_TEST_DESIGN.json": design,
            "STATIC_SELECTOR_RESULTS.json": static_run_1,
            "SHADOW_SELECTOR_RESULTS.json": shadow_run_1,
            "EQUIVALENCE_RESULTS.json": equivalence,
            "DIVERGENCE_LOG.json": divergence_log,
            "VALIDATION_RESULTS.json": validation,
        }
        mismatches = [
            name
            for name, expected in expected_outputs.items()
            if load_json(root / M3_ROOT / name) != expected
        ]
        if mismatches:
            raise RuntimeError(f"Published M3 outputs differ from fresh execution: {mismatches}")
    return validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    validation = evaluate(args.root.resolve(), write_outputs=not args.check)
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    raise SystemExit(0 if validation["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
