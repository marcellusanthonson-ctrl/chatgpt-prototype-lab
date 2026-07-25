#!/usr/bin/env python3
"""Dependency-free semantic validation for the LAB governance repository."""
from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from schemas.validation.context import FAILURES
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
from schemas.validation.registries import (
    validate_current_state,
    validate_decisions,
    validate_projects,
    validate_registries,
)
from schemas.validation.context import validate_chatgpt_project_sources, validate_text


def main() -> int:
    validate_text()
    validate_chatgpt_project_sources()
    validate_chatgpt_criterion_layer()
    index, registries = validate_registries()
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
