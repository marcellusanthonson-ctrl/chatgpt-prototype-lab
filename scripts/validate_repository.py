#!/usr/bin/env python3
"""Dependency-free semantic validation for the LAB governance repository."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []
PROJECT_STATUSES = {
    "active", "active_with_blocker", "active_pipeline_validated_phase_a",
    "known", "known_and_synced", "referenced", "paused", "archived",
}
DECISION_STATUSES = {
    "DRAFT", "PROPOSED", "UNDER_REVIEW", "APPROVED",
    "REJECTED", "SUPERSEDED", "WITHDRAWN",
}
SAFE_AUTH = {
    "commit_authorized": False,
    "push_authorized": False,
    "runtime_authorized": False,
    "integration_authorized": False,
    "product_changes_authorized": False,
    "codex_autonomous_authority": "NO",
}

def fail(message: str) -> None:
    FAILURES.append(message)

def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    counts = Counter(key for key, _ in pairs)
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError("duplicate keys: " + ", ".join(duplicates))
    return dict(pairs)

def load_json(relative: str) -> Any:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"{relative}: cannot load JSON: {exc}")
        return {}

def require_file(relative: str) -> None:
    if not (ROOT / relative).is_file():
        fail(f"missing required file: {relative}")

def validate_text() -> None:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".json", ".py"} and path.name != ".gitignore":
            continue
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            fail(f"{relative}: UTF-8 BOM forbidden")
        if b"\r" in data:
            fail(f"{relative}: LF line endings required")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            fail(f"{relative}: invalid UTF-8: {exc}")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip(" \t") != line:
                fail(f"{relative}:{number}: trailing whitespace")
        limit = 600 if path.suffix.lower() == ".md" else 1200
        if len(text.splitlines()) > limit:
            fail(f"{relative}: exceeds {limit} physical lines")
        if path.suffix.lower() == ".json":
            load_json(relative)

def type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)

def validate_instance(value: Any, schema: dict[str, Any], label: str) -> None:
    expected = schema.get("type")
    if expected and not type_matches(value, expected):
        fail(f"{label}: expected {expected}")
        return
    if "const" in schema and value != schema["const"]:
        fail(f"{label}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{label}: value not in enum")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                fail(f"{label}: missing field {key}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate_instance(item, properties[key], f"{label}.{key}")
            elif schema.get("additionalProperties") is False:
                fail(f"{label}: unexpected field {key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail(f"{label}: too few items")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            fail(f"{label}: duplicate array items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_instance(item, item_schema, f"{label}[{index}]")

def apply_schema(instance_path: str, schema_path: str) -> Any:
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    if isinstance(instance, dict) and isinstance(schema, dict):
        validate_instance(instance, schema, instance_path)
    return instance

def validate_registries() -> tuple[dict[str, Any], dict[str, Any]]:
    index = load_json("registry/index.json")
    registry_map = index.get("registries", {}) if isinstance(index, dict) else {}
    counts = index.get("counts", {}) if isinstance(index, dict) else {}
    loaded: dict[str, Any] = {}
    all_ids: list[str] = []
    for name, relative in registry_map.items():
        registry = load_json(relative)
        loaded[name] = registry
        records = registry.get("records", []) if isinstance(registry, dict) else []
        if not isinstance(records, list):
            fail(f"{relative}: records must be an array")
            continue
        if counts.get(name) != len(records):
            fail(f"registry/index.json: count mismatch for {name}")
        for record in records:
            if not isinstance(record, dict) or not record.get("id"):
                fail(f"{relative}: record without id")
                continue
            all_ids.append(record["id"])
            canonical = record.get("canonical_path")
            if canonical:
                require_file(canonical)
    duplicates = sorted(key for key, count in Counter(all_ids).items() if count > 1)
    if duplicates:
        fail("registry IDs not unique: " + ", ".join(duplicates))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(index.get("updated_at", ""))):
        fail("registry/index.json: invalid updated_at")
    return index, loaded

def validate_projects(registries: dict[str, Any]) -> None:
    projects = registries["projects"]
    decisions = {r["id"] for r in registries["decisions"].get("records", [])}
    for record in projects.get("records", []):
        project_id = record["id"]
        if record.get("status") not in PROJECT_STATUSES:
            fail(f"{project_id}: invalid project status")
        required = [
            f"projects/{project_id}/PROJECT_STATE.json",
            f"projects/{project_id}/ROADMAP.json",
            f"projects/{project_id}/PENDING.json",
            f"projects/{project_id}/decisions/index.json",
            f"projects/{project_id}/ideas/index.json",
            f"projects/{project_id}/integrations/index.json",
            f"projects/{project_id}/reassessments/index.json",
        ]
        for path in required:
            require_file(path)
        state = apply_schema(required[0], "schemas/project-state-v2.schema.json")
        if state.get("project_id") != project_id:
            fail(f"{required[0]}: project_id mismatch")
        if state.get("status") != record.get("status"):
            fail(f"{project_id}: state differs from project registry")
        if record.get("repository") == "marcellusanthonson-ctrl/chatgpt-prototype-lab":
            if "verified_head" in state:
                fail(f"{project_id}: self-referential verified_head is forbidden")
            if state.get("head_policy") != "VERIFY_LIVE_AT_USE":
                fail(f"{project_id}: head_policy must be VERIFY_LIVE_AT_USE")
            if state.get("self_head_is_canonical_state") is not False:
                fail(f"{project_id}: self_head_is_canonical_state must be false")
            if not isinstance(state.get("verified_parent_head"), str):
                fail(f"{project_id}: verified_parent_head is required")
        decision_index = load_json(required[3])
        for decision in decision_index.get("records", []):
            if decision.get("id") not in decisions:
                fail(f"{required[3]}: unknown decision {decision.get('id')}")

def validate_current_state(registries: dict[str, Any]) -> dict[str, Any]:
    state = apply_schema("CURRENT_STATE.json", "schemas/current-state.schema.json")
    project_records = {r["id"]: r for r in registries["projects"].get("records", [])}
    for project_id, value in state.get("projects", {}).items():
        if project_id not in project_records:
            fail(f"CURRENT_STATE.json: unknown project {project_id}")
            continue
        allowed = {"status", "canonical_path", "structured_state_path"}
        if set(value) - allowed:
            fail(f"CURRENT_STATE.json: copied project detail for {project_id}")
        if value.get("status") != project_records[project_id].get("status"):
            fail(f"CURRENT_STATE.json: status mismatch for {project_id}")
    known_decisions = {r["id"] for r in registries["decisions"].get("records", [])}
    known_errors = {r["id"] for r in registries["errors"].get("records", [])}
    known_patterns = {r["id"] for r in registries["patterns"].get("records", [])}
    for key, known in [
        ("decisions_in_force", known_decisions),
        ("open_errors", known_errors),
        ("validated_patterns", known_patterns),
    ]:
        unknown = sorted(set(state.get(key, [])) - known)
        if unknown:
            fail(f"CURRENT_STATE.json: unknown {key}: {', '.join(unknown)}")
    for key, expected in SAFE_AUTH.items():
        if state.get("authorization_state", {}).get(key) != expected:
            fail(f"CURRENT_STATE.json: unsafe authorization {key}")
    return state

def validate_decisions(registries: dict[str, Any]) -> None:
    for decision in registries["decisions"].get("records", []):
        if decision.get("status") not in DECISION_STATUSES:
            fail(f"{decision.get('id')}: invalid decision status")
        if decision.get("status") == "APPROVED" and not decision.get("approval_state"):
            fail(f"{decision.get('id')}: approval evidence state missing")

def validate_briefs_and_continuity() -> None:
    for path in sorted(ROOT.glob("projects/*/briefs/*.json")):
        apply_schema(path.relative_to(ROOT).as_posix(), "schemas/brief.schema.json")
    for project_dir in sorted((ROOT / "projects").iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue
        continuity = project_dir / "continuity"
        if not continuity.is_dir():
            continue
        current = continuity / "CURRENT_CONTINUITY.json"
        manifest = continuity / "ATTACHMENT_MANIFEST.json"
        prompt = continuity / "START_PROMPT.md"
        for path in [current, manifest, prompt]:
            if not path.is_file():
                fail(f"{project_dir.name}: incomplete continuity package")
        if current.is_file():
            package = apply_schema(current.relative_to(ROOT).as_posix(), "schemas/continuity.schema.json")
            if package.get("project_id") != project_dir.name:
                fail(f"{current}: project_id mismatch")
        if manifest.is_file():
            data = apply_schema(manifest.relative_to(ROOT).as_posix(), "schemas/attachment-manifest.schema.json")
            for item in data.get("required", []):
                if item.get("repository") == "marcellusanthonson-ctrl/chatgpt-prototype-lab":
                    require_file(item.get("path", ""))
        if prompt.is_file() and "No infieras autoridad" not in prompt.read_text(encoding="utf-8"):
            fail(f"{prompt}: authority boundary missing")

def validate_reassessments(registries: dict[str, Any]) -> None:
    global_records = registries["reassessments"].get("records", [])
    seen: set[str] = set()
    for project_dir in sorted((ROOT / "projects").iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue
        index_path = project_dir / "reassessments" / "index.json"
        if not index_path.is_file():
            fail(f"{project_dir.name}: missing reassessment index")
            continue
        index = load_json(index_path.relative_to(ROOT).as_posix())
        for record in index.get("records", []):
            relative = record.get("canonical_path", "")
            if not relative:
                fail(f"{index_path}: reassessment without canonical_path")
                continue
            document = apply_schema(relative, "schemas/decision-reassessment.schema.json")
            if document.get("project_id") != project_dir.name:
                fail(f"{relative}: project_id mismatch")
            if document.get("reassessment_id") in seen:
                fail(f"{relative}: duplicate reassessment ID")
            seen.add(document.get("reassessment_id"))
    if len(global_records) != len(seen):
        fail("global reassessment registry differs from project records")

def validate_evidence(registries: dict[str, Any]) -> None:
    registered = {r.get("path") for r in registries["evidence"].get("records", [])}
    reports = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.glob("projects/symphonie/reports/*.md")
    }
    missing = sorted(reports - registered)
    if missing:
        fail("unregistered Symphonie reports: " + ", ".join(missing))
    unincorporated = registries["unincorporated"]
    if unincorporated.get("records"):
        fail("material unincorporated records remain open")

def validate_fixture(state: dict[str, Any], index: dict[str, Any], registries: dict[str, Any]) -> None:
    expected = load_json("tests/expected_repository_state.json")
    actual = {
        "methodology_version": state.get("methodology", {}).get("version"),
        "active_project": state.get("active_project"),
        "current_phase": state.get("current_phase"),
        "project_statuses": {r["id"]: r["status"] for r in registries["projects"].get("records", [])},
        "decisions_in_force": state.get("decisions_in_force"),
        "open_errors": state.get("open_errors"),
        "validated_patterns": state.get("validated_patterns"),
        "registry_counts": index.get("counts"),
        "symphonie": {"head": state.get("verified_external_heads", {}).get("symphonie"), "fileset": 44, "total_phases": 8},
        "authorization_state": state.get("authorization_state"),
    }
    for key, value in actual.items():
        if expected.get(key) != value:
            fail(f"expected-state mismatch for {key}")

def main() -> int:
    validate_text()
    index, registries = validate_registries()
    validate_projects(registries)
    validate_decisions(registries)
    state = validate_current_state(registries)
    validate_briefs_and_continuity()
    validate_reassessments(registries)
    validate_evidence(registries)
    validate_fixture(state, index, registries)
    if FAILURES:
        for message in FAILURES:
            print("FAIL:", message)
        print(f"Repository validation: FAIL ({len(FAILURES)} failure(s))")
        return 1
    print("Repository validation: PASS")
    print("JSON and duplicate keys: PASS")
    print("Schema instances: PASS")
    print("Registry counts and references: PASS")
    print("Project structures: PASS")
    print("Brief, continuity and reassessment contracts: PASS")
    print("Evidence closure: PASS")
    print("Authority boundaries: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
