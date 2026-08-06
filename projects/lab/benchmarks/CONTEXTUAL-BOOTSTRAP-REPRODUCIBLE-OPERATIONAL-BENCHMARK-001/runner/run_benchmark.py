#!/usr/bin/env python3
"""Deterministic scorer for benchmark 202.

Authorization 202 forbids executing this runner. A later explicit authorization
must validate and run it.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

BENCHMARK_ID = "CONTEXTUAL-BOOTSTRAP-REPRODUCIBLE-OPERATIONAL-BENCHMARK-001"
EXACT_FIELDS = [
    "route", "risk", "terminal_state", "authority", "head_behavior",
    "conflict_behavior", "project_namespace"
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        row = json.loads(raw)
        task_id = row.get("task_id")
        if not isinstance(task_id, str) or task_id in seen:
            raise ValueError(f"invalid or duplicate task_id at line {line_number}")
        seen.add(task_id)
        rows.append(row)
    return sorted(rows, key=lambda row: row["task_id"])


def read_oracle(path: Path) -> dict[str, dict[str, Any]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("benchmark_id") != BENCHMARK_ID:
        raise ValueError("oracle benchmark_id mismatch")
    fields = doc["field_order"]
    oracle: dict[str, dict[str, Any]] = {}
    for values in doc["records"]:
        if len(values) != len(fields):
            raise ValueError("oracle record length mismatch")
        row = dict(zip(fields, values, strict=True))
        task_id = row["task_id"]
        if task_id in oracle:
            raise ValueError(f"duplicate oracle task_id {task_id}")
        oracle[task_id] = row
    return oracle


def f1(expected: set[str], selected: set[str]) -> tuple[float, int, int, int]:
    tp = len(expected & selected)
    fp = len(selected - expected)
    fn = len(expected - selected)
    precision = tp / (tp + fp) if tp + fp else (1.0 if not expected else 0.0)
    recall = tp / (tp + fn) if tp + fn else 1.0
    score = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return score, tp, fp, fn


def exact_accuracy(pairs: list[tuple[Any, Any]]) -> float:
    return sum(actual == expected for actual, expected in pairs) / len(pairs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tasks = read_jsonl(args.tasks)
    candidates = {row["task_id"]: row for row in read_jsonl(args.candidate)}
    oracle = read_oracle(args.oracle)
    task_ids = [row["task_id"] for row in tasks]
    if set(task_ids) != set(oracle) or set(task_ids) != set(candidates):
        raise ValueError("tasks, oracle and candidate task IDs must match exactly")

    macro_f1: list[float] = []
    tp = fp = fn = 0
    exact = {field: [] for field in EXACT_FIELDS}
    expected_constraints = recovered_constraints = 0
    forbidden_selected = 0
    missing_reason_trace = 0
    reductions_by_route: dict[str, list[float]] = {}
    source_count_reductions: list[float] = []

    for task_id in task_ids:
        expected = oracle[task_id]
        actual = candidates[task_id]
        selected = set(actual["selected_paths"])
        required = set(expected["required_paths"])
        optional = set(expected["optional_paths"])
        forbidden = set(expected["forbidden_paths"])
        score, row_tp, row_fp, row_fn = f1(required, selected - optional)
        macro_f1.append(score)
        tp += row_tp
        fp += row_fp
        fn += row_fn
        forbidden_selected += len(selected & forbidden)
        for field in EXACT_FIELDS:
            exact[field].append((actual[field], expected[field]))
        wanted = set(expected["critical_constraints"])
        got = set(actual["critical_constraints"])
        expected_constraints += len(wanted)
        recovered_constraints += len(wanted & got)
        if not actual.get("reason_trace"):
            missing_reason_trace += 1
        baseline_bytes = actual.get("baseline_source_bytes")
        selected_bytes = actual.get("selected_source_bytes")
        if isinstance(baseline_bytes, int) and baseline_bytes > 0 and isinstance(selected_bytes, int):
            reductions_by_route.setdefault(expected["route"], []).append(1 - selected_bytes / baseline_bytes)
        baseline_count = actual.get("baseline_source_count")
        selected_count = actual.get("selected_source_count")
        if isinstance(baseline_count, int) and baseline_count > 0 and isinstance(selected_count, int):
            source_count_reductions.append(1 - selected_count / baseline_count)

    micro_precision = tp / (tp + fp) if tp + fp else 0.0
    micro_recall = tp / (tp + fn) if tp + fn else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if micro_precision + micro_recall else 0.0
    route_reduction = {route: round(statistics.median(values), 6) for route, values in sorted(reductions_by_route.items())}
    metrics = {
        "macroPathF1": round(sum(macro_f1) / len(macro_f1), 6),
        "microPathF1": round(micro_f1, 6),
        "criticalConstraintRecall": round(recovered_constraints / expected_constraints if expected_constraints else 0.0, 6),
        "forbiddenPathPrecision": 1.0 if forbidden_selected == 0 else 0.0,
        "routeAccuracy": round(exact_accuracy(exact["route"]), 6),
        "riskAccuracy": round(exact_accuracy(exact["risk"]), 6),
        "terminalStateAccuracy": round(exact_accuracy(exact["terminal_state"]), 6),
        "authorityAccuracy": round(exact_accuracy(exact["authority"]), 6),
        "headAccuracy": round(exact_accuracy(exact["head_behavior"]), 6),
        "conflictAccuracy": round(exact_accuracy(exact["conflict_behavior"]), 6),
        "projectNamespaceAccuracy": round(exact_accuracy(exact["project_namespace"]), 6),
        "medianByteReductionByRoute": route_reduction,
        "medianSourceCountReduction": round(statistics.median(source_count_reductions), 6) if source_count_reductions else None,
        "missingReasonTraceCount": missing_reason_trace,
        "forbiddenPathSelectionCount": forbidden_selected
    }
    gates = {
        "macroPathF1AtLeast0_95": metrics["macroPathF1"] >= 0.95,
        "criticalConstraintRecall1": metrics["criticalConstraintRecall"] == 1.0,
        "forbiddenPathPrecision1": metrics["forbiddenPathPrecision"] == 1.0,
        "authorityAccuracy1": metrics["authorityAccuracy"] == 1.0,
        "headAccuracy1": metrics["headAccuracy"] == 1.0,
        "conflictAccuracy1": metrics["conflictAccuracy"] == 1.0,
        "projectNamespaceAccuracy1": metrics["projectNamespaceAccuracy"] == 1.0,
        "zeroMissingReasonTraces": metrics["missingReasonTraceCount"] == 0,
        "allObservedRoutesMedianByteReductionAtLeast0_30": bool(route_reduction) and all(value >= 0.30 for value in route_reduction.values())
    }
    violations = sorted(name for name, passed in gates.items() if not passed)
    summary = {
        "benchmark_id": BENCHMARK_ID,
        "status": "PASS" if not violations else "FAIL",
        "task_count": len(task_ids),
        "metrics": metrics,
        "gates": gates,
        "violations": violations
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
