from .context import *
from .visual_utils import *

def validate_foundation_library(registries: dict[str, Any]) -> None:
    library = load_json("registry/foundation-library.json")
    if registries.get("foundation_library") != library:
        fail("foundation library registry was not loaded canonically")
    design_required = set(library.get("required_design_archetypes", []))
    backend_required = set(library.get("required_backend_domains", []))
    if design_required != REQUIRED_DESIGN_ARCHETYPES:
        fail("foundation library: required design archetype set mismatch")
    if backend_required != REQUIRED_BACKEND_DOMAINS:
        fail("foundation library: required backend domain set mismatch")
    seen_designs: set[str] = set()
    seen_domains: set[str] = set()
    seen_ids: set[str] = set()
    for record in library.get("records", []):
        record_id = record.get("id")
        if record_id in seen_ids:
            fail(f"foundation library: duplicate record {record_id}")
        seen_ids.add(record_id)
        relative = record.get("canonical_path", "")
        if record.get("kind") == "DESIGN_ARCHETYPE":
            document = apply_schema(relative, "schemas/design-archetype.schema.json")
            archetype = document.get("archetype")
            seen_designs.add(archetype)
            if record_id != document.get("id") or record.get("archetype") != archetype:
                fail(f"{relative}: registry identity mismatch")
            roles = {item.get("role") for item in document.get("typography", {}).get("font_roles", [])}
            if roles != {"DISPLAY", "BODY", "MONO"}:
                fail(f"{relative}: typography roles incomplete")
            primitives = {
                item.get("token") for item in document.get("color", {}).get("primitives", [])
            }
            for semantic in document.get("color", {}).get("semantic", []):
                if semantic.get("primitive") not in primitives:
                    fail(f"{relative}: semantic color references unknown primitive")
            for check in document.get("color", {}).get("contrast_checks", []):
                minimum = 4.5 if check.get("usage") == "NORMAL_TEXT" else 3.0
                if check.get("ratio", 0) < minimum:
                    fail(f"{relative}: contrast below {minimum}:1 for {check.get('usage')}")
                foreground = primitives and next(
                    (item.get("value") for item in document["color"]["primitives"]
                     if item.get("token") == check.get("foreground")),
                    None,
                )
                background = primitives and next(
                    (item.get("value") for item in document["color"]["primitives"]
                     if item.get("token") == check.get("background")),
                    None,
                )
                calculated = (
                    contrast_ratio(foreground, background)
                    if isinstance(foreground, str) and isinstance(background, str)
                    else None
                )
                if calculated is None:
                    fail(f"{relative}: contrast references invalid color")
                elif calculated < minimum:
                    fail(f"{relative}: calculated contrast below {minimum}:1")
                elif abs(calculated - check.get("ratio", 0)) > 0.02:
                    fail(f"{relative}: declared contrast differs from calculated ratio")
            accessibility = document.get("accessibility", {})
            for field, minimum in [
                ("normal_text_contrast_min", 4.5),
                ("large_text_contrast_min", 3.0),
                ("ui_contrast_min", 3.0),
                ("pointer_target_min_px", 44),
            ]:
                if accessibility.get(field, 0) < minimum:
                    fail(f"{relative}: accessibility threshold too low for {field}")
            states = set(document.get("interaction_states", []))
            if states != REQUIRED_INTERACTION_STATES:
                fail(f"{relative}: interaction states incomplete")
            modes = document.get("responsive", {}).get("modes", [])
            if [item.get("id") for item in modes] != ["COMPACT", "STANDARD", "EXPANDED", "WIDE"]:
                fail(f"{relative}: responsive modes must use canonical order")
            if modes and modes[0].get("min_width_px") != 0:
                fail(f"{relative}: responsive ranges must start at zero")
            for previous, current in zip(modes, modes[1:]):
                upper = previous.get("max_width_px")
                if not isinstance(upper, int) or current.get("min_width_px") != upper + 1:
                    fail(f"{relative}: responsive ranges have gap or overlap")
            if modes and modes[-1].get("max_width_px") is not None:
                fail(f"{relative}: final responsive range must be unbounded")
            invariant_ids = [
                item.get("id") for item in document.get("responsive", {}).get("invariants", [])
            ]
            if len(invariant_ids) != len(set(invariant_ids)):
                fail(f"{relative}: responsive invariant IDs duplicated")
        elif record.get("kind") == "BACKEND_PATTERN":
            document = apply_schema(relative, "schemas/backend-pattern.schema.json")
            domain = document.get("domain")
            seen_domains.add(domain)
            if record_id != document.get("id") or record.get("domain") != domain:
                fail(f"{relative}: registry identity mismatch")
            if document.get("provider_neutral") is not True:
                fail(f"{relative}: pattern is not provider-neutral")
            boundary = document.get("secret_boundary", {})
            if boundary.get("repository_values_allowed") is not False:
                fail(f"{relative}: repository secret values must be forbidden")
            if boundary.get("reference_only") is not True:
                fail(f"{relative}: environment secrets must be reference-only")
            configuration = document.get("configuration_contract", {})
            client_fields = set(configuration.get("client_replaceable", []))
            environment_fields = set(configuration.get("environment_managed", []))
            if client_fields & environment_fields:
                fail(f"{relative}: client and environment configuration overlap")
            if domain == "PAYMENT_ORCHESTRATION":
                required_client = {
                    "merchant_display_name", "default_currency", "supported_currencies",
                    "locale", "return_route", "cancellation_route",
                }
                required_environment = {
                    "payment_account_reference", "api_credential_reference",
                    "webhook_secret_reference", "provider_endpoint_profile",
                }
                if not required_client <= client_fields:
                    fail(f"{relative}: payment client configuration incomplete")
                if not required_environment <= environment_fields:
                    fail(f"{relative}: payment environment boundary incomplete")
                forbidden_text = " ".join(document.get("forbidden", [])).lower()
                for term in ["pan", "cvc", "importe", "credenciales"]:
                    if term not in forbidden_text:
                        fail(f"{relative}: payment prohibition missing {term}")
        elif record.get("kind") in {
            "DESIGN_KNOWLEDGE_SOURCE_PACKAGE",
            "VISUAL_PREFERENCE_PROFILE",
            "HIGH_FIDELITY_VISUAL_PROTOCOL",
            "MINIMUM_VISUAL_FOUNDATION",
            "TRANSVERSAL_EVIDENTIAL_CONTROL_CAPABILITY",
            "PRODUCT_LEADERSHIP_CANDIDATE_PACKAGE",
        }:
            require_file(relative)
        elif record.get("kind") == "LOCAL_BRAND_ICON_ASSET_CANDIDATE_LIBRARY":
            document = load_json(relative)
            if document.get("library_id") != record_id:
                fail(f"{relative}: local brand icon library identity mismatch")
            if document.get("status") != "SELECTED_ASSET_INTEGRATED_AWAITING_HUMAN_FOOTER_REVIEW":
                fail(f"{relative}: local brand icon library status differs")
            if document.get("candidate_count") != 3:
                fail(f"{relative}: local brand icon candidate count differs")
            if document.get("integration_status") != "PUBLISHED":
                fail(f"{relative}: local brand icon integration publication state differs")
            if document.get("human_icon_selection") is not True:
                fail(f"{relative}: local brand icon human selection is not recorded")
            if document.get("selected_candidate_id") != "WHATSAPP-CANDIDATE-BOOTSTRAP-ICONS-001":
                fail(f"{relative}: local brand icon selected candidate differs")
            if document.get("brand_usage_approval") is not False:
                fail(f"{relative}: local brand icon brand approval boundary differs")
        else:
            fail(f"foundation library: unsupported kind for {record_id}")
    if seen_designs != REQUIRED_DESIGN_ARCHETYPES:
        fail("foundation library: design archetype instances incomplete")
    if seen_domains != REQUIRED_BACKEND_DOMAINS:
        fail("foundation library: backend pattern instances incomplete")

def validate_visual_foundation(registries: dict[str, Any]) -> None:
    profile_path = "foundation-library/visual-preferences/jonathan-martinez.visual-preference-profile.json"
    protocol_path = "foundation-library/visual-protocols/high-fidelity-visual-protocol.json"
    profile = apply_schema(profile_path, "schemas/visual-preference-profile.schema.json")
    protocol = apply_schema(protocol_path, "schemas/high-fidelity-visual-protocol.schema.json")
    dimensions = {"typography", "color", "composition", "imagery_and_render", "materiality", "controls", "information_density", "motion", "accessibility_boundaries"}
    if set(profile.get("dimensions", {})) != dimensions:
        fail("visual preference profile: required dimensions differ")
    if set(profile.get("signals", {})) != {"preferred", "contextual", "insufficient", "rejected"}:
        fail("visual preference profile: signal classifications differ")
    reconciliation_ids = {item.get("id") for item in profile.get("reconciliations", []) if isinstance(item, dict)}
    if reconciliation_ids != {"REC-001", "REC-002", "REC-003", "REC-004", "REC-005", "REC-006", "REC-007"}:
        fail("visual preference profile: required reconciliations differ")
    if profile.get("status") != "DOCUMENTED_WITH_PROPOSED_CODE_BENCHMARK":
        fail("visual preference profile: implementation boundary is unsafe")
    if profile.get("scope_boundary", {}).get("personal_profile_not_global_governance") is not True:
        fail("visual preference profile: global governance boundary is missing")
    stages = [item.get("id") for item in protocol.get("stages", []) if isinstance(item, dict)]
    expected_stages = ["MINIMUM_IMPECCABLE_TECHNICAL_FOUNDATION_GATE", "RESOLVE_PRODUCT_CONTEXT", "QUALIFY_APPLICABLE_REFERENCES", "RESOLVE_CONTEXTUAL_PREFERENCE_SIGNALS", "INTERPRET_PROPOSED_CODE_BENCHMARK_WITHOUT_AUTO_SELECTION", "VISUAL_ACCESSIBILITY_PREFLIGHT", "GENERATE_MONOLITHIC_VISUAL_CALIBRATION", "VISUAL_CALIBRATION_APPROVED", "EXPAND_APPROVED_DIRECTION_TO_ROUTES_AND_STATES", "RESPONSIVE_ACCESSIBILITY_AND_INTERACTION_VALIDATION", "HIGH_FIDELITY_VISUAL_BASELINE_APPROVED", "FINAL_PHASE3_CONTRACT_GENERATION"]
    if stages != expected_stages:
        fail("high-fidelity visual protocol: required stages differ")
    direction = protocol.get("visual_direction_contract", {})
    if direction.get("minimum_directions_before_first_calibration") != 1 or direction.get("selection_authority") != "JONATHAN_MARTINEZ_EXPLICIT_SELECTION":
        fail("high-fidelity visual protocol: reconciled direction and human selection rules differ")
    technical_gate = protocol.get("technical_foundation_gate", {})
    if technical_gate.get("id") != "MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001" or technical_gate.get("required_before_visual_direction_application") is not True or technical_gate.get("pass_with_known_defects") != "PROHIBITED":
        fail("high-fidelity visual protocol: minimum technical foundation gate is unsafe")
    gate = protocol.get("baseline_gate", {})
    if gate.get("approver") != "JONATHAN_MARTINEZ" or gate.get("model_self_approval") != "PROHIBITED" or gate.get("final_phase3_contract_allowed") is not False:
        fail("high-fidelity visual protocol: baseline gate is unsafe")
    if protocol.get("responsive_review", {}).get("widths_px") != [320, 640, 1024, 1440, 1920]:
        fail("high-fidelity visual protocol: responsive widths differ")
    areas = {"TYPOGRAPHIC_HIERARCHY", "COLOR_AND_CONTRAST", "COMPOSITIONAL_BALANCE", "ACTIVE_NEGATIVE_SPACE", "PRODUCT_OR_PURPOSE_PROMINENCE", "IMAGE_AND_RENDER_QUALITY", "MATERIAL_COHERENCE", "CONTROL_AFFORDANCE", "STATE_COMPLETENESS", "CONTENT_STRESS", "ZOOM_AND_REFLOW", "MOTION_AND_REDUCED_MOTION", "STRUCTURAL_GEOMETRY", "COMPONENT_FINISH", "GRID_ALIGNMENT_AND_SPACING", "LAYERS_AND_OVERLAYS", "FORM_BEHAVIOR"}
    if set(protocol.get("review_contract", {}).get("areas", [])) != areas or set(protocol.get("responsive_review", {}).get("areas", [])) != areas:
        fail("high-fidelity visual protocol: review areas differ")
    if protocol.get("status") != "DOCUMENTED_WITH_MINIMUM_TECHNICAL_FOUNDATION_AND_PROPOSED_PREFERENCE_BENCHMARK":
        fail("high-fidelity visual protocol: implementation boundary is unsafe")
    profile_boundary = profile.get("authorization_boundary", {})
    for key in ["application_code", "html_generation", "css_generation", "javascript_generation", "runtime", "product_changes", "deployment", "release"]:
        if profile_boundary.get(key) != "NOT_AUTHORIZED":
            fail("visual preference profile: core authorization boundary is unsafe")
    protocol_boundary = protocol.get("authority_boundary", {})
    for key in ["runtime", "application_code", "product_changes", "release"]:
        if protocol_boundary.get(key) != "NOT_AUTHORIZED":
            fail("high-fidelity visual protocol: core authority boundary is unsafe")
    library_ids = {record.get("id") for record in registries.get("foundation_library", {}).get("records", [])}
    visual_records = registries.get("visual_preferences", {}).get("records", [])
    if {"VPP-JM-001", "HFP-041-001", "MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"} - library_ids:
        fail("visual foundation: canonical artifacts are absent from Foundation Library")
    if len(visual_records) != 1 or visual_records[0].get("id") != "VISUAL-PREFERENCE-REGISTRY-041":
        fail("visual foundation: visual preference registry is incomplete")


