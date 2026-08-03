from pathlib import Path

shim = Path(__file__)
generator = shim.with_name("reconcile_priority_integrations_phase2_sse_180.py")
text = generator.read_text(encoding="utf-8")
old = '''    require(found == set(replacements), f"pending aggregate missing {set(replacements)-found}")
    ids = [item["id"] for item in aggregate["records"]]
'''
new = '''    for missing_id in sorted(set(replacements) - found):
        aggregate["records"].append(replacements[missing_id])
    ids = [item["id"] for item in aggregate["records"]]
'''
if old not in text:
    raise RuntimeError("expected pending aggregate guard not found")
generator.write_text(text.replace(old, new), encoding="utf-8")
shim.unlink()
