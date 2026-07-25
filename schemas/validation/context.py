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

ROOT = Path(__file__).resolve().parents[2]
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
IMMUTABLE_EXTERNAL_AUDIT_TEXT_HASHES = {
    "projects/lab/external-audits/AUDIT-CLAUDE-FULL-RAG-FAILURE-DISCRIMINATION-EXECUTION-002-001/AUDIT_REPORT.md":
        "2096b45a6ab907d73d410d050a4a760f4d3deb07918acaaeec6233920a048bfb",
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
    code_exts = {".js", ".jsx", ".ts", ".tsx", ".py", ".html", ".css", ".scss", ".vue", ".svelte", ".sh", ".ps1", ".sql"}
    exception_doc = load_json("projects/lab/evidence/EVD-LAB-SYMPHONIE-ALL-PHASES-082.json")
    exceptions = {
        item.get("path"): item
        for item in exception_doc.get("line_limit_reconciliation", {}).get("classifications", [])
        if isinstance(item, dict)
    }
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in code_exts | {".md", ".json"} and path.name != ".gitignore":
            continue
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        immutable_hash = IMMUTABLE_EXTERNAL_AUDIT_TEXT_HASHES.get(relative)
        immutable_bytes_verified = (
            immutable_hash is not None
            and hashlib.sha256(data).hexdigest() == immutable_hash
        )
        if immutable_hash is not None and not immutable_bytes_verified:
            fail(f"{relative}: immutable external audit bytes changed")
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
            if line.rstrip(" \t") != line and not immutable_bytes_verified:
                fail(f"{relative}:{number}: trailing whitespace")
        physical_lines = len(text.splitlines())
        if path.suffix.lower() == ".md" and physical_lines > 600:
            fail(f"{relative}: exceeds 600 physical lines")
        if path.suffix.lower() in code_exts and physical_lines > 280:
            exception = exceptions.get(relative, {})
            if exception.get("classification") not in {"GENERATED", "VENDORED", "HISTORICAL_IMMUTABLE", "EXTERNAL_FORMAT_CONSTRAINT", "LOCKFILE", "SNAPSHOT", "DATASET"}:
                fail(f"{relative}: exceeds 280 physical lines without a classified exception")
            if not exception.get("reason"):
                fail(f"{relative}: over-limit exception lacks a reason")
            if exception.get("modified") is not False:
                fail(f"{relative}: over-limit exception must be unmodified")
            if exception.get("classification") == "EXTERNAL_FORMAT_CONSTRAINT" and path.suffix.lower() == ".html" and not text.startswith("<!-- SYMPHONIE_MONOLITHIC_PRELIMINARY_VISUAL_EXCEPTION: AUTHORIZED_FOR_PRELIMINARY_VISUAL_VALIDATION_ONLY -->"):
                fail(f"{relative}: monolithic HTML exception header missing")
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
