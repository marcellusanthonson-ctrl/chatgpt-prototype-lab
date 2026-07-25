from .context import *

def validate_registries() -> tuple[dict[str, Any], dict[str, Any]]:
    index = load_json("registry/index.json")
    registry_map = index.get("registries", {}) if isinstance(index, dict) else {}
    counts = index.get("counts", {}) if isinstance(index, dict) else {}
    loaded: dict[str, Any] = {}
    for name, relative in registry_map.items():
        registry = load_json(relative)
        loaded[name] = registry
        records = registry.get("records", []) if isinstance(registry, dict) else []
        if name == "reconciliations" and isinstance(registry, dict) and registry.get("reconciliation_id"):
            records = [{
                **registry,
                "id": registry["reconciliation_id"],
                "canonical_path": relative,
            }]
        if not isinstance(records, list):
            fail(f"{relative}: records must be an array")
            continue
        if name in counts and counts.get(name) != len(records):
            fail(f"registry/index.json: count mismatch for {name}")
        registry_ids: list[str] = []
        for record in records:
            if not isinstance(record, dict) or not record.get("id"):
                fail(f"{relative}: record without id")
                continue
            registry_ids.append(record["id"])
            canonical = record.get("canonical_path")
            if canonical:
                require_file(canonical)
        duplicates = sorted(key for key, count in Counter(registry_ids).items() if count > 1)
        if duplicates:
            fail(f"{relative}: duplicate record IDs: " + ", ".join(duplicates))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(index.get("updated_at", ""))):
        fail("registry/index.json: invalid updated_at")
    authorizations = loaded.get("authorizations", {})
    authorization_updated = str(authorizations.get("updated_at", ""))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", authorization_updated):
        fail("registry/authorizations.json: invalid updated_at")
    authorization_dates: list[str] = []
    for record in authorizations.get("records", []):
        record_date = str(record.get("updated_at", ""))
        if record_date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", record_date):
            fail(f"{record.get('id')}: invalid authorization updated_at")
        elif record_date:
            authorization_dates.append(record_date)
    if authorization_dates and authorization_updated < max(authorization_dates):
        fail("registry/authorizations.json: updated_at precedes a record")
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
    authorization_state = state.get("authorization_state", {})
    transition_keys = {
        key for key, value in authorization_state.items()
        if key not in SAFE_AUTH and isinstance(value, str) and value.startswith("CONSUMED_")
    }
    authorization_records = registries["authorizations"].get("records", [])
    registered_keys: list[str] = []
    for record in authorization_records:
        state_key = record.get("state_key")
        if not state_key:
            fail(f"{record.get('id')}: authorization state_key missing")
            continue
        registered_keys.append(state_key)
        if state_key not in transition_keys:
            fail(f"{record.get('id')}: state_key not consumed in CURRENT_STATE.json")
        if not str(record.get("status", "")).startswith("CONSUMED_"):
            fail(f"{record.get('id')}: registry status is not consumed")
    duplicates = sorted(key for key, count in Counter(registered_keys).items() if count > 1)
    if duplicates:
        fail("authorization state_key duplicated: " + ", ".join(duplicates))
    missing = sorted(transition_keys - set(registered_keys))
    if missing:
        fail("consumed authorization transitions unregistered: " + ", ".join(missing))
    return state

def validate_decisions(registries: dict[str, Any]) -> None:
    for record in registries["decisions"].get("records", []):
        decision_id = record.get("id")
        if record.get("status") not in DECISION_STATUSES:
            fail(f"{decision_id}: invalid decision status")
        if record.get("status") == "APPROVED" and not record.get("approval_state"):
            fail(f"{decision_id}: approval evidence state missing")
        canonical_path = record.get("canonical_path", "")
        if not canonical_path:
            fail(f"{decision_id}: canonical decision path missing")
            continue
        decision = apply_schema(canonical_path, "schemas/decision.schema.json")
        if decision.get("id") != decision_id:
            fail(f"{canonical_path}: decision ID differs from registry")
        decision_status = decision.get("status")
        normalized_status = (
            "APPROVED"
            if isinstance(decision_status, str) and decision_status.startswith("APPROVED_")
            else decision_status
        )
        if normalized_status != record.get("status"):
            fail(f"{canonical_path}: decision status differs from registry")
        if "project_scope" in decision:
            if decision.get("project_scope") != record.get("project_scope"):
                fail(f"{canonical_path}: project_scope differs from registry")
        if normalized_status == "APPROVED":
            if decision.get("approved_by") != "Jonathan Martínez":
                fail(f"{canonical_path}: approved decision lacks sole approver")
            if not decision.get("approval_evidence"):
                fail(f"{canonical_path}: approved decision lacks approval evidence")
