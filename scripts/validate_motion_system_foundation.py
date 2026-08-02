#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'foundation-library/motion-system/MOTION-SYSTEM-001'
errors=[]
required=[BASE/'MANIFEST.json',BASE/'MOTION_EFFECTS_REGISTRY.json',BASE/'taxonomy/MOTION_TAXONOMY.json',BASE/'catalog/MOTION_EFFECTS_CATALOG.html']
for p in required:
    if not p.exists(): errors.append(f'MISSING:{p.relative_to(ROOT)}')
for p in list(BASE.rglob('*.json'))+[ROOT/f'schemas/motion-effect.schema.json',ROOT/f'schemas/motion-taxonomy.schema.json',ROOT/f'schemas/motion-formula-contract.schema.json',ROOT/f'schemas/motion-customization-contract.schema.json',ROOT/f'schemas/motion-test-contract.schema.json',ROOT/f'schemas/motion-source-provenance.schema.json']:
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'INVALID_JSON:{p.relative_to(ROOT)}:{exc}')
for manifest in BASE.glob('effects/*/*/MANIFEST.json'):
    data=json.loads(manifest.read_text())
    if data.get('status') not in {'TECHNICAL_CANDIDATE','HUMAN_REVIEW_PENDING'}: errors.append(f'INVALID_INITIAL_STATUS:{manifest}')
    if data.get('formula_required') and not (manifest.parent/'FORMULA_CONTRACT.json').exists(): errors.append(f'MISSING_FORMULA:{manifest.parent}')
html=(BASE/'catalog/MOTION_EFFECTS_CATALOG.html').read_text(encoding='utf-8') if (BASE/'catalog/MOTION_EFFECTS_CATALOG.html').exists() else ''
for forbidden in ('https://','http://','cdn.','fonts.googleapis.com'):
    if forbidden in html: errors.append(f'EXTERNAL_RESOURCE:{forbidden}')
print(json.dumps({'motion_system_pass':not errors,'errors':errors},indent=2))
sys.exit(1 if errors else 0)
