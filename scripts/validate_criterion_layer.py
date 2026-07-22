#!/usr/bin/env python3
"""Deterministic validation for CHATGPT-CRITERION-LAYER-001."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYER = ROOT / "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001"
EXPECTED_MODULES = [
    "EVIDENCE_AND_CLAIMS",
    "DESIGN_CRITERION",
    "WEB_ACCESSIBILITY",
    "CONTEXTUAL_VISUAL_PREFERENCE",
]
EXPECTED_PRINCIPLES = {
    *{f"DKP-{number:03d}" for number in range(1, 14)},
    "DKP-016",
    "DKP-018",
    *{f"DKP-{number:03d}" for number in range(19, 29)},
}

def load(name: str):
    return json.loads((LAYER / name).read_text(encoding="utf-8"))

def main() -> int:
    manifest = load("MANIFEST.json")
    contract = load("CONTRACT.json")
    selector = load("MODULE_SELECTOR.json")
    result = load("RESULT_CONTRACT.json")
    fixtures = load("ACCEPTANCE_FIXTURES.json")
    validation = load("VALIDATION_EVIDENCE.json")
    assert contract["layer_id"] == manifest["layer_id"] == "CHATGPT-CRITERION-LAYER-001"
    assert contract["modules"] == EXPECTED_MODULES
    assert [item["id"] for item in selector["modules"]] == EXPECTED_MODULES
    assert set(contract["referenced_principles"]) == EXPECTED_PRINCIPLES
    assert contract["limits"]["autonomous_authority"] is False
    assert contract["limits"]["runtime"] is False
    assert contract["limits"]["rag"] is False
    assert contract["limits"]["wcag_conformance_by_default"] is False
    assert "STATIC_PASS_DOES_NOT_IMPLY_ACCESSIBILITY" in result["mandatory_boundaries"]
    assert "AT_NOT_RUN" in result["accessibility_result_states"]["assistive_technology"]
    assert "WCAG_CONFORMANCE_NOT_ESTABLISHED" in result["accessibility_result_states"]["conformance"]
    assert contract["self_correction"]["known_correctable_defect_blocks_delivery"] is True
    assert contract["self_correction"]["structural_defect_requires_reconstruction"] is True
    assert contract["self_correction"]["pass_with_known_visual_defects"] is False
    assert result["forbidden_visual_artifact_state"] == "PASS_WITH_KNOWN_VISUAL_DEFECTS"
    assert "TECHNICAL_FOUNDATION_PASS_AWAITING_HUMAN_BASELINE_REVIEW" in result["visual_artifact_result_states"]
    ids = [item["id"] for item in fixtures["fixtures"]]
    assert len(ids) == len(set(ids)) == manifest["counts"]["fixtures"]
    known = set(EXPECTED_MODULES)
    for fixture in fixtures["fixtures"]:
        assert set(fixture["expected_modules"]) <= known
        assert set(fixture["forbidden_modules"]) <= known
        assert not (set(fixture["expected_modules"]) & set(fixture["forbidden_modules"]))
    assert validation["result_claims"]["selector_deterministically_validated"] is True
    assert validation["result_claims"]["terra_behavior_validated"] is False
    print("Criterion layer JSON and duplicate keys: PASS")
    print("Criterion layer references and module identity: PASS")
    print("Criterion layer fixture oracles: PASS")
    print("Criterion layer authority and claim boundaries: PASS")
    print("Terra 5.6 LIGHT empirical evaluation: NOT_EXECUTED_MODEL_SURFACE_UNAVAILABLE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
