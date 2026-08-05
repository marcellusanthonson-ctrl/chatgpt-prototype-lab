from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARENT = "0ef5f7428cf07652b567cc28321e85bb3b3c7e62"
PREPARED_HEAD = "c1d397c0a37e7c810753a466fd1296202ca6050e"
BRANCH = "agent/product-leadership-test003-fresh-retest-192"
FINAL_RESULT_SQUASH = "4dc5a5c96440fb99c99930cbc76bd2508ac5fc0c"
EXECUTION_ROOT = Path("projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-005")
EXECUTION_ID = "PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-005"
REDESIGN_ROOT = "projects/lab/test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/INSTRUMENT_REDESIGN_191"
HISTORICAL_ROOT = "projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-004"
PACKAGE_ROOT = "foundation-library/product-leadership/PRODUCT-LEADERSHIP-CANDIDATE-PACKAGE-001"
INT_PATH = "projects/lab/integrations/INT-LAB-004.json"
AUTH_PATH = Path("projects/lab/authorizations/AUTHORIZATION_LAB_PRODUCT_LEADERSHIP_TEST003_FRESH_RETEST_192.json")
BRIEF_PATH = Path("projects/lab/briefs/CODEX_PRODUCT_LEADERSHIP_TEST003_FRESH_RETEST_192_001.json")
LIFECYCLE_PATH = Path("projects/lab/authorization-lifecycle/PL003_AUTHORIZATION_LIFECYCLE_192.json")
EVIDENCE_PATH = Path("projects/lab/evidence/EVD-LAB-PL003-FRESH-RETEST-192.json")
DELTA_PATH = Path("registry/deltas/product-leadership-test003-fresh-retest-192.json")
ALLOWED_TERMINAL = "PRODUCT_LEADERSHIP_TEST003_FRESH_RETEST_BLOCKED_BEFORE_MODEL_REQUESTS_RESULT_PUBLISHED_AWAITING_SEPARATE_RECOVERY_OR_REISSUE_AUTHORIZATION"

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def passed(message: str) -> None:
    print(f"PASS: {message}")


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.check_output(["git", *args], cwd=ROOT)
    return result if binary else result.decode("utf-8").strip()


def load_json(relative: Path | str) -> Any:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")

    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key} in {relative}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=no_duplicates)


def changed_paths() -> set[str]:
    tracked = set(filter(None, str(git("diff", "--name-only", PARENT, "--")).splitlines()))
    untracked = set(filter(None, str(git("ls-files", "--others", "--exclude-standard")).splitlines()))
    return {path.replace("\\", "/") for path in tracked | untracked}


def historical_manifest() -> dict[str, Any]:
    raw = git("ls-tree", "-r", "-z", PARENT, HISTORICAL_ROOT, binary=True)
    assert isinstance(raw, bytes)
    rows: list[tuple[str, str, int]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, path_bytes = record.split(b"\t", 1)
        oid = meta.split(b" ")[2].decode("ascii")
        blob = git("cat-file", "blob", oid, binary=True)
        assert isinstance(blob, bytes)
        rows.append((path_bytes.decode("utf-8"), hashlib.sha256(blob).hexdigest(), len(blob)))
    rows.sort()
    payload = "".join(f"{path}\t{digest}\n" for path, digest, _ in rows).encode("utf-8")
    return {"count": len(rows), "bytes": sum(size for _, _, size in rows), "digest": hashlib.sha256(payload).hexdigest()}


def verify_git_state(paths: set[str]) -> None:
    current_branch = git("branch", "--show-current")
    if current_branch not in {BRANCH, ""}:
        fail("wrong working branch")
    if git("merge-base", "HEAD", PARENT) != PARENT:
        fail("branch does not descend from the exact authorized parent")
    if current_branch == BRANCH:
        if subprocess.run(["git", "merge-base", "--is-ancestor", PREPARED_HEAD, "HEAD"], cwd=ROOT).returncode != 0:
            fail("prepared two-commit branch head is not preserved")
    elif subprocess.run(["git", "merge-base", "--is-ancestor", FINAL_RESULT_SQUASH, "HEAD"], cwd=ROOT).returncode != 0:
        fail("detached post-publication finalization does not descend from the verified result squash")
    immutable_prefixes = [HISTORICAL_ROOT + "/", REDESIGN_ROOT + "/", PACKAGE_ROOT + "/"]
    prohibited = [path for path in paths if path == INT_PATH or any(path.startswith(prefix) for prefix in immutable_prefixes)]
    if prohibited:
        fail(f"immutable path changed: {prohibited}")
    expected_objects = {
        HISTORICAL_ROOT: "7bd45ce057ae8362207cc24e7d4cbdad4305d531",
        REDESIGN_ROOT: "cd3a2b8a7d7f62af65bb8cd90b21bfbc99d3f3ab",
        PACKAGE_ROOT: "56aa90d60df30c9ff25efccfd9552b24cc4ae88d",
        INT_PATH: "1643a11e7d627b345be427190472f396987b1885",
    }
    for path, expected in expected_objects.items():
        observed = git("rev-parse", f"{PARENT}:{path}")
        if observed != expected:
            fail(f"immutable parent object mismatch for {path}")
    manifest = historical_manifest()
    if manifest != {"count": 150, "bytes": 1023921, "digest": "e8830433d6a9fdba11c9227669a9155c16a7f58ad8c9ff49a0b93df79d85681c"}:
        fail(f"historical manifest mismatch: {manifest}")
    if not failures:
        passed("branch ancestry and all immutable Git baselines")


def verify_authority() -> None:
    auth = load_json(AUTH_PATH)
    brief = load_json(BRIEF_PATH)
    if auth.get("authorization_id") != "AUTHORIZATION_LAB_PRODUCT_LEADERSHIP_TEST003_FRESH_RETEST_192":
        fail("authorization identity mismatch")
    if auth.get("status") not in {"GRANTED", "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION_OF_TERMINAL_BLOCKED_RESULT"}:
        fail("authorization lifecycle state invalid")
    if auth.get("skill_routing", {}).get("selected_skills") != [] or auth.get("skill_routing", {}).get("cross_repository_access") is not False:
        fail("skill or repository isolation mismatch")
    if brief.get("status") not in {"READY", "EXECUTED_TERMINAL_BLOCKED_RESULT_PUBLICATION_PENDING", "CONSUMED"}:
        fail("brief lifecycle state invalid")
    if auth.get("request_budget", {}).get("maximum_total_model_requests") != 41 or auth.get("request_budget", {}).get("retries") != 0:
        fail("request budget mismatch")
    passed("authorization, skill isolation and request budget")


def verify_artifacts() -> None:
    required = [
        "MANIFEST.json", "EXECUTION_CONFIG.json", "RUN_PLAN.json", "RUN_TEST003_REDESIGNED.mjs",
        "ENVIRONMENT_DECLARATION.json", "MODEL_RUNNER_ATTESTATION.json", "FIXTURE_SET.json", "CONTROL_SET.json",
        "INPUT_FREEZE.json", "CHAIN_OF_CUSTODY_MANIFEST.json", "REQUEST_MANIFEST.jsonl", "EXECUTION_LOG.jsonl",
        "RAW_RESPONSE_MANIFEST.json", "BLINDING_MAP.sealed.json", "SCORING_MANIFEST.json", "CONTROL_GATE_RESULTS.json",
        "AGGREGATE_RESULTS.json", "VALIDATION_RESULTS.json"
    ]
    for name in required:
        if not (ROOT / EXECUTION_ROOT / name).exists():
            fail(f"missing required execution artifact: {name}")
    for path in (ROOT / EXECUTION_ROOT).rglob("*.json"):
        load_json(path.relative_to(ROOT))
    for relative in [Path("schemas/product-leadership-fresh-retest-execution.schema.json")]:
        load_json(relative)
    fixtures = load_json(EXECUTION_ROOT / "FIXTURE_SET.json")
    controls = load_json(EXECUTION_ROOT / "CONTROL_SET.json")
    if fixtures.get("fixture_count") != 8 or len(fixtures.get("fixtures", [])) != 8:
        fail("fixture cardinality is not exactly eight")
    required_context = {"TASK_OBJECTIVE", "TASK_STATE", "AUTHORITY_STATE", "BINDING_OBLIGATIONS", "AVAILABLE_EVIDENCE", "PRODUCT_DECISION_SCOPE", "REQUESTED_OUTPUT"}
    for fixture in fixtures.get("fixtures", []):
        if set(fixture.get("context", {})) != required_context:
            fail(f"fixture context incomplete: {fixture.get('fixture_id')}")
    if controls.get("positive_control_count") != 4 or controls.get("negative_control_count") != 4 or len(controls.get("controls", [])) != 4:
        fail("control cardinality mismatch")
    adapter = (ROOT / EXECUTION_ROOT / "RUN_TEST003_REDESIGNED.mjs").read_text(encoding="utf-8")
    if "INSTRUMENT_CORE.mjs" not in adapter or "RUN_TEST003.mjs" in adapter or "openai" in adapter.lower():
        fail("adapter is not strictly subordinate to the canonical core")
    passed("execution artifacts, fixtures, controls and subordinate adapter")


def verify_terminal_block() -> None:
    manifest = load_json(EXECUTION_ROOT / "MANIFEST.json")
    runner = load_json(EXECUTION_ROOT / "MODEL_RUNNER_ATTESTATION.json")
    custody = load_json(EXECUTION_ROOT / "CHAIN_OF_CUSTODY_MANIFEST.json")
    aggregate = load_json(EXECUTION_ROOT / "AGGREGATE_RESULTS.json")
    raw = load_json(EXECUTION_ROOT / "RAW_RESPONSE_MANIFEST.json")
    scoring = load_json(EXECUTION_ROOT / "SCORING_MANIFEST.json")
    if manifest.get("terminal_status") != ALLOWED_TERMINAL:
        fail("terminal response status is outside brief")
    if aggregate.get("execution_outcome") != "BLOCKED_BEFORE_MODEL_REQUESTS" or aggregate.get("numeric_aggregation_performed") is not False:
        fail("terminal blocked outcome invalid")
    counts = aggregate.get("request_counts", {})
    if any(counts.get(key) != 0 for key in ["smoke", "generation_baseline", "generation_package", "control_scoring", "experimental_scoring", "total"]):
        fail("nonzero model request count in blocked attempt")
    if aggregate.get("retries") != 0 or raw.get("raw_response_count") != 0 or scoring.get("total_scores") != 0:
        fail("blocked attempt contains responses, scores or retries")
    request_manifest = (ROOT / EXECUTION_ROOT / "REQUEST_MANIFEST.jsonl").read_bytes()
    if request_manifest not in {b"", b"\n"}:
        fail("request manifest must be empty")
    if runner.get("runner", {}).get("version_result") != "PASS" or runner.get("runner", {}).get("sha256_result") != "PASS":
        fail("runner binary identity did not pass")
    if runner.get("authentication", {}).get("result") != "FAIL_NOT_LOGGED_IN" or runner.get("authentication", {}).get("login_attempted") is not False:
        fail("authentication failure attestation invalid")
    entries = custody.get("entries", [])
    if custody.get("verification_result") != "FAIL" or custody.get("instrument_mismatch_count") != 13 or len(entries) != 13 or any(entry.get("match") is not False for entry in entries):
        fail("custody failure evidence incomplete")
    passed("truthful terminal block, zero requests, zero retries and custody failure")


def verify_custody_reproduction() -> None:
    custody = load_json(EXECUTION_ROOT / "CHAIN_OF_CUSTODY_MANIFEST.json")
    observed: dict[str, tuple[str, str, int, int, bool]] = {}
    for entry in custody.get("entries", []):
        path = entry["path"]
        git_bytes = git("show", f"HEAD:{path}", binary=True)
        assert isinstance(git_bytes, bytes)
        worktree_bytes = (ROOT / path).read_bytes()
        row = (hashlib.sha256(git_bytes).hexdigest(), hashlib.sha256(worktree_bytes).hexdigest(), len(git_bytes), len(worktree_bytes), git_bytes == worktree_bytes)
        observed[path] = row
        expected = (entry["git_sha256"], entry["worktree_sha256"], entry["git_bytes"], entry["worktree_bytes"], entry["match"])
        if row != expected:
            fail(f"custody evidence does not reproduce: {path}")
    if len(observed) == 13 and not failures:
        passed("13-of-13 raw-byte custody mismatches independently reproduced")


def verify_no_disallowed_content() -> None:
    neutral_files = [EXECUTION_ROOT / "FIXTURE_SET.json", EXECUTION_ROOT / "CONTROL_SET.json", EXECUTION_ROOT / "templates/GENERATION_REQUEST_TEMPLATE.json", EXECUTION_ROOT / "templates/SCORING_REQUEST_TEMPLATE.json"]
    forbidden = ["carolina", "clinical os", "real user", "real product"]
    for relative in neutral_files:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token in text:
                fail(f"non-neutral material in {relative}: {token}")
    passed("neutral synthetic materials and no cross-repository content")


def verify_stage_6_records() -> None:
    lifecycle = load_json(LIFECYCLE_PATH)
    evidence = load_json(EVIDENCE_PATH)
    delta = load_json(DELTA_PATH)
    pending = load_json("projects/lab/pending/PEND-LAB-048.json")
    aggregate_pending = load_json("projects/lab/PENDING.json")
    execution_index = load_json("projects/lab/test-executions/index.json")
    registry_index = load_json("registry/index.json")
    continuity = load_json("projects/lab/continuity/CURRENT_CONTINUITY.json")
    archive = load_json("projects/lab/continuity/archive/LAB-CONTINUITY-PRE-FRESH-RETEST-192-20260805.pointer.json")
    if lifecycle.get("execution_outcome") != "BLOCKED_BEFORE_MODEL_REQUESTS" or lifecycle.get("request_counts", {}).get("total") != 0:
        fail("authorization lifecycle does not preserve the terminal blocked result")
    if lifecycle.get("residual_authority") != "NONE" or lifecycle.get("publication", {}).get("squash_commit") != FINAL_RESULT_SQUASH:
        fail("authorization lifecycle is not consumed against the verified result squash")
    if evidence.get("execution", {}).get("outcome") != "BLOCKED_BEFORE_MODEL_REQUESTS" or evidence.get("execution", {}).get("model_requests") != 0:
        fail("evidence does not preserve the terminal blocked result")
    if evidence.get("publication", {}).get("verified_remote_main") is not True:
        fail("evidence does not record verified remote result publication")
    if delta.get("registry_counts_before") != {"authorizations": 106, "evidence": 88, "test_executions": 5}:
        fail("registry delta before-counts mismatch")
    if delta.get("registry_counts_after") != {"authorizations": 107, "evidence": 89, "test_executions": 6}:
        fail("registry delta after-counts mismatch")
    expected_pending = "OPEN_FRESH_RETEST_ATTEMPT_004_BLOCKED_BEFORE_MODEL_REQUESTS_AWAITING_SEPARATE_RECOVERY_OR_REISSUE_AUTHORIZATION"
    if pending.get("status") != expected_pending:
        fail("canonical PEND-LAB-048 status mismatch")
    aggregate_records = [record for record in aggregate_pending.get("records", []) if record.get("id") == "PEND-LAB-048"]
    if len(aggregate_records) != 1 or aggregate_records[0].get("status") != expected_pending:
        fail("aggregate PEND-LAB-048 status mismatch or duplicate")
    execution_records = [record for record in execution_index.get("records", []) if record.get("id") == EXECUTION_ID]
    if len(execution_records) != 1 or execution_records[0].get("model_requests") != 0:
        fail("execution index record missing, duplicate or nonzero")
    counts = registry_index.get("counts", {})
    if any(counts.get(key) != value for key, value in {"authorizations": 107, "evidence": 89, "test_executions": 6}.items()):
        fail("registry counts mismatch")
    delta_ref = str(DELTA_PATH).replace("\\", "/")
    registries = registry_index.get("registries", {})
    for name in ["authorization_deltas", "evidence_deltas", "current_state_deltas"]:
        if registries.get(name, []).count(delta_ref) != 1:
            fail(f"registry delta reference count mismatch in {name}")
    if continuity.get("product_leadership", {}).get("fresh_retest", {}).get("model_requests") != 0:
        fail("continuity model request count mismatch")
    expected_archive = {
        "projects/lab/continuity/CURRENT_CONTINUITY.json": ("25b671cbb0c9cb480d01889f2b9974548b1b3a7a", "c5bcb48470b0a4771426846c52386c29773ea1a89734bef5cc7c40970dea1f6f", 5457),
        "projects/lab/continuity/CURRENT_CONTINUITY.md": ("6461bd59f8ff727adc9c2b164d327a3328f48881", "422015c227e08e6a1d5460e6177dcae89c232b74dab7ed2b3f5312d6b6ac4914", 2121),
        "projects/lab/continuity/ATTACHMENT_MANIFEST.json": ("69390cdcbe400c4377df4da5a3350dfb1464ddcf", "b27ceebbbf470ab7b97a971c574427af5f8611eba230eb51c087adea3f4d57f1", 2645),
        "projects/lab/continuity/START_PROMPT.md": ("00f450c268d832226431fdfc5a290023cbda152d", "7860c5305de77dde433f4ad94cae4795817cac79496ba7682bc4da6ba6774a95", 1203),
    }
    observed_archive = {entry["path"]: (entry["git_blob_sha1"], entry["sha256"], entry["bytes"]) for entry in archive.get("files", [])}
    if observed_archive != expected_archive:
        fail("continuity archive pointer mismatch")
    passed("Stage 6 evidence, lifecycle, delta, indexes, pending and continuity")


def main() -> int:
    try:
        paths = changed_paths()
        verify_git_state(paths)
        verify_authority()
        verify_artifacts()
        verify_terminal_block()
        verify_custody_reproduction()
        verify_no_disallowed_content()
        verify_stage_6_records()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        fail(f"validator exception: {exc}")
    if failures:
        print(f"Product Leadership fresh retest 192 blocked-result validation: FAIL ({len(failures)} failure(s))")
        return 1
    print("Product Leadership fresh retest 192 blocked-result validation: PASS")
    print(f"Changed files inspected: {len(paths)}")
    print("Model requests: 0; retries: 0; outputs: 0; scores: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
