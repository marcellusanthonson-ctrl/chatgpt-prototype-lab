#!/usr/bin/env python3
"""Read-only validation for the LAB knowledge-base repository."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".json", ".py"}
DECISION_STATES = {"DRAFT", "PROPOSED", "UNDER_REVIEW", "APPROVED", "REJECTED", "SUPERSEDED", "WITHDRAWN"}
ERROR_STATES = {"OPEN", "CONTAINED", "CORRECTED", "VERIFIED", "CLOSED"}
PATTERN_STATES = {"PROPOSED", "VALIDATED", "DEPRECATED", "SUPERSEDED"}
PROJECT_STATES = {"active", "active_with_blocker", "active_pipeline_validated_phase_a", "known", "known_and_synced", "referenced", "paused", "archived"}
SCHEMA_NAMES = ["current-state", "decision", "error", "project-state", "pattern", "registry"]
failures: list[str] = []

def fail(message: str) -> None:
    failures.append(message)

def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

def canonical_bytes(path: Path) -> bytes:
    """Return prospective canonical Git bytes, honoring a dirty worktree."""
    relative = path.relative_to(ROOT).as_posix()
    tracked = git("ls-files", "--error-unmatch", "--", relative).returncode == 0
    unstaged = git("diff", "--quiet", "--", relative).returncode != 0
    if tracked and not unstaged:
        indexed = git("show", f":{relative}")
        if indexed.returncode == 0:
            return indexed.stdout
    return path.read_bytes()

def load_json(relative: str) -> object:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"{relative}: cannot load JSON: {exc}")
        return {}

def require_keys(value: object, keys: set[str], label: str) -> None:
    if not isinstance(value, dict):
        fail(f"{label}: expected object")
        return
    missing = sorted(keys - value.keys())
    if missing:
        fail(f"{label}: missing fields: {', '.join(missing)}")

def maintained_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and (path.suffix.lower() in TEXT_SUFFIXES or path.name == ".gitignore")
    )

def validate_text_and_json() -> None:
    for path in maintained_files():
        relative = path.relative_to(ROOT).as_posix()
        data = canonical_bytes(path)
        if data.startswith(b"\xef\xbb\xbf"):
            fail(f"{relative}: UTF-8 BOM is forbidden")
        if b"\r" in data:
            fail(f"{relative}: canonical content must use LF line endings")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            fail(f"{relative}: invalid UTF-8: {exc}")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip(" \t") != line:
                fail(f"{relative}:{number}: trailing whitespace")
        if len(text.splitlines()) > 280:
            fail(f"{relative}: exceeds 280 physical lines")
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            fail(f"{relative}: invalid JSON: {exc}")

def validate_schemas() -> None:
    for name in SCHEMA_NAMES:
        relative = f"schemas/{name}.schema.json"
        schema = load_json(relative)
        if not isinstance(schema, dict):
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"{relative}: expected JSON Schema Draft 2020-12")
        if schema.get("$id") != f"https://lab.local/schemas/{name}.schema.json":
            fail(f"{relative}: unexpected schema identifier")

def validate_registries() -> tuple[dict, dict, dict, dict]:
    projects = load_json("registry/projects.json")
    decisions = load_json("registry/decisions.json")
    errors = load_json("registry/errors.json")
    patterns = load_json("registry/patterns.json")
    registries = {"projects": projects, "decisions": decisions, "errors": errors, "patterns": patterns}
    all_ids: list[str] = []
    for name, registry in registries.items():
        require_keys(registry, {"schema_version", "updated_at", "records"}, f"registry/{name}.json")
        records = registry.get("records", []) if isinstance(registry, dict) else []
        if not isinstance(records, list):
            fail(f"registry/{name}.json: records must be an array")
            continue
        for index, record in enumerate(records):
            label = f"registry/{name}.json record {index}"
            require_keys(record, {"id", "status", "canonical_path", "updated_at"}, label)
            if not isinstance(record, dict):
                continue
            all_ids.append(record.get("id", ""))
            canonical = record.get("canonical_path", "")
            if not canonical or not (ROOT / canonical).is_file():
                fail(f"{label}: canonical path does not exist: {canonical}")
    duplicates = sorted(item for item, count in Counter(all_ids).items() if count > 1)
    if duplicates:
        fail(f"registry IDs are not unique: {', '.join(duplicates)}")
    state_sets = {
        "projects": PROJECT_STATES,
        "decisions": DECISION_STATES,
        "errors": ERROR_STATES,
        "patterns": PATTERN_STATES,
    }
    for name, valid in state_sets.items():
        for record in registries[name].get("records", []):
            if record.get("status") not in valid:
                fail(f"registry/{name}.json: invalid status for {record.get('id')}")
    for record in projects.get("records", []):
        require_keys(record, {"id", "name", "status", "canonical_path", "scope", "updated_at"}, record.get("id", "project"))
    for record in decisions.get("records", []):
        require_keys(record, {"title", "project_scope", "approval_state"}, record.get("id", "decision"))
    for record in errors.get("records", []):
        require_keys(record, {"title", "project_scope", "severity", "lifecycle_state"}, record.get("id", "error"))
        if record.get("lifecycle_state") != record.get("status"):
            fail(f"{record.get('id')}: lifecycle state differs from status")
    for record in patterns.get("records", []):
        require_keys(record, {"title", "project_scope", "validation_state"}, record.get("id", "pattern"))
        if record.get("validation_state") != record.get("status"):
            fail(f"{record.get('id')}: validation state differs from status")
    return projects, decisions, errors, patterns

def validate_decisions(decisions: dict) -> None:
    for record in decisions.get("records", []):
        decision = load_json(record["canonical_path"])
        require_keys(decision, {"id", "title", "project", "status", "effective_date", "approved_by", "approval_evidence", "decision", "supersedes", "superseded_by"}, record["id"])
        if decision.get("id") != record["id"] or decision.get("status") != record["status"]:
            fail(f"{record['id']}: registry and canonical decision differ")
        if decision.get("status") == "APPROVED" and not (decision.get("approved_by") and decision.get("approval_evidence")):
            fail(f"{record['id']}: approved decision lacks approval evidence")
        if decision.get("status") == "SUPERSEDED" and not decision.get("superseded_by"):
            fail(f"{record['id']}: superseded decision lacks replacement")

def validate_current_state(projects: dict, decisions: dict, errors: dict, patterns: dict) -> dict:
    state = load_json("CURRENT_STATE.json")
    required = {"schema_version", "document_id", "version", "status", "updated_at", "active_project", "current_phase", "methodology", "authority", "projects", "decisions_in_force", "open_errors", "validated_patterns", "authorization_state", "next_authorized_action", "continuity_read_order"}
    require_keys(state, required, "CURRENT_STATE.json")
    project_map = {record["id"]: record for record in projects.get("records", [])}
    decision_ids = {record["id"] for record in decisions.get("records", [])}
    error_ids = {record["id"] for record in errors.get("records", [])}
    pattern_ids = {record["id"] for record in patterns.get("records", [])}
    if state.get("active_project") not in project_map:
        fail("CURRENT_STATE.json: active project is absent from registry")
    if projects.get("active_project") != state.get("active_project"):
        fail("CURRENT_STATE.json: active project differs from project registry")
    for key, known in [("decisions_in_force", decision_ids), ("open_errors", error_ids), ("validated_patterns", pattern_ids)]:
        missing = sorted(set(state.get(key, [])) - known)
        if missing:
            fail(f"CURRENT_STATE.json: unknown {key}: {', '.join(missing)}")
    for project_id, project in state.get("projects", {}).items():
        if project_id not in project_map:
            fail(f"CURRENT_STATE.json: unknown project: {project_id}")
        elif project.get("status") != project_map[project_id].get("status"):
            fail(f"CURRENT_STATE.json: status mismatch for {project_id}")
        if not (ROOT / project.get("canonical_path", "")).is_file():
            fail(f"CURRENT_STATE.json: missing project-state path for {project_id}")
    return state

def validate_markdown_and_boundaries(state: dict) -> None:
    current = (ROOT / "CURRENT_STATE.md").read_text(encoding="utf-8")
    required_tokens = [state.get("active_project", ""), state.get("current_phase", ""), state.get("methodology", {}).get("version", "")]
    required_tokens += state.get("decisions_in_force", []) + state.get("open_errors", []) + state.get("validated_patterns", [])
    required_tokens += [f"{key} = {value}" for key, value in state.get("authorization_state", {}).items()]
    for token in required_tokens:
        if token and token not in current:
            fail(f"CURRENT_STATE.md: missing canonical state token: {token}")
    mammoth = (ROOT / "projects/mammothskills/PROJECT_STATE.md").read_text(encoding="utf-8")
    symphonie = (ROOT / "projects/symphonie/PROJECT_STATE.md").read_text(encoding="utf-8")
    if re.search(r"not the runtime where they\s+live", mammoth) is None:
        fail("MammothSkills must be explicitly described as not being the runtime")
    for skill in ["intake-brief", "project-scoping", "project-status"]:
        if skill not in mammoth or "SOURCE_PLATFORM = Claude" not in mammoth:
            fail(f"MammothSkills target classification missing for {skill}")
    if "not the canonical source of reusable skills" not in symphonie:
        fail("Symphonie must not be the canonical reusable-skill source")
    auth = state.get("authorization_state", {})
    expected_auth = {"mammothskills_implementation": "NOT_AUTHORIZED", "mammothskills_release": "NOT_AUTHORIZED", "symphonie_integration": "NOT_AUTHORIZED", "product_changes": "NOT_AUTHORIZED", "codex_autonomous_authority": "NO"}
    for key, value in expected_auth.items():
        if auth.get(key) != value:
            fail(f"CURRENT_STATE.json: unsafe authorization state for {key}")
    if state.get("authority", {}).get("codex_autonomous_authority") != "NO":
        fail("Codex must not have autonomous authority")

def validate_secrets() -> None:
    patterns = [
        re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)(api[_-]?key|password|access[_-]?token|client[_-]?secret)\s*[:=]\s*['\"]?[A-Za-z0-9/+_.=-]{12,}"),
    ]
    for path in maintained_files():
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in patterns):
            fail(f"{path.relative_to(ROOT).as_posix()}: possible secret pattern")

def assignment_map(text: str) -> dict[str, str]:
    return dict(re.findall(r"(?m)^([A-Z_]+) = ([A-Z_]+)$", text))

def validate_fixture(state: dict, projects: dict, errors: dict, patterns: dict) -> None:
    expected = load_json("tests/expected_repository_state.json")
    actual_projects = {record["id"]: record["status"] for record in projects.get("records", [])}
    actual_errors = [record["id"] for record in errors.get("records", []) if record["status"] in {"OPEN", "CONTAINED"}]
    actual_patterns = [record["id"] for record in patterns.get("records", []) if record["status"] == "VALIDATED"]
    mammoth = (ROOT / "projects/mammothskills/PROJECT_STATE.md").read_text(encoding="utf-8")
    symphonie = (ROOT / "projects/symphonie/PROJECT_STATE.md").read_text(encoding="utf-8")
    comparisons = {
        "methodology_version": state.get("methodology", {}).get("version"),
        "active_project": state.get("active_project"),
        "project_statuses": actual_projects,
        "decisions_in_force": state.get("decisions_in_force"),
        "open_or_contained_errors": actual_errors,
        "validated_patterns": actual_patterns,
        "mammothskills_gate_states": assignment_map(mammoth),
        "symphonie_authorization_states": assignment_map(symphonie),
        "codex_authority_state": state.get("authority", {}).get("codex_autonomous_authority"),
    }
    for key, actual in comparisons.items():
        if expected.get(key) != actual:
            fail(f"expected-state mismatch for {key}: expected {expected.get(key)!r}, got {actual!r}")

def main() -> int:
    validate_text_and_json()
    validate_schemas()
    projects, decisions, errors, patterns = validate_registries()
    validate_decisions(decisions)
    state = validate_current_state(projects, decisions, errors, patterns)
    validate_markdown_and_boundaries(state)
    validate_secrets()
    validate_fixture(state, projects, errors, patterns)
    if failures:
        for message in failures:
            print(f"FAIL: {message}")
        print(f"Repository validation: FAIL ({len(failures)} failure(s))")
        return 1
    print("Repository validation: PASS")
    print("JSON parsing: PASS")
    print("Registry integrity: PASS")
    print("Project-state consistency: PASS")
    print("Encoding and line endings: PASS")
    print("Line limits: PASS")
    print("Authority boundaries: PASS")
    print("Expected repository state: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
