#!/usr/bin/env python3
"""Create and validate the authorization-165 portable 333-finding baseline."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REL = Path("architecture/integrations/migration/M5/documentary-reconciliation-163/GENERAL_VALIDATOR_SUCCESSOR_BASELINE.json")
OUTPUT_REL = Path("architecture/integrations/migration/M5/canonical-reconciliation-165/GENERAL_VALIDATOR_PORTABLE_BASELINE.json")
DELTA_REL = Path("architecture/integrations/migration/M5/canonical-reconciliation-165/PORTABLE_BASELINE_DELTA.json")
SOURCE_BLOB = "0dec0e8660ab029f33be87c91c5e0ae0342961a1"
ROOT_PREFIX = re.compile(r"^[A-Za-z]:/(?:[^/]+/)*chatgpt-prototype-lab/")
FORBIDDEN = re.compile(r"(?:[A-Za-z]:[/\\]|(?:^|[/\\])Users[/\\]|(?:^|[/\\])home[/\\]|JF Martin|AppData|temporary_directory)", re.I)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob(relative: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative.as_posix()}"], cwd=ROOT, text=True,
    ).strip()


def normalize_message(message: str) -> tuple[str, bool]:
    slashed = message.replace("\\", "/")
    normalized = ROOT_PREFIX.sub("", slashed)
    return normalized, normalized != message


def build_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    source = load(ROOT / SOURCE_REL)
    findings: list[dict[str, Any]] = []
    normalized_ids: list[str] = []
    for original in source["findings"]:
        item = copy.deepcopy(original)
        message, changed = normalize_message(item["normalized_message"])
        item["normalized_message"] = message
        item["digest"] = sha256(message.encode("utf-8"))
        findings.append(item)
        if changed:
            normalized_ids.append(item["stable_id"])
    structured = sha256(canonical(findings))
    raw = sha256("\n".join(item["normalized_message"] for item in findings).encode("utf-8"))
    portable = {
        "schema_version": "1.0.0",
        "baseline_id": "INTEGRATION_FACTORY_M5_GENERAL_VALIDATOR_PORTABLE_BASELINE_165",
        "created_at": "2026-07-31T23:30:00-04:00",
        "source_baseline_path": SOURCE_REL.as_posix(),
        "source_baseline_blob": SOURCE_BLOB,
        "source_structured_inventory_digest": source["structured_inventory_digest"],
        "source_raw_ordered_message_digest": source["raw_ordered_message_digest"],
        "finding_count": len(findings),
        "complete_ordered_inventory": True,
        "ordered_stable_ids_preserved": True,
        "portable": True,
        "normalization": {
            "rule": "REMOVE_MACHINE_SPECIFIC_REPOSITORY_ROOT_PREFIX_ONLY",
            "normalized_finding_count": len(normalized_ids),
            "normalized_stable_ids": normalized_ids,
            "structured_digest_algorithm": "SHA256_CANONICAL_SORTED_COMPACT_JSON_FINDINGS",
            "raw_digest_algorithm": "SHA256_UTF8_LF_JOINED_ORDERED_NORMALIZED_MESSAGES_NO_TRAILING_LF",
        },
        "findings": findings,
        "structured_inventory_digest": structured,
        "raw_ordered_message_digest": raw,
        "global_repository_pass": False,
    }
    delta = {
        "schema_version": "1.0.0",
        "delta_id": "INTEGRATION_FACTORY_M5_PORTABLE_BASELINE_DELTA_165",
        "source_baseline_path": SOURCE_REL.as_posix(),
        "portable_baseline_path": OUTPUT_REL.as_posix(),
        "source_baseline_blob": SOURCE_BLOB,
        "finding_count_before": len(source["findings"]),
        "finding_count_after": len(findings),
        "ordered_stable_ids_identical": [x["stable_id"] for x in source["findings"]] == [x["stable_id"] for x in findings],
        "normalized_repository_root_prefixes": len(normalized_ids),
        "normalized_stable_ids": normalized_ids,
        "other_field_changes": "ONLY_DERIVED_PER_FINDING_DIGESTS_AND_BASELINE_DIGESTS",
        "structured_inventory_digest": structured,
        "raw_ordered_message_digest": raw,
        "global_repository_pass": False,
        "historical_baseline_335_unchanged_blob": "94997b3bdd46c2083b6371d93b7bc264a6d5cbd7",
        "successor_baseline_333_unchanged_blob": SOURCE_BLOB,
    }
    return portable, delta


def string_values(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from string_values(child)


def validate() -> dict[str, Any]:
    failures: list[str] = []
    if git_blob(SOURCE_REL) != SOURCE_BLOB:
        failures.append("SUCCESSOR_BASELINE_333_BLOB_ALTERED")
    expected, expected_delta = build_documents()
    actual = load(ROOT / OUTPUT_REL)
    delta = load(ROOT / DELTA_REL)
    source = load(ROOT / SOURCE_REL)
    if len(actual.get("findings", [])) != 333:
        failures.append("PORTABLE_BASELINE_FINDING_COUNT_NOT_333")
    if [x.get("stable_id") for x in actual.get("findings", [])] != [x.get("stable_id") for x in source["findings"]]:
        failures.append("PORTABLE_BASELINE_STABLE_ID_DRIFT")
    if any(FORBIDDEN.search(text) for text in string_values(actual)):
        failures.append("PORTABLE_BASELINE_CONTAINS_ABSOLUTE_PATH")
    if actual != expected:
        failures.append("PORTABLE_BASELINE_CONTENT_MISMATCH")
    if delta != expected_delta:
        failures.append("PORTABLE_BASELINE_DELTA_MISMATCH")
    if actual.get("global_repository_pass") is not False:
        failures.append("UNAUTHORIZED_GLOBAL_REPOSITORY_PASS_CLAIM")
    return {
        "classification": "PASS" if not failures else "BLOCK",
        "failure_codes": failures,
        "finding_count": len(actual.get("findings", [])),
        "structured_inventory_digest": actual.get("structured_inventory_digest"),
        "raw_ordered_message_digest": actual.get("raw_ordered_message_digest"),
        "ordered_stable_ids_preserved": not any(code == "PORTABLE_BASELINE_STABLE_ID_DRIFT" for code in failures),
        "global_repository_pass": actual.get("global_repository_pass"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        portable, delta = build_documents()
        (ROOT / OUTPUT_REL).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / OUTPUT_REL).write_text(json.dumps(portable, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (ROOT / DELTA_REL).write_text(json.dumps(delta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)


if __name__ == "__main__":
    main()
