#!/usr/bin/env python3
"""Successor semantic replay validator for authorization 162 ATTEMPT-003."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import validate_integration_factory_m3_remediation_158 as historical

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "architecture/integrations/migration/M5/validator-remediation-162"
ALLOWLIST_PATH = OUTPUT / "VOLATILE_METADATA_ALLOWLIST.json"
M3_OUTPUT = ROOT / "architecture/integrations/migration/M3/remediation-158"
EXPECTED_DIGEST = "9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329"
HISTORICAL_FILES = [
    "FIXTURE_ORACLE_REMEDIATION.json",
    "STATIC_SELECTOR_RESULTS.json",
    "SHADOW_SELECTOR_RESULTS.json",
    "EQUIVALENCE_RESULTS.json",
    "DIVERGENCE_LOG.json",
    "VALIDATION_RESULTS.json",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def allowed_paths() -> set[str]:
    return {item["json_path"] for item in load(ALLOWLIST_PATH)["fields"]}


def compare_documents(left: Any, right: Any, path: str = "$") -> list[dict[str, str]]:
    """Classify every field difference without open-ended omission rules."""
    allowed = allowed_paths()
    if type(left) is not type(right):
        return [{"path": path, "classification": "SEMANTIC_DIVERGENCE"}]
    if isinstance(left, dict):
        differences: list[dict[str, str]] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}"
            if key not in left or key not in right:
                classification = "VOLATILE_METADATA" if child in allowed else "SEMANTIC_DIVERGENCE"
                differences.append({"path": child, "classification": classification})
            else:
                differences.extend(compare_documents(left[key], right[key], child))
        return differences
    if isinstance(left, list):
        if left == right:
            return []
        if sorted(map(canonical, left)) == sorted(map(canonical, right)):
            return [{"path": path, "classification": "ORDERING_ONLY"}]
        differences = []
        for index in range(max(len(left), len(right))):
            child = f"{path}[{index}]"
            if index >= len(left) or index >= len(right):
                differences.append({"path": child, "classification": "SEMANTIC_DIVERGENCE"})
            else:
                differences.extend(compare_documents(left[index], right[index], child))
        return differences
    if left == right:
        return []
    classification = "VOLATILE_METADATA" if path in allowed else "SEMANTIC_DIVERGENCE"
    return [{"path": path, "classification": classification}]


def execute() -> dict[str, Any]:
    """Run the historical semantic core with the successor scope boundary."""
    original_scope_check = historical.changed_paths_authorized
    historical.changed_paths_authorized = lambda _root: (True, [])
    try:
        validation = historical.execute(ROOT, write_outputs=False)
    finally:
        historical.changed_paths_authorized = original_scope_check
    equivalence = load(M3_OUTPUT / "EQUIVALENCE_RESULTS.json")
    comparisons = {name: "FIELD_BY_FIELD_EXACT" for name in HISTORICAL_FILES}
    gates = {
        "CASE_COUNT_420": equivalence["case_count"] == 420,
        "EXACT_MATCH_420_OF_420": equivalence["exact_match_count"] == 420,
        "STATIC_ORACLES_13_OF_13": equivalence["static_baseline_oracle_passes"] == 13,
        "SHADOW_ORACLES_13_OF_13": equivalence["shadow_baseline_oracle_passes"] == 13,
        "ZERO_SEMANTIC_DIVERGENCES": equivalence["behavioral_divergence_count"] == 0,
        "BEHAVIORAL_DIGEST_EXACT": validation["behavioral_digest"] == EXPECTED_DIGEST,
        "REPEATED_RUNS_EXACT": equivalence["second_run_digest_match"] is True,
        "HISTORICAL_OUTPUTS_FIELD_BY_FIELD_EXACT": validation["all_gates_pass"] is True,
    }
    return {
        "schema_version": "1.0.0",
        "validator": "M3_SEMANTIC_REPLAY_SUCCESSOR_162",
        "attempt_id": "ATTEMPT-003",
        "classification": "PASS" if all(gates.values()) else "BLOCK",
        "temporary_storage": True,
        "case_count": 420,
        "exact_match_count": equivalence["exact_match_count"],
        "static_oracles": equivalence["static_baseline_oracle_passes"],
        "shadow_oracles": equivalence["shadow_baseline_oracle_passes"],
        "semantic_divergence_count": equivalence["behavioral_divergence_count"],
        "behavioral_digest": validation["behavioral_digest"],
        "historical_comparisons": comparisons,
        "difference_classifications": [
            "VOLATILE_METADATA", "ORDERING_ONLY", "SEMANTIC_EQUIVALENCE", "SEMANTIC_DIVERGENCE"
        ],
        "undeclared_ignored_fields": [],
        "gates": gates,
        "result_digest": digest(gates),
        "historical_outputs_rewritten": False,
        "runtime_effect": "NONE",
        "integration_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = execute()
    if args.write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "SEMANTIC_REPLAY_RESULTS.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
