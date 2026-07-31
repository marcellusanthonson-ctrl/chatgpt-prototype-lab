#!/usr/bin/env python3
"""Read-only M3 evaluator for the frozen M2 shadow registry and adapters."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REGISTRY = Path("architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json")
DEFAULT_CORPUS = Path("architecture/integrations/migration/M3/TEST_CORPUS.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def unique_in_order(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def adapter_matches(
    contract: dict[str, list[str]], signal_set: set[str]
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    any_signals = contract.get("activate_any")
    if any_signals:
        matched = [signal for signal in any_signals if signal in signal_set]
        if matched:
            matches.append({"operator": "ANY", "matched_signals": matched})
    all_signals = contract.get("activate_all")
    if all_signals and set(all_signals).issubset(signal_set):
        matches.append({"operator": "ALL", "matched_signals": list(all_signals)})
    alternative = contract.get("activate_alternative_all")
    if alternative and set(alternative).issubset(signal_set):
        matches.append(
            {"operator": "ALTERNATIVE_ALL", "matched_signals": list(alternative)}
        )
    return matches


def evaluate_case(
    registry: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any]:
    input_signals = list(case["input_signals"])
    signal_set = set(input_signals)
    known_signals: set[str] = set()
    for adapter in adapters.values():
        for values in adapter["activation_contract"].values():
            known_signals.update(values)
    for block in registry["composition"]["exclusions"]:
        known_signals.update(block["when_any"])

    matched_semantics: list[dict[str, Any]] = []
    activated: list[str] = []
    ordered_entries = sorted(registry["entries"], key=lambda entry: entry["order"])
    for entry in ordered_entries:
        module_id = entry["module_id"]
        matches = adapter_matches(adapters[module_id]["activation_contract"], signal_set)
        if matches:
            activated.append(module_id)
            matched_semantics.append({"module_id": module_id, "matches": matches})

    excluded: list[str] = []
    for block in registry["composition"]["exclusions"]:
        if signal_set.intersection(block["when_any"]):
            excluded.extend(block["exclude"])
    excluded = unique_in_order(excluded)
    selected = [module_id for module_id in activated if module_id not in excluded]

    result: dict[str, Any] = {
        "case_id": case["case_id"],
        "input_signals": input_signals,
        "selected_modules_in_order": selected,
        "excluded_modules": excluded,
        "matched_activation_semantics": matched_semantics,
        "empty_set_abstention": not selected,
        "unknown_signals": unique_in_order(
            [signal for signal in input_signals if signal not in known_signals]
        ),
    }
    result["result_digest"] = digest(result)
    return result


def evaluate(root: Path, corpus_path: Path) -> dict[str, Any]:
    registry = load_json(root / REGISTRY)
    adapters = {
        entry["module_id"]: load_json(root / entry["adapter_path"])
        for entry in registry["entries"]
    }
    corpus = load_json(root / corpus_path)
    results = [evaluate_case(registry, adapters, case) for case in corpus["cases"]]
    return {
        "schema_version": "1.0.0",
        "evaluation_id": "M3_SHADOW_SELECTOR_EVALUATION_001",
        "evaluator_id": "INDEPENDENT_SHADOW_SELECTOR_EVALUATOR_001",
        "representation": "FROZEN_M2_SHADOW_REGISTRY_AND_FOUR_ADAPTERS",
        "input_sources": [
            REGISTRY.as_posix(),
            *[entry["adapter_path"] for entry in registry["entries"]],
            corpus_path.as_posix(),
        ],
        "forbidden_sources": [
            "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/"
            "MODULE_SELECTOR.json AS A RESOLUTION SOURCE"
        ],
        "selector_use": "NONE",
        "resolution_implementation": "LOCAL_SHADOW_ADAPTER_RULE_INTERPRETER",
        "case_count": len(results),
        "results": results,
        "normalized_run_digest": digest(results),
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "integration_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.root.resolve(), args.corpus)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
