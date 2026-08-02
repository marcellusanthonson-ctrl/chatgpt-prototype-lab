#!/usr/bin/env python3
"""Validate Priority Integrations Phase 1 contracts without executing candidate tests."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

MODULE_IDS = [
    "EVIDENCE_AND_CLAIMS",
    "DESIGN_CRITERION",
    "WEB_ACCESSIBILITY",
    "CONTEXTUAL_VISUAL_PREFERENCE",
    "PRODUCT_LEADERSHIP",
    "SOFTWARE_SOLUTION_ENGINEERING",
]

PACKAGE_ROOTS = {
    "PRODUCT_LEADERSHIP": ROOT / "foundation-library/product-leadership/PRODUCT-LEADERSHIP-CANDIDATE-PACKAGE-001",
    "SOFTWARE_SOLUTION_ENGINEERING": ROOT / "foundation-library/software-solution-engineering/SOFTWARE-SOLUTION-ENGINEERING-CANDIDATE-PACKAGE-001",
}

STANDARD_ARTIFACTS = [
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
}

PROTECTED_BLOBS = {
    "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json": "618c2fe00a6b23a84c5ce90361cb3b7cfa5b9053",
    "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json": "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78",
    "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json": "301ba432907758fc49a9b3c86a83fc762eac4607",
    "foundation-library/motion-system/MOTION-SYSTEM-001/MANIFEST.json": "12f0af44023aee366f9e3df44b906fd50ffe6331",
}

SHARED_COMPOSITION = ROOT / "projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/contracts/PRODUCT-LEADERSHIP-TO-SSE-COMPOSITION-CONTRACT-001.json"

def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def git_blob_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-protected", action="store_true", help="Local subset validation only.")
    args = parser.parse_args()

    errors: list[str] = []
    schema_dir = ROOT / "architecture/integrations/schemas"
    schemas = {name: load(schema_dir / name) for name in set(SCHEMA_BY_ARTIFACT.values())}

    for schema_name in ["integration-manifest.schema.json", "activation-contract.schema.json"]:
        enum_values = schemas[schema_name]["properties"]["module_id"]["enum"]
        if enum_values != MODULE_IDS:
            errors.append(f"{schema_name}: expected exact six registered module IDs, got {enum_values}")

    for module_id, package_root in PACKAGE_ROOTS.items():
        for artifact in STANDARD_ARTIFACTS:
            path = package_root / artifact
            if not path.exists():
                errors.append(f"{module_id}: missing {artifact}")
                continue
            try:
                value = load(path)
            except Exception as exc:
                errors.append(f"{module_id}/{artifact}: invalid JSON: {exc}")
                continue
            schema_name = SCHEMA_BY_ARTIFACT.get(artifact)
            if schema_name:
                for error in Draft202012Validator(schemas[schema_name]).iter_errors(value):
                    errors.append(f"{module_id}/{artifact}: {error.message}")

        manifest = load(package_root / "MANIFEST.json")
        activation = load(package_root / "ACTIVATION_CONTRACT.json")
        test_design = load(package_root / "TEST_DESIGN.json")
        validation = load(package_root / "VALIDATION_EVIDENCE.json")

        if manifest["module_id"] != module_id:
            errors.append(f"{module_id}: manifest module_id mismatch")
        if manifest.get("status") != "CANDIDATE" or manifest.get("contract_status") != "CONTRACT_COMPLETE_TESTS_NOT_AUTHORIZED":
            errors.append(f"{module_id}: lifecycle status mismatch")
        if manifest.get("active") or manifest.get("integrated") or manifest.get("automatic_activation"):
            errors.append(f"{module_id}: candidate must remain inactive and not integrated")
        if activation.get("module_id") != module_id:
            errors.append(f"{module_id}: activation module_id mismatch")
        if activation.get("automatic_activation") or activation.get("implementation_authorized"):
            errors.append(f"{module_id}: implicit activation or implementation authority")
        if test_design.get("status") != "DRAFT_NOT_AUTHORIZED" or test_design.get("execution_authorized") is not False:
            errors.append(f"{module_id}: test design must remain unexecuted and unauthorized")
        if validation.get("status") != "PASS_CONTRACT_VALIDATION_ONLY":
            errors.append(f"{module_id}: validation evidence not closed")

    unknown_manifest = load(PACKAGE_ROOTS["PRODUCT_LEADERSHIP"] / "MANIFEST.json")
    unknown_manifest["module_id"] = "UNKNOWN_MODULE"
    if Draft202012Validator(schemas["integration-manifest.schema.json"]).is_valid(unknown_manifest):
        errors.append("integration-manifest schema accepts UNKNOWN_MODULE")

    unknown_activation = load(PACKAGE_ROOTS["PRODUCT_LEADERSHIP"] / "ACTIVATION_CONTRACT.json")
    unknown_activation["module_id"] = "UNKNOWN_MODULE"
    if Draft202012Validator(schemas["activation-contract.schema.json"]).is_valid(unknown_activation):
        errors.append("activation-contract schema accepts UNKNOWN_MODULE")

    if not SHARED_COMPOSITION.exists():
        errors.append("shared directional composition contract missing")
    else:
        shared = load(SHARED_COMPOSITION)
        if shared.get("source_module") != "PRODUCT_LEADERSHIP" or shared.get("target_module") != "SOFTWARE_SOLUTION_ENGINEERING":
            errors.append("shared composition direction mismatch")
        fail_closed = set(shared.get("handoff_gate", {}).get("fail_closed_when", []))
        required = {"PRODUCT_SCOPE_MISSING", "AUTHORITY_CONFLICT", "BINDING_DECISION_MISSING", "REQUEST_REQUIRES_UNAUTHORIZED_IMPLEMENTATION"}
        if not required.issubset(fail_closed):
            errors.append("shared composition fail-closed coverage incomplete")

    sse_test = load(PACKAGE_ROOTS["SOFTWARE_SOLUTION_ENGINEERING"] / "TEST_DESIGN.json")
    if len(sse_test.get("arms", [])) != 3 or sse_test.get("minimum_outputs") != 96:
        errors.append("SSE test design must preserve 3 arms and 96 minimum future outputs")

    sse_result = load(PACKAGE_ROOTS["SOFTWARE_SOLUTION_ENGINEERING"] / "RESULT_CONTRACT.json")
    required_negative = {
        "NO_MICROSERVICES_BY_DEFAULT",
        "NO_DDD_BY_DEFAULT",
        "NO_CLEAN_ARCHITECTURE_BY_DEFAULT",
        "NO_DISTRIBUTION_WITHOUT_VERIFIED_NEED",
        "NO_STACK_BIAS",
    }
    if not required_negative.issubset(set(sse_result.get("negative_transfer_controls", []))):
        errors.append("SSE negative-transfer controls incomplete")

    if not args.skip_protected:
        for relative, expected in PROTECTED_BLOBS.items():
            path = ROOT / relative
            if not path.exists():
                errors.append(f"protected path missing: {relative}")
            elif git_blob_sha(path) != expected:
                errors.append(f"protected path changed: {relative}")

    if errors:
        print(json.dumps({"status": "FAIL", "error_count": len(errors), "errors": errors}, indent=2))
        return 1

    print(json.dumps({
        "status": "PASS",
        "registered_module_ids": MODULE_IDS,
        "packages": {
            "PRODUCT_LEADERSHIP": {"standard_artifacts": 13, "lifecycle": "CONTRACT_COMPLETE_TESTS_NOT_AUTHORIZED"},
            "SOFTWARE_SOLUTION_ENGINEERING": {"standard_artifacts": 13, "lifecycle": "CONTRACT_COMPLETE_TESTS_NOT_AUTHORIZED", "test_arms": 3, "minimum_future_outputs": 96},
        },
        "test_execution": 0,
        "external_audit_execution": 0,
        "runtime_effect": "NONE",
        "product_effect": "NONE",
        "integration_activation_effect": "NONE",
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
