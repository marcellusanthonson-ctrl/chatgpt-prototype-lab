#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARENT = "234b595b40309e8bcdc01448d91ea6b88c9e1cd2"
AUTH_ID = "AUTHORIZATION_LAB_POST_178_CANONICAL_STATE_AND_PHASE1_EVIDENCE_RECONCILIATION_179"
BRIEF_ID = "CODEX_POST_178_CANONICAL_STATE_AND_PHASE1_EVIDENCE_RECONCILIATION_179_001"
EVIDENCE_ID = "EVD-LAB-POST-178-CANONICAL-STATE-RECONCILIATION-179"
DELTA_ID = "post-178-canonical-state-phase1-evidence-reconciliation-179"
BRANCH = "post178-canonical-reconciliation-179"
DATE = "2026-08-03"
TIMESTAMP = "2026-08-03T09:24:00-04:00"
PHASE = "PRIORITY_INTEGRATIONS_PHASE_1_CONTRACT_COMPLETE_TESTS_NOT_AUTHORIZED"

AUTH_PATH = f"projects/lab/authorizations/{AUTH_ID}.json"
BRIEF_PATH = f"projects/lab/briefs/{BRIEF_ID}.json"
EVIDENCE_PATH = f"projects/lab/evidence/{EVIDENCE_ID}.json"
DELTA_PATH = f"registry/deltas/{DELTA_ID}.json"

TARGET_PATHS = {
    "CURRENT_STATE.json",
    "projects/lab/PROJECT_STATE.json",
    "projects/lab/PENDING.json",
    "projects/lab/ROADMAP.json",
    "projects/lab/evidence/EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-1-170.json",
    "projects/lab/continuity/CURRENT_CONTINUITY.json",
    "projects/lab/continuity/CURRENT_CONTINUITY.md",
    "projects/lab/continuity/START_PROMPT.md",
    "projects/lab/continuity/ATTACHMENT_MANIFEST.json",
    "registry/index.json",
    AUTH_PATH,
    BRIEF_PATH,
    EVIDENCE_PATH,
    DELTA_PATH,
}
TRANSIENT_PATHS = {
    "scripts/reconcile_post178_canonical_state_179.py",
    ".github/workflows/reconcile-post178-179.yml",
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


def append_unique(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_parent() -> None:
    remote_main = run("git", "rev-parse", "origin/main")
    merge_base = run("git", "merge-base", "HEAD", "origin/main")
    require(remote_main == EXPECTED_PARENT, f"origin/main moved: {remote_main}")
    require(merge_base == EXPECTED_PARENT, f"unexpected merge base: {merge_base}")


def reconcile_phase1_evidence() -> None:
    path = "projects/lab/evidence/EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-1-170.json"
    doc = load(path)
    require(doc["status"] == "PASS_BRANCH_VALIDATED_PUBLICATION_PENDING", "unexpected EVD-170 status")
    doc["schema_version"] = "1.1.0"
    doc["status"] = "PASS_ON_VERIFIED_SQUASH_MERGE_AND_REMOTE_PUBLICATION"
    doc["publication"] = {
        "method": "SQUASH_MERGE",
        "pull_request": 12,
        "main_commit": "1204d9c56af79b4d9a840c6609716aca94ecfb65",
        "merged_at": "2026-08-02T06:14:48Z",
        "remote_verification": "PASS",
    }
    doc["remote_checks_completed"] = [
        "BRANCH_TO_MAIN_COMPARE_PASS",
        "SQUASH_MERGE_PASS",
        "REMOTE_HEAD_VERIFICATION_PASS",
    ]
    doc["remote_checks_pending"] = []
    doc["post_publication_reconciliation"] = {
        "authorization_ref": AUTH_ID,
        "classification": "MODIFIED",
        "reason": "Technical findings were correct; publication fields remained at the pre-merge branch state after PR 12 was squash-merged and verified.",
        "technical_result_changed": False,
    }
    write(path, doc)


def current_motion_state() -> dict[str, Any]:
    return {
        "status": "INITIAL_EFFECTS_COMPLETE_REMAINING_LIBRARY_POPULATION_AND_SEPARATE_PROMOTION_GATES",
        "decision": "DEC-LAB-029",
        "authorization": "AUTHORIZATION_LAB_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_167",
        "root": "foundation-library/motion-system/MOTION-SYSTEM-001",
        "implemented_effects": 2,
        "planned_effects": 61,
        "maximum_effect_status": "ROADMAP_AND_STATISTICS_COUNTER_HUMAN_APPROVED_CANONICAL_REFERENCES_DESIGNATED_BEHAVIOR_CORES_VALIDATED",
        "product_effect": "NONE",
        "runtime_effect": "NONE",
        "authorization_state": "AUTHORIZATIONS_167_THROUGH_178_CONSUMED_NO_RESIDUAL_AUTHORITY",
        "validation": "BOTH_INITIAL_EFFECTS_SOURCE_FIDELITY_APPROVED_AND_BEHAVIOR_CORE_VALIDATION_PASS",
        "source_fidelity_171": {
            "status": "SUPERSEDED_BY_SECTION_SCOPED_CANDIDATE_002_HUMAN_APPROVAL_AND_AUTHORIZATION_176",
            "current_neutral_derivation": "REJECTED_AS_CANONICAL_REFERENCE_PRESERVED_HISTORICALLY",
            "source_faithful_candidate_001": "HUMAN_REVIEW_REJECTED_SCOPE_OVERBROAD_PRESERVED_AS_FULL_CONTEXT_FORENSIC_CAPTURE",
            "source_faithful_candidate": "SUPERSEDED_BY_SECTION_SCOPED_CANDIDATE_002",
            "automated_gates": "PASS_HISTORICAL_CANDIDATE_001",
            "candidate_001_human_approval": False,
            "canonical_replacement": False,
            "reusable_promotion": False,
        },
        "roadmap_vertical_progress_001": {
            "candidate": "CAROLINA-ROADMAP-SECTION-SOURCE-FAITHFUL-002",
            "candidate_status": "HUMAN_APPROVED_SOURCE_FIDELITY_CANONICAL_REFERENCE_DESIGNATED",
            "human_approval": True,
            "canonical_reference": "DESIGNATED_BY_IMMUTABLE_POINTER",
            "canonical_reference_path": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/progress/ROADMAP-VERTICAL-PROGRESS-001/CANONICAL_REFERENCE.json",
            "behavior_core": "ROADMAP-VERTICAL-PROGRESS-BEHAVIOR-CORE-001",
            "behavior_core_status": "EXTRACTED_AND_VALIDATED_PASS_CONTROLLED_EXACT_BYTES",
            "behavior_core_path": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/progress/ROADMAP-VERTICAL-PROGRESS-001/behavior-core/BEHAVIOR_CORE_CONTRACT.json",
            "canonical_aggregate_reconciliation": "CLOSED_BY_AUTHORIZATION_177",
            "historical_neutral_derivation": "REJECTED_AS_CANONICAL_REFERENCE_PRESERVED_HISTORICALLY",
            "canonical_replacement": False,
            "neutral_adaptation": False,
            "reusable_promotion": False,
            "product_integration": False,
            "runtime_effect": "NONE",
        },
        "statistics_counter_001": {
            "effect_id": "STATISTICS-COUNTER-STATIC-SUFFIX-001",
            "status": "HUMAN_APPROVED_CANONICAL_REFERENCE_DESIGNATED_BEHAVIOR_CORE_VALIDATED_READY_FOR_FUTURE_BOUNDED_CONSUMPTION",
            "source_package_id": "CAROLINA-STATISTICS-MOTION-EXPERIMENT-001",
            "source_package_manifest": "foundation-library/motion-system/MOTION-SYSTEM-001/source-packages/CAROLINA-STATISTICS-MOTION-EXPERIMENT-001/SOURCE_PACKAGE_MANIFEST.json",
            "archive_sha256": "8eecd53dc698d4587dfa882a5eabe701ec9a77a45bb9747d57f0cf5d68c876b0",
            "original_monolith_sha256": "74274e55ff1c8b9edd849d433f12bf6ffe0abb00097872feb6bc7adde83b463e",
            "exact_dom_excerpt": "foundation-library/motion-system/MOTION-SYSTEM-001/source-packages/CAROLINA-STATISTICS-MOTION-EXPERIMENT-001/integration-source/SOURCE_STATS_SECTION.html",
            "exact_motion_script_excerpt": "foundation-library/motion-system/MOTION-SYSTEM-001/source-packages/CAROLINA-STATISTICS-MOTION-EXPERIMENT-001/integration-source/SOURCE_STATS_MOTION.js",
            "human_determination": "APPROVED_SOURCE_FIDELITY",
            "approved_by": "Jonathan Martínez",
            "determined_at": "2026-08-03T00:23:25-04:00",
            "canonical_reference_designation": True,
            "canonical_reference": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/data/STATISTICS-COUNTER-STATIC-SUFFIX-001/CANONICAL_REFERENCE.json",
            "behavior_core_extraction": True,
            "behavior_core": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/data/STATISTICS-COUNTER-STATIC-SUFFIX-001/behavior-core/BEHAVIOR_CORE_CONTRACT.json",
            "behavior_core_validation": "PASS_NODE_DETERMINISTIC_7_OF_7_WITH_HUMAN_SOURCE_FIDELITY",
            "future_consumption_contract": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/data/STATISTICS-COUNTER-STATIC-SUFFIX-001/FUTURE_CONSUMPTION_CONTRACT.json",
            "future_product_integration": "REQUIRES_SEPARATE_EXPLICIT_AUTHORIZATION",
            "product_integration": False,
        },
        "next_gate": "SEPARATELY_AUTHORIZE_A_BOUNDED_MOTION_LIBRARY_ACTION_IF_DESIRED",
        "latest_authorization": "AUTHORIZATION_LAB_STATISTICS_COUNTER_EXPERIMENT_SOURCE_ADOPTION_HUMAN_REVIEW_AND_CONDITIONAL_CLOSURE_178",
    }


def reconcile_current_state() -> None:
    doc = load("CURRENT_STATE.json")
    require(doc["version"] == "2.5.54", "unexpected CURRENT_STATE version")
    doc["version"] = "2.5.55"
    doc["updated_at"] = DATE
    doc["canonical_model"]["motion_system_foundation"] = current_motion_state()
    doc["canonical_model"]["post_178_reconciliation_authorization_179"] = AUTH_PATH
    doc["canonical_model"]["post_178_reconciliation_evidence_179"] = EVIDENCE_PATH
    doc["canonical_model"]["post_178_reconciliation_delta_179"] = DELTA_PATH
    state = doc["authorization_state"]
    state["statistics_counter_experiment_source_adoption_human_review_and_conditional_closure_178"] = "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION"
    state["post_178_canonical_state_and_phase1_evidence_reconciliation_179"] = "CONSUMED_ON_VERIFIED_SQUASH_MERGE"
    doc["next_authorized_action"] = "NONE_AFTER_AUTHORIZATION_179_CONSUMPTION"
    doc["next_recommended_transition"] = "SEPARATELY_AUTHORIZE_PRIORITY_INTEGRATIONS_PHASE_2_INDEPENDENT_EVIDENCE_CLOSURE"
    transitions = doc.setdefault("completed_research_transitions", [])
    append_unique(transitions, "STATISTICS_COUNTER_SOURCE_FIDELITY_APPROVED_CANONICAL_REFERENCE_DESIGNATED_BEHAVIOR_CORE_VALIDATED")
    if "motion_system_reconciliation_177" in doc:
        doc["motion_system_reconciliation_177"]["next_gate"] = "COMPLETED_BY_AUTHORIZATION_178"
    if "motion_statistics_counter_source_adoption_178" in doc:
        doc["motion_statistics_counter_source_adoption_178"] = {
            "authorization": "AUTHORIZATION_LAB_STATISTICS_COUNTER_EXPERIMENT_SOURCE_ADOPTION_HUMAN_REVIEW_AND_CONDITIONAL_CLOSURE_178",
            "authorization_status": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
            "source_package_id": "CAROLINA-STATISTICS-MOTION-EXPERIMENT-001",
            "source_package_status": "HUMAN_APPROVED_CANONICAL_REFERENCE_DESIGNATED_SOURCE_PRESERVED",
            "human_determination": "APPROVED_SOURCE_FIDELITY",
            "canonical_reference_designated": True,
            "behavior_core_extracted_and_validated": True,
            "future_consumption": "READY_REQUIRES_SEPARATE_EXPLICIT_PRODUCT_INTEGRATION_AUTHORIZATION",
            "official_landing_integration": "NOT_AUTHORIZED_NOT_PERFORMED",
            "runtime_effect": "NONE",
            "product_effect": "NONE",
        }
    write("CURRENT_STATE.json", doc)


def reconcile_project_state() -> None:
    path = "projects/lab/PROJECT_STATE.json"
    doc = load(path)
    require(doc["current_phase"] == PHASE, "priority integration phase changed unexpectedly")
    doc["updated_at"] = DATE
    doc["content_completeness"] = "STRUCTURED_V2_WITH_PRIORITY_INTEGRATIONS_PHASE_1_AND_POST_178_CANONICAL_RECONCILIATION"
    for ref in (AUTH_PATH, EVIDENCE_PATH, DELTA_PATH):
        append_unique(doc["source_refs"], ref)
    old = doc.get("motion_system_foundation", {})
    motion = current_motion_state()
    if "correction_168" in old:
        motion["correction_168"] = old["correction_168"]
    doc["motion_system_foundation"] = motion
    doc["motion_source_fidelity_workstream_171"] = {
        "status": "COMPLETED_SECTION_SCOPED_SOURCE_FIDELITY_APPROVED_CANONICAL_REFERENCE_AND_BEHAVIOR_CORE_PUBLISHED",
        "decision": "DEC-LAB-031",
        "historical_candidate_001": "REJECTED_SCOPE_OVERBROAD_PRESERVED",
        "approved_candidate_002": "CAROLINA-ROADMAP-SECTION-SOURCE-FAITHFUL-002",
        "human_approval": True,
        "authorizations_171_through_177": "CONSUMED_NO_RESIDUAL_AUTHORITY",
        "error": "ERR-LAB-011_CLOSED",
        "pending_046": "CLOSED",
        "pending_047": "CLOSED",
        "canonical_reference": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/progress/ROADMAP-VERTICAL-PROGRESS-001/CANONICAL_REFERENCE.json",
        "behavior_core": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/progress/ROADMAP-VERTICAL-PROGRESS-001/behavior-core/BEHAVIOR_CORE_CONTRACT.json",
        "global_current_phase": "PRESERVED_PRIORITY_INTEGRATIONS_PHASE_1_CONTRACT_COMPLETE_TESTS_NOT_AUTHORIZED",
        "product_effect": "NONE",
        "runtime_effect": "NONE",
        "integration_effect": "NONE",
    }
    doc["motion_statistics_counter_source_adoption_178"] = {
        "authorization": "AUTHORIZATION_LAB_STATISTICS_COUNTER_EXPERIMENT_SOURCE_ADOPTION_HUMAN_REVIEW_AND_CONDITIONAL_CLOSURE_178",
        "authorization_status": "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION",
        "source_package_id": "CAROLINA-STATISTICS-MOTION-EXPERIMENT-001",
        "source_package_status": "HUMAN_APPROVED_CANONICAL_REFERENCE_DESIGNATED_SOURCE_PRESERVED",
        "human_determination": "APPROVED_SOURCE_FIDELITY",
        "canonical_reference": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/data/STATISTICS-COUNTER-STATIC-SUFFIX-001/CANONICAL_REFERENCE.json",
        "behavior_core": "foundation-library/motion-system/MOTION-SYSTEM-001/effects/data/STATISTICS-COUNTER-STATIC-SUFFIX-001/behavior-core/BEHAVIOR_CORE_CONTRACT.json",
        "behavior_core_validation": "PASS_NODE_DETERMINISTIC_7_OF_7_WITH_HUMAN_SOURCE_FIDELITY",
        "future_consumption": "READY_REQUIRES_SEPARATE_EXPLICIT_PRODUCT_INTEGRATION_AUTHORIZATION",
        "official_landing_integration": "NOT_AUTHORIZED_NOT_PERFORMED",
        "runtime_effect": "NONE",
        "product_effect": "NONE",
    }
    if "motion_system_reconciliation_177" in doc:
        doc["motion_system_reconciliation_177"]["next_gate"] = "COMPLETED_BY_AUTHORIZATION_178"
        doc["motion_system_reconciliation_177"]["active_execution_authority"] = "NONE_AFTER_AUTHORIZATION_177_CONSUMPTION"
    doc["next_authorized_action"] = "NONE_AFTER_AUTHORIZATION_179_CONSUMPTION"
    doc["next_recommended_transition"] = "SEPARATELY_AUTHORIZE_PRIORITY_INTEGRATIONS_PHASE_2_INDEPENDENT_EVIDENCE_CLOSURE"
    write(path, doc)


def reconcile_pending() -> None:
    doc = load("projects/lab/PENDING.json")
    doc["updated_at"] = DATE
    current_043 = load("projects/lab/pending/PEND-LAB-043.json")
    found = False
    for index, record in enumerate(doc["records"]):
        if record.get("id") == "PEND-LAB-043":
            doc["records"][index] = current_043
            found = True
    require(found, "PEND-LAB-043 missing from aggregate")
    ids = [record["id"] for record in doc["records"]]
    require(len(ids) == len(set(ids)), "duplicate pending ids")
    write("projects/lab/PENDING.json", doc)


def reconcile_roadmap() -> None:
    path = "projects/lab/ROADMAP.json"
    doc = load(path)
    doc["updated_at"] = DATE
    by_order = {record["order"]: record for record in doc["records"]}
    require(33 in by_order and 34 in by_order, "motion roadmap records missing")
    by_order[33].update({
        "status": "INITIAL_EFFECTS_COMPLETE_REMAINING_LIBRARY_POPULATION_AND_SEPARATE_PROMOTION_GATES",
        "result": "ROADMAP_AND_STATISTICS_COUNTER_CANONICAL_REFERENCES_DESIGNATED_BEHAVIOR_CORES_VALIDATED",
        "latest_authorization": "AUTHORIZATION_LAB_STATISTICS_COUNTER_EXPERIMENT_SOURCE_ADOPTION_HUMAN_REVIEW_AND_CONDITIONAL_CLOSURE_178",
        "next_gate": "SEPARATELY_AUTHORIZED_BOUNDED_LIBRARY_POPULATION_OR_PROMOTION_ACTION",
    })
    by_order[34].update({
        "status": "COMPLETED_SECTION_SCOPED_SOURCE_FIDELITY_APPROVED_CANONICAL_REFERENCE_BEHAVIOR_CORE_VALIDATED",
        "source_faithful_candidate": "CAROLINA-ROADMAP-SECTION-SOURCE-FAITHFUL-002",
        "historical_candidate_001": "REJECTED_SCOPE_OVERBROAD_PRESERVED",
        "human_review": "COMPLETED_APPROVED_SOURCE_FIDELITY",
        "maximum_result": "ROADMAP_CANONICAL_REFERENCE_DESIGNATED_BEHAVIOR_CORE_VALIDATED_CANONICAL_AGGREGATES_RECONCILED",
        "next_gate": "COMPLETED_BY_AUTHORIZATIONS_173_THROUGH_177",
    })
    existing = next((r for r in doc["records"] if r.get("item") == "STATISTICS_COUNTER_SOURCE_ADOPTION_AND_CONDITIONAL_CLOSURE_178"), None)
    record_35 = {
        "order": 35,
        "item": "STATISTICS_COUNTER_SOURCE_ADOPTION_AND_CONDITIONAL_CLOSURE_178",
        "status": "COMPLETED_SOURCE_FIDELITY_APPROVED_CANONICAL_REFERENCE_BEHAVIOR_CORE_VALIDATED",
        "authorization": "AUTHORIZATION_LAB_STATISTICS_COUNTER_EXPERIMENT_SOURCE_ADOPTION_HUMAN_REVIEW_AND_CONDITIONAL_CLOSURE_178",
        "evidence": "EVD-LAB-STATISTICS-COUNTER-SOURCE-PACKAGE-178",
        "source_package": "CAROLINA-STATISTICS-MOTION-EXPERIMENT-001",
        "human_determination": "APPROVED_SOURCE_FIDELITY",
        "canonical_reference_designated": True,
        "behavior_core_validation": "PASS_7_OF_7",
        "official_landing_integration": "NOT_AUTHORIZED_NOT_PERFORMED",
        "next_gate": "SEPARATE_EXPLICIT_PRODUCT_INTEGRATION_AUTHORIZATION_IF_FUTURE_CONSUMPTION_IS_DESIRED",
        "runtime_effect": "NONE",
        "product_effect": "NONE",
    }
    if existing is None:
        doc["records"].append(record_35)
    else:
        existing.clear(); existing.update(record_35)
    orders = [record["order"] for record in doc["records"]]
    require(len(orders) == len(set(orders)), "duplicate roadmap order")
    write(path, doc)


def governance_records() -> None:
    authorization = {
        "schema_version": "1.0.0",
        "authorization_id": AUTH_ID,
        "project_id": "lab",
        "status": "CONSUMED_ON_VERIFIED_SQUASH_MERGE",
        "authorization_class": "BOUNDED_DOCUMENTARY_CANONICAL_RECONCILIATION",
        "approved_by": "Jonathan Martínez",
        "approved_at": TIMESTAMP,
        "approval_source": "Continuemos, ejecuta un análisis para determinar qué ha cambiado y ejecutar alguna reconciliación si es necesario.",
        "grant_inferred": False,
        "repository": {
            "name": "marcellusanthonson-ctrl/chatgpt-prototype-lab",
            "branch": "main",
            "expected_parent_head": EXPECTED_PARENT,
            "working_branch": BRANCH,
            "head_policy": "VERIFY_LIVE_AT_USE",
            "entrypoint": "project-sources/chatgpt/START_HERE.md",
        },
        "objective": "Analyze changes after Phase 1 and authorization 178, then reconcile only confirmed documentary contradictions without technical, runtime, integration or product effects.",
        "authorized_scope": sorted(TARGET_PATHS),
        "authority": {
            "commit_authorized": True,
            "push_authorized": True,
            "source_file_update_authorized": True,
            "test_execution_authorized": False,
            "external_audit_execution_authorized": False,
            "runtime_authorized": False,
            "integration_authorized": False,
            "product_changes_authorized": False,
            "pointer_mutation_authorized": False,
            "shadow_registry_mutation_authorized": False,
            "static_selector_mutation_authorized": False,
            "motion_technical_artifact_mutation_authorized": False,
            "product_leadership_or_sse_contract_mutation_authorized": False,
        },
        "findings_authorized_for_correction": [
            "PHASE1_EVIDENCE_170_PREMERGE_PUBLICATION_FIELDS_STALE",
            "CURRENT_STATE_POST_178_MOTION_SUMMARY_STALE",
            "PROJECT_STATE_POST_171_THROUGH_178_SUMMARIES_STALE",
            "PENDING_AGGREGATE_PEND_043_STAGE_1_COPY_STALE",
            "ROADMAP_GLOBAL_MOTION_ITEMS_33_AND_34_STALE_AND_178_ITEM_MISSING",
            "CURRENT_CONTINUITY_HUMAN_VIEWS_AND_ATTACHMENT_MANIFEST_STALE",
        ],
        "publication": {"method": "SQUASH_MERGE", "main_commit_count": 1},
        "residual_authority": "NONE",
        "maximum_result": "POST_178_CANONICAL_STATE_AND_PHASE1_EVIDENCE_RECONCILED_PHASE2_NOT_AUTHORIZED",
        "authority_effect": "NONE_AFTER_CONSUMPTION",
        "runtime_effect": "NONE",
        "product_effect": "NONE",
        "integration_effect": "NONE",
        "test_effect": "NONE",
        "audit_effect": "NONE",
    }
    brief = {
        "schema_version": "1.0.0",
        "task_id": BRIEF_ID,
        "project_id": "lab",
        "status": "COMPLETED_BY_AUTHORIZATION_179",
        "authorization_ref": AUTH_ID,
        "objective": authorization["objective"],
        "repository": authorization["repository"],
        "scope": sorted(TARGET_PATHS),
        "forbidden_actions": [
            "NO_TEST_OR_AUDIT_EXECUTION",
            "NO_RUNTIME_PRODUCT_OR_EXTERNAL_REPOSITORY_CHANGE",
            "NO_POINTER_SELECTOR_OR_SHADOW_REGISTRY_MUTATION",
            "NO_MOTION_BEHAVIOR_CORE_OR_CANONICAL_REFERENCE_CHANGE",
            "NO_PRODUCT_LEADERSHIP_OR_SSE_CONTRACT_SCHEMA_OR_FIXTURE_CHANGE",
            "NO_PHASE_2_EXECUTION_OR_AUTHORIZATION",
        ],
        "required_outputs": [AUTH_PATH, EVIDENCE_PATH, DELTA_PATH],
        "acceptance_checks": [
            "EXPECTED_PARENT_HEAD_MATCHES",
            "ALL_JSON_PARSE",
            "ZERO_DUPLICATE_PENDING_IDS",
            "ZERO_DUPLICATE_ROADMAP_ORDERS",
            "ZERO_DUPLICATE_REGISTRY_DELTA_PATHS",
            "ZERO_STALE_STAGE_1_OR_PUBLICATION_PENDING_CLAIMS_IN_RECONCILED_SURFACES",
            "ONLY_AUTHORIZED_PATHS_CHANGED",
            "PHASE_2_REMAINS_NOT_AUTHORIZED",
        ],
        "stop_conditions": [
            "MAIN_HEAD_MOVED",
            "CANONICAL_SOURCE_CONTRADICTION_OUTSIDE_SCOPE",
            "TECHNICAL_ARTIFACT_CHANGE_REQUIRED",
            "ATOMIC_SQUASH_PUBLICATION_UNAVAILABLE",
        ],
        "response_contract": "REPORT_RESULT_CHANGED_PATHS_VALIDATION_DIVERGENCES_AUTHORITY_AND_ONE_NEXT_ACTION",
    }
    evidence = {
        "schema_version": "1.0.0",
        "evidence_id": EVIDENCE_ID,
        "project_id": "lab",
        "evidence_type": "POST_PUBLICATION_AND_POST_178_CANONICAL_RECONCILIATION",
        "status": "PASS_CANONICAL_RECONCILIATION_COMPLETE_ON_AUTHORIZED_SQUASH_MERGE",
        "created_at": TIMESTAMP,
        "authorization_ref": AUTH_ID,
        "verified_parent_head": EXPECTED_PARENT,
        "analysis": {
            "commits_after_phase1": 119,
            "phase1_baseline": "1204d9c56af79b4d9a840c6609716aca94ecfb65",
            "phase1_contract_artifacts_changed_after_baseline": 0,
            "post_phase1_change_concentration": "MOTION_SYSTEM_SOURCE_FIDELITY_AND_STATISTICS_COUNTER_CLOSURE",
        },
        "findings": [
            {"claim": "Product Leadership and SSE Phase 1 contracts changed after the Phase 1 squash merge.", "classification": "REVERSED"},
            {"claim": "Phase 1 publication remained pending.", "classification": "REVERSED"},
            {"claim": "The statistics counter still awaited human review and Stage 2 was not triggered.", "classification": "REVERSED"},
            {"claim": "PEND-LAB-043 standalone and CURRENT_CONTINUITY.json already reflected the completed authorization 178 result.", "classification": "CONFIRMED"},
            {"claim": "Priority Integrations Phase 2 is authorized.", "classification": "REVERSED"},
        ],
        "reconciled_paths": sorted(TARGET_PATHS),
        "validation": {
            "json_parse": "PASS",
            "duplicate_pending_ids": 0,
            "duplicate_roadmap_orders": 0,
            "duplicate_registry_delta_paths": 0,
            "stale_claims_in_reconciled_surfaces": 0,
            "phase1_contract_diff": 0,
            "motion_technical_artifact_diff": 0,
            "runtime_effect": "NONE",
            "product_effect": "NONE",
            "integration_effect": "NONE",
            "test_execution": 0,
            "audit_execution": 0,
        },
        "next_pending": "projects/lab/pending/PEND-LAB-045.json",
        "authority_effect": "NONE",
    }
    delta = {
        "schema_version": "1.0.0",
        "delta_id": DELTA_ID,
        "project_id": "lab",
        "updated_at": DATE,
        "status": "PASS_POST_178_CANONICAL_STATE_AND_PHASE1_EVIDENCE_RECONCILED",
        "authorization": {"id": AUTH_ID, "status": "CONSUMED_ON_VERIFIED_SQUASH_MERGE", "path": AUTH_PATH},
        "evidence": {"id": EVIDENCE_ID, "status": evidence["status"], "path": EVIDENCE_PATH},
        "reconciled": {
            "phase1_evidence_170": "PUBLICATION_VERIFIED",
            "current_state": "POST_178_CURRENT",
            "project_state": "POST_178_CURRENT",
            "pending_aggregate": "PEND_LAB_043_CURRENT",
            "roadmap": "MOTION_171_THROUGH_178_CURRENT",
            "continuity_package": "CURRENT_AND_INTERNALLY_CONSISTENT",
        },
        "registry_counts_after": {"authorizations": 103, "evidence": 85},
        "preserved": {
            "global_phase": PHASE,
            "priority_integrations_phase2": "NOT_AUTHORIZED",
            "product_leadership_and_sse_contracts": "UNCHANGED",
            "motion_technical_artifacts": "UNCHANGED",
            "product_integration": "NONE",
            "runtime_effect": "NONE",
        },
        "authority_effect": "NONE_AFTER_AUTHORIZATION_179_CONSUMPTION",
    }
    write(AUTH_PATH, authorization)
    write(BRIEF_PATH, brief)
    write(EVIDENCE_PATH, evidence)
    write(DELTA_PATH, delta)


def reconcile_registry() -> None:
    path = "registry/index.json"
    doc = load(path)
    require(doc["counts"]["authorizations"] == 102, "unexpected authorization count")
    require(doc["counts"]["evidence"] == 84, "unexpected evidence count")
    doc["updated_at"] = DATE
    doc["counts"]["authorizations"] = 103
    doc["counts"]["evidence"] = 85
    registries = doc["registries"]
    append_unique(registries["authorization_deltas"], DELTA_PATH)
    append_unique(registries["evidence_deltas"], DELTA_PATH)
    append_unique(registries["current_state_deltas"], DELTA_PATH)
    for key in ("authorization_deltas", "evidence_deltas", "current_state_deltas"):
        require(len(registries[key]) == len(set(registries[key])), f"duplicate {key}")
    write(path, doc)


def reconcile_continuity() -> None:
    path = "projects/lab/continuity/CURRENT_CONTINUITY.json"
    doc = load(path)
    doc["schema_version"] = "1.4.0"
    doc["continuity_id"] = "LAB-CONTINUITY-POST-178-CANONICAL-RECONCILIATION-179-20260803"
    doc["status"] = "POST_178_CANONICAL_AGGREGATES_RECONCILED_PHASE1_EVIDENCE_CLOSED_PHASE2_NOT_AUTHORIZED"
    doc["created_at"] = TIMESTAMP
    for ref in (AUTH_PATH, BRIEF_PATH, EVIDENCE_PATH, DELTA_PATH):
        append_unique(doc["required_reading_order"], ref)
    doc["global_state"]["current_phase"] = PHASE
    doc["global_state"]["canonical_reconciliation_179"] = "PASS"
    doc["global_state"]["active_execution_authority"] = "NONE_AFTER_AUTHORIZATION_179_CONSUMPTION"
    doc["authorization_179"] = {
        "id": AUTH_ID,
        "status": "CONSUMED_ON_VERIFIED_SQUASH_MERGE",
        "active": False,
        "residual_authority": False,
    }
    doc["phase1_publication_evidence"] = {
        "evidence": "projects/lab/evidence/EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-1-170.json",
        "status": "PASS_ON_VERIFIED_SQUASH_MERGE_AND_REMOTE_PUBLICATION",
        "main_commit": "1204d9c56af79b4d9a840c6609716aca94ecfb65",
    }
    doc["results"]["canonical_aggregates"] = "RECONCILED_POST_AUTHORIZATION_178"
    doc["results"]["phase1_publication_fields"] = "CLOSED_VERIFIED"
    doc["validation"]["canonical_json_parse"] = "PASS"
    doc["validation"]["duplicate_pending_ids"] = 0
    doc["validation"]["duplicate_roadmap_orders"] = 0
    doc["validation"]["stale_stage1_claims"] = 0
    doc["next_action"] = {
        "single": "SEPARATELY_AUTHORIZE_PRIORITY_INTEGRATIONS_PHASE_2_INDEPENDENT_EVIDENCE_CLOSURE",
        "repository_write_authorized": False,
    }
    doc["authority_effect"] = "NONE_AFTER_AUTHORIZATION_179_CONSUMPTION"
    write(path, doc)

    md = f"""# Continuidad LAB — reconciliación canónica posterior a 178

El estado estructurado fue reconciliado bajo `{AUTH_ID}` después de comparar el HEAD vigente con el squash de Fase 1.

## Estado vigente

- Fase global: `{PHASE}`.
- Product Leadership y Software Solution Engineering conservan sus contratos de Fase 1 sin cambios.
- La evidencia `EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-1-170` registra ahora el squash merge y la verificación remota completados.
- Los dos efectos iniciales de Motion tienen referencia canónica designada y behavior core validado.
- `STATISTICS-COUNTER-STATIC-SUFFIX-001` fue aprobado por Jonathan Martínez, cerró Stage 2 y está listo únicamente para consumo futuro acotado con autorización separada.

## Límites

No existe autorización vigente para Fase 2, ejecución de tests, auditoría externa, activación, cambios del pointer o selector, integración en Carolina, runtime, despliegue o promoción reusable.

## Siguiente acción única

Autorizar separadamente la Fase 2 de cierre de evidencia independiente para Product Leadership y Software Solution Engineering.
"""
    write_text("projects/lab/continuity/CURRENT_CONTINUITY.md", md)

    prompt = """Continúa ChatGPT Prototype LAB reconstruyendo primero el estado desde `marcellusanthonson-ctrl/chatgpt-prototype-lab`, rama `main`, entrypoint `project-sources/chatgpt/START_HERE.md`; verifica el HEAD remoto mediante `VERIFY_LIVE_AT_USE` y sigue exactamente su orden de lectura.

La Fase 1 de Product Leadership y Software Solution Engineering permanece completa y sus contratos no cambiaron. La evidencia 170 ya está reconciliada con el squash merge verificado. La autorización 178 quedó consumida: el contador estadístico fue aprobado por Jonathan Martínez, tiene referencia canónica y behavior core validado, pero no fue integrado en el landing oficial. La autorización 179 reconcilió `CURRENT_STATE`, `PROJECT_STATE`, `PENDING`, `ROADMAP`, el paquete CURRENT y el registro. No existe autoridad para Fase 2, tests, auditorías, activación, producto o runtime. Comienza evaluando `PEND-LAB-045`; no lo ejecutes sin una autorización separada.
"""
    write_text("projects/lab/continuity/START_PROMPT.md", prompt)

    manifest = load("projects/lab/continuity/ATTACHMENT_MANIFEST.json")
    manifest["schema_version"] = "1.3.0"
    manifest["manifest_id"] = "LAB-CONTINUITY-ATTACHMENTS-POST-178-RECONCILIATION-179-20260803"
    manifest["created_at"] = TIMESTAMP
    for ref in (AUTH_PATH, BRIEF_PATH, EVIDENCE_PATH, DELTA_PATH, "projects/lab/ROADMAP.json", "projects/lab/PROJECT_STATE.json"):
        append_unique(manifest["repository_sources_not_duplicated_as_attachments"], ref)
    manifest["known_stale_canonical_aggregates"] = []
    manifest["blocking_pending"] = "PEND-LAB-045_REQUIRES_SEPARATE_AUTHORIZATION"
    manifest["missing_attachments"] = []
    manifest["authority_effect"] = "NONE_AFTER_AUTHORIZATION_179_CONSUMPTION"
    write("projects/lab/continuity/ATTACHMENT_MANIFEST.json", manifest)


def apply() -> None:
    verify_parent()
    reconcile_phase1_evidence()
    reconcile_current_state()
    reconcile_project_state()
    reconcile_pending()
    reconcile_roadmap()
    governance_records()
    reconcile_registry()
    reconcile_continuity()


def check() -> None:
    verify_parent()
    for path in TARGET_PATHS:
        require((ROOT / path).exists(), f"missing target: {path}")
        if path.endswith(".json"):
            load(path)
    require(load("CURRENT_STATE.json")["current_phase"] == PHASE, "global phase changed")
    require(load("projects/lab/PROJECT_STATE.json")["current_phase"] == PHASE, "project phase changed")
    require(load("projects/lab/pending/PEND-LAB-045.json")["current_authority"] == "NONE_UNTIL_SEPARATE_EXPLICIT_AUTHORIZATION", "Phase 2 authority changed")
    require(load("projects/lab/evidence/EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-1-170.json")["remote_checks_pending"] == [], "EVD-170 checks still pending")
    pending = load("projects/lab/PENDING.json")
    ids = [item["id"] for item in pending["records"]]
    require(len(ids) == len(set(ids)), "duplicate pending ids")
    record_043 = next(item for item in pending["records"] if item["id"] == "PEND-LAB-043")
    require(record_043["status"] == "INITIAL_EFFECTS_COMPLETE_REMAINING_LIBRARY_POPULATION_AND_SEPARATE_PROMOTION_GATES", "aggregate PEND-043 stale")
    roadmap = load("projects/lab/ROADMAP.json")
    orders = [item["order"] for item in roadmap["records"]]
    require(len(orders) == len(set(orders)), "duplicate roadmap orders")
    require(any(item.get("item") == "STATISTICS_COUNTER_SOURCE_ADOPTION_AND_CONDITIONAL_CLOSURE_178" for item in roadmap["records"]), "roadmap item 178 missing")
    stale_phrases = [
        "PASS_BRANCH_VALIDATED_PUBLICATION_PENDING",
        "FUNCTIONAL_SOURCE_PRESERVED_HUMAN_REVIEW_PENDING",
        "GRANTED_STAGE_1_PUBLISHED_STAGE_2_CONDITIONALLY_AUTHORIZED_AWAITING_HUMAN_DETERMINATION",
        "Stage 2 no está activado",
        "Stage 2 permanece condicional y no activado",
    ]
    scan_paths = [
        "CURRENT_STATE.json",
        "projects/lab/PROJECT_STATE.json",
        "projects/lab/PENDING.json",
        "projects/lab/ROADMAP.json",
        "projects/lab/evidence/EVD-LAB-PRIORITY-INTEGRATIONS-PHASE-1-170.json",
        "projects/lab/continuity/CURRENT_CONTINUITY.json",
        "projects/lab/continuity/CURRENT_CONTINUITY.md",
        "projects/lab/continuity/START_PROMPT.md",
        "projects/lab/continuity/ATTACHMENT_MANIFEST.json",
    ]
    for path in scan_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for phrase in stale_phrases:
            require(phrase not in text, f"stale phrase in {path}: {phrase}")
    changed = set(run("git", "diff", "--name-only", "origin/main").splitlines())
    require(changed <= TARGET_PATHS | TRANSIENT_PATHS, f"unauthorized diff: {sorted(changed - TARGET_PATHS - TRANSIENT_PATHS)}")
    require(not any(path.startswith("foundation-library/product-leadership/") for path in changed), "Product Leadership contract changed")
    require(not any(path.startswith("foundation-library/software-solution-engineering/") for path in changed), "SSE contract changed")
    require(not any("behavior-core" in path or "CANONICAL_REFERENCE.json" in path for path in changed), "motion technical artifact changed")
    print(json.dumps({"status": "PASS", "changed_paths": sorted(changed), "target_count": len(TARGET_PATHS)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("apply", "check"))
    args = parser.parse_args()
    if args.mode == "apply":
        apply()
    check()


if __name__ == "__main__":
    main()
