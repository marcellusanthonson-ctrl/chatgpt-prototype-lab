#!/usr/bin/env python3
"""Fail-closed executable for the authorization-160 pre-activation drill."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "e60cfe4b90b58a2e54c4ddfe671267afc2a1bcaa"
STATIC = ROOT / "project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/MODULE_SELECTOR.json"
CANDIDATE = ROOT / "architecture/integrations/migration/M2/SHADOW_INTEGRATION_REGISTRY.json"
POINTER = ROOT / "architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json"
EXPECTED_STATIC_BLOB = "301ba432907758fc49a9b3c86a83fc762eac4607"
EXPECTED_CANDIDATE_BLOB = "a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78"


def run(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def git_blob(path: Path) -> str:
    return str(run(["git", "hash-object", str(path.relative_to(ROOT))])["stdout"])


def check() -> dict[str, object]:
    head = run(["git", "rev-parse", "refs/remotes/origin/main"])
    checks = [
        run([sys.executable, "-B", "scripts/validate_integration_factory_m3_remediation_158.py", "--check"]),
        run([sys.executable, "-B", "scripts/validate_integration_factory_m5_readiness_161.py", "--check"]),
    ]
    passed = (
        head["stdout"] == EXPECTED_HEAD
        and git_blob(STATIC) == EXPECTED_STATIC_BLOB
        and git_blob(CANDIDATE) == EXPECTED_CANDIDATE_BLOB
        and not POINTER.exists()
        and all(item["exit_code"] == 0 for item in checks)
    )
    return {
        "classification": "PASS" if passed else "FAIL_CLOSED_NO_CUTOVER",
        "verified_remote_head": head["stdout"],
        "static_blob": git_blob(STATIC),
        "candidate_blob": git_blob(CANDIDATE),
        "pointer_exists": POINTER.exists(),
        "validators": checks,
        "fingerprint": hashlib.sha256(json.dumps(checks, sort_keys=True).encode()).hexdigest(),
    }


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["classification"] == "PASS" else 1)
