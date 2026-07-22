#!/usr/bin/env python3
"""Dependency-free semantic validation for the LAB governance repository."""
from __future__ import annotations

import json
import hashlib
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
REQUIRED_DESIGN_ARCHETYPES = {
    "PREMIUM_ECOMMERCE",
    "HIGH_DENSITY_DASHBOARD",
    "SERVICES_AND_DIRECTORIES",
    "SECURE_TRANSACTIONAL_FLOW",
    "BIDIRECTIONAL_MARKETPLACE",
}
REQUIRED_BACKEND_DOMAINS = {
    "AUTHENTICATION_AND_AUTHORIZATION",
    "PAYMENT_ORCHESTRATION",
    "WEBHOOK_PROCESSING",
    "IDEMPOTENCY_AND_RETRIES",
    "AUDIT_LOGGING",
    "DATA_VALIDATION",
    "ERROR_HANDLING",
    "TRANSACTIONAL_STATE",
    "PROVIDER_CONFIGURATION",
}
REQUIRED_INTERACTION_STATES = {
    "DEFAULT", "HOVER", "FOCUS_VISIBLE", "ACTIVE", "DISABLED",
    "LOADING", "ERROR", "SUCCESS", "EMPTY",
}
REQUIRED_DESIGN_EVIDENCE = {
    "RESPONSIVE_BOUNDARY_MATRIX", "CONTENT_STRESS_MATRIX", "ZOOM_AND_REFLOW",
    "KEYBOARD_AND_FOCUS", "SCREEN_READER_CONTRACT", "CONTRAST_RECALCULATION",
    "REDUCED_MOTION", "INTERACTION_STATE_COMPLETENESS",
    "EMPTY_LOADING_ERROR_SUCCESS_STATES",
}
REQUIRED_RESPONSIVE_WIDTHS = [320, 639, 640, 1023, 1024, 1439, 1440, 1920]
REQUIRED_BACKEND_EVIDENCE = {
    "HAPPY_PATH", "VALIDATION_FAILURES", "AUTHORIZATION_FAILURES",
    "IDEMPOTENCY_AND_DUPLICATES", "RETRY_EXHAUSTION",
    "CONCURRENT_STATE_CHANGES", "AUDIT_REDACTION",
    "CLIENT_ENVIRONMENT_ISOLATION", "SECRET_BOUNDARY",
    "RECOVERY_AND_COMPENSATION",
}
REQUIRED_PAYMENT_EVIDENCE = {
    "SERVER_CALCULATED_AMOUNT", "CURRENCY_CONSISTENCY", "HOSTED_PAYMENT_CAPTURE",
    "NO_CARD_DATA_HANDLING", "AUTHENTICATED_WEBHOOK", "DUPLICATE_WEBHOOK",
    "OUT_OF_ORDER_EVENT", "BROWSER_RETURN_NOT_AUTHORITATIVE",
    "IDEMPOTENT_PAYMENT_INTENT", "CLIENT_CONFIGURATION_ISOLATION",
    "CREDENTIAL_REFERENCE_ISOLATION", "REFUND_TRACEABILITY",
}
REQUIRED_RAG_NAMESPACES = ["LAB", "SYMPHONIE", "PROJECT"]
REQUIRED_RAG_METADATA = [
    "repository", "path", "document_id", "commit_sha", "content_sha256",
    "schema_version", "canonical_owner", "authority_class", "project_scope",
    "document_status", "indexed_at",
]
REQUIRED_RAG_AUTHORITY_RULES = {
    "AUTHORITY_BEFORE_SEMANTIC_SIMILARITY",
    "CANONICAL_OWNER_RESOLVES_SCOPE",
    "EXACT_COMMIT_TRACEABILITY",
    "NO_AUTOMATIC_CONFLICT_MERGE",
    "CONFLICT_REQUIRES_EXPLICIT_RESOLUTION",
    "PROJECT_DATA_CANNOT_OVERRIDE_GLOBAL_GOVERNANCE",
}
REQUIRED_RAG_INDEX_RULES = {
    "INDEX_IS_DERIVED_READ_ONLY_CACHE", "REPOSITORY_IS_SOURCE_OF_TRUTH",
    "REBUILD_ON_CANONICAL_PUSH", "REBUILD_ONLY_AFFECTED_NAMESPACE",
    "REMOVE_STALE_CHUNKS", "PIN_ACTIVE_COMMIT",
    "DETERMINISTIC_CHUNK_IDENTIFIERS", "NO_DIRECT_MODEL_WRITES",
}
REQUIRED_RAG_WRITE_RULES = {
    "MODEL_MAY_PROPOSE_STRUCTURED_CHANGE", "PROPOSAL_TARGETS_CANONICAL_OWNER",
    "VALIDATOR_RUNS_BEFORE_COMMIT", "VALIDATION_FAILURE_RETURNS_TO_MODEL",
    "COMMIT_REQUIRES_ACTIVE_AUTHORIZATION", "NO_AUTONOMOUS_AUTHORITY",
    "INDEX_REBUILDS_ONLY_AFTER_CANONICAL_COMMIT",
}
REQUIRED_PILOT_DELTA_AREAS = {
    "TYPOGRAPHY", "EARTH_TONE_COLOR_PALETTE", "EDITORIAL_COMPOSITION",
    "PRODUCT_PHOTOGRAPHY_DIRECTION", "COMPONENT_DENSITY", "CONTENT_VOICE",
}
REQUIRED_PILOT_IMMUTABLES = {
    "SEMANTIC_ORDER", "WCAG_2_2_AA", "RESPONSIVE_RANGE_CONTINUITY",
    "KEYBOARD_OPERABILITY", "FOCUS_VISIBILITY", "SCREEN_READER_SEMANTICS",
    "INTERACTION_STATE_COMPLETENESS", "PURCHASE_FLOW_RECOVERABILITY",
    "NO_HORIZONTAL_PAGE_OVERFLOW",
}
REQUIRED_PILOT_FIXTURES = {
    "PRODUCT_CATALOG", "PRODUCT_DETAIL", "LONG_PRODUCT_NAME", "MULTIPLE_VARIANTS",
    "AVAILABLE_STOCK", "UNAVAILABLE_STOCK", "EMPTY_CART", "LOADING_CART",
    "CART_ERROR", "CART_SUCCESS", "LOCALIZED_CONTENT", "MISSING_OPTIONAL_CONTENT",
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
        if b"\r" in data.replace(b"\r\n", b""):
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

def validate_chatgpt_project_sources() -> None:
    base = "project-sources/chatgpt"
    required = [
        "START_HERE.md",
        "01_SOURCE_MANIFEST.md",
        "02_GOVERNANCE_AUTHORITY_AND_TRUTH.md",
        "03_STARTUP_AND_CANONICAL_SOURCES.md",
        "04_EXECUTION_EFFICIENCY_AND_BRIEFS.md",
        "05_EPISTEMIC_INDEPENDENCE.md",
        "06_CONTINUITY_PROTOCOL.md",
        "07_ERRORS_AND_RESPONSE_CONTRACT.md",
        "08_CRITERION_LAYER.md",
        "CHATGPT_PROJECT_INTRODUCTION.txt",
    ]
    for name in required:
        require_file(f"{base}/{name}")
    start = ROOT / base / "START_HERE.md"
    manifest = ROOT / base / "01_SOURCE_MANIFEST.md"
    independence = ROOT / base / "05_EPISTEMIC_INDEPENDENCE.md"
    errors = ROOT / base / "07_ERRORS_AND_RESPONSE_CONTRACT.md"
    if start.is_file() and "VERIFY_LIVE_AT_USE" not in start.read_text(encoding="utf-8"):
        fail(f"{base}/START_HERE.md: live HEAD policy missing")
    if manifest.is_file() and "archivos adjuntos" not in manifest.read_text(encoding="utf-8"):
        fail(f"{base}/01_SOURCE_MANIFEST.md: attachment replacement missing")
    if independence.is_file():
        text = independence.read_text(encoding="utf-8")
        if "núcleo exacto" not in text or "REVERSED" not in text:
            fail(f"{base}/05_EPISTEMIC_INDEPENDENCE.md: exact claim classification missing")
    if errors.is_file() and "HEAD propio" not in errors.read_text(encoding="utf-8"):
        fail(f"{base}/07_ERRORS_AND_RESPONSE_CONTRACT.md: self-HEAD error missing")

def type_matches(value: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(type_matches(value, item) for item in expected)
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
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            fail(f"{label}: string shorter than minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            fail(f"{label}: string longer than maxLength")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            fail(f"{label}: string does not match pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            fail(f"{label}: number below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            fail(f"{label}: number above maximum")
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
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            fail(f"{label}: too many items")
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

def relative_luminance(hex_color: str) -> float | None:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_color):
        return None
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

def contrast_ratio(foreground: str, background: str) -> float | None:
    first = relative_luminance(foreground)
    second = relative_luminance(background)
    if first is None or second is None:
        return None
    lighter, darker = sorted((first, second), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)

def validate_registries() -> tuple[dict[str, Any], dict[str, Any]]:
    index = load_json("registry/index.json")
    registry_map = index.get("registries", {}) if isinstance(index, dict) else {}
    counts = index.get("counts", {}) if isinstance(index, dict) else {}
    loaded: dict[str, Any] = {}
    for name, relative in registry_map.items():
        registry = load_json(relative)
        loaded[name] = registry
        records = registry.get("records", []) if isinstance(registry, dict) else []
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

def validate_foundation_library(registries: dict[str, Any]) -> None:
    library = load_json("registry/foundation-library.json")
    if registries.get("foundation_library") != library:
        fail("foundation library registry was not loaded canonically")
    design_required = set(library.get("required_design_archetypes", []))
    backend_required = set(library.get("required_backend_domains", []))
    if design_required != REQUIRED_DESIGN_ARCHETYPES:
        fail("foundation library: required design archetype set mismatch")
    if backend_required != REQUIRED_BACKEND_DOMAINS:
        fail("foundation library: required backend domain set mismatch")
    seen_designs: set[str] = set()
    seen_domains: set[str] = set()
    seen_ids: set[str] = set()
    for record in library.get("records", []):
        record_id = record.get("id")
        if record_id in seen_ids:
            fail(f"foundation library: duplicate record {record_id}")
        seen_ids.add(record_id)
        relative = record.get("canonical_path", "")
        if record.get("kind") == "DESIGN_ARCHETYPE":
            document = apply_schema(relative, "schemas/design-archetype.schema.json")
            archetype = document.get("archetype")
            seen_designs.add(archetype)
            if record_id != document.get("id") or record.get("archetype") != archetype:
                fail(f"{relative}: registry identity mismatch")
            roles = {item.get("role") for item in document.get("typography", {}).get("font_roles", [])}
            if roles != {"DISPLAY", "BODY", "MONO"}:
                fail(f"{relative}: typography roles incomplete")
            primitives = {
                item.get("token") for item in document.get("color", {}).get("primitives", [])
            }
            for semantic in document.get("color", {}).get("semantic", []):
                if semantic.get("primitive") not in primitives:
                    fail(f"{relative}: semantic color references unknown primitive")
            for check in document.get("color", {}).get("contrast_checks", []):
                minimum = 4.5 if check.get("usage") == "NORMAL_TEXT" else 3.0
                if check.get("ratio", 0) < minimum:
                    fail(f"{relative}: contrast below {minimum}:1 for {check.get('usage')}")
                foreground = primitives and next(
                    (item.get("value") for item in document["color"]["primitives"]
                     if item.get("token") == check.get("foreground")),
                    None,
                )
                background = primitives and next(
                    (item.get("value") for item in document["color"]["primitives"]
                     if item.get("token") == check.get("background")),
                    None,
                )
                calculated = (
                    contrast_ratio(foreground, background)
                    if isinstance(foreground, str) and isinstance(background, str)
                    else None
                )
                if calculated is None:
                    fail(f"{relative}: contrast references invalid color")
                elif calculated < minimum:
                    fail(f"{relative}: calculated contrast below {minimum}:1")
                elif abs(calculated - check.get("ratio", 0)) > 0.02:
                    fail(f"{relative}: declared contrast differs from calculated ratio")
            accessibility = document.get("accessibility", {})
            for field, minimum in [
                ("normal_text_contrast_min", 4.5),
                ("large_text_contrast_min", 3.0),
                ("ui_contrast_min", 3.0),
                ("pointer_target_min_px", 44),
            ]:
                if accessibility.get(field, 0) < minimum:
                    fail(f"{relative}: accessibility threshold too low for {field}")
            states = set(document.get("interaction_states", []))
            if states != REQUIRED_INTERACTION_STATES:
                fail(f"{relative}: interaction states incomplete")
            modes = document.get("responsive", {}).get("modes", [])
            if [item.get("id") for item in modes] != ["COMPACT", "STANDARD", "EXPANDED", "WIDE"]:
                fail(f"{relative}: responsive modes must use canonical order")
            if modes and modes[0].get("min_width_px") != 0:
                fail(f"{relative}: responsive ranges must start at zero")
            for previous, current in zip(modes, modes[1:]):
                upper = previous.get("max_width_px")
                if not isinstance(upper, int) or current.get("min_width_px") != upper + 1:
                    fail(f"{relative}: responsive ranges have gap or overlap")
            if modes and modes[-1].get("max_width_px") is not None:
                fail(f"{relative}: final responsive range must be unbounded")
            invariant_ids = [
                item.get("id") for item in document.get("responsive", {}).get("invariants", [])
            ]
            if len(invariant_ids) != len(set(invariant_ids)):
                fail(f"{relative}: responsive invariant IDs duplicated")
        elif record.get("kind") == "BACKEND_PATTERN":
            document = apply_schema(relative, "schemas/backend-pattern.schema.json")
            domain = document.get("domain")
            seen_domains.add(domain)
            if record_id != document.get("id") or record.get("domain") != domain:
                fail(f"{relative}: registry identity mismatch")
            if document.get("provider_neutral") is not True:
                fail(f"{relative}: pattern is not provider-neutral")
            boundary = document.get("secret_boundary", {})
            if boundary.get("repository_values_allowed") is not False:
                fail(f"{relative}: repository secret values must be forbidden")
            if boundary.get("reference_only") is not True:
                fail(f"{relative}: environment secrets must be reference-only")
            configuration = document.get("configuration_contract", {})
            client_fields = set(configuration.get("client_replaceable", []))
            environment_fields = set(configuration.get("environment_managed", []))
            if client_fields & environment_fields:
                fail(f"{relative}: client and environment configuration overlap")
            if domain == "PAYMENT_ORCHESTRATION":
                required_client = {
                    "merchant_display_name", "default_currency", "supported_currencies",
                    "locale", "return_route", "cancellation_route",
                }
                required_environment = {
                    "payment_account_reference", "api_credential_reference",
                    "webhook_secret_reference", "provider_endpoint_profile",
                }
                if not required_client <= client_fields:
                    fail(f"{relative}: payment client configuration incomplete")
                if not required_environment <= environment_fields:
                    fail(f"{relative}: payment environment boundary incomplete")
                forbidden_text = " ".join(document.get("forbidden", [])).lower()
                for term in ["pan", "cvc", "importe", "credenciales"]:
                    if term not in forbidden_text:
                        fail(f"{relative}: payment prohibition missing {term}")
        elif record.get("kind") in {"DESIGN_KNOWLEDGE_SOURCE_PACKAGE", "VISUAL_PREFERENCE_PROFILE", "HIGH_FIDELITY_VISUAL_PROTOCOL", "MINIMUM_VISUAL_FOUNDATION"}:
            require_file(relative)
        else:
            fail(f"foundation library: unsupported kind for {record_id}")
    if seen_designs != REQUIRED_DESIGN_ARCHETYPES:
        fail("foundation library: design archetype instances incomplete")
    if seen_domains != REQUIRED_BACKEND_DOMAINS:
        fail("foundation library: backend pattern instances incomplete")

def validate_visual_foundation(registries: dict[str, Any]) -> None:
    profile_path = "foundation-library/visual-preferences/jonathan-martinez.visual-preference-profile.json"
    protocol_path = "foundation-library/visual-protocols/high-fidelity-visual-protocol.json"
    profile = apply_schema(profile_path, "schemas/visual-preference-profile.schema.json")
    protocol = apply_schema(protocol_path, "schemas/high-fidelity-visual-protocol.schema.json")
    dimensions = {"typography", "color", "composition", "imagery_and_render", "materiality", "controls", "information_density", "motion", "accessibility_boundaries"}
    if set(profile.get("dimensions", {})) != dimensions:
        fail("visual preference profile: required dimensions differ")
    if set(profile.get("signals", {})) != {"preferred", "contextual", "insufficient", "rejected"}:
        fail("visual preference profile: signal classifications differ")
    reconciliation_ids = {item.get("id") for item in profile.get("reconciliations", []) if isinstance(item, dict)}
    if reconciliation_ids != {"REC-001", "REC-002", "REC-003", "REC-004", "REC-005", "REC-006", "REC-007"}:
        fail("visual preference profile: required reconciliations differ")
    if profile.get("status") != "DOCUMENTED_WITH_PROPOSED_CODE_BENCHMARK":
        fail("visual preference profile: implementation boundary is unsafe")
    if profile.get("scope_boundary", {}).get("personal_profile_not_global_governance") is not True:
        fail("visual preference profile: global governance boundary is missing")
    stages = [item.get("id") for item in protocol.get("stages", []) if isinstance(item, dict)]
    expected_stages = ["MINIMUM_IMPECCABLE_TECHNICAL_FOUNDATION_GATE", "RESOLVE_PRODUCT_CONTEXT", "QUALIFY_APPLICABLE_REFERENCES", "RESOLVE_CONTEXTUAL_PREFERENCE_SIGNALS", "INTERPRET_PROPOSED_CODE_BENCHMARK_WITHOUT_AUTO_SELECTION", "VISUAL_ACCESSIBILITY_PREFLIGHT", "GENERATE_MONOLITHIC_VISUAL_CALIBRATION", "VISUAL_CALIBRATION_APPROVED", "EXPAND_APPROVED_DIRECTION_TO_ROUTES_AND_STATES", "RESPONSIVE_ACCESSIBILITY_AND_INTERACTION_VALIDATION", "HIGH_FIDELITY_VISUAL_BASELINE_APPROVED", "FINAL_PHASE3_CONTRACT_GENERATION"]
    if stages != expected_stages:
        fail("high-fidelity visual protocol: required stages differ")
    direction = protocol.get("visual_direction_contract", {})
    if direction.get("minimum_directions_before_first_calibration") != 1 or direction.get("selection_authority") != "JONATHAN_MARTINEZ_EXPLICIT_SELECTION":
        fail("high-fidelity visual protocol: reconciled direction and human selection rules differ")
    technical_gate = protocol.get("technical_foundation_gate", {})
    if technical_gate.get("id") != "MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001" or technical_gate.get("required_before_visual_direction_application") is not True or technical_gate.get("pass_with_known_defects") != "PROHIBITED":
        fail("high-fidelity visual protocol: minimum technical foundation gate is unsafe")
    gate = protocol.get("baseline_gate", {})
    if gate.get("approver") != "JONATHAN_MARTINEZ" or gate.get("model_self_approval") != "PROHIBITED" or gate.get("final_phase3_contract_allowed") is not False:
        fail("high-fidelity visual protocol: baseline gate is unsafe")
    if protocol.get("responsive_review", {}).get("widths_px") != [320, 640, 1024, 1440, 1920]:
        fail("high-fidelity visual protocol: responsive widths differ")
    areas = {"TYPOGRAPHIC_HIERARCHY", "COLOR_AND_CONTRAST", "COMPOSITIONAL_BALANCE", "ACTIVE_NEGATIVE_SPACE", "PRODUCT_OR_PURPOSE_PROMINENCE", "IMAGE_AND_RENDER_QUALITY", "MATERIAL_COHERENCE", "CONTROL_AFFORDANCE", "STATE_COMPLETENESS", "CONTENT_STRESS", "ZOOM_AND_REFLOW", "MOTION_AND_REDUCED_MOTION", "STRUCTURAL_GEOMETRY", "COMPONENT_FINISH", "GRID_ALIGNMENT_AND_SPACING", "LAYERS_AND_OVERLAYS", "FORM_BEHAVIOR"}
    if set(protocol.get("review_contract", {}).get("areas", [])) != areas or set(protocol.get("responsive_review", {}).get("areas", [])) != areas:
        fail("high-fidelity visual protocol: review areas differ")
    if protocol.get("status") != "DOCUMENTED_WITH_MINIMUM_TECHNICAL_FOUNDATION_AND_PROPOSED_PREFERENCE_BENCHMARK":
        fail("high-fidelity visual protocol: implementation boundary is unsafe")
    profile_boundary = profile.get("authorization_boundary", {})
    for key in ["application_code", "html_generation", "css_generation", "javascript_generation", "runtime", "product_changes", "deployment", "release"]:
        if profile_boundary.get(key) != "NOT_AUTHORIZED":
            fail("visual preference profile: core authorization boundary is unsafe")
    protocol_boundary = protocol.get("authority_boundary", {})
    for key in ["runtime", "application_code", "product_changes", "release"]:
        if protocol_boundary.get(key) != "NOT_AUTHORIZED":
            fail("high-fidelity visual protocol: core authority boundary is unsafe")
    library_ids = {record.get("id") for record in registries.get("foundation_library", {}).get("records", [])}
    visual_records = registries.get("visual_preferences", {}).get("records", [])
    if {"VPP-JM-001", "HFP-041-001", "MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"} - library_ids:
        fail("visual foundation: canonical artifacts are absent from Foundation Library")
    if len(visual_records) != 1 or visual_records[0].get("id") != "VISUAL-PREFERENCE-REGISTRY-041":
        fail("visual foundation: visual preference registry is incomplete")


def validate_minimum_impeccable_visual_foundation() -> None:
    base = "foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"
    names = [
        "MANIFEST.json", "STANDARD.json", "STRUCTURAL_GEOMETRY_CONTRACT.json",
        "COMPONENT_FINISH_CONTRACT.json", "LAYOUT_INTENT_MAP_CONTRACT.json",
        "FORM_BEHAVIOR_CONTRACT.json", "RESPONSIVE_RESILIENCE_CONTRACT.json",
        "SELF_CORRECTION_CONTRACT.json", "VALIDATION_MATRIX.json",
        "MINIMUM_IMPECCABLE_BASE_001.html",
    ]
    for name in names:
        require_file(f"{base}/{name}")
    manifest = load_json(f"{base}/MANIFEST.json")
    standard = load_json(f"{base}/STANDARD.json")
    correction = load_json(f"{base}/SELF_CORRECTION_CONTRACT.json")
    responsive = load_json(f"{base}/RESPONSIVE_RESILIENCE_CONTRACT.json")
    matrix = load_json(f"{base}/VALIDATION_MATRIX.json")
    if manifest.get("foundation_id") != standard.get("standard_id"):
        fail("minimum visual foundation: identity mismatch")
    if manifest.get("status") not in correction.get("allowed_terminal_states", []):
        fail("minimum visual foundation: invalid terminal state")
    if correction.get("forbidden_terminal_state") != "PASS_WITH_KNOWN_VISUAL_DEFECTS":
        fail("minimum visual foundation: known-defect delivery is not prohibited")
    if correction.get("autonomy_boundary", {}).get("override_human_visual_decision") is not False:
        fail("minimum visual foundation: human visual authority boundary missing")
    if responsive.get("continuous_sweep") != {"from_px": 320, "to_px": 1920, "maximum_step_px": 16}:
        fail("minimum visual foundation: continuous responsive sweep differs")
    case_ids = [case.get("id") for case in matrix.get("cases", [])]
    if len(case_ids) != len(set(case_ids)) or len(case_ids) != 14:
        fail("minimum visual foundation: validation matrix IDs duplicated or incomplete")
    html = (ROOT / base / "MINIMUM_IMPECCABLE_BASE_001.html").read_text(encoding="utf-8").lower()
    for token in ["http://", "https://", "@import", "fetch(", "xmlhttprequest", "overflow-x:hidden", "overflow-x: hidden"]:
        if token in html:
            fail(f"minimum visual foundation: forbidden HTML token {token}")

def validate_foundation_evidence(registries: dict[str, Any]) -> None:
    require_file("foundation-library/evidence/README.md")
    design_paths = sorted(ROOT.glob("foundation-library/evidence/design-archetypes/*.evidence.json"))
    backend_paths = sorted(ROOT.glob("foundation-library/evidence/backend-patterns/*.evidence.json"))
    if len(design_paths) != 5:
        fail("foundation evidence: exactly five design protocols required")
    if len(backend_paths) != 9:
        fail("foundation evidence: exactly nine backend protocols required")
    library = registries.get("foundation_library", {})
    subjects = {record.get("id"): record for record in library.get("records", []) if record.get("kind") in {"DESIGN_ARCHETYPE", "BACKEND_PATTERN"}}
    seen_subjects: set[str] = set()
    seen_protocol_ids: set[str] = set()
    for path in design_paths + backend_paths:
        relative = path.relative_to(ROOT).as_posix()
        protocol = apply_schema(relative, "schemas/foundation-evidence-protocol.schema.json")
        protocol_id = protocol.get("id")
        if protocol_id in seen_protocol_ids:
            fail(f"{relative}: duplicate protocol ID")
        seen_protocol_ids.add(protocol_id)
        subject = protocol.get("subject", {})
        subject_id = subject.get("id")
        if subject_id in seen_subjects:
            fail(f"{relative}: duplicate evidence subject")
        seen_subjects.add(subject_id)
        record = subjects.get(subject_id)
        if not record:
            fail(f"{relative}: evidence subject not registered")
            continue
        if subject.get("canonical_path") != record.get("canonical_path"):
            fail(f"{relative}: subject canonical path mismatch")
        expected_type = record.get("kind")
        if protocol.get("protocol_type") != expected_type:
            fail(f"{relative}: protocol type differs from subject kind")
        category_field = "archetype" if expected_type == "DESIGN_ARCHETYPE" else "domain"
        if subject.get("category") != record.get(category_field):
            fail(f"{relative}: subject category mismatch")
        required = set(protocol.get("required_categories", []))
        case_categories = [case.get("category") for case in protocol.get("cases", [])]
        if set(case_categories) != required:
            fail(f"{relative}: case coverage differs from required categories")
        if len(case_categories) != len(set(case_categories)):
            fail(f"{relative}: each evidence category must have exactly one case")
        case_ids = [case.get("id") for case in protocol.get("cases", [])]
        if len(case_ids) != len(set(case_ids)):
            fail(f"{relative}: evidence case IDs duplicated")
        claims = protocol.get("execution_claims", {})
        if any(claims.values()):
            fail(f"{relative}: unexecuted protocol makes execution claim")
        fixture_policy = protocol.get("synthetic_fixture_policy", {})
        for key in ["real_data_allowed", "personal_data_allowed", "payment_data_allowed", "secrets_allowed"]:
            if fixture_policy.get(key) is not False:
                fail(f"{relative}: unsafe synthetic fixture policy {key}")
        if expected_type == "DESIGN_ARCHETYPE":
            if required != REQUIRED_DESIGN_EVIDENCE:
                fail(f"{relative}: design evidence categories incomplete")
            if protocol.get("responsive_widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
                fail(f"{relative}: responsive evidence widths mismatch")
            responsive_case = next(
                (case for case in protocol.get("cases", [])
                 if case.get("category") == "RESPONSIVE_BOUNDARY_MATRIX"),
                {},
            )
            if responsive_case.get("synthetic_input", {}).get("widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
                fail(f"{relative}: responsive case does not exercise every required width")
        else:
            expected = set(REQUIRED_BACKEND_EVIDENCE)
            if record.get("domain") == "PAYMENT_ORCHESTRATION":
                expected |= REQUIRED_PAYMENT_EVIDENCE
            if required != expected:
                fail(f"{relative}: backend evidence categories incomplete")
            if protocol.get("responsive_widths_px") != []:
                fail(f"{relative}: backend protocol must not declare responsive widths")
    if seen_subjects != set(subjects):
        missing = sorted(set(subjects) - seen_subjects)
        fail("foundation evidence: subjects without protocol: " + ", ".join(missing))

def validate_rag_contracts(registries: dict[str, Any]) -> None:
    expected_paths = {
        "architecture/rag/FEDERATION_CONTRACT.json",
        "architecture/rag/CANONICAL_OWNERSHIP.md",
        "architecture/rag/RETRIEVAL_AND_RANKING.md",
        "architecture/rag/INDEX_LIFECYCLE.md",
        "architecture/rag/WRITE_BOUNDARY.md",
        "architecture/rag/FAILURE_MODES.md",
    }
    registry = registries.get("rag_contracts", {})
    records = registry.get("records", [])
    actual_paths = {record.get("canonical_path") for record in records}
    if actual_paths != expected_paths:
        fail("registry/rag-contracts.json: canonical contract set mismatch")
    for record in records:
        if record.get("status") != "DOCUMENTED_NOT_IMPLEMENTED":
            fail(f"{record.get('id')}: RAG contract has executable status")
        relative = record.get("canonical_path", "")
        if relative.endswith(".md"):
            path = ROOT / relative
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                if record.get("id") not in text:
                    fail(f"{relative}: canonical ID missing")
                if "DOCUMENTED_NOT_IMPLEMENTED" not in text:
                    fail(f"{relative}: non-implementation status missing")
    contract = apply_schema(
        "architecture/rag/FEDERATION_CONTRACT.json",
        "schemas/rag-federation.schema.json",
    )
    namespaces = contract.get("namespaces", [])
    namespace_ids = [item.get("id") for item in namespaces]
    if namespace_ids != REQUIRED_RAG_NAMESPACES:
        fail("RAG federation: namespace order or membership mismatch")
    if len({item.get("isolation_key") for item in namespaces}) != 3:
        fail("RAG federation: namespace isolation keys must be unique")
    project = next((item for item in namespaces if item.get("id") == "PROJECT"), {})
    if "lab_global_governance" not in project.get("forbidden_overrides", []):
        fail("RAG federation: project may override LAB governance")
    if "symphonie_orchestration_contract" not in project.get("forbidden_overrides", []):
        fail("RAG federation: project may override Symphonie contract")
    metadata = contract.get("chunk_metadata", {})
    if metadata.get("required_fields") != REQUIRED_RAG_METADATA:
        fail("RAG federation: required chunk metadata mismatch")
    field_contracts = metadata.get("field_contracts", [])
    field_names = [item.get("name") for item in field_contracts]
    if field_names != REQUIRED_RAG_METADATA:
        fail("RAG federation: metadata field contracts mismatch")
    mutable_fields = {item.get("name") for item in field_contracts if item.get("mutable")}
    if mutable_fields != {"indexed_at"}:
        fail("RAG federation: only indexed_at may be mutable cache metadata")
    if set(contract.get("authority_rules", [])) != REQUIRED_RAG_AUTHORITY_RULES:
        fail("RAG federation: authority rules mismatch")
    retrieval = contract.get("retrieval_pipeline", {})
    if retrieval.get("authority_precedes_similarity") is not True:
        fail("RAG federation: semantic similarity precedes authority")
    stages = retrieval.get("stages", [])
    expected_stage_ids = [
        "RESOLVE_TASK_SCOPE", "SELECT_AUTHORIZED_NAMESPACES",
        "VERIFY_ACTIVE_COMMITS", "FILTER_BY_AUTHORITY_AND_STATUS",
        "RETRIEVE_WITHIN_NAMESPACE", "RANK_AUTHORITY_THEN_RELEVANCE",
        "DETECT_CROSS_SOURCE_CONFLICTS", "RETURN_CITED_CONTEXT",
    ]
    if [item.get("order") for item in stages] != list(range(1, 9)):
        fail("RAG federation: retrieval stage order invalid")
    if [item.get("id") for item in stages] != expected_stage_ids:
        fail("RAG federation: retrieval stages mismatch")
    index = contract.get("index_contract", {})
    if set(index.get("rules", [])) != REQUIRED_RAG_INDEX_RULES:
        fail("RAG federation: index rules mismatch")
    if index.get("role") != "DERIVED_READ_ONLY_CACHE":
        fail("RAG federation: index is not a derived read-only cache")
    conflicts = contract.get("conflict_contract", {})
    if conflicts.get("automatic_merge") is not False:
        fail("RAG federation: automatic conflict merge enabled")
    if conflicts.get("on_confirmed_conflict") != "STOP_CONCLUSION_AND_RETURN_SOURCES":
        fail("RAG federation: confirmed conflict does not stop conclusion")
    boundary = contract.get("write_boundary", {})
    if set(boundary.get("rules", [])) != REQUIRED_RAG_WRITE_RULES:
        fail("RAG federation: write boundary rules mismatch")
    if boundary.get("model_direct_commit") is not False or boundary.get("model_direct_push") is not False:
        fail("RAG federation: model has direct Git authority")
    write_steps = boundary.get("steps", [])
    if [item.get("order") for item in write_steps] != list(range(1, 8)):
        fail("RAG federation: write boundary order invalid")
    security = contract.get("security", {})
    if security.get("cross_project_retrieval_default") is not False:
        fail("RAG federation: cross-project retrieval is enabled by default")
    if security.get("secrets_indexed") is not False:
        fail("RAG federation: secret indexing enabled")
    if security.get("real_data_ingestion_authorized") is not False:
        fail("RAG federation: real-data ingestion authorized")
    if any(contract.get("execution_claims", {}).values()):
        fail("RAG federation: documentary contract makes implementation claim")

def validate_foundation_pilots(registries: dict[str, Any]) -> None:
    pilot_path = "foundation-library/pilots/PILOT-PREMIUM-ECOMMERCE-001/PILOT.json"
    pilot = apply_schema(pilot_path, "schemas/foundation-pilot.schema.json")
    registry = registries.get("foundation_pilots", {})
    records = registry.get("records", [])
    if len(records) != 1 or records[0].get("id") != pilot.get("id"):
        fail("registry/foundation-pilots.json: canonical pilot mismatch")
    if records and records[0].get("canonical_path") != pilot_path:
        fail("registry/foundation-pilots.json: pilot path mismatch")
    if records and records[0].get("status") != "DEFINED_NOT_EXECUTED":
        fail("registry/foundation-pilots.json: pilot has executable status")
    if pilot.get("executor", {}).get("id") != "CODEX":
        fail(f"{pilot_path}: executor must be CODEX")
    if pilot.get("executor", {}).get("autonomous_authority") is not False:
        fail(f"{pilot_path}: Codex has autonomous authority")
    if set(pilot.get("required_delta_areas", [])) != REQUIRED_PILOT_DELTA_AREAS:
        fail(f"{pilot_path}: required delta areas mismatch")
    if set(pilot.get("immutable_requirements", [])) != REQUIRED_PILOT_IMMUTABLES:
        fail(f"{pilot_path}: immutable requirements mismatch")
    if set(pilot.get("required_fixture_types", [])) != REQUIRED_PILOT_FIXTURES:
        fail(f"{pilot_path}: fixture requirements mismatch")
    if pilot.get("responsive_widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
        fail(f"{pilot_path}: responsive widths mismatch")
    for pin_name in ["archetype_pin", "evidence_pin"]:
        pin = pilot.get(pin_name, {})
        relative = pin.get("path", "")
        path = ROOT / relative
        if not path.is_file():
            fail(f"{pilot_path}: missing pinned {pin_name}")
            continue
        actual_hash = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if pin.get("content_sha256") != actual_hash:
            fail(f"{pilot_path}: {pin_name} content hash mismatch")
        if pin.get("lab_commit_sha") != "d3af193f33a08f5714f9e8bdb1dfca5f1c4e4b52":
            fail(f"{pilot_path}: {pin_name} commit pin mismatch")
    documents = pilot.get("documents", {})
    for relative in documents.values():
        require_file(relative)
    delta_path = documents.get("design_delta", "")
    delta = load_json(delta_path)
    if delta.get("pilot_id") != pilot.get("id") or delta.get("status") != "DEFINED_NOT_EXECUTED":
        fail(f"{delta_path}: pilot identity or status mismatch")
    areas = delta.get("areas", [])
    area_ids = [area.get("id") for area in areas]
    if set(area_ids) != REQUIRED_PILOT_DELTA_AREAS or len(area_ids) != len(set(area_ids)):
        fail(f"{delta_path}: delta area coverage mismatch")
    if set(delta.get("immutable_requirements_preserved", [])) != REQUIRED_PILOT_IMMUTABLES:
        fail(f"{delta_path}: immutable preservation mismatch")
    color_area = next((area for area in areas if area.get("id") == "EARTH_TONE_COLOR_PALETTE"), {})
    for check in color_area.get("contrast_checks", []):
        calculated = contrast_ratio(check.get("foreground", ""), check.get("background", ""))
        minimum = 4.5 if check.get("usage") == "NORMAL_TEXT" else 3.0
        if calculated is None or calculated < minimum:
            fail(f"{delta_path}: calculated pilot contrast below threshold")
        elif abs(calculated - check.get("ratio", 0)) > 0.02:
            fail(f"{delta_path}: declared pilot contrast differs from calculation")
    if any(delta.get("execution_claims", {}).values()):
        fail(f"{delta_path}: delta makes execution claim")
    fixtures_path = documents.get("synthetic_fixtures", "")
    fixtures_doc = load_json(fixtures_path)
    fixtures = fixtures_doc.get("fixtures", [])
    fixture_types = [item.get("fixture_type") for item in fixtures]
    fixture_ids = [item.get("id") for item in fixtures]
    if set(fixture_types) != REQUIRED_PILOT_FIXTURES or len(fixture_types) != len(set(fixture_types)):
        fail(f"{fixtures_path}: fixture type coverage mismatch")
    if len(fixture_ids) != len(set(fixture_ids)):
        fail(f"{fixtures_path}: fixture IDs duplicated")
    for fixture in fixtures:
        if not str(fixture.get("id", "")).startswith("SYNTHETIC_FIXTURE_"):
            fail(f"{fixtures_path}: non-synthetic fixture ID")
        if fixture.get("synthetic") is not True:
            fail(f"{fixtures_path}: fixture not marked synthetic")
    policy = fixtures_doc.get("policy", {})
    for key in ["real_client_data", "real_product_data", "real_payment_data"]:
        if policy.get(key) is not False:
            fail(f"{fixtures_path}: unsafe fixture policy {key}")
    if any(fixtures_doc.get("execution_claims", {}).values()):
        fail(f"{fixtures_path}: fixtures make execution claim")
    matrix_path = documents.get("acceptance_matrix", "")
    matrix_doc = load_json(matrix_path)
    expected_requirements = (
        {f"IMMUTABLE_{item}" for item in REQUIRED_PILOT_IMMUTABLES}
        | {f"DELTA_{item}" for item in REQUIRED_PILOT_DELTA_AREAS}
        | {f"RESPONSIVE_WIDTH_{width}" for width in REQUIRED_RESPONSIVE_WIDTHS}
    )
    if set(matrix_doc.get("requirements_covered", [])) != expected_requirements:
        fail(f"{matrix_path}: acceptance requirement coverage mismatch")
    matrix = matrix_doc.get("matrix", [])
    requirements = [item.get("requirement") for item in matrix]
    if set(requirements) != expected_requirements or len(requirements) != len(set(requirements)):
        fail(f"{matrix_path}: acceptance matrix rows mismatch")
    known_fixture_ids = set(fixture_ids)
    evidence = load_json(pilot.get("evidence_pin", {}).get("path", ""))
    known_evidence_cases = {case.get("id") for case in evidence.get("cases", [])}
    for row in matrix:
        if not row.get("measurement") or not row.get("pass_condition") or not row.get("fail_condition"):
            fail(f"{matrix_path}: incomplete oracle for {row.get('id')}")
        if set(row.get("fixture_refs", [])) - known_fixture_ids:
            fail(f"{matrix_path}: unknown fixture reference for {row.get('id')}")
        if row.get("evidence_case") not in known_evidence_cases:
            fail(f"{matrix_path}: unknown evidence case for {row.get('id')}")
    if matrix_doc.get("responsive_widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
        fail(f"{matrix_path}: responsive matrix widths mismatch")
    if matrix_doc.get("result_policy", {}).get("default") != "NOT_EXECUTED":
        fail(f"{matrix_path}: unexecuted result default changed")
    if any(matrix_doc.get("execution_claims", {}).values()):
        fail(f"{matrix_path}: acceptance matrix makes execution claim")
    brief_path = documents.get("brief", "")
    if (ROOT / brief_path).is_file():
        brief = (ROOT / brief_path).read_text(encoding="utf-8")
        if "completamente ficticia" not in brief or "No se implementa checkout" not in brief:
            fail(f"{brief_path}: synthetic or payment boundary missing")
    preconditions_path = documents.get("execution_preconditions", "")
    if (ROOT / preconditions_path).is_file():
        preconditions = (ROOT / preconditions_path).read_text(encoding="utf-8")
        if "autorización posterior" not in preconditions or "fixtures sintéticas" not in preconditions:
            fail(f"{preconditions_path}: execution authority boundary missing")
    if any(pilot.get("execution_claims", {}).values()):
        fail(f"{pilot_path}: unexecuted pilot makes execution claim")


def validate_chatgpt_criterion_layer() -> None:
    base = "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001"
    required = [
        "MANIFEST.json", "CONTRACT.json", "MODULE_SELECTOR.json",
        "RESULT_CONTRACT.json", "ACCEPTANCE_FIXTURES.json", "VALIDATION_EVIDENCE.json",
    ]
    for name in required:
        require_file(f"{base}/{name}")
    manifest = load_json(f"{base}/MANIFEST.json")
    contract = load_json(f"{base}/CONTRACT.json")
    selector = load_json(f"{base}/MODULE_SELECTOR.json")
    result = load_json(f"{base}/RESULT_CONTRACT.json")
    fixtures = load_json(f"{base}/ACCEPTANCE_FIXTURES.json")
    validation = load_json(f"{base}/VALIDATION_EVIDENCE.json")
    expected_modules = [
        "EVIDENCE_AND_CLAIMS", "DESIGN_CRITERION",
        "WEB_ACCESSIBILITY", "CONTEXTUAL_VISUAL_PREFERENCE",
    ]
    if contract.get("layer_id") != "CHATGPT-CRITERION-LAYER-001":
        fail("criterion layer: identity mismatch")
    if contract.get("modules") != expected_modules:
        fail("criterion layer: module order or membership mismatch")
    if [item.get("id") for item in selector.get("modules", [])] != expected_modules:
        fail("criterion layer: selector modules mismatch")
    if any(contract.get("limits", {}).get(key) for key in [
        "runtime", "rag", "embeddings", "vector_database", "symphonie_integration",
        "product_change", "assistive_technology_execution", "wcag_conformance_by_default",
        "autonomous_authority",
    ]):
        fail("criterion layer: forbidden execution or authority effect")
    boundaries = set(result.get("mandatory_boundaries", []))
    for boundary in [
        "STATIC_PASS_DOES_NOT_IMPLY_ACCESSIBILITY",
        "AUTOMATION_DOES_NOT_ESTABLISH_WCAG_CONFORMANCE",
        "PREFERENCE_IS_NOT_STANDARD",
        "HEURISTIC_IS_NOT_EVIDENCE",
        "EVIDENCE_IS_NOT_AUTHORIZATION",
    ]:
        if boundary not in boundaries:
            fail(f"criterion layer: missing boundary {boundary}")
    fixture_records = fixtures.get("fixtures", [])
    fixture_ids = [item.get("id") for item in fixture_records]
    if len(fixture_ids) != len(set(fixture_ids)) or len(fixture_ids) != manifest.get("counts", {}).get("fixtures"):
        fail("criterion layer: fixture IDs duplicated or count mismatch")
    known = set(expected_modules)
    for fixture in fixture_records:
        expected = set(fixture.get("expected_modules", []))
        forbidden = set(fixture.get("forbidden_modules", []))
        if (expected | forbidden) - known:
            fail(f"criterion layer: unknown module in {fixture.get('id')}")
        if expected & forbidden:
            fail(f"criterion layer: contradictory oracle in {fixture.get('id')}")
    claims = validation.get("result_claims", {})
    if claims.get("selector_deterministically_validated") is not True:
        fail("criterion layer: selector validation claim missing")
    if claims.get("terra_behavior_validated") is not False:
        fail("criterion layer: unsupported Terra validation claim")
    self_correction = contract.get("self_correction", {})
    if self_correction.get("known_correctable_defect_blocks_delivery") is not True or self_correction.get("structural_defect_requires_reconstruction") is not True or self_correction.get("pass_with_known_visual_defects") is not False:
        fail("criterion layer: minimum visual self-correction boundary missing")
    if result.get("forbidden_visual_artifact_state") != "PASS_WITH_KNOWN_VISUAL_DEFECTS":
        fail("criterion layer: known-defect result state not prohibited")


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
    symphonie = next(
        (record for record in registries["projects"].get("records", []) if record.get("id") == "symphonie"),
        {},
    )
    actual = {
        "methodology_version": state.get("methodology", {}).get("version"),
        "active_project": state.get("active_project"),
        "current_phase": state.get("current_phase"),
        "project_statuses": {r["id"]: r["status"] for r in registries["projects"].get("records", [])},
        "decisions_in_force": state.get("decisions_in_force"),
        "open_errors": state.get("open_errors"),
        "validated_patterns": state.get("validated_patterns"),
        "registry_counts": index.get("counts"),
        "symphonie": {
            "head": state.get("verified_external_heads", {}).get("symphonie"),
            "fileset": symphonie.get("fileset"),
            "total_phases": 8,
        },
        "authorization_state": state.get("authorization_state"),
    }
    for key, value in actual.items():
        if expected.get(key) != value:
            fail(f"expected-state mismatch for {key}")

def main() -> int:
    validate_text()
    validate_chatgpt_project_sources()
    validate_chatgpt_criterion_layer()
    index, registries = validate_registries()
    validate_projects(registries)
    validate_decisions(registries)
    state = validate_current_state(registries)
    validate_foundation_library(registries)
    validate_visual_foundation(registries)
    validate_minimum_impeccable_visual_foundation()
    validate_foundation_evidence(registries)
    validate_rag_contracts(registries)
    validate_foundation_pilots(registries)
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
    print("Foundation evidence protocols: PASS")
    print("Minimum impeccable visual foundation: PASS")
    print("Transversal RAG contracts: PASS")
    print("Foundation pilot definition: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
