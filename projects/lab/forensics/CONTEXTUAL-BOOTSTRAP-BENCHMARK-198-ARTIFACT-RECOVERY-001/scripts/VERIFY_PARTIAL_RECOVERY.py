#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, hashlib, json
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "partial-recovery" / "oracle" / "PRIVATE_ORACLE.json.gz.b64"
INDEX = ROOT / "partial-recovery" / "oracle" / "INDEX.json"
EXPECTED_SHA256 = "8fb3cebaf83a27c13852cf64879d4e791a809ab94b4a062e7d38acfed8cc3ad9"
EXPECTED_BYTES = 2033
EXPECTED_GIT_BLOB_SHA = "f4ceb0d1a321240e98a1bdfed9a8cea43e942690"
raw = SOURCE.read_bytes()
assert len(raw) == EXPECTED_BYTES
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
git_blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
assert git_blob == EXPECTED_GIT_BLOB_SHA
parsed = json.loads(gzip.decompress(base64.b64decode(raw)))
index = json.loads(INDEX.read_text(encoding="utf-8"))
assert index["task_count"] == len(parsed["tasks"]) == 21
by_id = {task["id"]: task for task in parsed["tasks"]}
for entry in index["tasks"]:
    path = INDEX.parent / entry["path"]
    data = path.read_bytes()
    assert len(data) == entry["bytes"]
    assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    assert json.loads(data) == by_id[entry["id"]]
print(json.dumps({"result":"PASS","bytes":len(raw),"sha256":EXPECTED_SHA256,"git_blob_sha":git_blob,"tasks":len(by_id)}, indent=2))
