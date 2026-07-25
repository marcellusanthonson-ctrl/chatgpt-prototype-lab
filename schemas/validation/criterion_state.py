from .context import *

def validate_chatgpt_criterion_layer() -> None:
    base = "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001"
    required = [
        "MANIFEST.json", "CONTRACT.json", "MODULE_SELECTOR.json",
        "RESULT_CONTRACT.json", "ACCEPTANCE_FIXTURES.json", "VALIDATION_EVIDENCE.json",
    ]
    for name in required:
        require_file(f"{base}/{name}")
    manifest = load_json(f"{base}/MANIFEST.json")
    contract = load_json(f"{base}/CONTRACT.json")
    selector = load_json(f"{base}/MODULE_SELECTOR.json")
    result = load_json(f"{base}/RESULT_CONTRACT.json")
    fixtures = load_json(f"{base}/ACCEPTANCE_FIXTURES.json")
    validation = load_json(f"{base}/VALIDATION_EVIDENCE.json")
    expected_modules = [
        "EVIDENCE_AND_CLAIMS", "DESIGN_CRITERION",
        "WEB_ACCESSIBILITY", "CONTEXTUAL_VISUAL_PREFERENCE",
    ]
    if contract.get("layer_id") != "CHATGPT-CRITERION-LAYER-001":
        fail("criterion layer: identity mismatch")
    if contract.get("modules") != expected_modules:
        fail("criterion layer: module order or membership mismatch")
    if [item.get("id") for item in selector.get("modules", [])] != expected_modules:
        fail("criterion layer: selector modules mismatch")
    if any(contract.get("limits", {}).get(key) for key in [
        "runtime", "rag", "embeddings", "vector_database", "symphonie_integration",
        "product_change", "assistive_technology_execution", "wcag_conformance_by_default",
        "autonomous_authority",
    ]):
        fail("criterion layer: forbidden execution or authority effect")
    boundaries = set(result.get("mandatory_boundaries", []))
    for boundary in [
        "STATIC_PASS_DOES_NOT_IMPLY_ACCESSIBILITY",
        "AUTOMATION_DOES_NOT_ESTABLISH_WCAG_CONFORMANCE",
        "PREFERENCE_IS_NOT_STANDARD",
        "HEURISTIC_IS_NOT_EVIDENCE",
        "EVIDENCE_IS_NOT_AUTHORIZATION",
    ]:
        if boundary not in boundaries:
            fail(f"criterion layer: missing boundary {boundary}")
    fixture_records = fixtures.get("fixtures", [])
    fixture_ids = [item.get("id") for item in fixture_records]
    if len(fixture_ids) != len(set(fixture_ids)) or len(fixture_ids) != manifest.get("counts", {}).get("fixtures"):
        fail("criterion layer: fixture IDs duplicated or count mismatch")
    known = set(expected_modules)
    for fixture in fixture_records:
        expected = set(fixture.get("expected_modules", []))
        forbidden = set(fixture.get("forbidden_modules", []))
        if (expected | forbidden) - known:
            fail(f"criterion layer: unknown module in {fixture.get('id')}")
        if expected & forbidden:
            fail(f"criterion layer: contradictory oracle in {fixture.get('id')}")
    claims = validation.get("result_claims", {})
    if claims.get("selector_deterministically_validated") is not True:
        fail("criterion layer: selector validation claim missing")
    if claims.get("terra_behavior_validated") is not False:
        fail("criterion layer: unsupported Terra validation claim")
    self_correction = contract.get("self_correction", {})
    if self_correction.get("known_correctable_defect_blocks_delivery") is not True or self_correction.get("structural_defect_requires_reconstruction") is not True or self_correction.get("pass_with_known_visual_defects") is not False:
        fail("criterion layer: minimum visual self-correction boundary missing")
    if result.get("forbidden_visual_artifact_state") != "PASS_WITH_KNOWN_VISUAL_DEFECTS":
        fail("criterion layer: known-defect result state not prohibited")


def validate_briefs_and_continuity() -> None:
    for path in sorted(ROOT.glob("projects/*/briefs/*.json")):
        apply_schema(path.relative_to(ROOT).as_posix(), "schemas/brief.schema.json")
    for project_dir in sorted((ROOT / "projects").iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue
        continuity = project_dir / "continuity"
        if not continuity.is_dir():
            continue
        current = continuity / "CURRENT_CONTINUITY.json"
        manifest = continuity / "ATTACHMENT_MANIFEST.json"
        prompt = continuity / "START_PROMPT.md"
        for path in [current, manifest, prompt]:
            if not path.is_file():
                fail(f"{project_dir.name}: incomplete continuity package")
        if current.is_file():
            package = apply_schema(current.relative_to(ROOT).as_posix(), "schemas/continuity.schema.json")
            if package.get("project_id") != project_dir.name:
                fail(f"{current}: project_id mismatch")
        if manifest.is_file():
            data = apply_schema(manifest.relative_to(ROOT).as_posix(), "schemas/attachment-manifest.schema.json")
            for item in data.get("required", []):
                if item.get("repository") == "marcellusanthonson-ctrl/chatgpt-prototype-lab":
                    require_file(item.get("path", ""))
        if prompt.is_file() and "No infieras autoridad" not in prompt.read_text(encoding="utf-8"):
            fail(f"{prompt}: authority boundary missing")

def validate_reassessments(registries: dict[str, Any]) -> None:
    global_records = registries["reassessments"].get("records", [])
    seen: set[str] = set()
    for project_dir in sorted((ROOT / "projects").iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue
        index_path = project_dir / "reassessments" / "index.json"
        if not index_path.is_file():
            fail(f"{project_dir.name}: missing reassessment index")
            continue
        index = load_json(index_path.relative_to(ROOT).as_posix())
        for record in index.get("records", []):
            relative = record.get("canonical_path", "")
            if not relative:
                fail(f"{index_path}: reassessment without canonical_path")
                continue
            document = apply_schema(relative, "schemas/decision-reassessment.schema.json")
            if document.get("project_id") != project_dir.name:
                fail(f"{relative}: project_id mismatch")
            if document.get("reassessment_id") in seen:
                fail(f"{relative}: duplicate reassessment ID")
            seen.add(document.get("reassessment_id"))
    if len(global_records) != len(seen):
        fail("global reassessment registry differs from project records")

def validate_evidence(registries: dict[str, Any]) -> None:
    registered = {r.get("path") for r in registries["evidence"].get("records", [])}
    reports = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.glob("projects/symphonie/reports/*.md")
    }
    missing = sorted(reports - registered)
    if missing:
        fail("unregistered Symphonie reports: " + ", ".join(missing))
    unincorporated = registries["unincorporated"]
    if unincorporated.get("records"):
        fail("material unincorporated records remain open")

def validate_fixture(state: dict[str, Any], index: dict[str, Any], registries: dict[str, Any]) -> None:
    expected = load_json("tests/expected_repository_state.json")
    symphonie = next(
        (record for record in registries["projects"].get("records", []) if record.get("id") == "symphonie"),
        {},
    )
    actual = {
        "methodology_version": state.get("methodology", {}).get("version"),
        "active_project": state.get("active_project"),
        "current_phase": state.get("current_phase"),
        "project_statuses": {r["id"]: r["status"] for r in registries["projects"].get("records", [])},
        "decisions_in_force": state.get("decisions_in_force"),
        "open_errors": state.get("open_errors"),
        "validated_patterns": state.get("validated_patterns"),
        "registry_counts": index.get("counts"),
        "symphonie": {
            "head": state.get("verified_external_heads", {}).get("symphonie"),
            "fileset": symphonie.get("fileset"),
            "total_phases": 8,
        },
        "authorization_state": state.get("authorization_state"),
    }
    for key, value in actual.items():
        if expected.get(key) != value:
            fail(f"expected-state mismatch for {key}")

