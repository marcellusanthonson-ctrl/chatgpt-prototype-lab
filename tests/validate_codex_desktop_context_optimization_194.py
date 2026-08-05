#!/usr/bin/env python3
"""Static validator for authorization 194 artifacts."""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _reject_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate key: {key}")
        out[key] = value
    return out


def load(path: str):
    with (ROOT / path).open("r", encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=_reject_duplicates)


def fail(message: str):
    raise AssertionError(message)


def metrics(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    return {
        "non_empty_lines": sum(1 for line in text.splitlines() if line.strip()),
        "utf8_bytes": len(text.encode("utf-8")),
        "estimated_tokens": math.ceil(len(text) / 4),
    }


def main() -> int:
    manifest = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/MANIFEST.json")
    budgets = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/CONTEXT_BUDGETS.json")
    routing = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/ROUTING_POLICY.json")
    loading = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/CONTEXT_LOADING_POLICY.json")
    parallel = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/PARALLELISM_POLICY.json")
    auth = load("projects/lab/authorizations/AUTHORIZATION_LAB_CODEX_DESKTOP_CONTEXT_AND_MULTI_AGENT_OPTIMIZATION_194.json")
    change = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/CHANGE_MANIFEST.json")

    expected_profiles = {"LAB_DISCOVERY", "LAB_IMPLEMENTATION", "LAB_VALIDATION", "LAB_AUDIT"}
    if set(manifest["profiles"]) != expected_profiles:
        fail("profile set mismatch")
    for profile_id in expected_profiles:
        profile = load(f"architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/profiles/{profile_id}.json")
        if profile["profile_id"] != profile_id:
            fail(f"profile id mismatch: {profile_id}")
        if profile["authority_effect"] != "NONE_ROLE_PROFILE_DOES_NOT_AUTHORIZE_EXECUTION":
            fail(f"profile creates authority: {profile_id}")
        if profile.get("private_chain_of_thought") != "NOT_REQUIRED_NOT_RECORDED":
            fail(f"private reasoning contract missing: {profile_id}")

    agents_path = ROOT / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8")
    agents_metrics = metrics(agents_path)
    root_budget = budgets["artifacts"]["ROOT_AGENTS_MD"]
    if agents_metrics["non_empty_lines"] > root_budget["max_non_empty_lines"]:
        fail("AGENTS.md line budget exceeded")
    if agents_metrics["utf8_bytes"] > root_budget["max_utf8_bytes"]:
        fail("AGENTS.md byte budget exceeded")
    if agents_metrics["estimated_tokens"] > root_budget["max_estimated_tokens"]:
        fail("AGENTS.md token estimate budget exceeded")
    for pattern in [r"\b[0-9a-f]{40}\b", "AUTHORIZATION_STATUS", "CURRENT_CONTINUITY", "PEND-LAB-", "current HEAD:"]:
        if re.search(pattern, agents_text, flags=re.IGNORECASE):
            fail(f"dynamic content in root AGENTS.md: {pattern}")

    if {r["class"] for r in routing["routes"]} != {"SMALL_CLEAR", "MEDIUM", "UNCERTAIN", "CRITICAL"}:
        fail("routing classes incomplete")
    required_policies = {"ALWAYS", "REQUIRED", "FILTERED", "ON_TRIGGER", "AUDIT_ONLY", "HISTORICAL_REFERENCE", "FORBIDDEN"}
    if set(loading["load_policies"]) != required_policies:
        fail("context loading policies incomplete")
    if "COMMIT_PUSH_PULL_REQUEST_MERGE_AND_AUTHORIZATION_CONSUMPTION" not in parallel["must_be_sequential"]:
        fail("publication is not serialized")

    if auth["authority"]["model_requests"] is not False:
        fail("model requests unexpectedly authorized")
    for key in ("codex_login_or_credentials", "skill_creation_installation_or_selection", "sdk_or_runtime_orchestration", "product_or_integration_change", "external_repository_access"):
        if auth["authority"][key] is not False:
            fail(f"forbidden authority enabled: {key}")

    if change["protected_path_changes"]:
        fail("protected Product Leadership path changed")
    if any(change[key] != 0 for key in ("model_requests", "login_actions", "skills_or_sdk_actions", "external_repository_accesses")):
        fail("nonzero forbidden execution count")

    measurement = load("architecture/governance/CODEX_DESKTOP_CONTEXT_OPTIMIZATION_001/MEASUREMENT_PROTOCOL.json")
    if "STATIC_STANDARD_PASS_DOES_NOT_PROVE_RUNTIME_SPEEDUP" not in measurement["claim_limits"]:
        fail("unmeasured speed claim guard missing")
    for required_path in change["changed_paths"]:
        if not (ROOT / required_path).exists():
            fail(f"missing changed path: {required_path}")

    print(json.dumps({"status": "PASS_CODEX_DESKTOP_CONTEXT_OPTIMIZATION_194", "files": len(change["changed_paths"]), "profiles": sorted(expected_profiles), "root_agents_metrics": agents_metrics, "benchmark": "NOT_RUN"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
