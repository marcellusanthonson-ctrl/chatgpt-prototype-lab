#!/usr/bin/env python3
"""Deterministic contract checks for MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"


def load(name: str):
    def hook(items):
        keys = [key for key, _ in items]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            raise AssertionError(f"{name}: duplicate keys {duplicates}")
        return dict(items)
    return json.loads((BASE / name).read_text(encoding="utf-8"), object_pairs_hook=hook)


class Node:
    def __init__(self, tag: str, attrs: list[tuple[str, str | None]], parent: "Node | None"):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children: list[Node] = []

    def descendants(self, tag: str | None = None):
        for child in self.children:
            if tag is None or child.tag == tag:
                yield child
            yield from child.descendants(tag)


class FixtureParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("document", [], None)
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return


def classes(node: Node) -> set[str]:
    return set((node.attrs.get("class") or "").split())


def numeric_metadata(node: Node, name: str) -> int:
    value = node.attrs.get(name, "")
    assert re.fullmatch(r"[1-9]\d*", value), f"{name} must be a positive integer"
    return int(value)


def main() -> int:
    manifest = load("MANIFEST.json")
    standard = load("STANDARD.json")
    geometry = load("STRUCTURAL_GEOMETRY_CONTRACT.json")
    components = load("COMPONENT_FINISH_CONTRACT.json")
    iconography = load("FUNCTIONAL_ICONOGRAPHY_CONTRACT.json")
    layout = load("LAYOUT_INTENT_MAP_CONTRACT.json")
    forms = load("FORM_BEHAVIOR_CONTRACT.json")
    responsive = load("RESPONSIVE_RESILIENCE_CONTRACT.json")
    correction = load("SELF_CORRECTION_CONTRACT.json")
    matrix = load("VALIDATION_MATRIX.json")

    assert manifest["foundation_id"] == standard["standard_id"] == "MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001"
    assert manifest["version"] == standard["version"] == iconography["foundation_version"] == "1.1.1"
    assert "FUNCTIONAL_ICONOGRAPHY_CONTRACT.json" in manifest["files"]
    assert manifest["status"] in correction["allowed_terminal_states"]
    assert correction["forbidden_terminal_state"] == "PASS_WITH_KNOWN_VISUAL_DEFECTS"
    assert correction["cycle"] == [
        "RENDER", "INSPECT", "MEASURE", "INTERACT", "STRESS",
        "CLASSIFY_DEFECTS", "DIAGNOSE_ROOT_CAUSE", "CORRECT_OR_RECONSTRUCT",
        "REVALIDATE_COMPLETE_SURFACE",
    ]
    assert len(standard["defect_domains"]) >= 16
    assert "ZERO_KNOWN_CORRECTABLE_DEFECTS_AT_DELIVERY" in standard["non_negotiable_outcomes"]
    assert "FUNCTIONAL_ICONOGRAPHY_CONTRACT_ENFORCED" in standard["non_negotiable_outcomes"]
    assert "STRUCTURAL_OVERFLOW" in geometry["blocking_defects"]
    assert set(components["components"]) == {"icons", "buttons_and_controls", "typography", "navbar", "hero", "footer"}
    assert components["functional_iconography_contract_ref"] == "FUNCTIONAL_ICONOGRAPHY_CONTRACT.json"
    assert len(layout["fixture_map"]) == 5
    assert "DATA_LOSS_ON_VALIDATION" in forms["blocking_defects"]
    assert responsive["continuous_sweep"] == {"from_px": 320, "to_px": 1920, "maximum_step_px": 16}
    case_ids = [case["id"] for case in matrix["cases"]]
    assert len(case_ids) == len(set(case_ids)) == 18
    assert iconography["render_models"]["allowed"] == ["STROKE", "FILL", "HYBRID"]
    assert set(iconography["categories"]) == {
        "FUNCTIONAL_INTERFACE_ICON", "SOCIAL_OR_BRAND_ASSOCIATED_ICON",
        "ILLUSTRATIVE_ICON", "PHOTOGRAPHIC_OR_DECORATIVE_ASSET",
    }
    assert iconography["verification_sizes_css_px"]["glyphs"] == [16, 18, 20, 24]
    assert iconography["verification_sizes_css_px"]["containers"] == [36, 40, 44]
    assert iconography["verification_sizes_css_px"]["device_scale_factors"] == [1, 2]
    assert iconography["geometry"]["filter_on_glyph_allowed"] is False
    assert iconography["geometry"]["base_transform_allowed"] is False
    assert iconography["state_behavior"]["active_perceptual_deformation_allowed"] is False
    assert iconography["accessibility"]["minimum_touch_surface_css_px"] == 44
    assert not any(value for key, value in iconography["claim_boundaries"].items() if key in {"human_visual_approval", "wcag_conformance", "benchmark_approval"})

    html = (BASE / "MINIMUM_IMPECCABLE_BASE_001.html").read_text(encoding="utf-8")
    lowered = html.lower()
    for forbidden in ["@import", "fetch(", "xmlhttprequest", "overflow-x:hidden", "overflow-x: hidden"]:
        assert forbidden not in lowered, f"HTML contains forbidden token: {forbidden}"
    assert "<style>" in lowered and "<script>" in lowered
    assert "<header" in lowered and "<main" in lowered and "<footer" in lowered and "<dialog" in lowered
    assert "prefers-reduced-motion" in lowered
    assert 'id="main"' in lowered and 'class="skip-link"' in lowered
    assert "window.__MIVF_DIAGNOSTIC__" in html
    assert '<section class="footer__group" aria-labelledby="footer-status-title">' in html
    assert '<dl class="footer__status">' in html
    assert len(re.findall(r"<dt>", html)) == len(re.findall(r"<dd>", html)) == 2
    assert not re.search(r"<img\b", lowered), "Neutral fixture must not contain images"
    assert not re.search(r"<link\b[^>]*rel=[\"']stylesheet", lowered), "Linked stylesheets are forbidden"
    assert not re.search(r"<use\b[^>]*(?:href|xlink:href)=[\"'](?!#)", lowered), "External SVG use is forbidden"

    parser = FixtureParser()
    parser.feed(html)
    nodes = list(parser.root.descendants())
    ids = [node.attrs["id"] for node in nodes if node.attrs.get("id")]
    assert len(ids) == len(set(ids)), "Fixture IDs must be unique"
    social_links = [node for node in nodes if node.tag == "a" and "footer__social-link" in classes(node)]
    assert len(social_links) == 4, "Exactly four social controls are required"
    assert sum(bool(link.attrs.get("aria-label", "").strip()) for link in social_links) == 4
    allowed_urls = {
        "https://www.instagram.com/", "https://www.whatsapp.com/",
        "https://www.facebook.com/", "https://www.linkedin.com/",
    }
    assert {link.attrs.get("href") for link in social_links} == allowed_urls

    declared_boxes = set()
    declared_sizes = set()
    for link in social_links:
        assert set((link.attrs.get("rel") or "").split()) == {"noopener", "noreferrer"}
        svgs = [node for node in link.descendants("svg")]
        assert len(svgs) == 1, "Each social control must contain exactly one inline SVG"
        svg = svgs[0]
        assert svg.attrs.get("aria-hidden") == "true"
        category = svg.attrs.get("data-icon-category")
        render = svg.attrs.get("data-icon-render")
        assert category in iconography["governed_categories"]
        assert category == "SOCIAL_OR_BRAND_ASSOCIATED_ICON"
        assert render in iconography["render_models"]["allowed"]
        size = numeric_metadata(svg, "data-icon-size")
        box = numeric_metadata(svg, "data-icon-box")
        declared_sizes.add(size)
        declared_boxes.add(box)
        assert box >= iconography["accessibility"]["minimum_touch_surface_css_px"]
        values = [float(value) for value in re.split(r"[\s,]+", svg.attrs.get("viewbox", "").strip()) if value]
        assert len(values) == 4 and values[2] > 0 and values[2] == values[3], "SVG viewBox must be valid and square"
        assert not svg.attrs.get("filter") and svg.attrs.get("transform") in {None, "none"}
        descendants = list(svg.descendants())
        assert all(not node.attrs.get("filter") for node in descendants)
        assert all(node.attrs.get("transform") in {None, "none"} for node in descendants)
        if render in {"STROKE", "HYBRID"}:
            assert svg.attrs.get("stroke") == "currentColor"
            assert svg.attrs.get("stroke-linecap") and svg.attrs.get("stroke-linejoin")
        if render == "FILL":
            assert svg.attrs.get("fill") == "currentColor"
        if render == "HYBRID":
            assert any(node.attrs.get("fill") == "currentColor" for node in descendants)
    assert declared_boxes == {44} and declared_sizes == {22}, "Social controls must share identical declared boxes and nominal sizes"

    whatsapp_link = next(link for link in social_links if link.attrs.get("href") == "https://www.whatsapp.com/")
    whatsapp_svg = list(whatsapp_link.descendants("svg"))[0]
    whatsapp_paths = list(whatsapp_svg.descendants("path"))
    assert whatsapp_svg.attrs.get("viewbox") == "0 0 16 16"
    assert whatsapp_svg.attrs.get("fill") == "currentColor"
    assert whatsapp_svg.attrs.get("data-icon-render") == "FILL"
    assert len(whatsapp_paths) == 1
    assert whatsapp_paths[0].attrs.get("d", "").startswith("M13.601 2.326")
    assert not list(whatsapp_svg.descendants("circle"))

    css = re.search(r"<style>(.*?)</style>", html, re.S | re.I).group(1)
    link_rule = re.search(r"\.footer__social-link\s*\{([^}]*)\}", css, re.S).group(1)
    svg_rule = re.search(r"\.footer__social-link svg\s*\{([^}]*)\}", css, re.S).group(1)
    assert re.search(r"\bwidth:\s*44px\b", link_rule) and re.search(r"\bheight:\s*44px\b", link_rule)
    assert re.search(r"\bwidth:\s*22px\b", svg_rule) and re.search(r"\bheight:\s*22px\b", svg_rule)
    assert re.search(r"\bflex-shrink:\s*0\b", svg_rule)
    assert re.search(r"\bfilter:\s*none\b", svg_rule) and re.search(r"\btransform:\s*none\b", svg_rule)
    social_state_rules = re.findall(r"\.footer__social-link(?::[\w-]+)?\s*\{([^}]*)\}", css, re.S)
    assert all(not re.search(r"\btransform:\s*(?!none\b)", rule) for rule in social_state_rules)
    assert not re.search(r"\.footer__social-link[^{}]*\{[^}]*\bscale\s*\(", css, re.S)

    external_urls = re.findall(r"https?://[^\"']+", lowered)
    assert set(external_urls) == allowed_urls and len(external_urls) == 4
    print("Minimum impeccable foundation JSON and duplicate keys: PASS")
    print("Functional iconography contract and classification: PASS")
    print("Social inline SVG geometry, metadata and state rules: PASS")
    print("Selected Bootstrap WhatsApp geometry and neutral glyph removal: PASS")
    print("Neutral monolithic HTML self-containment and URL allowlist: PASS")
    print("Static semantics, touch surface and reduced-motion preflight: PASS")
    print("Human visual approval: NOT_ESTABLISHED")
    print("WCAG conformance: NOT_ESTABLISHED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
