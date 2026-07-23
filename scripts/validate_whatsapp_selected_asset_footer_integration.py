from __future__ import annotations

import hashlib
import json
import re
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "foundation-library/brand-icons/LOCAL-ICON-ASSET-CANDIDATE-LIBRARY-001"
FOUNDATION = ROOT / "foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"
FIXTURE = FOUNDATION / "MINIMUM_IMPECCABLE_BASE_001.html"
ASSET = LIBRARY / "assets/bootstrap-icons-v1.13.1-whatsapp.svg"
EXPECTED_ASSET_SHA256 = "86ed6b7d9090fd1616604a9546defbc301546794a09c7dfa90c317e3ed09727e"
EXPECTED_FIXTURE_SHA256_LF = "d7b4539ca1957f6e9a8648be797da604ebaa5b9fcd175cb381f9deef2917245e"
EXPECTED_UNCHANGED_SOCIAL_HASHES = {
    "instagram.com": "d5225435efb36e76a295ecd7683839ef079a6bb6a955ba165c5a4ea6fb564e3e",
    "facebook.com": "cd2d7e25a70769b3ced492a92d642d1ddd58b8a5715443cb704573eec13deabf",
    "linkedin.com": "c1ae6bb8d2d6d3aa899d8b59bcd78c1a7518e5e671d878a7a0dda511cf6cdd0c",
}
FORBIDDEN_SVG_TAGS = {"script", "foreignObject", "iframe", "image", "audio", "video", "use", "filter"}
FORBIDDEN_SVG_ATTRIBUTES = {"href", "xlink:href", "onload", "onclick", "onerror", "style", "transform", "filter"}


def load_json(path: Path) -> dict:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            assert key not in result, f"duplicate key {key!r} in {path}"
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def social_anchor(html: str, domain: str) -> str:
    match = re.search(
        rf'<a class="footer__social-link" href="https://www\.{re.escape(domain)}/".*?</a>',
        html,
        re.S,
    )
    assert match, f"missing social anchor for {domain}"
    return match.group(0)


def main() -> int:
    candidates = load_json(LIBRARY / "CANDIDATES.json")
    library_manifest = load_json(LIBRARY / "MANIFEST.json")
    legal = load_json(LIBRARY / "LEGAL_REGISTER.json")
    foundation_manifest = load_json(FOUNDATION / "MANIFEST.json")
    standard = load_json(FOUNDATION / "STANDARD.json")
    iconography = load_json(FOUNDATION / "FUNCTIONAL_ICONOGRAPHY_CONTRACT.json")
    records = {record["candidate_id"]: record for record in candidates["records"]}

    bootstrap = records["WHATSAPP-CANDIDATE-BOOTSTRAP-ICONS-001"]
    font_awesome = records["WHATSAPP-CANDIDATE-FONT-AWESOME-001"]
    tabler = records["WHATSAPP-CANDIDATE-TABLER-ICONS-001"]
    assert sha256_bytes(ASSET.read_bytes()) == bootstrap["sha256"] == EXPECTED_ASSET_SHA256
    assert bootstrap["human_review"] == "SELECTED"
    assert bootstrap["selection_rank"] == "PRIMARY"
    assert bootstrap["integration_status"] == "AUTHORIZED_FOR_FOCUSED_FOUNDATION_INTEGRATION"
    assert font_awesome["human_review"] == "ACCEPTED_AS_SECONDARY_ALTERNATIVE"
    assert font_awesome["selection_rank"] == "SECONDARY"
    assert font_awesome["integration_status"] == "NOT_INTEGRATED"
    assert tabler["human_review"] == "REJECTED"
    assert tabler["selection_rank"] == "NONE"
    assert tabler["integration_status"] == "NOT_INTEGRATED"

    legal_records = {record["candidate_id"]: record for record in legal["records"]}
    assert legal_records[bootstrap["candidate_id"]]["integration_legally_cleared"] is False
    assert legal_records[bootstrap["candidate_id"]]["lab_foundation_technical_integration_authorized"] is True
    for record in records.values():
        assert record["trademark"]["status"] == "PENDING_HUMAN_BRAND_USAGE_APPROVAL"

    html = FIXTURE.read_text(encoding="utf-8")
    fixture_lf = html.replace("\r\n", "\n").encode("utf-8")
    assert sha256_bytes(fixture_lf) == EXPECTED_FIXTURE_SHA256_LF
    whatsapp = social_anchor(html, "whatsapp.com")
    assert 'aria-label="WhatsApp (abre sitio externo)"' in whatsapp
    assert 'target="_blank"' in whatsapp
    assert 'rel="noopener noreferrer"' in whatsapp
    integrated_svg_match = re.search(r"<svg\b.*?</svg>", whatsapp, re.S)
    assert integrated_svg_match
    integrated_svg = ET.fromstring(integrated_svg_match.group(0))
    source_svg = ET.fromstring(ASSET.read_text(encoding="utf-8"))
    source_path = next(node for node in source_svg.iter() if local_name(node.tag) == "path")
    integrated_paths = [node for node in integrated_svg.iter() if local_name(node.tag) == "path"]
    assert len(integrated_paths) == 1
    assert integrated_svg.get("viewBox") == source_svg.get("viewBox") == "0 0 16 16"
    assert integrated_paths[0].get("d") == source_path.get("d")
    assert integrated_svg.get("fill") == "currentColor"
    assert integrated_svg.get("data-icon-render") == "FILL"
    assert integrated_svg.get("data-icon-size") == "22"
    assert integrated_svg.get("data-icon-box") == "44"
    assert integrated_svg.get("aria-hidden") == "true"
    assert "M20 11.5c0 4.42" not in html
    for node in integrated_svg.iter():
        assert local_name(node.tag) not in FORBIDDEN_SVG_TAGS
        lowered = {local_name(key).lower() for key in node.attrib}
        assert not lowered.intersection({item.lower() for item in FORBIDDEN_SVG_ATTRIBUTES})

    for domain, expected_hash in EXPECTED_UNCHANGED_SOCIAL_HASHES.items():
        assert sha256_bytes(social_anchor(html, domain).encode("utf-8")) == expected_hash
    anchors = re.findall(r'<a class="footer__social-link".*?</a>', html, re.S)
    assert ["instagram.com", "whatsapp.com", "facebook.com", "linkedin.com"] == [
        re.search(r"https://www\.([^/]+)/", anchor).group(1) for anchor in anchors
    ]

    css = re.search(r"<style>(.*?)</style>", html, re.S | re.I).group(1)
    control_rule = re.search(r"\.footer__social-link\s*\{([^}]*)\}", css, re.S).group(1)
    svg_rule = re.search(r"\.footer__social-link svg\s*\{([^}]*)\}", css, re.S).group(1)
    assert re.search(r"\bwidth:\s*44px\b", control_rule)
    assert re.search(r"\bheight:\s*44px\b", control_rule)
    assert re.search(r"\bwidth:\s*22px\b", svg_rule)
    assert re.search(r"\bheight:\s*22px\b", svg_rule)
    assert ".footer__social-link:hover" in css
    assert ":focus-visible" in css
    assert ".footer__social-link:active" in css
    assert "prefers-reduced-motion" in html

    assert foundation_manifest["version"] == standard["version"] == iconography["foundation_version"] == "1.1.1"
    assert foundation_manifest["artifact_sha256"] == EXPECTED_FIXTURE_SHA256_LF
    assert library_manifest["version"] == "1.1.0"
    assert library_manifest["human_icon_selection"] is True
    assert library_manifest["selected_candidate_id"] == bootstrap["candidate_id"]
    assert library_manifest["brand_usage_approval"] is False
    assert library_manifest["validation"]["browser_review"] == "NOT_EXECUTED_AUTOMATION_SURFACE_UNAVAILABLE"
    assert library_manifest["validation"]["manual_footer_review"] == "PENDING"

    remote_urls = re.findall(r"https?://[^\"']+", html.lower())
    assert set(remote_urls) == {
        "https://www.instagram.com/",
        "https://www.whatsapp.com/",
        "https://www.facebook.com/",
        "https://www.linkedin.com/",
    }

    print("Selected Bootstrap asset SHA-256: PASS")
    print("Human candidate selection states: PASS")
    print("Integrated viewBox and path geometry byte-for-text equality: PASS")
    print("WhatsApp URL, accessible name and inline SVG safety: PASS")
    print("44px control and 22px SVG contracts: PASS")
    print("Instagram, Facebook and LinkedIn exact markup hashes: PASS")
    print("Offline resource boundary and social order: PASS")
    print("Focused browser validation: NOT_EXECUTED_AUTOMATION_SURFACE_UNAVAILABLE")
    print("Manual human footer review: PENDING")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ET.ParseError, json.JSONDecodeError) as exc:
        print(f"Selected asset footer integration validation: FAIL: {exc}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
