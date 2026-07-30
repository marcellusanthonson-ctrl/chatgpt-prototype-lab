#!/usr/bin/env python3
"""Materialize and validate the bounded M1A integration-factory artifacts."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:
    print(
        "Missing validation-only dependency. Run: "
        "python -m pip install --target .validation/python "
        "--requirement scripts/requirements-integration-factory-validation.txt",
        file=sys.stderr,
    )
    raise


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "architecture/integrations/schemas"
TEMPLATE_DIR = ROOT / "architecture/integrations/templates"
OVERLAY_DIR = TEMPLATE_DIR / "criterion-module"
AUTH_TEMPLATE_DIR = TEMPLATE_DIR / "authorizations"
M1A_DIR = ROOT / "architecture/integrations/migration/M1A"
PACKAGE_DIR = M1A_DIR / "generated"

EXPECTED_PARENT_HEAD = "babcbf5427dfc555a93cc65ba99b34e9452e8a25"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
RECORDED_AT = "2026-07-30T17:39:00-04:00"
AUTH_REF = (
    "projects/lab/authorizations/"
    "AUTHORIZATION_LAB_M1A_EXECUTABLE_SCHEMA_TEMPLATE_AND_OVERLAY_MATERIALIZATION_153.json"
)
BRIEF_REF = (
    "projects/lab/briefs/"
    "CODEX_M1A_EXECUTABLE_SCHEMA_TEMPLATE_AND_OVERLAY_MATERIALIZATION_001.json"
)
SELECTOR_REF = (
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
)
FIXTURE_REF = (
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/ACCEPTANCE_FIXTURES.json"
)
RESULT_REF = (
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/RESULT_CONTRACT.json"
)
CONTRACT_REF = (
    "project-sources/chatgpt/criterion-layer/"
    "CHATGPT-CRITERION-LAYER-001/CONTRACT.json"
)
M0_MODULE_REF = "architecture/integrations/migration/M0/CURRENT_MODULE_INVENTORY.json"
M0_SIGNAL_REF = "architecture/integrations/migration/M0/CURRENT_SIGNAL_MAP.json"
M0_COMPOSITION_REF = "architecture/integrations/migration/M0/CURRENT_COMPOSITION_RULES.json"
M0_FIXTURE_REF = "architecture/integrations/migration/M0/BASELINE_FIXTURES.json"

MODULE_IDS = [
    "EVIDENCE_AND_CLAIMS",
    "DESIGN_CRITERION",
    "WEB_ACCESSIBILITY",
    "CONTEXTUAL_VISUAL_PREFERENCE",
]

SCHEMA_FILES = [
    "integration-intake.schema.json",
    "integration-manifest.schema.json",
    "activation-contract.schema.json",
    "input-contract.schema.json",
    "result-contract.schema.json",
    "composition-contract.schema.json",
    "test-design.schema.json",
    "scoring-and-gates.schema.json",
    "rollback.schema.json",
    "operational-trust-preflight.schema.json",
]

TEMPLATE_FILES = [
    "INTEGRATION_INTAKE.template.json",
    "MANIFEST.template.json",
    "ACTIVATION_CONTRACT.template.json",
    "INPUT_CONTRACT.template.json",
    "RESULT_CONTRACT.template.json",
    "COMPOSITION_CONTRACT.template.json",
    "CONFLICTS.template.json",
    "MISUSE_RISKS.template.json",
    "FIXTURES.template.json",
    "TEST_DESIGN.template.json",
    "SCORING_AND_GATES.template.json",
    "ROLLBACK.template.json",
    "VALIDATION_EVIDENCE.template.json",
]

OVERLAY_FILES = [
    "ACTIVATION_DISCRIMINATION.overlay.json",
    "NEGATIVE_TRANSFER.overlay.json",
    "TOKEN_AND_LATENCY.overlay.json",
]

AUTH_TEMPLATE_FILES = [
    "DOCUMENTARY_DESIGN_AUTHORIZATION.template.json",
    "TEST_EXECUTION_AUTHORIZATION.template.json",
    "READ_ONLY_EXTERNAL_AUDIT_AUTHORIZATION.template.json",
    "INTEGRATION_AUTHORIZATION.template.json",
    "SUSPENSION_OR_ROLLBACK_AUTHORIZATION.template.json",
]

PACKAGE_ARTIFACTS = [
    "INTEGRATION_INTAKE.json",
    "MANIFEST.json",
    "ACTIVATION_CONTRACT.json",
    "INPUT_CONTRACT.json",
    "RESULT_CONTRACT.json",
    "COMPOSITION_CONTRACT.json",
    "CONFLICTS.json",
    "MISUSE_RISKS.json",
    "FIXTURES.json",
    "TEST_DESIGN.json",
    "SCORING_AND_GATES.json",
    "ROLLBACK.json",
    "VALIDATION_EVIDENCE.json",
    "OPERATIONAL_TRUST_PREFLIGHT.json",
]

SCHEMA_BY_ARTIFACT = {
    "INTEGRATION_INTAKE.json": "integration-intake.schema.json",
    "MANIFEST.json": "integration-manifest.schema.json",
    "ACTIVATION_CONTRACT.json": "activation-contract.schema.json",
    "INPUT_CONTRACT.json": "input-contract.schema.json",
    "RESULT_CONTRACT.json": "result-contract.schema.json",
    "COMPOSITION_CONTRACT.json": "composition-contract.schema.json",
    "TEST_DESIGN.json": "test-design.schema.json",
    "SCORING_AND_GATES.json": "scoring-and-gates.schema.json",
    "ROLLBACK.json": "rollback.schema.json",
    "OPERATIONAL_TRUST_PREFLIGHT.json": "operational-trust-preflight.schema.json",
}


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def normalized_digest(items: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for path in sorted(items):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(canonical_bytes(items[path]))
        digest.update(b"\0")
    return digest.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def unresolved(field: str, source_refs: list[str]) -> dict[str, Any]:
    return {
        "status": "UNRESOLVED",
        "reason": "NOT_ESTABLISHED_BY_CANONICAL_SOURCES",
        "required_resolution": f"SUPPLY_{field.upper()}_THROUGH_A_SEPARATE_GOVERNED_SOURCE",
        "source_refs": source_refs,
    }


UNRESOLVED_SCHEMA = {
    "type": "object",
    "required": ["status", "reason", "required_resolution", "source_refs"],
    "properties": {
        "status": {"const": "UNRESOLVED"},
        "reason": {"type": "string", "minLength": 1},
        "required_resolution": {"type": "string", "minLength": 1},
        "source_refs": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
    },
    "additionalProperties": False,
}


def text_or_unresolved() -> dict[str, Any]:
    return {
        "oneOf": [
            {"type": "string", "minLength": 1},
            {"$ref": "#/$defs/unresolved"},
        ]
    }


def integer_or_unresolved() -> dict[str, Any]:
    return {
        "oneOf": [
            {"type": "integer", "minimum": 0},
            {"$ref": "#/$defs/unresolved"},
        ]
    }


def array_of_text(min_items: int = 0) -> dict[str, Any]:
    return {
        "type": "array",
        "minItems": min_items,
        "items": {"type": "string", "minLength": 1},
    }


def array_or_unresolved(min_items: int = 0) -> dict[str, Any]:
    return {
        "oneOf": [
            array_of_text(min_items),
            {"$ref": "#/$defs/unresolved"},
        ]
    }


def schema_document(
    filename: str,
    artifact_type: str,
    required: list[str],
    properties: dict[str, Any],
) -> dict[str, Any]:
    safety_required = [
        "schema_version",
        "artifact_type",
        "authority_effect",
        "runtime_effect",
        "automatic_activation",
        "implementation_authorized",
    ]
    safety_properties = {
        "schema_version": {"const": "1.0.0"},
        "artifact_type": {"const": artifact_type},
        "authority_effect": {"const": "NONE"},
        "runtime_effect": {"const": "NONE"},
        "automatic_activation": {"const": False},
        "implementation_authorized": {"const": False},
    }
    return {
        "$schema": DIALECT,
        "$id": f"https://lab.local/architecture/integrations/schemas/{filename}",
        "title": artifact_type,
        "description": (
            "Executable provider-neutral M1A contract. Structured UNRESOLVED "
            "values are permitted only where canonical sources do not establish a value."
        ),
        "type": "object",
        "required": list(dict.fromkeys(safety_required + required)),
        "properties": safety_properties | properties,
        "$defs": {"unresolved": UNRESOLVED_SCHEMA},
        "additionalProperties": True,
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }


def build_schemas() -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    schemas["integration-intake.schema.json"] = schema_document(
        "integration-intake.schema.json",
        "INTEGRATION_INTAKE",
        [
            "integration_id",
            "profile",
            "problem",
            "producer",
            "consumer",
            "value_hypothesis",
            "risk_signals",
            "rollback_strategy",
            "source_refs",
        ],
        {
            "integration_id": {"type": "string", "minLength": 1},
            "profile": {"const": "CRITERION_MODULE"},
            "problem": text_or_unresolved(),
            "producer": text_or_unresolved(),
            "consumer": {"type": "string", "minLength": 1},
            "value_hypothesis": text_or_unresolved(),
            "risk_signals": array_of_text(1),
            "rollback_strategy": {"type": "string", "minLength": 1},
            "source_refs": array_of_text(1),
        },
    )
    schemas["integration-manifest.schema.json"] = schema_document(
        "integration-manifest.schema.json",
        "MANIFEST",
        [
            "integration_id",
            "module_id",
            "version",
            "status",
            "profile",
            "producer",
            "consumer",
            "contract_refs",
            "evidence_refs",
            "compatibility",
            "rollback_ref",
        ],
        {
            "integration_id": {"type": "string", "minLength": 1},
            "module_id": {"enum": MODULE_IDS},
            "version": text_or_unresolved(),
            "status": {"const": "CANDIDATE"},
            "profile": {"const": "CRITERION_MODULE"},
            "producer": text_or_unresolved(),
            "consumer": {"type": "string", "minLength": 1},
            "contract_refs": array_of_text(1),
            "evidence_refs": array_of_text(1),
            "compatibility": {
                "type": "object",
                "required": ["compatible_with", "conflicts_with"],
                "properties": {
                    "compatible_with": array_of_text(),
                    "conflicts_with": array_or_unresolved(),
                },
            },
            "rollback_ref": {"const": "ROLLBACK.json"},
        },
    )
    schemas["activation-contract.schema.json"] = schema_document(
        "activation-contract.schema.json",
        "ACTIVATION_CONTRACT",
        [
            "active_when",
            "inactive_when",
            "limited_when",
            "fail_closed_when",
            "automatic_activation",
        ],
        {
            "module_id": {"enum": MODULE_IDS},
            "active_when": {"type": "object", "minProperties": 2},
            "inactive_when": {"type": "object", "minProperties": 1},
            "limited_when": text_or_unresolved(),
            "fail_closed_when": array_of_text(1),
        },
    )
    schemas["input-contract.schema.json"] = schema_document(
        "input-contract.schema.json",
        "INPUT_CONTRACT",
        [
            "required_inputs",
            "optional_inputs",
            "forbidden_inputs",
            "minimum_context_rule",
        ],
        {
            "required_inputs": array_of_text(1),
            "optional_inputs": array_of_text(),
            "forbidden_inputs": array_of_text(1),
            "minimum_context_rule": {"type": "string", "minLength": 1},
        },
    )
    schemas["result-contract.schema.json"] = schema_document(
        "result-contract.schema.json",
        "RESULT_CONTRACT",
        [
            "result_envelope",
            "allowed_claims",
            "required_uncertainties",
            "evidence_requirements",
            "authority_effect",
        ],
        {
            "result_envelope": array_of_text(1),
            "allowed_claims": array_of_text(1),
            "required_uncertainties": array_of_text(1),
            "evidence_requirements": array_of_text(1),
        },
    )
    schemas["composition-contract.schema.json"] = schema_document(
        "composition-contract.schema.json",
        "COMPOSITION_CONTRACT",
        [
            "precedence_class",
            "compatible_with",
            "conflicts_with",
            "supersedes",
            "maximum_role",
            "conflict_keys",
            "composition_rules",
            "exclusions",
            "empty_set_abstention",
        ],
        {
            "precedence_class": {"type": "integer", "minimum": 1},
            "compatible_with": array_of_text(),
            "conflicts_with": array_or_unresolved(),
            "supersedes": array_of_text(),
            "maximum_role": {"type": "string", "minLength": 1},
            "conflict_keys": array_of_text(),
            "composition_rules": array_of_text(6),
            "exclusions": {"type": "array", "minItems": 1},
            "empty_set_abstention": {"const": True},
        },
    )
    schemas["test-design.schema.json"] = schema_document(
        "test-design.schema.json",
        "TEST_DESIGN",
        [
            "test_id",
            "status",
            "arms",
            "fixture_families",
            "minimum_outputs",
            "blinding",
            "telemetry",
            "stop_conditions",
        ],
        {
            "test_id": {"type": "string", "minLength": 1},
            "status": {"const": "DRAFT_NOT_AUTHORIZED"},
            "arms": {"type": "array", "minItems": 1},
            "fixture_families": array_of_text(1),
            "minimum_outputs": integer_or_unresolved(),
            "blinding": text_or_unresolved(),
            "telemetry": array_of_text(1),
            "stop_conditions": array_of_text(1),
        },
    )
    schemas["scoring-and-gates.schema.json"] = schema_document(
        "scoring-and-gates.schema.json",
        "SCORING_AND_GATES",
        [
            "dimensions",
            "penalties",
            "thresholds",
            "zero_tolerance_events",
            "aggregation",
            "promotion_rules",
        ],
        {
            "dimensions": {"type": "array", "minItems": 1},
            "penalties": {"type": "array", "minItems": 1},
            "thresholds": {
                "anyOf": [
                    {"type": "object", "minProperties": 1},
                    {"$ref": "#/$defs/unresolved"},
                ]
            },
            "zero_tolerance_events": array_of_text(1),
            "aggregation": text_or_unresolved(),
            "promotion_rules": array_of_text(1),
        },
    )
    schemas["rollback.schema.json"] = schema_document(
        "rollback.schema.json",
        "ROLLBACK",
        [
            "trigger_conditions",
            "steps",
            "baseline_verification",
            "evidence_retention",
            "authority_required",
        ],
        {
            "trigger_conditions": array_of_text(1),
            "steps": array_of_text(1),
            "baseline_verification": array_of_text(1),
            "evidence_retention": {"type": "string", "minLength": 1},
            "authority_required": {"const": True},
        },
    )
    schemas["operational-trust-preflight.schema.json"] = schema_document(
        "operational-trust-preflight.schema.json",
        "OPERATIONAL_TRUST_PREFLIGHT",
        [
            "required",
            "reference_environment",
            "portable_capabilities",
            "provider_adapter",
            "gates",
            "teardown",
            "normalized_result",
        ],
        {
            "required": {"const": False},
            "reference_environment": {"const": "REPOSITORY_ONLY_LOCAL_VALIDATION"},
            "portable_capabilities": array_of_text(1),
            "provider_adapter": {"const": "NONE"},
            "gates": array_of_text(1),
            "teardown": array_of_text(1),
            "normalized_result": {"const": "NOT_REQUIRED"},
        },
    )
    return schemas


def source(path: str) -> dict[str, str]:
    return {"$source": path}


def base_render(artifact_type: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "artifact_type": artifact_type,
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }


def template_document(
    filename: str,
    target_artifact: str,
    schema_ref: str | None,
    render: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "template_id": filename.removesuffix(".template.json"),
        "status": "EXECUTABLE_TEMPLATE",
        "profile": "COMMON",
        "target_artifact": target_artifact,
        "schema_ref": schema_ref,
        "render": render,
        "unresolved_policy": {
            "representation": "STRUCTURED_UNRESOLVED_OBJECT",
            "inference_forbidden": True,
            "silent_default_forbidden": True,
        },
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }


def build_templates() -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    templates["INTEGRATION_INTAKE.template.json"] = template_document(
        "INTEGRATION_INTAKE.template.json",
        "INTEGRATION_INTAKE.json",
        "architecture/integrations/schemas/integration-intake.schema.json",
        base_render("INTEGRATION_INTAKE")
        | {
            "integration_id": source("integration_id"),
            "profile": "CRITERION_MODULE",
            "problem": source("problem"),
            "producer": source("producer"),
            "consumer": "CHATGPT_PROJECT",
            "value_hypothesis": source("value_hypothesis"),
            "risk_signals": source("risk_signals"),
            "rollback_strategy": "DISCARD_ISOLATED_CANDIDATE_AND_RETAIN_STATIC_SELECTOR",
            "source_refs": source("source_refs"),
        },
    )
    templates["MANIFEST.template.json"] = template_document(
        "MANIFEST.template.json",
        "MANIFEST.json",
        "architecture/integrations/schemas/integration-manifest.schema.json",
        base_render("MANIFEST")
        | {
            "integration_id": source("integration_id"),
            "module_id": source("module_id"),
            "version": source("version"),
            "status": "CANDIDATE",
            "profile": "CRITERION_MODULE",
            "producer": source("producer"),
            "consumer": "CHATGPT_PROJECT",
            "contract_refs": source("contract_refs"),
            "evidence_refs": source("evidence_refs"),
            "compatibility": source("compatibility"),
            "rollback_ref": "ROLLBACK.json",
        },
    )
    templates["ACTIVATION_CONTRACT.template.json"] = template_document(
        "ACTIVATION_CONTRACT.template.json",
        "ACTIVATION_CONTRACT.json",
        "architecture/integrations/schemas/activation-contract.schema.json",
        base_render("ACTIVATION_CONTRACT")
        | {
            "module_id": source("module_id"),
            "active_when": source("active_when"),
            "inactive_when": source("inactive_when"),
            "limited_when": source("limited_when"),
            "fail_closed_when": [
                "SOURCE_REFERENCE_MISSING",
                "ACTIVATION_INPUT_INCOMPLETE",
                "AUTHORITY_INFERENCE_ATTEMPT",
            ],
        },
    )
    templates["INPUT_CONTRACT.template.json"] = template_document(
        "INPUT_CONTRACT.template.json",
        "INPUT_CONTRACT.json",
        "architecture/integrations/schemas/input-contract.schema.json",
        base_render("INPUT_CONTRACT")
        | {
            "required_inputs": source("required_inputs"),
            "optional_inputs": source("optional_inputs"),
            "forbidden_inputs": [
                "IMPLICIT_AUTHORIZATION",
                "UNDECLARED_PROVIDER_SPECIFIC_CORE_VALUE",
                "UNREFERENCED_MATERIAL_CLAIM",
            ],
            "minimum_context_rule": "ONLY_EXPLICIT_INPUTS_AND_REFERENCED_CANONICAL_SOURCES",
        },
    )
    templates["RESULT_CONTRACT.template.json"] = template_document(
        "RESULT_CONTRACT.template.json",
        "RESULT_CONTRACT.json",
        "architecture/integrations/schemas/result-contract.schema.json",
        base_render("RESULT_CONTRACT")
        | {
            "result_envelope": source("result_envelope"),
            "allowed_claims": source("allowed_claims"),
            "required_uncertainties": source("required_uncertainties"),
            "evidence_requirements": source("evidence_requirements"),
        },
    )
    templates["COMPOSITION_CONTRACT.template.json"] = template_document(
        "COMPOSITION_CONTRACT.template.json",
        "COMPOSITION_CONTRACT.json",
        "architecture/integrations/schemas/composition-contract.schema.json",
        base_render("COMPOSITION_CONTRACT")
        | {
            "precedence_class": source("precedence_class"),
            "compatible_with": source("compatible_with"),
            "conflicts_with": source("conflicts_with"),
            "supersedes": [],
            "maximum_role": source("maximum_role"),
            "conflict_keys": [],
            "composition_rules": source("composition_rules"),
            "exclusions": source("exclusions"),
            "empty_set_abstention": True,
        },
    )
    templates["CONFLICTS.template.json"] = template_document(
        "CONFLICTS.template.json",
        "CONFLICTS.json",
        None,
        base_render("CONFLICTS")
        | {
            "module_id": source("module_id"),
            "known_conflicts": [],
            "unassessed_conflicts": source("conflicts_with"),
            "conflict_resolution": "FAIL_CLOSED_AND_REQUIRE_SEPARATE_HUMAN_DECISION",
            "source_refs": source("source_refs"),
        },
    )
    templates["MISUSE_RISKS.template.json"] = template_document(
        "MISUSE_RISKS.template.json",
        "MISUSE_RISKS.json",
        None,
        base_render("MISUSE_RISKS")
        | {
            "module_id": source("module_id"),
            "risks": source("misuse_risks"),
            "zero_tolerance_events": [
                "AUTHORITY_INFERENCE",
                "AUTOMATIC_ACTIVATION",
                "RUNTIME_OR_SELECTOR_MUTATION",
            ],
            "source_refs": source("source_refs"),
        },
    )
    templates["FIXTURES.template.json"] = template_document(
        "FIXTURES.template.json",
        "FIXTURES.json",
        None,
        base_render("FIXTURES")
        | {
            "module_id": source("module_id"),
            "baseline_fixture_blob_sha": source("fixture_blob_sha"),
            "all_baseline_fixture_refs": source("all_fixture_refs"),
            "applicable_fixture_refs": source("applicable_fixture_refs"),
            "negative_transfer_fixture_refs": source("negative_fixture_refs"),
            "fixture_source_ref": FIXTURE_REF,
        },
    )
    templates["TEST_DESIGN.template.json"] = template_document(
        "TEST_DESIGN.template.json",
        "TEST_DESIGN.json",
        "architecture/integrations/schemas/test-design.schema.json",
        base_render("TEST_DESIGN")
        | {
            "test_id": source("test_id"),
            "status": "DRAFT_NOT_AUTHORIZED",
            "arms": source("test_arms"),
            "fixture_families": [
                "ACTIVATION_DISCRIMINATION",
                "NEGATIVE_TRANSFER",
                "BASELINE_PRESERVATION",
            ],
            "minimum_outputs": source("minimum_outputs"),
            "blinding": source("blinding"),
            "telemetry": [
                "NORMALIZED_RESULT_DIGEST",
                "FAILURE_AND_DIVERGENCE_LOG",
                "TOKEN_AND_LATENCY_PLACEHOLDER_WITHOUT_RUNTIME_MEASUREMENT",
            ],
            "stop_conditions": [
                "BASELINE_HASH_MISMATCH",
                "AUTHORITY_INFERENCE",
                "RUNTIME_EFFECT_DETECTED",
                "MISSING_REFERENCE",
            ],
        },
    )
    templates["SCORING_AND_GATES.template.json"] = template_document(
        "SCORING_AND_GATES.template.json",
        "SCORING_AND_GATES.json",
        "architecture/integrations/schemas/scoring-and-gates.schema.json",
        base_render("SCORING_AND_GATES")
        | {
            "dimensions": source("scoring_dimensions"),
            "penalties": source("scoring_penalties"),
            "thresholds": source("scoring_thresholds"),
            "zero_tolerance_events": [
                "AUTHORITY_INFERENCE",
                "SELECTOR_DRIFT",
                "RUNTIME_EFFECT",
                "M0_BASELINE_DIVERGENCE",
            ],
            "aggregation": source("aggregation"),
            "promotion_rules": [
                "TECHNICAL_PASS_DOES_NOT_AUTHORIZE_TEST_EXECUTION",
                "TESTED_DOES_NOT_IMPLY_AUTHORIZED",
                "AUDITED_DOES_NOT_IMPLY_INTEGRATED",
                "SEPARATE_HUMAN_AUTHORIZATION_REQUIRED",
            ],
        },
    )
    templates["ROLLBACK.template.json"] = template_document(
        "ROLLBACK.template.json",
        "ROLLBACK.json",
        "architecture/integrations/schemas/rollback.schema.json",
        base_render("ROLLBACK")
        | {
            "trigger_conditions": [
                "ANY_VALIDATION_FAILURE",
                "ANY_BASELINE_DIVERGENCE",
                "ANY_AUTHORITY_OR_RUNTIME_DRIFT",
                "HUMAN_REJECTION",
            ],
            "steps": [
                "DISCARD_ISOLATED_GENERATED_PACKAGE",
                "RETAIN_UNMODIFIED_STATIC_SELECTOR",
                "RETAIN_MACHINE_READABLE_FAILURE_EVIDENCE",
            ],
            "baseline_verification": [
                "VERIFY_SELECTOR_GIT_BLOB_SHA",
                "VERIFY_ACCEPTANCE_FIXTURE_GIT_BLOB_SHA",
                "VERIFY_M0_COUNTS_AND_COMPOSITION",
            ],
            "evidence_retention": "RETAIN_ALL_FAILURES_AND_DIVERGENCES_IN_M1A_VALIDATION_RESULTS",
            "authority_required": True,
        },
    )
    templates["VALIDATION_EVIDENCE.template.json"] = template_document(
        "VALIDATION_EVIDENCE.template.json",
        "VALIDATION_EVIDENCE.json",
        None,
        base_render("VALIDATION_EVIDENCE")
        | {
            "module_id": source("module_id"),
            "status": "VALIDATED_ISOLATED_CANDIDATE_NOT_AUTHORIZED",
            "schema_validations": source("schema_validations"),
            "baseline_refs": [M0_MODULE_REF, M0_SIGNAL_REF, M0_COMPOSITION_REF, M0_FIXTURE_REF],
            "failures": [],
            "divergences": [],
            "test_authorized": False,
            "integration_authorized": False,
        },
    )
    return templates


def overlay_document(
    filename: str, target: str, path: list[str], value: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "overlay_id": filename.removesuffix(".overlay.json"),
        "status": "EXECUTABLE_OVERLAY",
        "profile": "CRITERION_MODULE",
        "applies_to": target,
        "operations": [{"operation": "SET", "path": path, "value": value}],
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }


def build_overlays() -> dict[str, dict[str, Any]]:
    return {
        "ACTIVATION_DISCRIMINATION.overlay.json": overlay_document(
            "ACTIVATION_DISCRIMINATION.overlay.json",
            "ACTIVATION_CONTRACT.json",
            ["profile_controls", "activation_discrimination"],
            {
                "required": True,
                "positive_fixture_refs": source("applicable_fixture_refs"),
                "negative_fixture_refs": source("negative_fixture_refs"),
                "empty_set_preserved": True,
            },
        ),
        "NEGATIVE_TRANSFER.overlay.json": overlay_document(
            "NEGATIVE_TRANSFER.overlay.json",
            "MISUSE_RISKS.json",
            ["profile_controls", "negative_transfer"],
            {
                "required": True,
                "forbidden_module_contamination": source("negative_fixture_refs"),
                "failure_retention": "MACHINE_READABLE",
            },
        ),
        "TOKEN_AND_LATENCY.overlay.json": overlay_document(
            "TOKEN_AND_LATENCY.overlay.json",
            "VALIDATION_EVIDENCE.json",
            ["profile_controls", "token_and_latency"],
            {
                "status": "NOT_MEASURED_M1A_REPOSITORY_ONLY",
                "runtime_measurement_authorized": False,
                "future_test_contract_required": True,
            },
        ),
    }


def build_authorization_templates() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for filename in AUTH_TEMPLATE_FILES:
        kind = filename.removesuffix(".template.json")
        result[filename] = {
            "schema_version": "1.0.0",
            "template_id": kind,
            "status": "EXECUTABLE_DRAFT_GENERATOR",
            "render": {
                "schema_version": "1.0.0",
                "authorization_id": unresolved("authorization_id", [AUTH_REF]),
                "project_id": unresolved("project_id", [AUTH_REF]),
                "status": "DRAFT",
                "approved_by": unresolved("approved_by", [AUTH_REF]),
                "approved_at": unresolved("approved_at", [AUTH_REF]),
                "repository": unresolved("repository", [AUTH_REF]),
                "branch": unresolved("branch", [AUTH_REF]),
                "objective": unresolved("objective", [AUTH_REF]),
                "allowed_actions": [],
                "forbidden_actions": ["AUTOMATIC_GRANT", "AUTOMATIC_ACTIVATION"],
                "authority_effect": "NONE_UNTIL_SEPARATE_VALID_HUMAN_AUTHORIZATION",
                "runtime_effect": "NONE",
                "automatic_activation": False,
                "implementation_authorized": False,
            },
            "generation_guards": [
                "STATUS_MUST_BEGIN_DRAFT_OR_PROPOSED",
                "APPROVED_BY_MUST_REMAIN_UNRESOLVED",
                "GENERATION_CANNOT_GRANT_AUTHORITY",
                "COMMIT_PUSH_TEST_OR_AUDIT_CANNOT_CHANGE_STATUS_AUTOMATICALLY",
            ],
            "authority_effect": "NONE",
            "runtime_effect": "NONE",
            "automatic_activation": False,
            "implementation_authorized": False,
        }
    return result


def get_path(context: dict[str, Any], dotted: str) -> Any:
    value: Any = context
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"Unresolved template source: {dotted}")
        value = value[part]
    return copy.deepcopy(value)


def resolve(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        if set(value) == {"$source"}:
            return get_path(context, value["$source"])
        return {key: resolve(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item, context) for item in value]
    return copy.deepcopy(value)


def set_nested(target: dict[str, Any], path: list[str], value: Any) -> None:
    cursor = target
    for part in path[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[path[-1]] = value


def build_module_contexts() -> dict[str, dict[str, Any]]:
    selector = load_json(SELECTOR_REF)
    fixtures = load_json(FIXTURE_REF)
    result_contract = load_json(RESULT_REF)
    m0_fixtures = load_json(M0_FIXTURE_REF)
    module_by_id = {module["id"]: module for module in selector["modules"]}
    all_fixture_refs = [fixture["id"] for fixture in fixtures["fixtures"]]
    contexts: dict[str, dict[str, Any]] = {}

    maximum_roles = {
        "EVIDENCE_AND_CLAIMS": "EVIDENCE_BOUNDING_BEFORE_RECOMMENDATION",
        "DESIGN_CRITERION": "DESIGN_CRITERION_WITHOUT_AUTOMATIC_IMPLEMENTATION",
        "WEB_ACCESSIBILITY": "ACCESSIBILITY_CONSTRAINT_WITHOUT_AESTHETIC_SELECTION",
        "CONTEXTUAL_VISUAL_PREFERENCE": "CONTEXT_BOUND_PREFERENCE_WITHOUT_UNIVERSAL_STYLE",
    }
    allowed_claims = {
        "EVIDENCE_AND_CLAIMS": ["EVIDENCE_BOUNDED_ANALYSIS", "SCOPED_VALIDATION_RESULT"],
        "DESIGN_CRITERION": ["DESIGN_CRITERION_RECOMMENDATION", "SCOPED_VISUAL_TECHNICAL_RESULT"],
        "WEB_ACCESSIBILITY": ["SCOPED_ACCESSIBILITY_RESULT", "TEST_LAYER_STATUS"],
        "CONTEXTUAL_VISUAL_PREFERENCE": ["CONTEXTUAL_PREFERENCE_RECOMMENDATION"],
    }
    for index, module_id in enumerate(MODULE_IDS):
        module = module_by_id[module_id]
        if "activate_any" in module:
            active_when = {"mode": "ANY", "signals": module["activate_any"]}
        else:
            active_when = {
                "mode": "ANY_COMPLETE_GROUP",
                "signal_groups": [
                    module["activate_all"],
                    module["activate_alternative_all"],
                ],
            }
        applicable = [
            fixture["id"]
            for fixture in fixtures["fixtures"]
            if module_id in fixture["expected_modules"]
        ]
        negative = [
            fixture["id"]
            for fixture in fixtures["fixtures"]
            if module_id in fixture["forbidden_modules"]
        ]
        compatible = sorted(
            {
                peer
                for fixture in fixtures["fixtures"]
                if module_id in fixture["expected_modules"]
                for peer in fixture["expected_modules"]
                if peer != module_id
            }
        )
        source_refs = [SELECTOR_REF, RESULT_REF, CONTRACT_REF] + module["source_refs"]
        unresolved_refs = [SELECTOR_REF, M0_MODULE_REF]
        contexts[module_id] = {
            "integration_id": f"CRITERION_MODULE_{module_id}_CANDIDATE_001",
            "module_id": module_id,
            "problem": unresolved("problem", unresolved_refs),
            "producer": unresolved("producer", unresolved_refs),
            "version": unresolved("module_version", unresolved_refs),
            "value_hypothesis": unresolved("value_hypothesis", unresolved_refs),
            "risk_signals": [
                "AUTHORITY_INFERENCE",
                "NEGATIVE_TRANSFER",
                "SELECTOR_OR_RUNTIME_DRIFT",
            ],
            "source_refs": source_refs,
            "contract_refs": [
                "ACTIVATION_CONTRACT.json",
                "INPUT_CONTRACT.json",
                "RESULT_CONTRACT.json",
                "COMPOSITION_CONTRACT.json",
                "CONFLICTS.json",
                "MISUSE_RISKS.json",
                "FIXTURES.json",
                "TEST_DESIGN.json",
                "SCORING_AND_GATES.json",
                "ROLLBACK.json",
                "VALIDATION_EVIDENCE.json",
                "OPERATIONAL_TRUST_PREFLIGHT.json",
            ],
            "evidence_refs": [
                M0_MODULE_REF,
                M0_SIGNAL_REF,
                M0_COMPOSITION_REF,
                M0_FIXTURE_REF,
            ],
            "compatibility": {
                "compatible_with": compatible,
                "conflicts_with": unresolved("conflicts_with", [M0_COMPOSITION_REF]),
            },
            "active_when": active_when,
            "inactive_when": {
                "mode": "NO_ACTIVATION_RULE_MATCH_OR_APPLICABLE_EXCLUSION",
                "exclusion_signals": [
                    signal
                    for exclusion in selector["exclusions"]
                    if module_id in exclusion["exclude"]
                    for signal in exclusion["when_any"]
                ],
            },
            "limited_when": unresolved("limited_when", [SELECTOR_REF]),
            "required_inputs": selector["input_contract"]["required"],
            "optional_inputs": selector["input_contract"]["optional"],
            "result_envelope": result_contract["required_trace_when_any_module_active"],
            "allowed_claims": allowed_claims[module_id],
            "required_uncertainties": [
                "MATERIAL_UNCERTAINTY",
                "UNEXECUTED_TEST_LAYER",
                "UNRESOLVED_CANONICAL_VALUE",
            ],
            "evidence_requirements": [
                "SOURCE_REFS_FOR_MATERIAL_CLAIMS",
                "SEPARATE_EVIDENCE_FROM_AUTHORIZATION",
            ],
            "precedence_class": index + 1,
            "compatible_with": compatible,
            "conflicts_with": unresolved("conflicts_with", [M0_COMPOSITION_REF]),
            "maximum_role": maximum_roles[module_id],
            "composition_rules": selector["composition_rules"],
            "exclusions": selector["exclusions"],
            "misuse_risks": [
                "ACTIVATION_OUTSIDE_EXPLICIT_SIGNAL_RULE",
                "PREFERENCE_OR_HEURISTIC_PRESENTED_AS_STANDARD",
                "TECHNICAL_RESULT_PRESENTED_AS_AUTHORIZATION",
            ],
            "fixture_blob_sha": m0_fixtures["source"]["git_blob_sha"],
            "all_fixture_refs": all_fixture_refs,
            "applicable_fixture_refs": applicable,
            "negative_fixture_refs": negative,
            "test_id": f"DRAFT_{module_id}_ACTIVATION_DISCRIMINATION_001",
            "test_arms": [unresolved("test_arms", [M0_FIXTURE_REF])],
            "minimum_outputs": unresolved("minimum_outputs", [M0_FIXTURE_REF]),
            "blinding": unresolved("blinding", [M0_FIXTURE_REF]),
            "scoring_dimensions": [unresolved("scoring_dimensions", [M0_FIXTURE_REF])],
            "scoring_penalties": [unresolved("scoring_penalties", [M0_FIXTURE_REF])],
            "scoring_thresholds": unresolved("scoring_thresholds", [M0_FIXTURE_REF]),
            "aggregation": unresolved("aggregation", [M0_FIXTURE_REF]),
            "schema_validations": sorted(SCHEMA_BY_ARTIFACT.values()),
        }
    return contexts


def build_packages(
    templates: dict[str, dict[str, Any]],
    overlays: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    contexts = build_module_contexts()
    packages: dict[str, dict[str, Any]] = {}
    for module_id, context in contexts.items():
        artifacts: dict[str, Any] = {}
        for filename in TEMPLATE_FILES:
            template = templates[filename]
            artifacts[template["target_artifact"]] = resolve(template["render"], context)
        artifacts["OPERATIONAL_TRUST_PREFLIGHT.json"] = base_render(
            "OPERATIONAL_TRUST_PREFLIGHT"
        ) | {
            "required": False,
            "reference_environment": "REPOSITORY_ONLY_LOCAL_VALIDATION",
            "portable_capabilities": [
                "DECLARATIVE_REPRODUCIBILITY",
                "TEARDOWN_OR_BASELINE_RESTORATION",
                "REDACTED_HASHED_EVIDENCE",
            ],
            "provider_adapter": "NONE",
            "gates": ["M0_BASELINE_PRESERVED", "NO_RUNTIME_EFFECT"],
            "teardown": ["DISCARD_ISOLATED_GENERATED_PACKAGE"],
            "normalized_result": "NOT_REQUIRED",
        }
        for overlay in overlays.values():
            target = artifacts[overlay["applies_to"]]
            for operation in overlay["operations"]:
                set_nested(
                    target,
                    operation["path"],
                    resolve(operation["value"], context),
                )
        for artifact_name in PACKAGE_ARTIFACTS:
            packages[
                f"architecture/integrations/migration/M1A/generated/{module_id}/{artifact_name}"
            ] = artifacts[artifact_name]
    return packages


def build_static_artifacts() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    return (
        build_schemas(),
        build_templates(),
        build_overlays(),
        build_authorization_templates(),
    )


def validate_unresolved(value: Any, failures: list[str], path: str) -> None:
    if isinstance(value, dict):
        if value.get("status") == "UNRESOLVED":
            required = {"status", "reason", "required_resolution", "source_refs"}
            if set(value) != required or not value["source_refs"]:
                failures.append(f"{path}: malformed UNRESOLVED marker")
            return
        for key, item in value.items():
            validate_unresolved(item, failures, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate_unresolved(item, failures, f"{path}[{index}]")
    elif isinstance(value, str) and value.upper() in {"TBD", "TODO", "UNKNOWN"}:
        failures.append(f"{path}: unstructured unavailable value {value!r}")


def validate_references(value: Any, failures: list[str], label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith("_ref") and isinstance(item, str):
                candidate = item.split("#", 1)[0]
                if "/" in candidate and not (ROOT / candidate).exists():
                    failures.append(f"{label}: missing reference {candidate}")
            if key.endswith("_refs") and isinstance(item, list):
                for ref in item:
                    if isinstance(ref, str):
                        candidate = ref.split("#", 1)[0]
                        if "/" in candidate and not (ROOT / candidate).exists():
                            failures.append(f"{label}: missing reference {candidate}")
            validate_references(item, failures, label)
    elif isinstance(value, list):
        for item in value:
            validate_references(item, failures, label)


def validate_artifacts(
    schemas: dict[str, dict[str, Any]],
    templates: dict[str, dict[str, Any]],
    overlays: dict[str, dict[str, Any]],
    auth_templates: dict[str, dict[str, Any]],
    packages: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    failures: list[str] = []
    divergences: list[str] = [
        "PREEXISTING_NON_BLOCKING: scripts/validate_repository.py crashes at the "
        "authorized parent because schemas/validation/registries.py treats "
        "array-valued registry delta entries as filesystem paths; M1A uses its "
        "bounded Draft 2020-12 validator and does not modify that unrelated validator."
    ]
    meta_schema_validations = 0
    instance_validations = 0
    repository_json_files_parsed = 0

    for json_path in sorted(ROOT.rglob("*.json")):
        if ".git" in json_path.parts or ".validation" in json_path.parts:
            continue
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
            repository_json_files_parsed += 1
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            failures.append(
                f"{json_path.relative_to(ROOT).as_posix()}: JSON parse failed: {exc}"
            )

    if len(schemas) != 10:
        failures.append(f"Expected 10 schemas, found {len(schemas)}")
    if len(templates) != 13:
        failures.append(f"Expected 13 common templates, found {len(templates)}")
    if len(overlays) != 3:
        failures.append(f"Expected 3 CRITERION_MODULE overlays, found {len(overlays)}")
    if len(packages) != 4 * len(PACKAGE_ARTIFACTS):
        failures.append(
            f"Expected {4 * len(PACKAGE_ARTIFACTS)} generated package artifacts, "
            f"found {len(packages)}"
        )

    for filename, schema in schemas.items():
        if schema.get("$schema") != DIALECT:
            failures.append(f"{filename}: missing Draft 2020-12 dialect")
        try:
            Draft202012Validator.check_schema(schema)
            meta_schema_validations += 1
        except Exception as exc:  # jsonschema provides detailed nested exceptions
            failures.append(f"{filename}: meta-schema validation failed: {exc}")

    expected_targets = {template["target_artifact"] for template in templates.values()}
    if expected_targets != set(PACKAGE_ARTIFACTS) - {"OPERATIONAL_TRUST_PREFLIGHT.json"}:
        failures.append("Common template targets do not resolve to the 13 expected artifacts")
    for filename, template in templates.items():
        schema_ref = template["schema_ref"]
        if schema_ref and schema_ref.split("/")[-1] not in schemas:
            failures.append(f"{filename}: missing schema_ref {schema_ref}")
        try:
            resolve(template["render"], build_module_contexts()[MODULE_IDS[0]])
        except KeyError as exc:
            failures.append(f"{filename}: {exc}")

    for filename, overlay in overlays.items():
        if overlay["applies_to"] not in expected_targets:
            failures.append(f"{filename}: missing target {overlay['applies_to']}")
        try:
            resolve(overlay["operations"], build_module_contexts()[MODULE_IDS[0]])
        except KeyError as exc:
            failures.append(f"{filename}: {exc}")

    for filename, template in auth_templates.items():
        rendered = template["render"]
        if rendered["status"] not in {"DRAFT", "PROPOSED"}:
            failures.append(f"{filename}: generated authorization status is not draft-only")
        if rendered["approved_by"].get("status") != "UNRESOLVED":
            failures.append(f"{filename}: approved_by is not UNRESOLVED")
        if rendered["automatic_activation"] is not False:
            failures.append(f"{filename}: automatic_activation must be false")

    loaded_by_module: dict[str, dict[str, Any]] = {module: {} for module in MODULE_IDS}
    for path, artifact in packages.items():
        parts = Path(path).parts
        module_id = parts[-2]
        artifact_name = parts[-1]
        loaded_by_module[module_id][artifact_name] = artifact
        validate_unresolved(artifact, failures, path)
        if artifact.get("authority_effect") != "NONE":
            failures.append(f"{path}: authority_effect must be NONE")
        if artifact.get("runtime_effect") != "NONE":
            failures.append(f"{path}: runtime_effect must be NONE")
        if artifact.get("automatic_activation") is not False:
            failures.append(f"{path}: automatic_activation must be false")
        if artifact.get("implementation_authorized") is not False:
            failures.append(f"{path}: implementation_authorized must be false")
        if artifact_name in SCHEMA_BY_ARTIFACT:
            schema_name = SCHEMA_BY_ARTIFACT[artifact_name]
            errors = sorted(
                Draft202012Validator(schemas[schema_name]).iter_errors(artifact),
                key=lambda error: list(error.path),
            )
            if errors:
                for error in errors:
                    failures.append(
                        f"{path}: schema {schema_name}: "
                        f"{'/'.join(map(str, error.path))}: {error.message}"
                    )
            else:
                instance_validations += 1

    for module_id, artifacts in loaded_by_module.items():
        missing = sorted(set(PACKAGE_ARTIFACTS) - set(artifacts))
        if missing:
            failures.append(f"{module_id}: missing package artifacts {missing}")
            continue
        manifest = artifacts["MANIFEST.json"]
        for contract_ref in manifest["contract_refs"]:
            if contract_ref not in artifacts:
                failures.append(f"{module_id}: unresolved package contract {contract_ref}")
        if manifest["status"] != "CANDIDATE":
            failures.append(f"{module_id}: package promoted beyond CANDIDATE")
        rollback = artifacts["ROLLBACK.json"]
        if not rollback["steps"] or rollback["authority_required"] is not True:
            failures.append(f"{module_id}: rollback is not explicit")
        if len(artifacts["FIXTURES.json"]["all_baseline_fixture_refs"]) != 13:
            failures.append(f"{module_id}: 13 frozen fixture references not preserved")

    selector = load_json(SELECTOR_REF)
    fixtures = load_json(FIXTURE_REF)
    m0_modules = load_json(M0_MODULE_REF)
    m0_fixtures = load_json(M0_FIXTURE_REF)
    distinct_signals = set()
    for module in selector["modules"]:
        for key in ("activate_any", "activate_all", "activate_alternative_all"):
            distinct_signals.update(module.get(key, []))
    for exclusion in selector["exclusions"]:
        distinct_signals.update(exclusion["when_any"])
    m0_checks = {
        "module_count": len(selector["modules"]) == 4 == m0_modules["counts"]["modules"],
        "distinct_activation_signals": (
            len(distinct_signals) == 27 == m0_modules["counts"]["distinct_activation_signals"]
        ),
        "composition_rule_count": len(selector["composition_rules"]) == 6,
        "exclusion_block_count": len(selector["exclusions"]) == 1,
        "empty_set_abstention": "NO_MATCH_RETURNS_EMPTY_MODULE_SET"
        in selector["composition_rules"],
        "fixture_count": len(fixtures["fixtures"]) == 13 == m0_fixtures["fixture_count"],
        "selector_blob_sha": git_blob_sha(ROOT / SELECTOR_REF)
        == m0_modules["source"]["git_blob_sha"],
        "fixture_blob_sha": git_blob_sha(ROOT / FIXTURE_REF)
        == m0_fixtures["source"]["git_blob_sha"],
    }
    for check, passed in m0_checks.items():
        if not passed:
            failures.append(f"M0 baseline check failed: {check}")

    for filename, value in (
        list(schemas.items())
        + list(templates.items())
        + list(overlays.items())
        + list(auth_templates.items())
    ):
        validate_unresolved(value, failures, filename)
        if value.get("authority_effect") != "NONE":
            failures.append(f"{filename}: governed source authority_effect must be NONE")
        if value.get("runtime_effect") != "NONE":
            failures.append(f"{filename}: governed source runtime_effect must be NONE")
        if value.get("automatic_activation") is not False:
            failures.append(f"{filename}: governed source automatic_activation must be false")
        if value.get("implementation_authorized") is not False:
            failures.append(f"{filename}: governed source implementation_authorized must be false")

    for path, value in packages.items():
        validate_references(value, failures, path)

    normalized_inputs: dict[str, Any] = {}
    normalized_inputs.update(
        {f"architecture/integrations/schemas/{key}": value for key, value in schemas.items()}
    )
    normalized_inputs.update(
        {f"architecture/integrations/templates/{key}": value for key, value in templates.items()}
    )
    normalized_inputs.update(
        {
            f"architecture/integrations/templates/criterion-module/{key}": value
            for key, value in overlays.items()
        }
    )
    normalized_inputs.update(
        {
            f"architecture/integrations/templates/authorizations/{key}": value
            for key, value in auth_templates.items()
        }
    )
    normalized_inputs.update(packages)
    first_digest = normalized_digest(normalized_inputs)

    schemas_2, templates_2, overlays_2, auth_templates_2 = build_static_artifacts()
    packages_2 = build_packages(templates_2, overlays_2)
    normalized_inputs_2: dict[str, Any] = {}
    normalized_inputs_2.update(
        {f"architecture/integrations/schemas/{key}": value for key, value in schemas_2.items()}
    )
    normalized_inputs_2.update(
        {f"architecture/integrations/templates/{key}": value for key, value in templates_2.items()}
    )
    normalized_inputs_2.update(
        {
            f"architecture/integrations/templates/criterion-module/{key}": value
            for key, value in overlays_2.items()
        }
    )
    normalized_inputs_2.update(
        {
            f"architecture/integrations/templates/authorizations/{key}": value
            for key, value in auth_templates_2.items()
        }
    )
    normalized_inputs_2.update(packages_2)
    second_digest = normalized_digest(normalized_inputs_2)
    reproducible = first_digest == second_digest
    if not reproducible:
        failures.append("Second unchanged-input generation produced a different normalized digest")

    return {
        "status": "PASS" if not failures else "BLOCKED",
        "schema_count": len(schemas),
        "template_count": len(templates),
        "overlay_count": len(overlays),
        "authorization_template_count": len(auth_templates),
        "package_count": len(loaded_by_module),
        "package_artifact_count": len(packages),
        "meta_schema_validations": meta_schema_validations,
        "instance_validations": instance_validations,
        "repository_json_files_parsed": repository_json_files_parsed,
        "m0_checks": m0_checks,
        "first_normalized_digest": first_digest,
        "second_normalized_digest": second_digest,
        "reproducible": reproducible,
        "failures": failures,
        "divergences": divergences,
    }


def update_catalogs() -> dict[str, Any]:
    schema_catalog = load_json(
        "architecture/integrations/schemas/INTEGRATION_PACKAGE_SCHEMA_SET_001.json"
    )
    schema_catalog["status"] = "EXECUTABLE_ARTIFACTS_MATERIALIZED_VALIDATED"
    schema_catalog["executable_dialect"] = DIALECT
    schema_catalog["executable_schema_paths"] = [
        f"architecture/integrations/schemas/{name}" for name in SCHEMA_FILES
    ]
    schema_catalog["materialization"] = {
        "authorization_ref": AUTH_REF,
        "count": 10,
        "runtime_effect": "NONE",
        "implementation_authorized": False,
    }
    template_catalog = load_json(
        "architecture/integrations/templates/INTEGRATION_TEMPLATE_CATALOG_001.json"
    )
    template_catalog["status"] = "EXECUTABLE_ARTIFACTS_MATERIALIZED_VALIDATED"
    template_catalog["executable_paths"] = {
        "common_templates": [
            f"architecture/integrations/templates/{name}" for name in TEMPLATE_FILES
        ],
        "criterion_module_overlays": [
            f"architecture/integrations/templates/criterion-module/{name}"
            for name in OVERLAY_FILES
        ],
        "draft_only_authorization_templates": [
            f"architecture/integrations/templates/authorizations/{name}"
            for name in AUTH_TEMPLATE_FILES
        ],
    }
    template_catalog["materialization"] = {
        "authorization_ref": AUTH_REF,
        "common_template_count": 13,
        "criterion_module_overlay_count": 3,
        "authorization_template_count": 5,
        "runtime_effect": "NONE",
        "implementation_authorized": False,
    }
    return {
        "architecture/integrations/schemas/INTEGRATION_PACKAGE_SCHEMA_SET_001.json": schema_catalog,
        "architecture/integrations/templates/INTEGRATION_TEMPLATE_CATALOG_001.json": template_catalog,
    }


def expected_changed_paths() -> list[dict[str, str]]:
    created = [
        BRIEF_REF,
        AUTH_REF,
        "scripts/requirements-integration-factory-validation.txt",
        "scripts/validate_integration_factory_m1a.py",
        "architecture/integrations/migration/M1A/README.md",
        "architecture/integrations/migration/M1A/VALIDATION_RESULTS.json",
        "architecture/integrations/migration/M1A/CHANGED_FILES.json",
        "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M1A-153.json",
        "registry/deltas/integration-factory-m1a-executable-materialization-153.json",
    ]
    created += [f"architecture/integrations/schemas/{name}" for name in SCHEMA_FILES]
    created += [f"architecture/integrations/templates/{name}" for name in TEMPLATE_FILES]
    created += [
        f"architecture/integrations/templates/criterion-module/{name}"
        for name in OVERLAY_FILES
    ]
    created += [
        f"architecture/integrations/templates/authorizations/{name}"
        for name in AUTH_TEMPLATE_FILES
    ]
    created += [
        f"architecture/integrations/migration/M1A/generated/{module}/{artifact}"
        for module in MODULE_IDS
        for artifact in PACKAGE_ARTIFACTS
    ]
    modified = [
        "architecture/integrations/schemas/INTEGRATION_PACKAGE_SCHEMA_SET_001.json",
        "architecture/integrations/templates/INTEGRATION_TEMPLATE_CATALOG_001.json",
        "architecture/integrations/migration/M1/SCHEMA_VALIDATION_REPORT.json",
        "architecture/integrations/migration/M1/TEMPLATE_INSTANTIATION_REPORT.json",
        "projects/lab/pending/PEND-LAB-033.json",
    ]
    return [
        *[{"path": path, "operation": "CREATE"} for path in sorted(created)],
        *[{"path": path, "operation": "MODIFY"} for path in sorted(modified)],
    ]


def build_records(result: dict[str, Any]) -> dict[str, Any]:
    passed = result["status"] == "PASS"
    exit_value = "PASS" if passed else "BLOCKED"
    validation_results = {
        "schema_version": "1.0.0",
        "validation_id": "INTEGRATION_FACTORY_M1A_VALIDATION_001",
        "project_id": "lab",
        "status": result["status"],
        "recorded_at": RECORDED_AT,
        "authorization_ref": AUTH_REF,
        "brief_ref": BRIEF_REF,
        "execution_parent_head": EXPECTED_PARENT_HEAD,
        "command": "python scripts/validate_integration_factory_m1a.py --check",
        "dialect": DIALECT,
        "counts": {
            "common_executable_schemas": result["schema_count"],
            "common_executable_templates": result["template_count"],
            "criterion_module_overlays": result["overlay_count"],
            "draft_only_authorization_templates": result["authorization_template_count"],
            "isolated_generated_module_packages": result["package_count"],
            "generated_package_artifacts": result["package_artifact_count"],
            "schema_meta_validations": result["meta_schema_validations"],
            "package_schema_instance_validations": result["instance_validations"],
            "repository_json_files_parsed": result["repository_json_files_parsed"],
        },
        "reproducibility": {
            "first_normalized_digest": result["first_normalized_digest"],
            "second_normalized_digest": result["second_normalized_digest"],
            "equivalent": result["reproducible"],
        },
        "m0_baseline": result["m0_checks"],
        "authority_and_runtime_boundary": {
            "authority_inference": "NONE_DETECTED" if passed else "CHECK_FAILURE_RETAINED",
            "runtime_effect": "NONE",
            "automatic_activation": False,
            "implementation_authorized": False,
            "generated_authorization_statuses": ["DRAFT"],
            "global_stack_selected": False,
            "production_provider_selected": False,
            "shadow_registry_created": False,
            "m2_started": False,
            "active_selector_modified": False,
        },
        "m1_exit_criteria": {
            "ALL_COMMON_SCHEMAS_VALID": exit_value,
            "ALL_PROFILE_OVERLAYS_RESOLVE": exit_value,
            "NO_AUTHORITY_INFERENCE": exit_value,
            "M0_BASELINE_PRESERVED": exit_value,
            "ACTIVE_SELECTOR_UNCHANGED": exit_value,
            "NO_RUNTIME_EFFECT": exit_value,
        },
        "m1_classification": "M1_PASS" if passed else "M1_BLOCKED_WITH_DOCUMENTED_DIVERGENCES",
        "authorization_consumption_boundary": (
            "CONSUMED_WHEN_BOUNDED_RESULT_COMMIT_IS_PUSHED_AND_REMOTE_HEAD_VERIFIED"
        ),
        "failures": result["failures"],
        "divergences": result["divergences"],
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }
    schema_report = {
        "schema_version": "1.0.0",
        "validation_report_id": "INTEGRATION_FACTORY_M1_SCHEMA_VALIDATION_REPORT_001",
        "project_id": "lab",
        "migration_phase": "M1_SCHEMA_AND_TEMPLATE_VALIDATION_RERUN_AFTER_M1A",
        "status": "PASS_ALL_EXECUTABLE_SCHEMAS_VALID" if passed else "BLOCKED",
        "recorded_at": RECORDED_AT,
        "authorization_ref": AUTH_REF,
        "execution_baseline_head": EXPECTED_PARENT_HEAD,
        "executable_dialect": DIALECT,
        "schema_files": [
            f"architecture/integrations/schemas/{name}" for name in SCHEMA_FILES
        ],
        "mechanical_validation": {
            "json_parse": exit_value,
            "declared_schema_count": 10,
            "materialized_schema_count": result["schema_count"],
            "meta_schema_validations": result["meta_schema_validations"],
            "package_instance_validations": result["instance_validations"],
            "cross_references": exit_value,
            "unresolved_representation": exit_value,
            "second_run_equivalence": exit_value,
        },
        "m0_baseline_preservation": result["m0_checks"],
        "exit_criteria": validation_results["m1_exit_criteria"],
        "failures": result["failures"],
        "divergences": result["divergences"],
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "active_selector_modified": False,
        "shadow_registry_created": False,
    }
    template_report = {
        "schema_version": "1.0.0",
        "instantiation_report_id": "INTEGRATION_FACTORY_M1_TEMPLATE_INSTANTIATION_REPORT_001",
        "project_id": "lab",
        "migration_phase": "M1_SCHEMA_AND_TEMPLATE_VALIDATION_RERUN_AFTER_M1A",
        "status": "PASS_ALL_TEMPLATES_AND_OVERLAYS_RESOLVE" if passed else "BLOCKED",
        "recorded_at": RECORDED_AT,
        "authorization_ref": AUTH_REF,
        "execution_baseline_head": EXPECTED_PARENT_HEAD,
        "materialization": {
            "common_template_count": result["template_count"],
            "criterion_module_overlay_count": result["overlay_count"],
            "draft_only_authorization_template_count": result[
                "authorization_template_count"
            ],
            "generated_package_count": result["package_count"],
            "generated_package_artifact_count": result["package_artifact_count"],
        },
        "generated_modules": MODULE_IDS,
        "resolution": {
            "template_references": exit_value,
            "overlay_targets": exit_value,
            "structured_unresolved_markers": exit_value,
            "draft_only_authorization_generation": exit_value,
            "rollback_explicit": exit_value,
            "composition_and_exclusion_preserved": exit_value,
        },
        "exit_criteria": validation_results["m1_exit_criteria"],
        "failures": result["failures"],
        "divergences": result["divergences"],
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "active_selector_modified": False,
        "shadow_registry_created": False,
    }
    pending = load_json("projects/lab/pending/PEND-LAB-033.json")
    if passed:
        pending.update(
            {
                "status": "COMPLETED_M1_PASS",
                "closed_at": RECORDED_AT,
                "closed_by_authorization": AUTH_REF,
                "resolution_evidence": (
                    "architecture/integrations/migration/M1A/VALIDATION_RESULTS.json"
                ),
                "m1_classification": "M1_PASS",
                "m2_authorized": False,
                "shadow_registry_authorized": False,
                "authority_effect": "NONE",
                "runtime_effect": "NONE",
            }
        )
    evidence = {
        "schema_version": "1.0.0",
        "evidence_id": "EVD-LAB-INTEGRATION-FACTORY-M1A-153",
        "project_id": "lab",
        "status": "VALIDATED_M1_PASS" if passed else "VALIDATED_M1_BLOCKED",
        "recorded_at": RECORDED_AT,
        "authorization_ref": AUTH_REF,
        "brief_ref": BRIEF_REF,
        "execution_parent_head": EXPECTED_PARENT_HEAD,
        "validation_result_ref": (
            "architecture/integrations/migration/M1A/VALIDATION_RESULTS.json"
        ),
        "observations": {
            "schemas_materialized": result["schema_count"],
            "templates_materialized": result["template_count"],
            "overlays_materialized": result["overlay_count"],
            "authorization_templates_materialized": result[
                "authorization_template_count"
            ],
            "isolated_packages_generated": result["package_count"],
            "schema_meta_validations": result["meta_schema_validations"],
            "package_instance_validations": result["instance_validations"],
            "reproducibility": result["reproducible"],
            "m0_baseline_preserved": all(result["m0_checks"].values()),
        },
        "m1_classification": validation_results["m1_classification"],
        "authorization_consumption": (
            "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION_OF_BOUNDED_RESULT"
        ),
        "failures": result["failures"],
        "divergences": result["divergences"],
        "claims_not_created": [
            "M2_AUTHORIZED",
            "SHADOW_REGISTRY_CREATED",
            "ACTIVE_SELECTOR_CHANGED",
            "RUNTIME_RESOLVER_IMPLEMENTED",
            "MODULE_ACTIVATED_OR_INTEGRATED",
            "GLOBAL_STACK_SELECTED",
            "PRODUCTION_PROVIDER_SELECTED",
            "SSE_TEST_147_EXECUTED",
        ],
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }
    delta = {
        "schema_version": "1.0.0",
        "delta_id": "integration-factory-m1a-executable-materialization-153",
        "recorded_at": RECORDED_AT,
        "project_id": "lab",
        "authorization_ref": AUTH_REF,
        "authorization_status": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
        "brief_ref": BRIEF_REF,
        "changes": [
            "M1A_EXECUTABLE_SCHEMA_TEMPLATE_AND_OVERLAY_MATERIALIZATION",
            "FOUR_ISOLATED_CRITERION_MODULE_CANDIDATE_PACKAGES_GENERATED",
            "M1_MECHANICALLY_RERUN",
            "PEND_LAB_033_CLOSED_ONLY_AFTER_ALL_GATES_PASS"
            if passed
            else "PEND_LAB_033_REMAINS_OPEN",
        ],
        "state_after": {
            "migration_phase": "M1_PASS" if passed else "M1_BLOCKED",
            "blocking_pending": None if passed else "PEND-LAB-033",
            "m2_authorized": False,
            "shadow_registry_created": False,
            "active_selector_modified": False,
            "runtime_effect": "NONE",
            "integration_effect": "NONE",
            "sse_test_147": "UNCHANGED_SEPARATE_AUTHORIZATION",
            "global_preferred_stack": "NONE",
            "production_provider": "NONE",
        },
        "validation_result_ref": (
            "architecture/integrations/migration/M1A/VALIDATION_RESULTS.json"
        ),
        "evidence_ref": "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M1A-153.json",
        "failures": result["failures"],
        "divergences": result["divergences"],
        "next_action": (
            "SEPARATE_HUMAN_DECISION_AND_AUTHORIZATION_REQUIRED_BEFORE_ANY_M2_WORK"
        ),
        "authority_effect": "NONE_AFTER_CONSUMPTION",
        "runtime_effect": "NONE",
    }
    changed_manifest = {
        "schema_version": "1.0.0",
        "manifest_id": "INTEGRATION_FACTORY_M1A_CHANGED_FILES_153",
        "project_id": "lab",
        "recorded_at": RECORDED_AT,
        "authorization_ref": AUTH_REF,
        "files": expected_changed_paths(),
        "unrelated_changes_allowed": False,
        "authority_effect": "NONE",
        "runtime_effect": "NONE",
        "automatic_activation": False,
        "implementation_authorized": False,
    }
    return {
        "architecture/integrations/migration/M1A/VALIDATION_RESULTS.json": validation_results,
        "architecture/integrations/migration/M1/SCHEMA_VALIDATION_REPORT.json": schema_report,
        "architecture/integrations/migration/M1/TEMPLATE_INSTANTIATION_REPORT.json": template_report,
        "projects/lab/pending/PEND-LAB-033.json": pending,
        "projects/lab/evidence/EVD-LAB-INTEGRATION-FACTORY-M1A-153.json": evidence,
        "registry/deltas/integration-factory-m1a-executable-materialization-153.json": delta,
        "architecture/integrations/migration/M1A/CHANGED_FILES.json": changed_manifest,
    }


def write_json(relative: str, value: Any) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def materialize() -> dict[str, Any]:
    schemas, templates, overlays, auth_templates = build_static_artifacts()
    packages = build_packages(templates, overlays)
    for filename, value in schemas.items():
        write_json(f"architecture/integrations/schemas/{filename}", value)
    for filename, value in templates.items():
        write_json(f"architecture/integrations/templates/{filename}", value)
    for filename, value in overlays.items():
        write_json(
            f"architecture/integrations/templates/criterion-module/{filename}", value
        )
    for filename, value in auth_templates.items():
        write_json(
            f"architecture/integrations/templates/authorizations/{filename}", value
        )
    for relative, value in packages.items():
        write_json(relative, value)
    for relative, value in update_catalogs().items():
        write_json(relative, value)
    result = validate_artifacts(
        schemas, templates, overlays, auth_templates, packages
    )
    for relative, value in build_records(result).items():
        write_json(relative, value)
    return result


def load_disk_artifacts() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    schemas = {name: load_json(f"architecture/integrations/schemas/{name}") for name in SCHEMA_FILES}
    templates = {
        name: load_json(f"architecture/integrations/templates/{name}")
        for name in TEMPLATE_FILES
    }
    overlays = {
        name: load_json(f"architecture/integrations/templates/criterion-module/{name}")
        for name in OVERLAY_FILES
    }
    auth_templates = {
        name: load_json(f"architecture/integrations/templates/authorizations/{name}")
        for name in AUTH_TEMPLATE_FILES
    }
    packages = {
        f"architecture/integrations/migration/M1A/generated/{module}/{artifact}": load_json(
            f"architecture/integrations/migration/M1A/generated/{module}/{artifact}"
        )
        for module in MODULE_IDS
        for artifact in PACKAGE_ARTIFACTS
    }
    return schemas, templates, overlays, auth_templates, packages


def check_disk() -> dict[str, Any]:
    disk = load_disk_artifacts()
    result = validate_artifacts(*disk)
    expected_static = build_static_artifacts()
    expected_packages = build_packages(expected_static[1], expected_static[2])
    labels = ["schemas", "templates", "overlays", "authorization_templates"]
    for label, actual, expected in zip(labels, disk[:4], expected_static):
        if canonical_bytes(actual) != canonical_bytes(expected):
            result["failures"].append(f"Checked-in {label} differ from deterministic materialization")
    if canonical_bytes(disk[4]) != canonical_bytes(expected_packages):
        result["failures"].append(
            "Checked-in generated packages differ from deterministic materialization"
        )
    stored = load_json(
        "architecture/integrations/migration/M1A/VALIDATION_RESULTS.json"
    )
    if stored["reproducibility"]["first_normalized_digest"] != result[
        "first_normalized_digest"
    ]:
        result["failures"].append("Stored validation digest differs from current inputs")
    if result["failures"]:
        result["status"] = "BLOCKED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--materialize", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = materialize() if args.materialize else check_disk()
    print(f"M1A validation: {result['status']}")
    print(f"Draft 2020-12 schema meta-validations: {result['meta_schema_validations']}")
    print(f"Generated package schema-instance validations: {result['instance_validations']}")
    print(f"Normalized digest: {result['first_normalized_digest']}")
    print(f"Second-run equivalent: {result['reproducible']}")
    print(f"M0 baseline preserved: {all(result['m0_checks'].values())}")
    if result["failures"]:
        for failure in result["failures"]:
            print(f"FAIL: {failure}")
        return 1
    print("Authority inference: NONE_DETECTED")
    print("Runtime effect: NONE")
    print("M1 classification: M1_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
