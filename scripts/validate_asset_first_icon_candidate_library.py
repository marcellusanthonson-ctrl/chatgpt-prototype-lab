from __future__ import annotations

import hashlib
import json
import re
import sys
import traceback
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "foundation-library/brand-icons/LOCAL-ICON-ASSET-CANDIDATE-LIBRARY-001"
FIXTURE = ROOT / "foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001/MINIMUM_IMPECCABLE_BASE_001.html"
EXPECTED_FIXTURE_SHA256_LF = "13cab2709775e9c2923b85c2557988c57ce57987dac0fcb1aedc0e347660b405"
EXPECTED_IDS = {
    "WHATSAPP-CANDIDATE-BOOTSTRAP-ICONS-001",
    "WHATSAPP-CANDIDATE-FONT-AWESOME-001",
    "WHATSAPP-CANDIDATE-TABLER-ICONS-001",
}
FORBIDDEN_SVG_TAGS = {"script", "foreignObject", "iframe", "image", "audio", "video", "use", "filter"}
FORBIDDEN_SVG_ATTRIBUTES = {"href", "xlink:href", "onload", "onclick", "onerror", "style", "transform", "filter"}


def load_json(path: Path) -> dict:
    def reject_duplicate(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise AssertionError(f"duplicate key {key!r} in {path}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


class ReviewParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.candidate_ids: set[str] = set()
        self.sources: list[str] = []
        self.external_resources: list[str] = []
        self.buttons = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("data-candidate-id"):
            self.candidate_ids.add(str(values["data-candidate-id"]))
        if tag == "img" and values.get("src"):
            self.sources.append(str(values["src"]))
        if tag in {"img", "script", "link", "iframe", "object", "embed", "source"}:
            resource = values.get("src") or values.get("href") or values.get("data")
            if resource and re.match(r"^(?:https?:)?//", str(resource), flags=re.I):
                self.external_resources.append(str(resource))
        if tag == "button":
            self.buttons += 1
            assert values.get("aria-label"), "every review button requires an accessible name"


def main() -> int:
    manifest = load_json(BASE / "MANIFEST.json")
    candidates = load_json(BASE / "CANDIDATES.json")
    legal = load_json(BASE / "LEGAL_REGISTER.json")
    review_text = (BASE / "REVIEW.html").read_text(encoding="utf-8")
    notices = (BASE / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")

    assert manifest["library_id"] == candidates["library_id"] == "LOCAL-ICON-ASSET-CANDIDATE-LIBRARY-001"
    assert manifest["status"] == "READY_FOR_HUMAN_REVIEW"
    assert manifest["principle"] == "ASSET_FIRST_FOR_BRAND_ASSOCIATED_VISUALS"
    assert manifest["candidate_count"] == len(candidates["records"]) == 3
    assert manifest["human_icon_selection"] is False
    assert manifest["brand_usage_approval"] is False
    assert manifest["integration_status"] == "NOT_INTEGRATED"
    assert manifest["fixture_modified"] is False
    assert manifest["product_effect"] == manifest["runtime_effect"] == manifest["rag_effect"] == manifest["integration_effect"] == "NONE"
    assert manifest["wcag_conformance"] == "NOT_ESTABLISHED"

    records = {record["candidate_id"]: record for record in candidates["records"]}
    assert set(records) == EXPECTED_IDS
    assert candidates["selection_policy"] == "HUMAN_SELECTION_REQUIRED_NO_AUTOMATIC_RANKING"
    legal_records = {record["candidate_id"]: record for record in legal["records"]}
    assert set(legal_records) == EXPECTED_IDS

    for candidate_id, record in records.items():
        asset = BASE / record["local_path"]
        assert asset.is_file(), f"missing asset for {candidate_id}"
        assert sha256(asset) == record["sha256"], f"hash mismatch for {candidate_id}"
        assert re.fullmatch(r"[0-9a-f]{40}", record["source"]["commit"])
        assert record["source"]["commit"] in record["source"]["raw_url"]
        assert record["source"]["path"] in record["source"]["raw_url"]
        assert record["source"]["acquired_at"] == "2026-07-22"
        assert record["copyright"]["status"] in {
            "MIT_LICENSE_RECORDED",
            "CC_BY_4_0_LICENSE_AND_ATTRIBUTION_RECORDED",
        }
        assert record["trademark"]["status"] == "PENDING_HUMAN_BRAND_USAGE_APPROVAL"
        assert record["trademark"]["library_license_does_not_grant_trademark_rights"] is True
        assert record["brand_guidance"]["status"] == "LOCATED_ACCESS_REQUIRES_META_LOGIN"
        assert (
            record["modification_policy"].startswith("SOURCE_BYTES_PRESERVED")
            or record["modification_policy"].startswith("FINAL_NEWLINE_NORMALIZATION_ONLY")
        )
        source_bytes = asset.read_bytes()
        source_hash = record["source"]["source_sha256"]
        if record["modification_policy"].startswith("FINAL_NEWLINE_NORMALIZATION_ONLY"):
            assert source_bytes.endswith(b"\n")
            assert hashlib.sha256(source_bytes[:-1]).hexdigest() == source_hash
        else:
            assert record["sha256"] == source_hash
        assert record["technical_validation"] == "PASS"
        assert record["human_status"] == "PENDING"
        assert record["integration_status"] == "NOT_INTEGRATED"
        assert legal_records[candidate_id]["integration_legally_cleared"] is False

        root = ET.fromstring(asset.read_text(encoding="utf-8"))
        assert local_name(root.tag) == "svg"
        assert root.get("viewBox"), f"viewBox missing for {candidate_id}"
        assert any(local_name(node.tag) == "path" and node.get("d") for node in root.iter())
        for node in root.iter():
            assert local_name(node.tag) not in FORBIDDEN_SVG_TAGS, f"forbidden SVG tag in {candidate_id}"
            lowered = {local_name(key).lower() for key in node.attrib}
            assert not lowered.intersection({item.lower() for item in FORBIDDEN_SVG_ATTRIBUTES}), f"forbidden SVG attribute in {candidate_id}"

    assert "The Bootstrap Authors" in notices
    assert "Font Awesome Free 7.2.0" in notices
    assert "Paweł Kuna" in notices
    assert "do not grant trademark rights" in notices

    parser = ReviewParser()
    parser.feed(review_text)
    assert parser.candidate_ids == EXPECTED_IDS
    assert parser.external_resources == [], f"external review resources: {parser.external_resources}"
    assert parser.buttons >= 45
    for record in records.values():
        assert parser.sources.count(record["local_path"]) >= 12
    for size in (16, 18, 20, 22, 24):
        assert review_text.count(f"--icon:{size}px") >= 3
    for box in (36, 40, 44):
        assert review_text.count(f"--box:{box}px") >= 3
    assert review_text.count("surface--light") >= 4
    assert review_text.count("surface--dark") >= 4
    assert review_text.count("is-hover") >= 7
    assert review_text.count("is-focus") >= 7
    assert ":focus-visible" in review_text
    assert "prefers-reduced-motion" in review_text
    assert "ninguna selección automática" in review_text.lower()

    manifest_files = set(manifest["files"])
    expected_files = {
        str(path.relative_to(BASE)).replace("\\", "/")
        for path in BASE.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    assert manifest_files == expected_files

    fixture_lf = FIXTURE.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
    assert hashlib.sha256(fixture_lf).hexdigest() == EXPECTED_FIXTURE_SHA256_LF, "governed fixture changed"

    print("Asset candidate manifest, JSON and duplicate keys: PASS")
    print("Three source-pinned candidate records and SHA-256 values: PASS")
    print("SVG security and structural allowlist: PASS")
    print("Copyright notices and trademark boundaries: PASS")
    print("REVIEW.html sizes, containers, themes and states: PASS")
    print("REVIEW.html offline local-resource boundary: PASS")
    print("MINIMUM_IMPECCABLE_BASE_001.html unchanged: PASS")
    print("Human icon selection: PENDING")
    print("Brand usage approval: PENDING")
    print("WCAG conformance: NOT_ESTABLISHED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ET.ParseError, json.JSONDecodeError) as exc:
        print(f"Asset candidate library validation: FAIL: {exc}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
