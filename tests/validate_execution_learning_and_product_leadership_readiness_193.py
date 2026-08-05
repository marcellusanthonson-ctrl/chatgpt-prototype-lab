#!/usr/bin/env python3
"""Validate authorization 193 execution-learning and Product Leadership readiness package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED = [
    "architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/CONTRACT.json",
    "architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/CODEX_DECISION_PROTOCOL.json",
    "architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/BRIEF_LEARNING_CONTEXT_TEMPLATE.json",
    "architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/VALIDATION_RESULTS.json",
    "schemas/brief-learning-context.schema.json",
    "schemas/incident-ledger.schema.json",
    "schemas/learning-application-report.schema.json",
    "schemas/brief.schema.json",
    "schemas/error.schema.json",
    "projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/product-leadership/INCIDENT_LEDGER.json",
    "projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/product-leadership/INTEGRATION_READINESS.json",
    "errors/ERR-LAB-013.json",
    "patterns/PAT-LAB-012.json",
    "projects/lab/authorizations/AUTHORIZATION_LAB_TRANSVERSAL_EXECUTION_LEARNING_AND_PRODUCT_LEADERSHIP_READINESS_REMEDIATION_193.json",
    "projects/lab/briefs/CHATGPT_TRANSVERSAL_EXECUTION_LEARNING_AND_PRODUCT_LEADERSHIP_READINESS_REMEDIATION_193_001.json",
    "projects/lab/authorization-lifecycle/TRANSVERSAL_EXECUTION_LEARNING_AUTHORIZATION_LIFECYCLE_193.json",
    "projects/lab/evidence/EVD-LAB-EXECUTION-LEARNING-193.json",
    "projects/lab/evidence/LEARNING_APPLICATION_REPORT_193.json",
    "registry/deltas/transversal-execution-learning-product-leadership-readiness-193.json",
]

def no_dupes(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out

def load(root: Path, path: str) -> Any:
    return json.loads((root / path).read_text(encoding="utf-8"), object_pairs_hook=no_dupes)

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    for path in REQUIRED:
        require((root / path).is_file(), f"missing required file: {path}")

    parsed = {}
    for path in REQUIRED:
        if path.endswith(".json"):
            parsed[path] = load(root, path)

    contract = parsed[REQUIRED[0]]
    protocol = parsed[REQUIRED[1]]
    brief_schema = parsed["schemas/brief.schema.json"]
    error_schema = parsed["schemas/error.schema.json"]
    ledger = parsed["projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/product-leadership/INCIDENT_LEDGER.json"]
    readiness = parsed["projects/lab/programs/PRIORITY-INTEGRATIONS-PROGRAM-001/product-leadership/INTEGRATION_READINESS.json"]
    error = parsed["errors/ERR-LAB-013.json"]
    pattern = parsed["patterns/PAT-LAB-012.json"]
    auth = parsed["projects/lab/authorizations/AUTHORIZATION_LAB_TRANSVERSAL_EXECUTION_LEARNING_AND_PRODUCT_LEADERSHIP_READINESS_REMEDIATION_193.json"]
    brief = parsed["projects/lab/briefs/CHATGPT_TRANSVERSAL_EXECUTION_LEARNING_AND_PRODUCT_LEADERSHIP_READINESS_REMEDIATION_193_001.json"]
    learning_report = parsed["projects/lab/evidence/LEARNING_APPLICATION_REPORT_193.json"]

    require(contract["contract_id"] == "EXECUTION-LEARNING-FEEDBACK-LOOP-001", "wrong learning contract")
    require("DISTINGUISH_CANONICAL_ERROR_HISTORY_FROM_CURRENT_RECURRENCE" in contract["principles"], "history/current recurrence distinction missing")
    require(set(contract["recurrence_determinations"]) == {
        "CONFIRMED_CURRENT_OCCURRENCE", "NOT_REPRODUCED", "NOT_APPLICABLE", "INSUFFICIENT_EVIDENCE"
    }, "incomplete determination vocabulary")
    require("do not record private chain-of-thought" in protocol["private_reasoning_boundary"], "private reasoning boundary missing")
    require("learning_context" in brief_schema["properties"], "brief schema missing learning_context")
    for field in ("root_cause", "impact", "corrective_action", "preventive_control", "validation_of_fix"):
        require(field in error_schema["properties"], f"error schema missing {field}")
    require(len(ledger["incidents"]) >= 7, "incident ledger incomplete")
    require(set(ledger["active_blockers"]) == {"PL-INC-002", "PL-INC-004", "PL-INC-005"}, "active blockers changed")
    require(readiness["status"] == "NOT_READY_FOR_FRESH_RETEST_REISSUE", "readiness must remain fail closed")
    require(readiness["ready_for_retest_authorization"] is False, "retest readiness incorrectly true")
    require(readiness["ready_for_integration"] is False, "integration readiness incorrectly true")
    require(error["id"] == "ERR-LAB-013", "wrong error record")
    require(error["validation_of_fix"]["fresh_windows_worktree_raw_byte_proof"].startswith("NOT_RUN"), "raw-byte proof must remain not run")
    require(pattern["id"] == "PAT-LAB-012", "wrong pattern")
    require(auth["authority"]["model_requests"] is False, "models must be unauthorized")
    require(auth["authority"]["codex_login_or_credential_action"] is False, "login must be unauthorized")
    require(auth["authority"]["fresh_retest"] is False, "retest must be unauthorized")
    require(brief["learning_context"]["mode"] == "MANDATORY", "brief learning mode must be mandatory")
    require(brief["learning_operating_directive"]["private_reasoning_required"] is False, "brief must not require private reasoning")
    require(brief["response_contract"]["single_next_action"] == "SEPARATELY_AUTHORIZE_A_ZERO_MODEL_LOCAL_PRODUCT_LEADERSHIP_READINESS_PROBE", "wrong next action")
    require(learning_report["private_chain_of_thought_recorded"] is False, "learning report must not record private reasoning")
    require(any(x["determination"] == "CONFIRMED_CURRENT_OCCURRENCE" for x in learning_report["current_recurrence_determinations"]), "no confirmed current occurrence recorded")

    attrs = (root / ".gitattributes").read_text(encoding="utf-8")
    require("INSTRUMENT_REDESIGN_191/** text eol=lf" in attrs, "targeted LF rule missing")

    protected_prefixes = (
        "foundation-library/product-leadership/",
        "projects/lab/integrations/INT-LAB-004.json",
        "projects/lab/test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/INSTRUMENT_REDESIGN_191/",
        "projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-004/",
        "projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-005/",
    )
    package_manifest = parsed["architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/VALIDATION_RESULTS.json"]
    for changed in package_manifest["changed_paths"]:
        require(not changed.startswith(protected_prefixes), f"protected path changed: {changed}")

    print("PASS_EXECUTION_LEARNING_AND_PRODUCT_LEADERSHIP_READINESS_REMEDIATION_193")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
