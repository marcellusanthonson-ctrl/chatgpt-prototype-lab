from .context import *
from .visual_utils import *

def validate_minimum_impeccable_visual_foundation() -> None:
    base = "foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"
    names = [
        "MANIFEST.json", "STANDARD.json", "STRUCTURAL_GEOMETRY_CONTRACT.json",
        "COMPONENT_FINISH_CONTRACT.json", "FUNCTIONAL_ICONOGRAPHY_CONTRACT.json", "LAYOUT_INTENT_MAP_CONTRACT.json",
        "FORM_BEHAVIOR_CONTRACT.json", "RESPONSIVE_RESILIENCE_CONTRACT.json",
        "SELF_CORRECTION_CONTRACT.json", "VALIDATION_MATRIX.json",
        "MINIMUM_IMPECCABLE_BASE_001.html",
    ]
    for name in names:
        require_file(f"{base}/{name}")
    manifest = load_json(f"{base}/MANIFEST.json")
    standard = load_json(f"{base}/STANDARD.json")
    iconography = load_json(f"{base}/FUNCTIONAL_ICONOGRAPHY_CONTRACT.json")
    correction = load_json(f"{base}/SELF_CORRECTION_CONTRACT.json")
    responsive = load_json(f"{base}/RESPONSIVE_RESILIENCE_CONTRACT.json")
    matrix = load_json(f"{base}/VALIDATION_MATRIX.json")
    if manifest.get("foundation_id") != standard.get("standard_id"):
        fail("minimum visual foundation: identity mismatch")
    if manifest.get("version") != "1.1.1" or standard.get("version") != "1.1.1" or iconography.get("foundation_version") != "1.1.1":
        fail("minimum visual foundation: functional iconography version mismatch")
    if iconography.get("render_models", {}).get("allowed") != ["STROKE", "FILL", "HYBRID"]:
        fail("minimum visual foundation: functional iconography render models differ")
    if set(iconography.get("categories", {})) != {"FUNCTIONAL_INTERFACE_ICON", "SOCIAL_OR_BRAND_ASSOCIATED_ICON", "ILLUSTRATIVE_ICON", "PHOTOGRAPHIC_OR_DECORATIVE_ASSET"}:
        fail("minimum visual foundation: functional iconography categories differ")
    if manifest.get("status") not in correction.get("allowed_terminal_states", []):
        fail("minimum visual foundation: invalid terminal state")
    if correction.get("forbidden_terminal_state") != "PASS_WITH_KNOWN_VISUAL_DEFECTS":
        fail("minimum visual foundation: known-defect delivery is not prohibited")
    if correction.get("autonomy_boundary", {}).get("override_human_visual_decision") is not False:
        fail("minimum visual foundation: human visual authority boundary missing")
    if responsive.get("continuous_sweep") != {"from_px": 320, "to_px": 1920, "maximum_step_px": 16}:
        fail("minimum visual foundation: continuous responsive sweep differs")
    case_ids = [case.get("id") for case in matrix.get("cases", [])]
    if len(case_ids) != len(set(case_ids)) or len(case_ids) != 18:
        fail("minimum visual foundation: validation matrix IDs duplicated or incomplete")
    html = (ROOT / base / "MINIMUM_IMPECCABLE_BASE_001.html").read_text(encoding="utf-8").lower()
    allowed_social_destinations = {
        "https://www.instagram.com/",
        "https://www.whatsapp.com/",
        "https://www.facebook.com/",
        "https://www.linkedin.com/",
    }
    external_urls = re.findall(r"https?://[^\"']+", html)
    external_anchor_urls = re.findall(r"<a\b[^>]*\bhref=[\"'](https?://[^\"']+)[\"']", html)
    if set(external_urls) != allowed_social_destinations or set(external_anchor_urls) != allowed_social_destinations or len(external_urls) != 4:
        fail("minimum visual foundation: external URLs differ from the four explicit social-link destinations")
    for token in ["@import", "fetch(", "xmlhttprequest", "overflow-x:hidden", "overflow-x: hidden"]:
        if token in html:
            fail(f"minimum visual foundation: forbidden HTML token {token}")

def validate_foundation_evidence(registries: dict[str, Any]) -> None:
    require_file("foundation-library/evidence/README.md")
    design_paths = sorted(ROOT.glob("foundation-library/evidence/design-archetypes/*.evidence.json"))
    backend_paths = sorted(ROOT.glob("foundation-library/evidence/backend-patterns/*.evidence.json"))
    if len(design_paths) != 5:
        fail("foundation evidence: exactly five design protocols required")
    if len(backend_paths) != 9:
        fail("foundation evidence: exactly nine backend protocols required")
    library = registries.get("foundation_library", {})
    subjects = {record.get("id"): record for record in library.get("records", []) if record.get("kind") in {"DESIGN_ARCHETYPE", "BACKEND_PATTERN"}}
    seen_subjects: set[str] = set()
    seen_protocol_ids: set[str] = set()
    for path in design_paths + backend_paths:
        relative = path.relative_to(ROOT).as_posix()
        protocol = apply_schema(relative, "schemas/foundation-evidence-protocol.schema.json")
        protocol_id = protocol.get("id")
        if protocol_id in seen_protocol_ids:
            fail(f"{relative}: duplicate protocol ID")
        seen_protocol_ids.add(protocol_id)
        subject = protocol.get("subject", {})
        subject_id = subject.get("id")
        if subject_id in seen_subjects:
            fail(f"{relative}: duplicate evidence subject")
        seen_subjects.add(subject_id)
        record = subjects.get(subject_id)
        if not record:
            fail(f"{relative}: evidence subject not registered")
            continue
        if subject.get("canonical_path") != record.get("canonical_path"):
            fail(f"{relative}: subject canonical path mismatch")
        expected_type = record.get("kind")
        if protocol.get("protocol_type") != expected_type:
            fail(f"{relative}: protocol type differs from subject kind")
        category_field = "archetype" if expected_type == "DESIGN_ARCHETYPE" else "domain"
        if subject.get("category") != record.get(category_field):
            fail(f"{relative}: subject category mismatch")
        required = set(protocol.get("required_categories", []))
        case_categories = [case.get("category") for case in protocol.get("cases", [])]
        if set(case_categories) != required:
            fail(f"{relative}: case coverage differs from required categories")
        if len(case_categories) != len(set(case_categories)):
            fail(f"{relative}: each evidence category must have exactly one case")
        case_ids = [case.get("id") for case in protocol.get("cases", [])]
        if len(case_ids) != len(set(case_ids)):
            fail(f"{relative}: evidence case IDs duplicated")
        claims = protocol.get("execution_claims", {})
        if any(claims.values()):
            fail(f"{relative}: unexecuted protocol makes execution claim")
        fixture_policy = protocol.get("synthetic_fixture_policy", {})
        for key in ["real_data_allowed", "personal_data_allowed", "payment_data_allowed", "secrets_allowed"]:
            if fixture_policy.get(key) is not False:
                fail(f"{relative}: unsafe synthetic fixture policy {key}")
        if expected_type == "DESIGN_ARCHETYPE":
            if required != REQUIRED_DESIGN_EVIDENCE:
                fail(f"{relative}: design evidence categories incomplete")
            if protocol.get("responsive_widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
                fail(f"{relative}: responsive evidence widths mismatch")
            responsive_case = next(
                (case for case in protocol.get("cases", [])
                 if case.get("category") == "RESPONSIVE_BOUNDARY_MATRIX"),
                {},
            )
            if responsive_case.get("synthetic_input", {}).get("widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
                fail(f"{relative}: responsive case does not exercise every required width")
        else:
            expected = set(REQUIRED_BACKEND_EVIDENCE)
            if record.get("domain") == "PAYMENT_ORCHESTRATION":
                expected |= REQUIRED_PAYMENT_EVIDENCE
            if required != expected:
                fail(f"{relative}: backend evidence categories incomplete")
            if protocol.get("responsive_widths_px") != []:
                fail(f"{relative}: backend protocol must not declare responsive widths")
    if seen_subjects != set(subjects):
        missing = sorted(set(subjects) - seen_subjects)
        fail("foundation evidence: subjects without protocol: " + ", ".join(missing))

