#!/usr/bin/env python3
"""Dependency-free semantic validation for the LAB governance repository."""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path
from typing import Callable

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from schemas.validation.context import FAILURES, fail, load_json
from schemas.validation.criterion_state import (
    validate_briefs_and_continuity,
    validate_chatgpt_criterion_layer,
    validate_evidence,
    validate_fixture,
    validate_reassessments,
)
from schemas.validation.foundation_evidence import (
    validate_foundation_evidence,
    validate_minimum_impeccable_visual_foundation,
)
from schemas.validation.foundations import (
    validate_foundation_library,
    validate_visual_foundation,
)
from schemas.validation.rag_pilots import (
    validate_foundation_pilots,
    validate_rag_contracts,
)
from schemas.validation import registries as registry_validation
from schemas.validation.registries import (
    validate_current_state,
    validate_decisions,
    validate_projects,
)
from schemas.validation.context import validate_chatgpt_project_sources, validate_text


def normalize_registry_paths(
    registry_map: object,
    path_exists: Callable[[str], bool],
) -> tuple[dict[str, str], list[str]]:
    """Separate scalar registries from array-valued delta/path collections."""
    if not isinstance(registry_map, dict):
        return {}, ["registry/index.json: registries must be an object"]
    scalar: dict[str, str] = {}
    issues: list[str] = []
    for name, value in registry_map.items():
        if isinstance(value, str):
            scalar[name] = value
            if not path_exists(value):
                issues.append(f"registry/index.json: missing registry path {name}: {value}")
            continue
        if isinstance(value, list):
            seen: set[str] = set()
            for position, relative in enumerate(value):
                if not isinstance(relative, str):
                    issues.append(
                        f"registry/index.json: {name}[{position}] must be a path string"
                    )
                    continue
                if relative in seen:
                    issues.append(
                        f"registry/index.json: duplicate path in {name}: {relative}"
                    )
                    continue
                seen.add(relative)
                if not path_exists(relative):
                    issues.append(
                        f"registry/index.json: missing path in {name}: {relative}"
                    )
            continue
        issues.append(
            f"registry/index.json: {name} must be a path string or path array"
        )
    return scalar, issues


def validate_registries_with_delta_paths() -> tuple[dict, dict]:
    """Validate array path collections, then run legacy scalar registry checks."""
    index = load_json("registry/index.json")
    registry_map = index.get("registries", {}) if isinstance(index, dict) else {}
    scalar, issues = normalize_registry_paths(
        registry_map,
        lambda relative: (REPOSITORY_ROOT / relative).is_file(),
    )
    for issue in issues:
        fail(issue)
    scalar_index = deepcopy(index) if isinstance(index, dict) else {}
    scalar_index["registries"] = scalar
    original_load_json = registry_validation.load_json

    def load_json_compat(relative: str):
        if relative == "registry/index.json":
            return scalar_index
        return original_load_json(relative)

    registry_validation.load_json = load_json_compat
    try:
        return registry_validation.validate_registries()
    finally:
        registry_validation.load_json = original_load_json


def main() -> int:
    validate_text()
    validate_chatgpt_project_sources()
    validate_chatgpt_criterion_layer()
    index, registries = validate_registries_with_delta_paths()
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
