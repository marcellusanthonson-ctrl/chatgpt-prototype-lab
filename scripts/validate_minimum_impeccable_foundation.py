#!/usr/bin/env python3
"""Deterministic checks for MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"


def load(name: str):
    pairs = []
    def hook(items):
        keys = [key for key, _ in items]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            raise AssertionError(f"{name}: duplicate keys {duplicates}")
        pairs.append(keys)
        return dict(items)
    return json.loads((BASE / name).read_text(encoding="utf-8"), object_pairs_hook=hook)


def main() -> int:
    manifest = load("MANIFEST.json")
    standard = load("STANDARD.json")
    geometry = load("STRUCTURAL_GEOMETRY_CONTRACT.json")
    components = load("COMPONENT_FINISH_CONTRACT.json")
    layout = load("LAYOUT_INTENT_MAP_CONTRACT.json")
    forms = load("FORM_BEHAVIOR_CONTRACT.json")
    responsive = load("RESPONSIVE_RESILIENCE_CONTRACT.json")
    correction = load("SELF_CORRECTION_CONTRACT.json")
    matrix = load("VALIDATION_MATRIX.json")
    assert manifest["foundation_id"] == standard["standard_id"] == "MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"
    assert manifest["status"] in correction["allowed_terminal_states"]
    assert correction["forbidden_terminal_state"] == "PASS_WITH_KNOWN_VISUAL_DEFECTS"
    assert correction["cycle"] == [
        "RENDER", "INSPECT", "MEASURE", "INTERACT", "STRESS",
        "CLASSIFY_DEFECTS", "DIAGNOSE_ROOT_CAUSE", "CORRECT_OR_RECONSTRUCT",
        "REVALIDATE_COMPLETE_SURFACE",
    ]
    assert len(standard["defect_domains"]) >= 16
    assert "ZERO_KNOWN_CORRECTABLE_DEFECTS_AT_DELIVERY" in standard["non_negotiable_outcomes"]
    assert "STRUCTURAL_OVERFLOW" in geometry["blocking_defects"]
    assert set(components["components"]) == {"icons", "buttons_and_controls", "typography", "navbar", "hero", "footer"}
    assert len(layout["fixture_map"]) == 5
    assert "DATA_LOSS_ON_VALIDATION" in forms["blocking_defects"]
    assert responsive["continuous_sweep"] == {"from_px": 320, "to_px": 1920, "maximum_step_px": 16}
    case_ids = [case["id"] for case in matrix["cases"]]
    assert len(case_ids) == len(set(case_ids)) == 14

    html = (BASE / "MINIMUM_IMPECCABLE_BASE_001.html").read_text(encoding="utf-8")
    lowered = html.lower()
    for forbidden in ["http://", "https://", "@import", "fetch(", "xmlhttprequest", "overflow-x:hidden", "overflow-x: hidden"]:
        assert forbidden not in lowered, f"HTML contains forbidden token: {forbidden}"
    assert "<style>" in lowered and "<script>" in lowered
    assert "<header" in lowered and "<main" in lowered and "<footer" in lowered and "<dialog" in lowered
    assert "prefers-reduced-motion" in lowered
    assert 'id="main"' in lowered and 'class="skip-link"' in lowered
    assert 'novalidate' in lowered and 'role="status"' in lowered
    assert "window.__MIVF_DIAGNOSTIC__" in html
    assert not re.search(r"<img\b", lowered), "Neutral fixture must not contain product photography"
    assert not re.search(r"<link\b[^>]*rel=[\"']stylesheet", lowered), "Remote or linked stylesheets are forbidden"
    print("Minimum impeccable foundation JSON and duplicate keys: PASS")
    print("Minimum impeccable foundation contract closure: PASS")
    print("Neutral monolithic HTML self-containment: PASS")
    print("Static semantics, form and reduced-motion preflight: PASS")
    print("Human visual approval: NOT_ESTABLISHED")
    print("WCAG conformance: NOT_ESTABLISHED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
