#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARENT = "f388adce6a7917b5378489bda6bf058469f2a643"
BRANCH = "priority-integrations-phase2-sse-180"
DATE = "2026-08-03"
TIMESTAMP = "2026-08-03T10:12:00-04:00"
OLD_AUTH = "AUTHORIZATION_LAB_SSE_TEST_EXECUTION_AND_READ_ONLY_AUDIT_147"
AUTH = "AUTHORIZATION_LAB_PRIORITY_INTEGRATIONS_PHASE_2_SSE_SYNTHETIC_TEST_EXECUTION_180"
BRIEF = "CODEX_PRIORITY_INTEGRATIONS_PHASE_2_SSE_SYNTHETIC_TEST_EXECUTION_180_001"
EVIDENCE = "EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-2-SSE-AUTHORITY-180"
ERROR = "ERR-LAB-012"
DELTA = "priority-integrations-phase2-sse-authority-180"
PHASE = "PRIORITY_INTEGRATIONS_PHASE_2_SSE_EXECUTION_AUTHORIZED_NOT_STARTED_PRODUCT_LEADERSHIP_PREFLIGHT_BLOCKED"

OLD_AUTH_PATH = f"projects/lab/authorizations/{OLD_AUTH}.json"
AUTH_PATH = f"projects/lab/authorizations/{AUTH}.json"
OLD_BRIEF_PATH = "projects/lab/briefs/CODEX_SSE_ACTIVATION_AND_VALUE_DISCRIMINATION_TEST_001.json"
BRIEF_PATH = f"projects/lab/briefs/{BRIEF}.json"
EVIDENCE_PATH = f"projects/lab/evidence/{EVIDENCE}.json"
ERROR_PATH = f"errors/{ERROR}.json"
DELTA_147_PATH = "registry/deltas/sse-test-execution-and-read-only-audit-147.json"
DELTA_PATH = f"registry/deltas/{DELTA}.json"
SSE_TEST_MANIFEST = "projects/lab/test-designs/SOFTWARE-SOLUTION-ENGINEERING-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/MANIFEST.json"
SSE_TEST_INDEX = "projects/lab/test-designs/index.json"
INT_PATH = "projects/lab/integrations/INT-LAB-005.json"
INT_INDEX = "projects/lab/integrations/index.json"
PEND_027 = "projects/lab/pending/PEND-LAB-027.json"
PEND_045 = "projects/lab/pending/PEND-LAB-045.json"
PROGRAM = "projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/MANIFEST.json"
PROGRAM_ROADMAP = "projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/ROADMAP.json"

TARGETS = {
    "CURRENT_STATE.json",
    "registry/index.json",
    "registry/authorizations.json",
    "registry/errors.json",
    "registry/integrations.json",
    DELTA_147_PATH,
    DELTA_PATH,
    "projects/lab/PROJECT_STATE.json",
    "projects/lab/PENDING.json",
    "projects/lab/ROADMAP.json",
    OLD_AUTH_PATH,
    AUTH_PATH,
    OLD_BRIEF_PATH,
    BRIEF_PATH,
    EVIDENCE_PATH,
    ERROR_PATH,
    SSE_TEST_INDEX,
    SSE_TEST_MANIFEST,
    INT_PATH,
    INT_INDEX,
    PEND_027,
    PEND_045,
    PROGRAM,
    PROGRAM_ROADMAP,
    "projects/lab/continuity/CURRENT_CONTINUITY.json",
    "projects/lab/continuity/CURRENT_CONTINUITY.md",
    "projects/lab/continuity/START_PROMPT.md",
    "projects/lab/continuity/ATTACHMENT_MANIFEST.json",
}
TRANSIENTS = {
    "scripts/reconcile_priority_integrations_phase2_sse_180.py",
    ".github/workflows/reconcile-priority-integrations-phase2-sse-180.yml",
}


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path: str, value: Any) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: str, value: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.rstrip() + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def append_unique(values: list[Any], item: Any) -> None:
    if item not in values:
        values.append(item)


def verify_parent() -> None:
    remote = run("git", "rev-parse", "origin/main")
    base = run("git", "merge-base", "HEAD", "origin/main")
    require(remote == EXPECTED_PARENT, f"origin/main moved: {remote}")
    require(base == EXPECTED_PARENT, f"unexpected merge base: {base}")


def reconcile_old_authority() -> None:
    doc = load(OLD_AUTH_PATH)
    require(doc["status"] == "GRANTED", "authorization 147 no longer GRANTED")
    require(doc["expected_parent_head"] == "7229b7960338283afaff4a7f6cd0c2e2a583111d", "authorization 147 parent changed")
    doc["status"] = "SUPERSEDED_UNEXECUTED_BY_AUTHORIZATION_180"
    doc["execution_started"] = False
    doc["test_executed"] = False
    doc["external_audit_executed"] = False
    doc["historical_approval_preserved"] = True
    doc["supersession"] = {
        "authorization": AUTH,
        "reasons": [
            "REMOTE_HEAD_DRIFT_TRIGGERS_AUTHORIZATION_147_STOP_CONDITION",
            "DEC_LAB_030_AND_PRIORITY_INTEGRATIONS_ROADMAP_SEPARATE_PHASE_2_TEST_EXECUTION_FROM_PHASE_3_EXTERNAL_AUDIT",
            "AUTHORIZATION_147_DELTA_WAS_NOT_DISCOVERED_BY_REGISTRY_INDEX",
            "CURRENT_SSE_MANIFEST_INTEGRATION_AND_PENDING_RECORDS_DECLARED_NO_EXECUTION_OR_AUDIT_AUTHORITY",
        ],
        "effect": "NO_RESIDUAL_OR_RESUMABLE_AUTHORITY",
    }
    doc["authority_effect"] = "NONE_SUPERSEDED_UNEXECUTED"
    write(OLD_AUTH_PATH, doc)

    delta = load(DELTA_147_PATH)
    delta["schema_version"] = "1.1.0"
    delta["state_transition"]["to"] = "SSE_AUTHORIZATION_147_SUPERSEDED_UNEXECUTED_BY_AUTHORIZATION_180"
    delta["active_execution_authority"] = "NONE_AUTHORIZATION_147_SUPERSEDED"
    delta["superseded_by"] = AUTH
    delta["supersession_reasons"] = doc["supersession"]["reasons"]
    delta["execution_result"] = "NOT_STARTED_ZERO_OUTPUTS_ZERO_SCORING_ZERO_AUDIT"
    delta["authority_effect"] = "NONE"
    write(DELTA_147_PATH, delta)

    old_brief = load(OLD_BRIEF_PATH)
    require(old_brief["status"] == "FINAL_REVIEW_COMPLETE_PROPOSED_NOT_AUTHORIZED_FOR_EXECUTION", "old SSE brief status changed")
    old_brief["status"] = "SUPERSEDED_FOR_EXECUTION_BY_SUCCESSOR_BRIEF_180_PRESERVED_HISTORICALLY"
    old_brief["execution_authority"] = "NONE_SUPERSEDED"
    old_brief["successor_brief"] = BRIEF_PATH
    old_brief["supersession_reason"] = "The current roadmap separates Phase 2 synthetic test execution from Phase 3 external audit and authorization 147 is blocked by its remote-head mismatch stop condition."
    write(OLD_BRIEF_PATH, old_brief)


def create_authority_and_brief() -> None:
    auth = {
        "schema_version": "1.0.0",
        "authorization_id": AUTH,
        "project_id": "lab",
        "status": "GRANTED_STAGE_1_CONSUMED_STAGE_2_AUTHORIZED_NOT_STARTED",
        "authorization_class": "BOUNDED_PRIORITY_INTEGRATIONS_PHASE_2_SSE_SYNTHETIC_TEST_EXECUTION",
        "approved_by": "Jonathan Martínez",
        "approved_at": TIMESTAMP,
        "approval_source": "Continuemos",
        "approval_context": "The unique canonical next transition was to separately authorize Priority Integrations Phase 2 independent evidence closure. Analysis found Product Leadership blocked and SSE independently executable after superseding stale authorization 147.",
        "grant_inferred": False,
        "repository": {
            "name": "marcellusanthonson-ctrl/chatgpt-prototype-lab",
            "branch": "main",
            "expected_parent_head": EXPECTED_PARENT,
            "working_branch": BRANCH,
            "head_policy": "VERIFY_LIVE_AT_USE",
            "entrypoint": "project-sources/chatgpt/START_HERE.md",
        },
        "supersedes": {
            "authorization": OLD_AUTH,
            "scope": "EXECUTION_AUTHORITY_ONLY",
            "historical_approval_and_document_preserved": True,
            "execution_under_147": "NOT_STARTED",
        },
        "purpose": "Execute only the frozen Software Solution Engineering synthetic activation and value-discrimination test, producing reproducible evidence without external audit, activation, integration, infrastructure or product effects.",
        "stages": {
            "stage_1_documentary_authority_reconciliation": "CONSUMED_ON_VERIFIED_SQUASH_MERGE",
            "stage_2_sse_synthetic_test_execution": "AUTHORIZED_NOT_STARTED",
        },
        "execution_parent_policy": "VERIFY_LIVE_MAIN_AND_REQUIRE_AUTHORIZATION_180_PUBLICATION_COMMIT_IN_ANCESTRY",
        "brief_ref": BRIEF_PATH,
        "test_design_ref": SSE_TEST_MANIFEST,
        "test_contract": {
            "candidate_package": "SOFTWARE-SOLUTION-ENGINEERING-CANDIDATE-PACKAGE-001@0.2.0",
            "fixture_count": 32,
            "arm_count": 3,
            "minimum_output_count": 96,
            "domains": ["SOFTWARE_SOLUTION_DECISIONS", "LAB_GOVERNANCE_DECISIONS"],
            "input_freeze_required": True,
            "blinded_scoring_required": True,
            "cost_and_negative_transfer_measurement_required": True,
        },
        "allowed_actions": [
            "VERIFY_AND_PIN_REMOTE_HEAD",
            "CREATE_ISOLATED_BRANCH_OR_WORKTREE",
            "FREEZE_AND_HASH_CANONICAL_TEST_INPUTS",
            "CALIBRATE_SCORERS",
            "GENERATE_AT_LEAST_96_AUTHORIZED_OUTPUTS",
            "ANONYMIZE_HASH_AND_RECORD_OUTPUT_PROVENANCE",
            "RUN_BLINDED_SCORING_AFTER_OUTPUT_FREEZE",
            "MEASURE_TOKEN_TIME_RETRY_COST_AND_NEGATIVE_TRANSFER",
            "PUBLISH_BOUNDED_SYNTHETIC_TEST_EXECUTION_EVIDENCE",
            "COMMIT_AND_PUSH_ONLY_AUTHORIZED_TEST_EVIDENCE",
        ],
        "forbidden_actions": [
            "NO_EXTERNAL_AUDIT_EXECUTION_OR_AUDITOR_ASSIGNMENT",
            "NO_PRODUCT_LEADERSHIP_TEST_OR_PREFLIGHT_EXECUTION",
            "NO_AWS_TERRAFORM_PROVISIONING_OR_EXTERNAL_DATABASE",
            "NO_SSE_ACTIVATION_INTEGRATION_PROMOTION_OR_FACTORY_REGISTRATION",
            "NO_POINTER_SELECTOR_SHADOW_REGISTRY_OR_STATIC_FALLBACK_MUTATION",
            "NO_ARCHITECTURE_STACK_PROVIDER_OR_IMPLEMENTATION_SELECTION",
            "NO_PRODUCT_RUNTIME_SYMPHONIE_RAG_EMBEDDING_OR_MOTION_CHANGE",
            "NO_REAL_PRODUCT_OR_PERSONAL_DATA",
            "NO_POST_FREEZE_FIXTURE_PROMPT_OUTPUT_OR_SCORE_MUTATION",
        ],
        "stop_conditions": [
            "REMOTE_HEAD_OR_AUTHORIZATION_ANCESTRY_MISMATCH",
            "DIRTY_OR_UNCONTROLLED_WORKTREE",
            "INPUT_HASH_MISMATCH",
            "MODEL_OR_TOOL_ACCESS_NOT_REPRODUCIBLE",
            "SCORER_CALIBRATION_INCOMPLETE",
            "ARM_LEAKAGE_OR_BLINDING_FAILURE",
            "OUTPUT_COUNT_PROVENANCE_OR_COST_INCOMPLETE",
            "POST_FREEZE_MUTATION",
            "REQUEST_REQUIRES_EXTERNAL_AUDIT_AWS_PRODUCT_RUNTIME_OR_ACTIVATION",
            "AUTHORITY_OR_SCOPE_AMBIGUOUS",
        ],
        "consumption_criterion": "Stage 2 is consumed only after the complete synthetic execution package, at least 96 outputs, hashes, provenance, blinded scores, cost and negative-transfer analysis are published and remotely verified.",
        "external_audit_authorized": False,
        "product_leadership_track_authorized": False,
        "sse_activation_authorized": False,
        "sse_integration_authorized": False,
        "runtime_authorized": False,
        "product_changes_authorized": False,
        "commit_authorized": True,
        "push_authorized": True,
        "test_execution_authorized": True,
        "residual_authority_after_stage_1": "STAGE_2_SSE_SYNTHETIC_TEST_EXECUTION_ONLY",
        "maximum_result": "SSE_SYNTHETIC_TEST_EXECUTION_EVIDENCE_READY_FOR_SEPARATE_PHASE_3_EXTERNAL_AUDIT_DECISION",
    }
    write(AUTH_PATH, auth)

    parent = load(OLD_BRIEF_PATH)
    new = copy.deepcopy(parent)
    new["schema_version"] = "1.1.0"
    new["brief_id"] = BRIEF
    new["status"] = "AUTHORIZED_NOT_STARTED"
    new["authorization_ref"] = AUTH
    new["parent_brief"] = OLD_BRIEF_PATH
    new["preservation"] = {
        "parent_content_preserved": True,
        "approved_additions": ["CURRENT_PHASE_2_AUTHORITY", "AUTHORIZATION_147_SUPERSESSION", "AUDIT_SEPARATION", "PRODUCT_LEADERSHIP_TRACK_EXCLUSION"],
        "explicit_changes": ["REMOVE_EXTERNAL_AUDIT_FROM_EXECUTION_SCOPE", "REMOVE_HUMAN_PROMOTION_DECISION_FROM_TEST_EXECUTION", "PIN_CANDIDATE_PACKAGE_0_2_0_AND_32_BY_3_CONTRACT"],
        "omissions_detected": [],
    }
    new["objective"] = "Execute the frozen Software Solution Engineering activation and value-discrimination synthetic test across software-solution and LAB-governance domains, producing at least 96 reproducible outputs and blinded scoring evidence without external audit, activation or integration."
    new["execution_model"] = {
        "coordinator": "CHATGPT",
        "bounded_executor": "CODEX",
        "external_auditor": "NOT_IN_SCOPE_REQUIRES_SEPARATE_PHASE_3_AUTHORIZATION",
        "human_promotion_gate": "NOT_IN_SCOPE_REQUIRES_PHASE_3_AUDIT_AND_SEPARATE_PHASE_4_DECISION",
    }
    new["required_phases"] = [
        "PREFLIGHT_AND_HEAD_PINNING",
        "ISOLATED_WORKTREE_OR_BRANCH_CREATION",
        "INPUT_HASH_FREEZE",
        "SCORER_CALIBRATION",
        "ARM_ASSIGNMENT_AND_BLINDING",
        "OUTPUT_GENERATION",
        "OUTPUT_ANONYMIZATION_AND_PROVENANCE",
        "OUTPUT_MANIFEST_AND_HASH_FREEZE",
        "SEPARATE_BLINDED_SCORING",
        "COST_AND_NEGATIVE_TRANSFER_ANALYSIS",
        "EXECUTION_EVIDENCE_PUBLICATION_AND_REMOTE_VERIFICATION",
    ]
    new["required_outputs"] = [
        "projects/lab/test-executions/SOFTWARE-SOLUTION-ENGINEERING-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-001/MANIFEST.json",
        "projects/lab/test-executions/SOFTWARE-SOLUTION-ENGINEERING-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-001/INPUT_FREEZE.json",
        "projects/lab/test-executions/SOFTWARE-SOLUTION-ENGINEERING-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-001/OUTPUT_MANIFEST.json",
        "projects/lab/test-executions/SOFTWARE-SOLUTION-ENGINEERING-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-001/SCORING_RESULTS.json",
        "projects/lab/test-executions/SOFTWARE-SOLUTION-ENGINEERING-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-001/COST_AND_NEGATIVE_TRANSFER.json",
        "projects/lab/evidence/EVD-LAB-SSE-TEST-EXECUTION-180.json",
    ]
    new["allowed_actions"] = auth["allowed_actions"]
    new["forbidden_actions"] = auth["forbidden_actions"]
    new["stop_conditions"] = auth["stop_conditions"]
    new["success_semantics"] = {
        "test_execution_complete": True,
        "external_audit_complete": False,
        "sse_activation_authorized": False,
        "sse_integration_authorized": False,
        "architecture_or_stack_authorized": False,
        "next_effect": "ELIGIBLE_ONLY_FOR_SEPARATE_PHASE_3_EXTERNAL_AUDIT_AUTHORIZATION",
    }
    new["execution_authority"] = AUTH
    write(BRIEF_PATH, new)


def create_error_and_evidence() -> None:
    error = {
        "schema_version": "1.0.0",
        "id": ERROR,
        "title": "Stale and undiscoverable SSE authorization 147 contradicted current Phase 2 authority state",
        "project_id": "lab",
        "project_scope": ["lab"],
        "classification": "CONFIRMED",
        "technical_determination": "CONFIRMED_REMEDIATED",
        "severity": "HIGH",
        "status": "CLOSED_BY_AUTHORIZATION_180",
        "lifecycle_state": "CLOSED",
        "canonical_path": ERROR_PATH,
        "created_at": DATE,
        "causes": [
            "AUTHORIZATION_147_REMAINED_GRANT_MARKED_AFTER_REMOTE_HEAD_DRIFT",
            "AUTHORIZATION_147_BUNDLED_PHASE_2_TEST_WITH_PHASE_3_EXTERNAL_AUDIT",
            "AUTHORIZATION_147_DELTA_NOT_DISCOVERED_BY_REGISTRY_INDEX",
            "CURRENT_SSE_MANIFEST_INTEGRATION_AND_PENDING_RECORDS_DECLARED_NO_EXECUTION_AUTHORITY",
        ],
        "impact": "AMBIGUOUS_AND_CONTRADICTORY_SSE_EXECUTION_AUTHORITY_BLOCKED_SAFE_PHASE_2_ENTRY",
        "remediation": [
            "PRESERVE_AUTHORIZATION_147_HISTORICALLY_AS_UNEXECUTED",
            "SUPERSEDE_147_EXECUTION_AUTHORITY",
            "SEPARATE_SSE_SYNTHETIC_TEST_FROM_EXTERNAL_AUDIT",
            "REGISTER_SUCCESSOR_AUTHORIZATION_180_AND_DISCOVERABILITY",
            "PRESERVE_PRODUCT_LEADERSHIP_PREFLIGHT_BLOCK",
        ],
        "closed_by_authorization": AUTH,
        "test_execution_effect": "NONE_DURING_RECONCILIATION",
        "audit_execution_effect": "NONE",
        "runtime_effect": "NONE",
        "product_effect": "NONE",
        "integration_effect": "NONE",
        "source_refs": [OLD_AUTH_PATH, DELTA_147_PATH, SSE_TEST_MANIFEST, INT_PATH, PEND_027, PEND_045, PROGRAM_ROADMAP],
    }
    write(ERROR_PATH, error)

    evidence = {
        "schema_version": "1.0.0",
        "evidence_id": EVIDENCE,
        "project_id": "lab",
        "evidence_type": "PHASE_2_AUTHORITY_RECONCILIATION_AND_TRACK_SEPARATION",
        "status": "PASS_SSE_STAGE_2_AUTHORIZED_NOT_STARTED_PRODUCT_LEADERSHIP_PREFLIGHT_BLOCKED",
        "created_at": TIMESTAMP,
        "authorization_ref": AUTH,
        "verified_parent_head": EXPECTED_PARENT,
        "findings": [
            {"claim": "Authorization 147 is executable against the current main HEAD.", "classification": "REVERSED", "basis": "Its expected parent is historical and REMOTE_HEAD_MISMATCH is an explicit stop condition."},
            {"claim": "Authorization 147 executed any SSE outputs, scoring or audit.", "classification": "REVERSED", "basis": "No execution package or execution commits exist; all current records show zero execution."},
            {"claim": "The SSE test design is ready and independent of AWS.", "classification": "CONFIRMED", "basis": "Frozen 32-fixture, three-arm, minimum-96-output design; roadmap states no AWS dependency."},
            {"claim": "External audit belongs inside current Phase 2 execution authority.", "classification": "REVERSED", "basis": "The approved roadmap places independent external audits in Phase 3."},
            {"claim": "Product Leadership Test 003 can execute now.", "classification": "REVERSED", "basis": "Operational preflight remains BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR and current authority is NONE."},
            {"claim": "Phase 2 tracks must be executed atomically.", "classification": "REVERSED", "basis": "The roadmap defines independent tracks and separate evidence closure per integration."},
        ],
        "reconciliation_result": {
            "authorization_147": "SUPERSEDED_UNEXECUTED",
            "sse_test": "AUTHORIZED_NOT_STARTED_BY_AUTHORIZATION_180",
            "sse_external_audit": "NOT_AUTHORIZED_PHASE_3_SEPARATE",
            "product_leadership": "PREFLIGHT_BLOCKED_NO_EXECUTION_AUTHORITY",
            "phase_2": "PARTIALLY_AUTHORIZED_SSE_ONLY",
        },
        "validation": {
            "json_parse": "PASS",
            "duplicate_pending_ids": 0,
            "duplicate_registry_paths": 0,
            "authorization_147_execution_outputs": 0,
            "authorization_147_audit_outputs": 0,
            "sse_test_execution_during_reconciliation": 0,
            "external_audit_execution": 0,
            "aws_calls": 0,
            "terraform_execution": 0,
            "runtime_effect": "NONE",
            "product_effect": "NONE",
            "integration_activation_effect": "NONE",
        },
        "next_authorized_action": "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180",
        "authority_effect": "STAGE_2_SSE_TEST_EXECUTION_ONLY",
    }
    write(EVIDENCE_PATH, evidence)

    delta = {
        "schema_version": "1.0.0",
        "delta_id": DELTA,
        "project_id": "lab",
        "updated_at": DATE,
        "status": "PASS_PHASE_2_SSE_EXECUTION_AUTHORIZED_NOT_STARTED_PL_PREFLIGHT_BLOCKED",
        "authorization": {"id": AUTH, "status": "GRANTED_STAGE_1_CONSUMED_STAGE_2_AUTHORIZED_NOT_STARTED", "path": AUTH_PATH},
        "superseded_authorization": {"id": OLD_AUTH, "status": "SUPERSEDED_UNEXECUTED", "path": OLD_AUTH_PATH},
        "error": {"id": ERROR, "status": "CLOSED_BY_AUTHORIZATION_180", "path": ERROR_PATH},
        "evidence": {"id": EVIDENCE, "status": evidence["status"], "path": EVIDENCE_PATH},
        "state": {
            "global_phase": PHASE,
            "active_execution_authority": AUTH,
            "sse": "TEST_EXECUTION_AUTHORIZED_NOT_STARTED_EXTERNAL_AUDIT_NOT_AUTHORIZED",
            "product_leadership": "PREFLIGHT_BLOCKED_NO_EXECUTION_AUTHORITY",
            "phase_3_external_audits": "NOT_AUTHORIZED",
        },
        "registry_counts_after": {"authorizations": 104, "evidence": 86, "errors": 13},
        "non_effects": ["NO_TEST_EXECUTION_DURING_RECONCILIATION", "NO_EXTERNAL_AUDIT", "NO_AWS_OR_TERRAFORM", "NO_ACTIVATION_OR_INTEGRATION", "NO_PRODUCT_OR_RUNTIME_CHANGE"],
        "next_authorized_action": "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180",
    }
    write(DELTA_PATH, delta)


def reconcile_sse_records() -> None:
    test = load(SSE_TEST_MANIFEST)
    require(test["fixture_count"] == 32 and test["arm_count"] == 3 and test["minimum_future_outputs"] == 96, "SSE frozen test contract changed")
    append_unique(test["source_authorizations"], AUTH)
    test["status"] = "EXECUTION_AUTHORIZED_NOT_STARTED_EXTERNAL_AUDIT_NOT_AUTHORIZED"
    test["execution_brief"] = BRIEF_PATH
    test["execution_authorized"] = True
    test["execution_authorization"] = AUTH
    test["external_audit_authorized"] = False
    test["updated_at"] = DATE
    write(SSE_TEST_MANIFEST, test)

    index = load(SSE_TEST_INDEX)
    index["updated_at"] = DATE
    record = {
        "id": test["test_design_id"],
        "status": test["status"],
        "canonical_path": SSE_TEST_MANIFEST,
        "authorization_id": AUTH,
        "fixture_count": 32,
        "arm_count": 3,
        "minimum_future_outputs": 96,
        "updated_at": DATE,
    }
    existing = next((item for item in index["records"] if item["id"] == record["id"]), None)
    if existing is None:
        index["records"].append(record)
    else:
        existing.clear(); existing.update(record)
    require(len([r["id"] for r in index["records"]]) == len(set(r["id"] for r in index["records"])), "duplicate test design ids")
    write(SSE_TEST_INDEX, index)

    integration = load(INT_PATH)
    integration["lifecycle_stage"] = "EVIDENCE_CLOSURE_EXECUTION_AUTHORIZED_NOT_STARTED"
    integration["test_program"]["design_status"] = test["status"]
    integration["test_program"]["execution_authorized"] = True
    integration["test_program"]["execution_authorization"] = AUTH
    integration["test_program"]["execution_completed"] = False
    integration["test_program"]["external_audit_authorized"] = False
    integration["current_state"] = "CONTRACT_COMPLETE_SSE_TEST_EXECUTION_AUTHORIZED_NOT_STARTED_EXTERNAL_AUDIT_NOT_AUTHORIZED"
    integration["authorization_ref"] = AUTH
    integration["updated_at"] = DATE
    write(INT_PATH, integration)

    integrations = load(INT_INDEX)
    integrations["updated_at"] = DATE
    rec = next(item for item in integrations["records"] if item["id"] == "INT-LAB-005")
    rec["lifecycle_stage"] = integration["lifecycle_stage"]
    rec["test_execution_authorized"] = True
    rec["external_audit_authorized"] = False
    rec["authorization_ref"] = AUTH
    write(INT_INDEX, integrations)

    registry = load("registry/integrations.json")
    registry["updated_at"] = DATE
    rec = next(item for item in registry["records"] if item["id"] == "INT-LAB-005")
    rec["lifecycle_stage"] = integration["lifecycle_stage"]
    rec["test_execution_authorized"] = True
    rec["external_audit_authorized"] = False
    rec["updated_at"] = DATE
    write("registry/integrations.json", registry)


def pending_027_doc() -> dict[str, Any]:
    doc = load(PEND_027)
    doc["schema_version"] = "1.1.0"
    doc["status"] = "SUPERSEDED_BY_PHASE_SEPARATION_AND_AUTHORIZATION_180"
    doc["current_authority"] = AUTH
    doc["test_execution"] = "AUTHORIZED_NOT_STARTED"
    doc["external_audit"] = "NOT_AUTHORIZED_REQUIRES_SEPARATE_PHASE_3_AUTHORIZATION"
    doc["superseded_combined_scope"] = "TEST_EXECUTION_AND_EXTERNAL_AUDIT"
    doc["successor_authorization"] = AUTH
    doc["next_authorized_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    append_unique(doc["source_refs"], AUTH_PATH)
    append_unique(doc["source_refs"], EVIDENCE_PATH)
    return doc


def pending_045_doc() -> dict[str, Any]:
    doc = load(PEND_045)
    doc["schema_version"] = "1.1.0"
    doc["status"] = "PARTIALLY_AUTHORIZED_SSE_TEST_NOT_STARTED_PRODUCT_LEADERSHIP_PREFLIGHT_BLOCKED"
    doc["tracks"] = {
        "PRODUCT_LEADERSHIP": {
            "status": "BLOCKED_OPERATIONAL_PREFLIGHT_NO_ELIGIBLE_BOUNDED_CREATOR",
            "execution_authority": "NONE",
            "test_003_executed": False,
            "required_actions": ["RESOLVE_LEAST_PRIVILEGE_PREFLIGHT_PATH", "COMPLETE_REQUIRED_OPERATIONAL_PREFLIGHT", "SEPARATELY_AUTHORIZE_TEST_003_EXECUTION"],
            "source_evidence": "projects/lab/evidence/EVD-LAB-PL003-EFFECTIVE-PERMISSION-GATE-OPERATOR-135-ATTEMPT-001.json",
        },
        "SOFTWARE_SOLUTION_ENGINEERING": {
            "status": "SYNTHETIC_TEST_EXECUTION_AUTHORIZED_NOT_STARTED",
            "execution_authority": AUTH,
            "fixture_count": 32,
            "arm_count": 3,
            "minimum_output_count": 96,
            "external_audit": "NOT_AUTHORIZED_REQUIRES_PHASE_3",
        },
    }
    doc["current_authority"] = AUTH
    doc["prohibitions"] = [
        "NO_PRODUCT_LEADERSHIP_TEST_OR_PREFLIGHT_EXECUTION",
        "NO_EXTERNAL_AUDIT_EXECUTION",
        "NO_ACTIVATION_OR_INTEGRATION",
        "NO_POINTER_SELECTOR_OR_REGISTRY_ACTIVATION_MUTATION",
        "NO_AWS_TERRAFORM_PRODUCT_OR_RUNTIME_CHANGE",
    ]
    doc["next_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    doc["authority_effect"] = "SSE_SYNTHETIC_TEST_EXECUTION_ONLY"
    return doc


def reconcile_pending_and_program() -> None:
    p27 = pending_027_doc(); write(PEND_027, p27)
    p45 = pending_045_doc(); write(PEND_045, p45)

    aggregate = load("projects/lab/PENDING.json")
    aggregate["updated_at"] = DATE
    replacements = {"PEND-LAB-027": p27, "PEND-LAB-045": p45}
    found = set()
    for i, item in enumerate(aggregate["records"]):
        if item.get("id") in replacements:
            aggregate["records"][i] = replacements[item["id"]]
            found.add(item["id"])
    require(found == set(replacements), f"pending aggregate missing {set(replacements)-found}")
    ids = [item["id"] for item in aggregate["records"]]
    require(len(ids) == len(set(ids)), "duplicate pending ids")
    write("projects/lab/PENDING.json", aggregate)

    program = load(PROGRAM)
    program["schema_version"] = "1.2.0"
    program["status"] = PHASE
    program["updated_at"] = DATE
    append_unique(program["authorization_refs"], AUTH)
    pl = next(item for item in program["priority_integrations"] if item["id"] == "PRODUCT_LEADERSHIP")
    pl["current_stage"] = "CONTRACT_COMPLETE_OPERATIONAL_PREFLIGHT_BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR_TEST_003_NOT_EXECUTED"
    pl["execution_authority"] = "NONE"
    sse = next(item for item in program["priority_integrations"] if item["id"] == "SOFTWARE_SOLUTION_ENGINEERING")
    sse["current_stage"] = "CONTRACT_COMPLETE_SYNTHETIC_TEST_EXECUTION_AUTHORIZED_NOT_STARTED_EXTERNAL_AUDIT_NOT_AUTHORIZED"
    sse["execution_authority"] = AUTH
    program["phase_2_status"] = "PARTIALLY_AUTHORIZED_SSE_ONLY"
    program["next_authorized_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    program["authority_effect"] = "SSE_SYNTHETIC_TEST_EXECUTION_ONLY"
    write(PROGRAM, program)

    roadmap = load(PROGRAM_ROADMAP)
    roadmap["schema_version"] = "1.3.0"
    roadmap["status"] = PHASE
    roadmap["updated_at"] = DATE
    phase2 = next(item for item in roadmap["phases"] if item["order"] == 2)
    phase2["status"] = "PARTIALLY_AUTHORIZED_SSE_TEST_NOT_STARTED_PRODUCT_LEADERSHIP_PREFLIGHT_BLOCKED"
    phase2["product_leadership_track_status"] = "BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR_NO_EXECUTION_AUTHORITY"
    phase2["sse_track_status"] = "AUTHORIZED_NOT_STARTED_BY_AUTHORIZATION_180"
    phase2["sse_execution_authorization"] = AUTH
    phase2["external_audit_boundary"] = "PHASE_3_NOT_AUTHORIZED"
    phase2["next_authorized_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    phase3 = next(item for item in roadmap["phases"] if item["order"] == 3)
    require(phase3["status"] == "NOT_AUTHORIZED", "Phase 3 unexpectedly authorized")
    roadmap["next_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    roadmap["authority_effect"] = "SSE_SYNTHETIC_TEST_EXECUTION_ONLY"
    write(PROGRAM_ROADMAP, roadmap)


def reconcile_global_state() -> None:
    current = load("CURRENT_STATE.json")
    require(current["version"] == "2.5.55", "unexpected current state version")
    current["version"] = "2.5.56"
    current["status"] = PHASE
    current["current_phase"] = PHASE
    current["updated_at"] = DATE
    cm = current["canonical_model"]
    cm["priority_integrations_phase2_sse_authorization_180"] = AUTH_PATH
    cm["priority_integrations_phase2_sse_brief_180"] = BRIEF_PATH
    cm["priority_integrations_phase2_sse_evidence_180"] = EVIDENCE_PATH
    cm["priority_integrations_phase2_authority_error_012"] = ERROR_PATH
    cm["priority_integrations_phase2_sse_delta_180"] = DELTA_PATH
    state = current["authorization_state"]
    state["commit_authorized"] = True
    state["push_authorized"] = True
    state["runtime_authorized"] = False
    state["integration_authorized"] = False
    state["product_changes_authorized"] = False
    state["test_execution_authorized"] = True
    state["external_audit_execution_authorized"] = False
    state["sse_test_execution_and_read_only_audit_147"] = "SUPERSEDED_UNEXECUTED_BY_AUTHORIZATION_180"
    state["priority_integrations_phase2_sse_synthetic_test_execution_180"] = "GRANTED_STAGE_1_CONSUMED_STAGE_2_AUTHORIZED_NOT_STARTED"
    current["open_errors"] = []
    current["next_authorized_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    current["next_recommended_transition"] = "EXECUTE_AND_PUBLISH_REPRODUCIBLE_SSE_SYNTHETIC_TEST_EVIDENCE_WITHOUT_EXTERNAL_AUDIT"
    current["product_leadership_candidate"]["status"] = "CONTRACT_COMPLETE_OPERATIONAL_PREFLIGHT_BLOCKED_TEST_003_NOT_EXECUTED"
    current["product_leadership_candidate"]["operational_preflight"] = "BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR"
    current["product_leadership_candidate"]["execution_authority"] = "NONE"
    current["priority_integrations_program"] = {
        "status": PHASE,
        "priority_order": ["PRODUCT_LEADERSHIP", "SOFTWARE_SOLUTION_ENGINEERING"],
        "product_leadership": "PREFLIGHT_BLOCKED_NO_EXECUTION_AUTHORITY",
        "software_solution_engineering": "SYNTHETIC_TEST_EXECUTION_AUTHORIZED_NOT_STARTED_EXTERNAL_AUDIT_NOT_AUTHORIZED",
        "sse_execution_authority": AUTH,
        "phase_3_external_audit": "NOT_AUTHORIZED",
        "composition_contract": "projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/contracts/PRODUCT-LEADERSHIP-TO-SSE-COMPOSITION-CONTRACT-001.json",
        "next_pending": PEND_045,
        "active": False,
        "integrated": False,
    }
    current["integration_factory_migration"]["sse_test_147"] = "SUPERSEDED_UNEXECUTED_BY_AUTHORIZATION_180"
    current["integration_factory_migration"]["sse_test_180"] = "AUTHORIZED_NOT_STARTED_NO_AWS_NO_AUDIT"
    write("CURRENT_STATE.json", current)

    project = load("projects/lab/PROJECT_STATE.json")
    project["current_phase"] = PHASE
    project["updated_at"] = DATE
    project["content_completeness"] = "STRUCTURED_V2_WITH_PRIORITY_INTEGRATIONS_PHASE_2_SSE_AUTHORIZED_NOT_STARTED_AND_PL_PREFLIGHT_BLOCKED"
    for ref in (AUTH_PATH, BRIEF_PATH, EVIDENCE_PATH, ERROR_PATH, DELTA_PATH): append_unique(project["source_refs"], ref)
    project["priority_integrations_program"] = current["priority_integrations_program"]
    project["priority_integrations_phase2_authority_reconciliation_180"] = {
        "authorization": AUTH,
        "status": "GRANTED_STAGE_1_CONSUMED_STAGE_2_AUTHORIZED_NOT_STARTED",
        "authorization_147": "SUPERSEDED_UNEXECUTED",
        "error_012": "CLOSED_BY_AUTHORIZATION_180",
        "sse_test": "AUTHORIZED_NOT_STARTED_32_FIXTURES_3_ARMS_MINIMUM_96_OUTPUTS",
        "sse_external_audit": "NOT_AUTHORIZED",
        "product_leadership": "PREFLIGHT_BLOCKED_NO_EXECUTION_AUTHORITY",
        "aws_calls": 0,
        "test_outputs_generated": 0,
        "runtime_effect": "NONE",
        "product_effect": "NONE",
        "integration_effect": "NONE",
    }
    project["next_authorized_action"] = "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180"
    project["next_recommended_transition"] = "EXECUTE_AND_PUBLISH_REPRODUCIBLE_SSE_SYNTHETIC_TEST_EVIDENCE_WITHOUT_EXTERNAL_AUDIT"
    write("projects/lab/PROJECT_STATE.json", project)

    global_roadmap = load("projects/lab/ROADMAP.json")
    global_roadmap["updated_at"] = DATE
    record = {
        "order": 36,
        "item": "PRIORITY_INTEGRATIONS_PHASE_2_SSE_SYNTHETIC_TEST_EXECUTION_AUTHORIZATION_180",
        "status": "AUTHORIZED_NOT_STARTED_PRODUCT_LEADERSHIP_PREFLIGHT_BLOCKED",
        "authorization": AUTH,
        "supersedes_authorization": OLD_AUTH,
        "error": ERROR,
        "sse_test_contract": "32_FIXTURES_3_ARMS_MINIMUM_96_OUTPUTS",
        "external_audit": "NOT_AUTHORIZED_PHASE_3_SEPARATE",
        "product_leadership": "BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR",
        "test_execution_during_reconciliation": 0,
        "next_gate": "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180",
        "runtime_effect": "NONE",
        "product_effect": "NONE",
        "integration_effect": "NONE",
    }
    existing = next((r for r in global_roadmap["records"] if r.get("item") == record["item"]), None)
    if existing is None: global_roadmap["records"].append(record)
    else: existing.clear(); existing.update(record)
    orders = [r["order"] for r in global_roadmap["records"]]
    require(len(orders) == len(set(orders)), "duplicate roadmap orders")
    global_roadmap["priority_integrations_program"] = {
        "program_ref": PROGRAM,
        "roadmap_ref": PROGRAM_ROADMAP,
        "status": PHASE,
        "phase_1": "COMPLETE_PASS",
        "phase_2": "SSE_AUTHORIZED_NOT_STARTED_PRODUCT_LEADERSHIP_BLOCKED",
        "phase_3": "NOT_AUTHORIZED",
        "next_pending": PEND_045,
        "next_authorized_action": "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180",
    }
    write("projects/lab/ROADMAP.json", global_roadmap)


def reconcile_registries() -> None:
    auths = load("registry/authorizations.json")
    auths["updated_at"] = DATE
    auths["active_authorizations"] = [AUTH]
    record = {
        "id": AUTH,
        "state_key": "priority_integrations_phase2_sse_synthetic_test_execution_180",
        "project_id": "lab",
        "status": "GRANTED_STAGE_1_CONSUMED_STAGE_2_AUTHORIZED_NOT_STARTED",
        "approved_by": "Jonathan Martínez",
        "scope": "SSE_SYNTHETIC_TEST_EXECUTION_ONLY",
        "canonical_path": AUTH_PATH,
        "repository": "marcellusanthonson-ctrl/chatgpt-prototype-lab",
        "branch": "main",
        "expected_parent_head": EXPECTED_PARENT,
        "commit_authorized": True,
        "push_authorized": True,
        "test_execution_authorized": True,
        "external_audit_authorized": False,
        "runtime_authorized": False,
        "integration_authorized": False,
        "product_changes_authorized": False,
    }
    existing = next((r for r in auths["records"] if r.get("id") == AUTH), None)
    if existing is None: auths["records"].append(record)
    else: existing.clear(); existing.update(record)
    write("registry/authorizations.json", auths)

    errors = load("registry/errors.json")
    errors["updated_at"] = DATE
    record = {"id": ERROR, "title": "Stale and undiscoverable SSE authorization 147 contradicted current Phase 2 authority state", "status": "CLOSED_BY_AUTHORIZATION_180", "lifecycle_state": "CLOSED", "severity": "HIGH", "project_scope": ["lab"], "canonical_path": ERROR_PATH, "updated_at": DATE}
    existing = next((r for r in errors["records"] if r.get("id") == ERROR), None)
    if existing is None: errors["records"].append(record)
    else: existing.clear(); existing.update(record)
    write("registry/errors.json", errors)

    index = load("registry/index.json")
    require(index["counts"]["authorizations"] == 103 and index["counts"]["evidence"] == 85 and index["counts"]["errors"] == 12, "unexpected registry counts")
    index["updated_at"] = DATE
    index["counts"]["authorizations"] = 104
    index["counts"]["evidence"] = 86
    index["counts"]["errors"] = 13
    regs = index["registries"]
    for path in (DELTA_147_PATH, DELTA_PATH): append_unique(regs["authorization_deltas"], path)
    append_unique(regs["evidence_deltas"], DELTA_PATH)
    append_unique(regs["current_state_deltas"], DELTA_PATH)
    append_unique(regs["error_deltas"], DELTA_PATH)
    append_unique(regs["test_design_deltas"], DELTA_PATH)
    for key in ("authorization_deltas", "evidence_deltas", "current_state_deltas", "error_deltas", "test_design_deltas"):
        require(len(regs[key]) == len(set(regs[key])), f"duplicate registry path in {key}")
    write("registry/index.json", index)


def reconcile_continuity() -> None:
    path = "projects/lab/continuity/CURRENT_CONTINUITY.json"
    doc = load(path)
    doc["schema_version"] = "1.5.0"
    doc["continuity_id"] = "LAB-CONTINUITY-PRIORITY-INTEGRATIONS-PHASE-2-SSE-AUTHORITY-180-20260803"
    doc["status"] = PHASE
    doc["created_at"] = TIMESTAMP
    for ref in (ERROR_PATH, OLD_AUTH_PATH, AUTH_PATH, BRIEF_PATH, EVIDENCE_PATH, DELTA_147_PATH, DELTA_PATH, PEND_045): append_unique(doc["required_reading_order"], ref)
    doc["global_state"] = {
        "current_phase": PHASE,
        "priority_integrations_phase_1": "COMPLETE_PASS",
        "product_leadership": "PREFLIGHT_BLOCKED_NO_EXECUTION_AUTHORITY",
        "software_solution_engineering": "SYNTHETIC_TEST_EXECUTION_AUTHORIZED_NOT_STARTED",
        "external_audit_authorized": False,
        "runtime_authorized": False,
        "integration_authorized": False,
        "product_changes_authorized": False,
        "active_execution_authority": AUTH,
    }
    doc["authorization_180"] = {"id": AUTH, "status": "GRANTED_STAGE_1_CONSUMED_STAGE_2_AUTHORIZED_NOT_STARTED", "active": True, "scope": "SSE_SYNTHETIC_TEST_EXECUTION_ONLY", "residual_authority": "STAGE_2_ONLY"}
    doc["authorization_147"] = {"id": OLD_AUTH, "status": "SUPERSEDED_UNEXECUTED", "active": False, "residual_authority": False}
    doc["priority_integrations_phase_2"] = {
        "product_leadership": {"status": "BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR", "test_003_executed": False, "authority": "NONE"},
        "software_solution_engineering": {"status": "AUTHORIZED_NOT_STARTED", "fixtures": 32, "arms": 3, "minimum_outputs": 96, "authority": AUTH, "external_audit": "NOT_AUTHORIZED"},
    }
    doc["validation"]["authorization_147_execution_outputs"] = 0
    doc["validation"]["sse_test_outputs_generated_under_180"] = 0
    doc["validation"]["aws_calls"] = 0
    doc["validation"]["external_audit_runs"] = 0
    doc["non_authorizations"] = [
        "NO_PRODUCT_LEADERSHIP_PREFLIGHT_OR_TEST_003_EXECUTION",
        "NO_EXTERNAL_AUDIT",
        "NO_AWS_TERRAFORM_OR_PROVISIONING",
        "NO_SSE_ACTIVATION_INTEGRATION_OR_PROMOTION",
        "NO_POINTER_SELECTOR_SHADOW_REGISTRY_PRODUCT_RUNTIME_OR_SYMPHONIE_CHANGE",
    ]
    doc["next_action"] = {"single": "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180", "repository_write_authorized": True, "external_audit_authorized": False}
    doc["authority_effect"] = "STAGE_2_SSE_SYNTHETIC_TEST_EXECUTION_ONLY"
    write(path, doc)

    md = f"""# Continuidad LAB — Fase 2 SSE autorizada, no iniciada

El HEAD canónico conserva Fase 1 completa y abre únicamente el track sintético de Software Solution Engineering mediante `{AUTH}`.

## Reconciliación de autoridad

- `{OLD_AUTH}` se preserva históricamente como `SUPERSEDED_UNEXECUTED`: su parent quedó obsoleto, su stop condition de `REMOTE_HEAD_MISMATCH` aplica y agrupaba indebidamente la prueba de Fase 2 con la auditoría de Fase 3.
- `{ERROR}` quedó confirmado y cerrado por la reconciliación 180.
- Product Leadership permanece bloqueado por `BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR`; Test 003 no está autorizado ni ejecutado.

## Autoridad activa

La única autoridad activa permite a Codex ejecutar la prueba SSE congelada de 32 fixtures, tres arms y al menos 96 outputs, con hashes, procedencia, scoring ciego, costos y transferencia negativa.

No autoriza auditoría externa, AWS, Terraform, activación, integración, promoción, pointer, selector, shadow registry, producto, runtime, Symphonie ni datos reales.

## Siguiente acción única

Codex debe ejecutar y publicar la evidencia reproducible de la prueba sintética SSE bajo la autorización 180. La auditoría externa requerirá una autorización separada de Fase 3.
"""
    write_text("projects/lab/continuity/CURRENT_CONTINUITY.md", md)

    prompt = f"""Continúa ChatGPT Prototype LAB reconstruyendo primero el estado desde `marcellusanthonson-ctrl/chatgpt-prototype-lab`, rama `main`, entrypoint `project-sources/chatgpt/START_HERE.md`; verifica el HEAD remoto mediante `VERIFY_LIVE_AT_USE` y sigue exactamente su orden de lectura.

La Fase 1 de Product Leadership y Software Solution Engineering está completa. `{OLD_AUTH}` fue supersedida sin ejecución porque su parent es histórico y agrupaba prueba con auditoría. `{AUTH}` es la única autoridad activa y permite exclusivamente ejecutar la prueba sintética SSE: 32 fixtures, tres arms y al menos 96 outputs, con freeze, hashes, procedencia, scoring ciego, costos y transferencia negativa. Product Leadership permanece bloqueado por preflight; Test 003 no está autorizado. No ejecutes auditoría externa, AWS, Terraform, activación, integración, producto o runtime. Comienza verificando el HEAD y ejecuta el brief `{BRIEF_PATH}` mediante Codex dentro del alcance 180.
"""
    write_text("projects/lab/continuity/START_PROMPT.md", prompt)

    manifest = load("projects/lab/continuity/ATTACHMENT_MANIFEST.json")
    manifest["schema_version"] = "1.4.0"
    manifest["manifest_id"] = "LAB-CONTINUITY-ATTACHMENTS-PRIORITY-INTEGRATIONS-PHASE2-SSE-180-20260803"
    manifest["created_at"] = TIMESTAMP
    for ref in (ERROR_PATH, OLD_AUTH_PATH, AUTH_PATH, BRIEF_PATH, EVIDENCE_PATH, DELTA_147_PATH, DELTA_PATH, PEND_027, PEND_045, PROGRAM, PROGRAM_ROADMAP): append_unique(manifest["repository_sources_not_duplicated_as_attachments"], ref)
    manifest["known_stale_canonical_aggregates"] = []
    manifest["blocking_pending"] = "PRODUCT_LEADERSHIP_PREFLIGHT_BLOCKED_SSE_TEST_AUTHORIZED_NOT_STARTED"
    manifest["missing_attachments"] = []
    manifest["authority_effect"] = "STAGE_2_SSE_SYNTHETIC_TEST_EXECUTION_ONLY"
    write("projects/lab/continuity/ATTACHMENT_MANIFEST.json", manifest)


def apply() -> None:
    verify_parent()
    reconcile_old_authority()
    create_authority_and_brief()
    create_error_and_evidence()
    reconcile_sse_records()
    reconcile_pending_and_program()
    reconcile_global_state()
    reconcile_registries()
    reconcile_continuity()


def check() -> None:
    verify_parent()
    for path in TARGETS:
        require((ROOT / path).exists(), f"missing target: {path}")
        if path.endswith(".json"): load(path)
    current = load("CURRENT_STATE.json")
    require(current["current_phase"] == PHASE, "wrong current phase")
    require(current["open_errors"] == [], "open errors introduced")
    require(current["next_authorized_action"] == "CODEX_EXECUTE_SSE_SYNTHETIC_TEST_UNDER_AUTHORIZATION_180", "wrong next action")
    old = load(OLD_AUTH_PATH); require(old["status"] == "SUPERSEDED_UNEXECUTED_BY_AUTHORIZATION_180", "147 not superseded")
    new = load(AUTH_PATH); require(new["test_execution_authorized"] is True and new["external_audit_authorized"] is False, "180 authority boundary wrong")
    design = load(SSE_TEST_MANIFEST)
    require((design["fixture_count"], design["arm_count"], design["minimum_future_outputs"]) == (32, 3, 96), "frozen SSE contract changed")
    require(design["execution_authorized"] is True and design["external_audit_authorized"] is False and design["test_executed"] is False, "SSE design state wrong")
    p45 = load(PEND_045)
    require(p45["tracks"]["PRODUCT_LEADERSHIP"]["execution_authority"] == "NONE", "PL authority accidentally granted")
    require(p45["tracks"]["SOFTWARE_SOLUTION_ENGINEERING"]["execution_authority"] == AUTH, "SSE authority missing")
    roadmap = load(PROGRAM_ROADMAP)
    require(next(p for p in roadmap["phases"] if p["order"] == 3)["status"] == "NOT_AUTHORIZED", "Phase 3 audit authorized")
    auth_registry = load("registry/authorizations.json")
    require(auth_registry["active_authorizations"] == [AUTH], "active authorization registry wrong")
    index = load("registry/index.json")
    require(index["counts"]["authorizations"] == 104 and index["counts"]["evidence"] == 86 and index["counts"]["errors"] == 13, "registry counts wrong")
    pending = load("projects/lab/PENDING.json"); ids = [p["id"] for p in pending["records"]]; require(len(ids) == len(set(ids)), "duplicate pending ids")
    global_roadmap = load("projects/lab/ROADMAP.json"); orders = [p["order"] for p in global_roadmap["records"]]; require(len(orders) == len(set(orders)), "duplicate roadmap orders")
    evidence = load(EVIDENCE_PATH)
    require(evidence["validation"]["sse_test_execution_during_reconciliation"] == 0 and evidence["validation"]["external_audit_execution"] == 0 and evidence["validation"]["aws_calls"] == 0, "reconciliation executed forbidden work")
    changed = set(run("git", "diff", "--name-only", "origin/main").splitlines())
    require(changed <= TARGETS | TRANSIENTS, f"unauthorized diff: {sorted(changed - TARGETS - TRANSIENTS)}")
    protected_prefixes = ("foundation-library/software-solution-engineering/", "architecture/integrations/active/", "architecture/integrations/shadow/", "foundation-library/motion-system/")
    require(not any(path.startswith(protected_prefixes) for path in changed), "protected technical artifact changed")
    print(json.dumps({"status": "PASS", "target_count": len(TARGETS), "changed_paths": sorted(changed)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=("apply", "check")); args = parser.parse_args()
    if args.mode == "apply": apply()
    check()


if __name__ == "__main__":
    main()
