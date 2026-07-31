#!/usr/bin/env python3
"""Read-only M3 evaluator for the frozen static MODULE_SELECTOR representation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SELECTOR = Path(
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
)
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


def evaluate_case(selector: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    input_signals = list(case["input_signals"])
    signal_set = set(input_signals)
    activation_signals: list[str] = []
    for module in selector["modules"]:
        for operator in ("activate_any", "activate_all", "activate_alternative_all"):
            activation_signals.extend(module.get(operator, []))
    exclusion_signals = [
        signal
        for block in selector["exclusions"]
        for signal in block["when_any"]
    ]
    known_signals = set(activation_signals) | set(exclusion_signals)

    matched_semantics: list[dict[str, Any]] = []
    activated: list[str] = []
    for module in selector["modules"]:
        module_id = module["id"]
        module_matches: list[dict[str, Any]] = []
        if "activate_any" in module:
            matched = [s for s in module["activate_any"] if s in signal_set]
            if matched:
                module_matches.append({"operator": "ANY", "matched_signals": matched})
        if "activate_all" in module:
            clause = list(module["activate_all"])
            if set(clause).issubset(signal_set):
                module_matches.append({"operator": "ALL", "matched_signals": clause})
        if "activate_alternative_all" in module:
            clause = list(module["activate_alternative_all"])
            if set(clause).issubset(signal_set):
                module_matches.append(
                    {"operator": "ALTERNATIVE_ALL", "matched_signals": clause}
                )
        if module_matches:
            activated.append(module_id)
            matched_semantics.append(
                {"module_id": module_id, "matches": module_matches}
            )

    excluded: list[str] = []
    for block in selector["exclusions"]:
        if any(signal in signal_set for signal in block["when_any"]):
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
    selector = load_json(root / SELECTOR)
    corpus = load_json(root / corpus_path)
    results = [evaluate_case(selector, case) for case in corpus["cases"]]
    return {
        "schema_version": "1.0.0",
        "evaluation_id": "M3_STATIC_SELECTOR_EVALUATION_001",
        "evaluator_id": "INDEPENDENT_STATIC_SELECTOR_EVALUATOR_001",
        "representation": "FROZEN_STATIC_MODULE_SELECTOR",
        "input_sources": [SELECTOR.as_posix(), corpus_path.as_posix()],
        "forbidden_sources": [
            "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json",
            "architecture/integrations/migration/M2/module-adapters/*/ADAPTER.json",
        ],
        "resolution_implementation": "LOCAL_STATIC_SELECTOR_RULE_INTERPRETER",
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
