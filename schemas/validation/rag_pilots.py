from .context import *
from .visual_utils import *

def validate_rag_contracts(registries: dict[str, Any]) -> None:
    expected_paths = {
        "architecture/rag/FEDERATION_CONTRACT.json",
        "architecture/rag/CANONICAL_OWNERSHIP.md",
        "architecture/rag/RETRIEVAL_AND_RANKING.md",
        "architecture/rag/INDEX_LIFECYCLE.md",
        "architecture/rag/WRITE_BOUNDARY.md",
        "architecture/rag/FAILURE_MODES.md",
    }
    registry = registries.get("rag_contracts", {})
    records = registry.get("records", [])
    actual_paths = {record.get("canonical_path") for record in records}
    if actual_paths != expected_paths:
        fail("registry/rag-contracts.json: canonical contract set mismatch")
    for record in records:
        if record.get("status") != "DOCUMENTED_NOT_IMPLEMENTED":
            fail(f"{record.get('id')}: RAG contract has executable status")
        relative = record.get("canonical_path", "")
        if relative.endswith(".md"):
            path = ROOT / relative
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                if record.get("id") not in text:
                    fail(f"{relative}: canonical ID missing")
                if "DOCUMENTED_NOT_IMPLEMENTED" not in text:
                    fail(f"{relative}: non-implementation status missing")
    contract = apply_schema(
        "architecture/rag/FEDERATION_CONTRACT.json",
        "schemas/rag-federation.schema.json",
    )
    namespaces = contract.get("namespaces", [])
    namespace_ids = [item.get("id") for item in namespaces]
    if namespace_ids != REQUIRED_RAG_NAMESPACES:
        fail("RAG federation: namespace order or membership mismatch")
    if len({item.get("isolation_key") for item in namespaces}) != 3:
        fail("RAG federation: namespace isolation keys must be unique")
    project = next((item for item in namespaces if item.get("id") == "PROJECT"), {})
    if "lab_global_governance" not in project.get("forbidden_overrides", []):
        fail("RAG federation: project may override LAB governance")
    if "symphonie_orchestration_contract" not in project.get("forbidden_overrides", []):
        fail("RAG federation: project may override Symphonie contract")
    metadata = contract.get("chunk_metadata", {})
    if metadata.get("required_fields") != REQUIRED_RAG_METADATA:
        fail("RAG federation: required chunk metadata mismatch")
    field_contracts = metadata.get("field_contracts", [])
    field_names = [item.get("name") for item in field_contracts]
    if field_names != REQUIRED_RAG_METADATA:
        fail("RAG federation: metadata field contracts mismatch")
    mutable_fields = {item.get("name") for item in field_contracts if item.get("mutable")}
    if mutable_fields != {"indexed_at"}:
        fail("RAG federation: only indexed_at may be mutable cache metadata")
    if set(contract.get("authority_rules", [])) != REQUIRED_RAG_AUTHORITY_RULES:
        fail("RAG federation: authority rules mismatch")
    retrieval = contract.get("retrieval_pipeline", {})
    if retrieval.get("authority_precedes_similarity") is not True:
        fail("RAG federation: semantic similarity precedes authority")
    stages = retrieval.get("stages", [])
    expected_stage_ids = [
        "RESOLVE_TASK_SCOPE", "SELECT_AUTHORIZED_NAMESPACES",
        "VERIFY_ACTIVE_COMMITS", "FILTER_BY_AUTHORITY_AND_STATUS",
        "RETRIEVE_WITHIN_NAMESPACE", "RANK_AUTHORITY_THEN_RELEVANCE",
        "DETECT_CROSS_SOURCE_CONFLICTS", "RETURN_CITED_CONTEXT",
    ]
    if [item.get("order") for item in stages] != list(range(1, 9)):
        fail("RAG federation: retrieval stage order invalid")
    if [item.get("id") for item in stages] != expected_stage_ids:
        fail("RAG federation: retrieval stages mismatch")
    index = contract.get("index_contract", {})
    if set(index.get("rules", [])) != REQUIRED_RAG_INDEX_RULES:
        fail("RAG federation: index rules mismatch")
    if index.get("role") != "DERIVED_READ_ONLY_CACHE":
        fail("RAG federation: index is not a derived read-only cache")
    conflicts = contract.get("conflict_contract", {})
    if conflicts.get("automatic_merge") is not False:
        fail("RAG federation: automatic conflict merge enabled")
    if conflicts.get("on_confirmed_conflict") != "STOP_CONCLUSION_AND_RETURN_SOURCES":
        fail("RAG federation: confirmed conflict does not stop conclusion")
    boundary = contract.get("write_boundary", {})
    if set(boundary.get("rules", [])) != REQUIRED_RAG_WRITE_RULES:
        fail("RAG federation: write boundary rules mismatch")
    if boundary.get("model_direct_commit") is not False or boundary.get("model_direct_push") is not False:
        fail("RAG federation: model has direct Git authority")
    write_steps = boundary.get("steps", [])
    if [item.get("order") for item in write_steps] != list(range(1, 8)):
        fail("RAG federation: write boundary order invalid")
    security = contract.get("security", {})
    if security.get("cross_project_retrieval_default") is not False:
        fail("RAG federation: cross-project retrieval is enabled by default")
    if security.get("secrets_indexed") is not False:
        fail("RAG federation: secret indexing enabled")
    if security.get("real_data_ingestion_authorized") is not False:
        fail("RAG federation: real-data ingestion authorized")
    if any(contract.get("execution_claims", {}).values()):
        fail("RAG federation: documentary contract makes implementation claim")

def validate_foundation_pilots(registries: dict[str, Any]) -> None:
    pilot_path = "foundation-library/pilots/PILOT-PREMIUM-ECOMMERCE-001/PILOT.json"
    pilot = apply_schema(pilot_path, "schemas/foundation-pilot.schema.json")
    registry = registries.get("foundation_pilots", {})
    records = registry.get("records", [])
    if len(records) != 1 or records[0].get("id") != pilot.get("id"):
        fail("registry/foundation-pilots.json: canonical pilot mismatch")
    if records and records[0].get("canonical_path") != pilot_path:
        fail("registry/foundation-pilots.json: pilot path mismatch")
    if records and records[0].get("status") != "DEFINED_NOT_EXECUTED":
        fail("registry/foundation-pilots.json: pilot has executable status")
    if pilot.get("executor", {}).get("id") != "CODEX":
        fail(f"{pilot_path}: executor must be CODEX")
    if pilot.get("executor", {}).get("autonomous_authority") is not False:
        fail(f"{pilot_path}: Codex has autonomous authority")
    if set(pilot.get("required_delta_areas", [])) != REQUIRED_PILOT_DELTA_AREAS:
        fail(f"{pilot_path}: required delta areas mismatch")
    if set(pilot.get("immutable_requirements", [])) != REQUIRED_PILOT_IMMUTABLES:
        fail(f"{pilot_path}: immutable requirements mismatch")
    if set(pilot.get("required_fixture_types", [])) != REQUIRED_PILOT_FIXTURES:
        fail(f"{pilot_path}: fixture requirements mismatch")
    if pilot.get("responsive_widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
        fail(f"{pilot_path}: responsive widths mismatch")
    for pin_name in ["archetype_pin", "evidence_pin"]:
        pin = pilot.get(pin_name, {})
        relative = pin.get("path", "")
        path = ROOT / relative
        if not path.is_file():
            fail(f"{pilot_path}: missing pinned {pin_name}")
            continue
        actual_hash = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if pin.get("content_sha256") != actual_hash:
            fail(f"{pilot_path}: {pin_name} content hash mismatch")
        if pin.get("lab_commit_sha") != "d3af193f33a08f5714f9e8bdb1dfca5f1c4e4b52":
            fail(f"{pilot_path}: {pin_name} commit pin mismatch")
    documents = pilot.get("documents", {})
    for relative in documents.values():
        require_file(relative)
    delta_path = documents.get("design_delta", "")
    delta = load_json(delta_path)
    if delta.get("pilot_id") != pilot.get("id") or delta.get("status") != "DEFINED_NOT_EXECUTED":
        fail(f"{delta_path}: pilot identity or status mismatch")
    areas = delta.get("areas", [])
    area_ids = [area.get("id") for area in areas]
    if set(area_ids) != REQUIRED_PILOT_DELTA_AREAS or len(area_ids) != len(set(area_ids)):
        fail(f"{delta_path}: delta area coverage mismatch")
    if set(delta.get("immutable_requirements_preserved", [])) != REQUIRED_PILOT_IMMUTABLES:
        fail(f"{delta_path}: immutable preservation mismatch")
    color_area = next((area for area in areas if area.get("id") == "EARTH_TONE_COLOR_PALETTE"), {})
    for check in color_area.get("contrast_checks", []):
        calculated = contrast_ratio(check.get("foreground", ""), check.get("background", ""))
        minimum = 4.5 if check.get("usage") == "NORMAL_TEXT" else 3.0
        if calculated is None or calculated < minimum:
            fail(f"{delta_path}: calculated pilot contrast below threshold")
        elif abs(calculated - check.get("ratio", 0)) > 0.02:
            fail(f"{delta_path}: declared pilot contrast differs from calculation")
    if any(delta.get("execution_claims", {}).values()):
        fail(f"{delta_path}: delta makes execution claim")
    fixtures_path = documents.get("synthetic_fixtures", "")
    fixtures_doc = load_json(fixtures_path)
    fixtures = fixtures_doc.get("fixtures", [])
    fixture_types = [item.get("fixture_type") for item in fixtures]
    fixture_ids = [item.get("id") for item in fixtures]
    if set(fixture_types) != REQUIRED_PILOT_FIXTURES or len(fixture_types) != len(set(fixture_types)):
        fail(f"{fixtures_path}: fixture type coverage mismatch")
    if len(fixture_ids) != len(set(fixture_ids)):
        fail(f"{fixtures_path}: fixture IDs duplicated")
    for fixture in fixtures:
        if not str(fixture.get("id", "")).startswith("SYNTHETIC_FIXTURE_"):
            fail(f"{fixtures_path}: non-synthetic fixture ID")
        if fixture.get("synthetic") is not True:
            fail(f"{fixtures_path}: fixture not marked synthetic")
    policy = fixtures_doc.get("policy", {})
    for key in ["real_client_data", "real_product_data", "real_payment_data"]:
        if policy.get(key) is not False:
            fail(f"{fixtures_path}: unsafe fixture policy {key}")
    if any(fixtures_doc.get("execution_claims", {}).values()):
        fail(f"{fixtures_path}: fixtures make execution claim")
    matrix_path = documents.get("acceptance_matrix", "")
    matrix_doc = load_json(matrix_path)
    expected_requirements = (
        {f"IMMUTABLE_{item}" for item in REQUIRED_PILOT_IMMUTABLES}
        | {f"DELTA_{item}" for item in REQUIRED_PILOT_DELTA_AREAS}
        | {f"RESPONSIVE_WIDTH_{width}" for width in REQUIRED_RESPONSIVE_WIDTHS}
    )
    if set(matrix_doc.get("requirements_covered", [])) != expected_requirements:
        fail(f"{matrix_path}: acceptance requirement coverage mismatch")
    matrix = matrix_doc.get("matrix", [])
    requirements = [item.get("requirement") for item in matrix]
    if set(requirements) != expected_requirements or len(requirements) != len(set(requirements)):
        fail(f"{matrix_path}: acceptance matrix rows mismatch")
    known_fixture_ids = set(fixture_ids)
    evidence = load_json(pilot.get("evidence_pin", {}).get("path", ""))
    known_evidence_cases = {case.get("id") for case in evidence.get("cases", [])}
    for row in matrix:
        if not row.get("measurement") or not row.get("pass_condition") or not row.get("fail_condition"):
            fail(f"{matrix_path}: incomplete oracle for {row.get('id')}")
        if set(row.get("fixture_refs", [])) - known_fixture_ids:
            fail(f"{matrix_path}: unknown fixture reference for {row.get('id')}")
        if row.get("evidence_case") not in known_evidence_cases:
            fail(f"{matrix_path}: unknown evidence case for {row.get('id')}")
    if matrix_doc.get("responsive_widths_px") != REQUIRED_RESPONSIVE_WIDTHS:
        fail(f"{matrix_path}: responsive matrix widths mismatch")
    if matrix_doc.get("result_policy", {}).get("default") != "NOT_EXECUTED":
        fail(f"{matrix_path}: unexecuted result default changed")
    if any(matrix_doc.get("execution_claims", {}).values()):
        fail(f"{matrix_path}: acceptance matrix makes execution claim")
    brief_path = documents.get("brief", "")
    if (ROOT / brief_path).is_file():
        brief = (ROOT / brief_path).read_text(encoding="utf-8")
        if "completamente ficticia" not in brief or "No se implementa checkout" not in brief:
            fail(f"{brief_path}: synthetic or payment boundary missing")
    preconditions_path = documents.get("execution_preconditions", "")
    if (ROOT / preconditions_path).is_file():
        preconditions = (ROOT / preconditions_path).read_text(encoding="utf-8")
        if "autorización posterior" not in preconditions or "fixtures sintéticas" not in preconditions:
            fail(f"{preconditions_path}: execution authority boundary missing")
    if any(pilot.get("execution_claims", {}).values()):
        fail(f"{pilot_path}: unexecuted pilot makes execution claim")


