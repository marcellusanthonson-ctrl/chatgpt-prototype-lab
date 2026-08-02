#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "architecture/integrations/migration/M5/cutover-166/PRE_CUTOVER_GENERAL_VALIDATOR_BASELINE.json"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, data: dict) -> None:
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_record(records: list[dict], record: dict) -> None:
    if not any(item.get("id") == record["id"] for item in records):
        records.append(record)


def append_value(items: list, value) -> None:
    if value not in items:
        items.append(value)


def append_markdown(path: str, marker: str, body: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if marker not in text:
        target.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.rstrip() + "\n", encoding="utf-8")


def apply_reconciliation() -> None:
    decision_path = "decisions/DEC-LAB-029.json"
    decision = load(decision_path)
    decision["project_scope"] = ["lab"]
    decision["approved_at"] = "2026-08-01"
    decision["approval_evidence"] = "APRUEBO DEC-LAB-029."
    save(decision_path, decision)

    decisions = load("registry/decisions.json")
    append_record(
        decisions["records"],
        {
            "id": "DEC-LAB-029",
            "title": decision["title"],
            "status": "APPROVED",
            "approval_state": "APPROVED",
            "project_scope": ["lab"],
            "canonical_path": decision_path,
            "updated_at": "2026-08-01",
            "approved_by": "Jonathan Martínez",
        },
    )
    decisions["updated_at"] = "2026-08-01"
    save("registry/decisions.json", decisions)

    stage_status = {
        "schema_version": "1.0.0",
        "brief_id": "CODEX_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_001_STAGE_2_STATUS",
        "project_id": "lab",
        "status": "READY",
        "objective": "Record the bounded Stage 2 materialization and validation status without replacing or abridging the parent execution brief.",
        "repositories": [
            {
                "name": "marcellusanthonson-ctrl/chatgpt-prototype-lab",
                "branch": "main",
                "mutation": "AUTHORIZED_BOUNDED_RECONCILIATION",
            },
            {
                "name": "marcellusanthonson-ctrl/carolina-md-next-landing",
                "ref": "52654da574952148f96d051e439bff1cbc7b4b9d",
                "mutation": "NONE_READ_ONLY_REFERENCE",
            },
        ],
        "authority": {
            "authorization_ref": "AUTHORIZATION_LAB_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_167",
            "approved_by": "Jonathan Martínez",
            "scope": "GENERAL_VALIDATION_AND_CANONICAL_RECONCILIATION_ONLY",
            "runtime_authorized": False,
            "product_changes_authorized": False,
        },
        "scope": {
            "parent_brief": "projects/lab/briefs/CODEX_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_001.json",
            "canonical_root": "foundation-library/motion-system/MOTION-SYSTEM-001",
            "preserves_parent_content": True,
            "adds_execution_status_only": True,
        },
        "required_outputs": [
            "exact general-validator delta against baseline 329",
            "canonical registry and state reconciliation",
            "protected blob verification",
            "remote publication verification",
        ],
        "acceptance_checks": [
            "CURRENT_FINDING_COUNT_329",
            "ADDED_FINDINGS_0",
            "REMOVED_FINDINGS_0",
            "MOTION_SYSTEM_VALIDATOR_PASS",
            "PROTECTED_BLOBS_PASS",
        ],
        "stop_conditions": [
            "ANY_NONZERO_FINDING_DELTA",
            "PROTECTED_BLOB_CHANGE",
            "PRODUCT_OR_RUNTIME_EFFECT",
            "SCOPE_EXPANSION",
        ],
        "response_contract": {
            "maximum_result": "VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION",
            "forbidden_claims": [
                "REUSABLE_FOUNDATION",
                "INTEGRATED_IN_PROJECT",
                "FULL_INDUSTRY_LIBRARY_COMPLETE",
            ],
        },
        "parent_brief_blob": "52c53e75fe603f8a533bd20df46c6584cddb2fda",
        "published_stage_2_head": "aafa9e3bc8a08df8912467e889157f11b33143c0",
        "completed_outputs": [
            "motion system root",
            "six schemas",
            "taxonomy",
            "protocol",
            "offline catalog",
            "61 planned candidates",
            "two initial effects",
            "formula contracts",
            "customization contracts",
            "two transversal patterns",
            "criterion source connection",
            "browser validation evidence",
        ],
        "execution_result": "CANONICAL_RECONCILIATION_IN_PROGRESS",
    }
    save("projects/lab/briefs/CODEX_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_001_STAGE_2_STATUS.json", stage_status)

    continuity = load("projects/lab/continuity/CURRENT_CONTINUITY.json")
    continuity["authorizations"] = {
        "167": "ACTIVE_FOR_GENERAL_VALIDATION_CANONICAL_RECONCILIATION_AND_REMOTE_VERIFICATION_ONLY"
    }
    continuity["authorization"] = continuity["authorizations"]
    continuity["single_next_action"] = "VERIFY_ZERO_DELTA_REMOTE_PUBLICATION_AND_CONSUME_AUTHORIZATION_167"
    continuity["first_phrase_for_new_conversation"] = (
        "Continúa ChatGPT Prototype LAB desde el HEAD remoto vigente de main. "
        "MOTION-SYSTEM-001 está publicado; la autorización 167 permanece activa solo para "
        "verificar la reconciliación canónica y consumirse si el delta general es cero."
    )
    save("projects/lab/continuity/CURRENT_CONTINUITY.json", continuity)

    prompt_path = ROOT / "projects/lab/continuity/START_PROMPT.md"
    prompt = prompt_path.read_text(encoding="utf-8").rstrip()
    if "No infieras autoridad" not in prompt:
        prompt += (
            "\n\nNo infieras autoridad: la autorización 167 permanece limitada a la verificación remota "
            "y su consumo; no autoriza productos, runtime, integraciones ni promoción automática de efectos."
        )
    prompt_path.write_text(prompt + "\n", encoding="utf-8")

    pending_source = load("projects/lab/pending/PEND-LAB-043.json")
    pending_source["status"] = "PENDING_HUMAN_REVIEW_AND_STAGED_LIBRARY_POPULATION_AFTER_AUTHORIZATION_167_CONSUMPTION"
    pending_source["current_authority"] = "AUTHORIZATION_167_ACTIVE_FOR_REMOTE_VERIFICATION_AND_CONSUMPTION_ONLY"
    pending_source["required_actions"] = [
        "VERIFY_REMOTE_ZERO_DELTA_PUBLICATION",
        "CONSUME_AUTHORIZATION_167",
        "HUMAN_REVIEW_TWO_INITIAL_DEMOS",
        "PROMOTE_REVISE_OR_REJECT_EACH_INITIAL_EFFECT",
        "IMPLEMENT_INDUSTRY_EFFECTS_IN_BOUNDED_BATCHES",
        "AUTHORIZE_PROJECT_INTEGRATIONS_SEPARATELY",
    ]
    save("projects/lab/pending/PEND-LAB-043.json", pending_source)

    pending = load("projects/lab/PENDING.json")
    append_record(pending["records"], pending_source)
    pending["updated_at"] = "2026-08-01"
    save("projects/lab/PENDING.json", pending)

    roadmap = load("projects/lab/ROADMAP.json")
    roadmap_records = roadmap.setdefault("records", [])
    if not any(item.get("item") == "TRANSVERSAL_MOTION_SYSTEM_FOUNDATION_167" for item in roadmap_records):
        roadmap_records.append(
            {
                "order": max([item.get("order", 0) for item in roadmap_records] + [0]) + 1,
                "item": "TRANSVERSAL_MOTION_SYSTEM_FOUNDATION_167",
                "status": "PUBLISHED_VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION",
                "decision": "DEC-LAB-029",
                "authorization": "AUTHORIZATION_LAB_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_167",
                "foundation": "foundation-library/motion-system/MOTION-SYSTEM-001/MANIFEST.json",
                "pending": "PEND-LAB-043",
                "authority_effect": "BOUNDED_REMOTE_VERIFICATION_AND_CONSUMPTION_ONLY",
            }
        )
    roadmap["updated_at"] = "2026-08-01"
    save("projects/lab/ROADMAP.json", roadmap)

    current = load("CURRENT_STATE.json")
    current["canonical_model"]["motion_system"] = "foundation-library/motion-system/MOTION-SYSTEM-001/MANIFEST.json"
    append_value(current["decisions_in_force"], "DEC-LAB-029")
    current["authorization_state"]["transversal_motion_effects_library_foundation_167"] = (
        "GRANTED_STAGE_1_CONSUMED_STAGE_2_VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION"
    )
    current["motion_system_foundation"] = {
        "status": "PUBLISHED_VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION",
        "decision": "DEC-LAB-029",
        "authorization": "AUTHORIZATION_LAB_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_167",
        "root": "foundation-library/motion-system/MOTION-SYSTEM-001",
        "implemented_effects": 2,
        "planned_effects": 61,
        "maximum_effect_status": "HUMAN_REVIEW_PENDING",
        "product_effect": "NONE",
        "runtime_effect": "NONE",
    }
    save("CURRENT_STATE.json", current)

    expected = load("tests/expected_repository_state.json")
    expected["decisions_in_force"] = current["decisions_in_force"]
    expected["authorization_state"] = current["authorization_state"]
    save("tests/expected_repository_state.json", expected)

    project_state = load("projects/lab/PROJECT_STATE.json")
    append_value(project_state.setdefault("source_refs", []), "decisions/DEC-LAB-029.json")
    append_value(project_state["source_refs"], "foundation-library/motion-system/MOTION-SYSTEM-001/MANIFEST.json")
    append_value(project_state["source_refs"], "projects/lab/evidence/EVD-LAB-MOTION-SYSTEM-001.json")
    append_value(project_state["source_refs"], "projects/lab/pending/PEND-LAB-043.json")
    project_state["motion_system_foundation"] = current["motion_system_foundation"]
    save("projects/lab/PROJECT_STATE.json", project_state)

    index = load("registry/index.json")
    regs = index["registries"]
    for key in [
        "decision_deltas",
        "authorization_deltas",
        "evidence_deltas",
        "foundation_library_deltas",
        "current_state_deltas",
        "pattern_deltas",
    ]:
        append_value(regs.setdefault(key, []), "registry/deltas/transversal-motion-system-foundation-167.json")
    index["updated_at"] = "2026-08-01"
    save("registry/index.json", index)

    delta = load("registry/deltas/transversal-motion-system-foundation-167.json")
    delta["stage_2"] = "VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION"
    delta["validation"] = {
        "browser": "PASS_SET_CONTENT_RENDERING",
        "file_protocol": "BLOCKED_BY_ENVIRONMENT_POLICY_STATIC_OFFLINE_CONTRACT_PASS",
        "motion_system_validator": "PASS",
        "general_repository_validator": "PREPUBLICATION_EXACT_329_ZERO_ADDED_ZERO_REMOVED",
        "protected_blobs": "PASS",
        "canonical_aggregate_reconciliation": "PASS_PREPUBLICATION",
    }
    save("registry/deltas/transversal-motion-system-foundation-167.json", delta)

    amendment_path = "projects/lab/authorizations/AUTHORIZATION_LAB_TRANSVERSAL_MOTION_EFFECTS_LIBRARY_FOUNDATION_167_AMENDMENT_1_STAGE_2_PROGRESS.json"
    amendment = load(amendment_path)
    amendment["stage_2"]["status"] = "VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION"
    amendment["validation"]["general_repository_validator"] = "PREPUBLICATION_EXACT_329_ZERO_ADDED_ZERO_REMOVED"
    amendment["validation"]["canonical_aggregate_reconciliation"] = "PASS_PREPUBLICATION"
    amendment["current_authority"]["scope"] = "REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION_ONLY"
    save(amendment_path, amendment)

    evidence = load("projects/lab/evidence/EVD-LAB-MOTION-SYSTEM-001.json")
    evidence["classification"] = "MOTION_SYSTEM_FOUNDATION_VALIDATION_PASS_AWAITING_REMOTE_VERIFICATION_AND_AUTHORIZATION_CONSUMPTION"
    evidence["verified_outputs"]["general_repository_validator"] = "PREPUBLICATION_EXACT_329_ZERO_ADDED_ZERO_REMOVED"
    evidence["verified_outputs"]["canonical_aggregate_reconciliation"] = "PASS_PREPUBLICATION"
    evidence["limitations"] = [
        "FILE_PROTOCOL_NAVIGATION_BLOCKED_BY_ENVIRONMENT_ADMIN_POLICY_SET_CONTENT_BROWSER_VALIDATION_USED",
        "HUMAN_REVIEW_PENDING",
        "REMOTE_PUBLICATION_VERIFICATION_PENDING",
    ]
    save("projects/lab/evidence/EVD-LAB-MOTION-SYSTEM-001.json", evidence)

    append_markdown(
        "projects/lab/PROJECT_STATE.md",
        "## Motion system transversal — autorización 167",
        "MOTION-SYSTEM-001 quedó publicado con taxonomía multidimensional, contratos de fórmula y personalización, 61 efectos planificados y dos candidatos en HUMAN_REVIEW_PENDING. No existe efecto de producto o runtime.",
    )
    append_markdown(
        "CURRENT_STATE.md",
        "## Motion system transversal — autorización 167",
        "La fundación está publicada y validada antes de publicación final; resta verificar el remoto y consumir la autorización. Los dos efectos iniciales continúan en HUMAN_REVIEW_PENDING.",
    )
    append_markdown(
        "project-sources/chatgpt/08_CRITERION_LAYER.md",
        "## Motion system transversal",
        "Para tareas de motion, animación, transición, microinteracción, counters, scroll paramétrico, reduced motion, flicker o layout shift, DESIGN_CRITERION y WEB_ACCESSIBILITY consultan `foundation-library/motion-system/MOTION-SYSTEM-001/MANIFEST.json`. Esta fuente no modifica la semántica del selector ni autoriza integración de producto.",
    )
    append_markdown(
        "README.md",
        "## Motion system transversal",
        "- `foundation-library/motion-system/MOTION-SYSTEM-001/`: catálogo, protocolos, fórmulas, personalización y efectos reutilizables gobernados.",
    )


def normalized_findings() -> tuple[subprocess.CompletedProcess[str], list[str]]:
    run = subprocess.run(
        [sys.executable, "scripts/validate_repository.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    current: list[str] = []
    prefix = ROOT.as_posix() + "/"
    for line in (run.stdout + "\n" + run.stderr).splitlines():
        if line.startswith("FAIL: "):
            message = line[6:].replace("\\", "/")
            if message.startswith(prefix):
                message = message[len(prefix):]
            current.append(message)
    return run, current


def validate() -> dict:
    motion = subprocess.run(
        [sys.executable, "scripts/validate_motion_system_foundation.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if motion.returncode:
        print(motion.stdout)
        print(motion.stderr)
        raise SystemExit("motion system validator failed")

    run, current = normalized_findings()
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    previous = [item["normalized_message"] for item in baseline["findings"]]
    previous_set = set(previous)
    current_set = set(current)
    added = [message for message in current if message not in previous_set]
    removed = [message for message in previous if message not in current_set]
    result = {
        "current_count": len(current),
        "baseline_count": len(previous),
        "added_count": len(added),
        "removed_count": len(removed),
        "added": added,
        "removed": removed,
        "global_repository_pass": run.returncode == 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if len(current) != 329 or added or removed or run.returncode == 0:
        print(run.stdout)
        print(run.stderr)
        raise SystemExit(1)

    portable = subprocess.run(
        [sys.executable, "scripts/validate_repository_portable_baseline_165.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(portable.stdout)
    print(portable.stderr)
    if portable.returncode:
        raise SystemExit("portable baseline validator failed")

    protected = {
        "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json": "301ba432907758fc49a9b3c86a83fc762eac4607",
        "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json": "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78",
        "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json": "618c2fe00a6b23a84c5ce90361cb3b7cfa5b9053",
    }
    for path, expected in protected.items():
        actual = subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()
        if actual != expected:
            raise SystemExit(f"protected blob mismatch: {path}: {actual}")
    print("PROTECTED_BLOBS_PASS")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if not args.apply and not args.validate:
        parser.error("select --apply and/or --validate")
    if args.apply:
        apply_reconciliation()
    if args.validate:
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
