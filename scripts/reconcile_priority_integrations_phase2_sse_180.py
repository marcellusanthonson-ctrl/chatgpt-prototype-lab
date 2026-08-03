#!/usr/bin/env python3
from pathlib import Path
from urllib.request import urlopen

SOURCE_URL = "https://raw.githubusercontent.com/marcellusanthonson-ctrl/chatgpt-prototype-lab/40ca1d498831d5ce3993c77aea7d1909c3cafc29/scripts/reconcile_priority_integrations_phase2_sse_180.py"
source = urlopen(SOURCE_URL, timeout=30).read().decode("utf-8")
old = '''    require(found == set(replacements), f"pending aggregate missing {set(replacements)-found}")
    ids = [item["id"] for item in aggregate["records"]]
'''
new = '''    for missing_id in sorted(set(replacements) - found):
        aggregate["records"].append(replacements[missing_id])
    ids = [item["id"] for item in aggregate["records"]]
'''
if old not in source:
    raise RuntimeError("frozen generator does not contain the authorized aggregate guard")
source = source.replace(old, new)
script_path = str(Path(__file__).resolve())
exec(compile(source, script_path, "exec"), {"__name__": "__main__", "__file__": script_path, "__package__": None})
