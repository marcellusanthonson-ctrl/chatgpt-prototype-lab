#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SELECTOR = Path("project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json")
REGISTRY = Path("architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json")
ADAPTER_ROOT = Path("architecture/integrations/migration/M2/module-adapters")
EXPECTED_SELECTOR_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
EXPECTED_M1A_DIGEST = "048c2e7995986ca061ce66ce65a1a33f532a8ab17819ea057a0ff979a12ee55d"
EXPECTED_FIXTURES = [f"CRIT-FIX-{i:03d}" for i in range(1, 14)]

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def normalized_digest(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()

def validate(root: Path):
    selector = load(root / SELECTOR)
    registry = load(root / REGISTRY)
    adapters = {e["module_id"]: load(root / e["adapter_path"]) for e in registry["entries"]}
    module_ids = [m["id"] for m in selector["modules"]]
    registry_ids = [e["module_id"] for e in registry["entries"]]
    gates = {}
    gates["STATIC_AND_SHADOW_MODULE_SET_EQUIVALENT"] = set(module_ids) == set(registry_ids) == set(adapters)
    gates["STATIC_AND_SHADOW_MODULE_ORDER_EQUIVALENT"] = module_ids == registry_ids
    gates["ACTIVATION_OPERATORS_EQUIVALENT"] = all(
        {k: m[k] for k in ("activate_any", "activate_all", "activate_alternative_all") if k in m}
        == adapters[m["id"]]["activation_contract"]
        for m in selector["modules"]
    )
    static_activation, shadow_activation = [], []
    for module in selector["modules"]:
        for key in ("activate_any", "activate_all", "activate_alternative_all"):
            static_activation.extend(module.get(key, []))
    for module_id in module_ids:
        for values in adapters[module_id]["activation_contract"].values():
            shadow_activation.extend(values)
    static_exclusions = selector["exclusions"][0]["when_any"]
    shadow_exclusions = registry["composition"]["exclusions"][0]["when_any"]
    gates["ALL_27_SELECTOR_SIGNALS_PRESERVED"] = (
        set(static_activation) == set(shadow_activation)
        and static_exclusions == shadow_exclusions
        and len(set(static_activation) | set(static_exclusions)) == 27
    )
    gates["ALL_6_COMPOSITION_RULES_PRESERVED"] = (
        registry["composition"]["rules"] == selector["composition_rules"]
        and len(selector["composition_rules"]) == 6
    )
    gates["EXCLUSION_BLOCK_PRESERVED"] = registry["composition"]["exclusions"] == selector["exclusions"]
    gates["EMPTY_SET_ABSTENTION_PRESERVED"] = registry["composition"]["empty_set_abstention"] == "NO_MATCH_RETURNS_EMPTY_MODULE_SET"
    gates["ALL_13_FIXTURE_REFERENCES_PRESERVED"] = registry["baseline_fixtures"]["fixture_ids"] == EXPECTED_FIXTURES
    gates["SOURCE_REFERENCES_PRESERVED"] = all(adapters[m["id"]]["source_refs"] == m["source_refs"] for m in selector["modules"])
    gates["M1A_BASELINE_UNCHANGED"] = (
        registry["m1a_baseline"]["normalized_digest"] == EXPECTED_M1A_DIGEST
        and registry["m1a_baseline"]["unchanged"] is True
    )
    gates["NO_AUTHORITY_DRIFT"] = (
        registry["authority_effect"] == "NONE"
        and all(a["authority_effect"] == "NONE" and a["automatic_activation"] is False for a in adapters.values())
    )
    gates["NO_ACTIVE_SELECTOR_CHANGE"] = (
        registry["active_selector"]["git_blob_sha"] == EXPECTED_SELECTOR_BLOB
        and registry["active_selector"]["modified"] is False
    )
    gates["NO_RUNTIME_OR_INTEGRATION_EFFECT"] = (
        registry["runtime_effect"] == "NONE"
        and registry["integration_effect"] == "NONE"
        and all(a["runtime_effect"] == "NONE" and a["integration_effect"] == "NONE" for a in adapters.values())
    )
    digest = normalized_digest({"registry": registry, "adapters": adapters})
    return gates, digest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    gates1, digest1 = validate(args.root)
    gates2, digest2 = validate(args.root)
    gates1["SECOND_RUN_EQUIVALENCE"] = digest1 == digest2
    result = {
        "classification": "M2_PASS" if all(gates1.values()) else "M2_BLOCKED_WITH_DOCUMENTED_DIVERGENCES",
        "gates": gates1,
        "normalized_digest_run_1": digest1,
        "normalized_digest_run_2": digest2,
        "deterministic": digest1 == digest2
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if all(gates1.values()) else 1)

if __name__ == "__main__":
    main()
