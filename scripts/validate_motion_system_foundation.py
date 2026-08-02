#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'foundation-library/motion-system/MOTION-SYSTEM-001'
errors=[]
required=[BASE/'MANIFEST.json',BASE/'MOTION_EFFECTS_REGISTRY.json',BASE/'taxonomy/MOTION_TAXONOMY.json',BASE/'catalog/MOTION_EFFECTS_CATALOG.html']
for p in required:
    if not p.exists(): errors.append(f'MISSING:{p.relative_to(ROOT)}')
schemas=['motion-effect','motion-taxonomy','motion-formula-contract','motion-customization-contract','motion-test-contract','motion-source-provenance','motion-source-fidelity-contract','motion-visual-anatomy-contract','motion-geometry-invariants']
for p in list(BASE.rglob('*.json'))+[ROOT/f'schemas/{name}.schema.json' for name in schemas]:
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'INVALID_JSON:{p.relative_to(ROOT)}:{exc}')
for manifest in BASE.glob('effects/*/*/MANIFEST.json'):
    data=json.loads(manifest.read_text())
    if data.get('status') not in {'TECHNICAL_CANDIDATE','HUMAN_REVIEW_PENDING'}: errors.append(f'INVALID_INITIAL_STATUS:{manifest}')
    if data.get('formula_required') and not (manifest.parent/'FORMULA_CONTRACT.json').exists(): errors.append(f'MISSING_FORMULA:{manifest.parent}')
CANDIDATE=BASE/'source-fidelity-candidates/CAROLINA-ROADMAP-SOURCE-FAITHFUL-001'
candidate_required=['MANIFEST.json','REFERENCE_IMPLEMENTATION.html','SOURCE_FILE_INVENTORY.json','SOURCE_PROVENANCE.json','SOURCE_FIDELITY_CONTRACT.json','VISUAL_ANATOMY_CONTRACT.json','GEOMETRY_INVARIANTS.json','RESPONSIVE_CONTRACT.json','MOTION_STATE_CONTRACT.json','FORMULA_CONTRACT.json','COMPUTED_STYLE_BASELINE.json','SOURCE_RENDER_BASELINE.json','CANDIDATE_RENDER_RESULTS.json','COMPARISON_METRICS.json','COMPARISON_REPORT.md','HUMAN_COMPARISON.html']
for name in candidate_required:
    if not (CANDIDATE/name).exists(): errors.append(f'MISSING_SOURCE_FIDELITY_ARTIFACT:{name}')
metrics=json.loads((CANDIDATE/'COMPARISON_METRICS.json').read_text(encoding='utf-8'))
if metrics.get('status')!='PASS_AUTOMATED_GATES_HUMAN_REVIEW_PENDING': errors.append('SOURCE_FIDELITY_AUTOMATED_GATE_FAILED')
if metrics.get('minimum_observed_ssim',0)<.995: errors.append('SOURCE_FIDELITY_THRESHOLD_FAILED')
for field in ('computed_style_mismatch_count','geometry_mismatch_count','candidate_external_request_count'):
    if metrics.get(field)!=0: errors.append(f'NONZERO_{field.upper()}')
manifest=json.loads((CANDIDATE/'MANIFEST.json').read_text(encoding='utf-8'))
if manifest.get('status')!='HUMAN_REVIEW_PENDING' or manifest.get('canonical_replacement') or manifest.get('reusable_promotion') or manifest.get('human_approval'): errors.append('CANDIDATE_AUTHORITY_BOUNDARY_FAILED')
axis_max=concentricity_max=0.0
for path in (CANDIDATE/'evidence/geometry').glob('*.json'):
    payload=json.loads(path.read_text(encoding='utf-8'))
    for side in ('source','candidate'):
        geometry=payload[side]
        center=lambda r:(r['x']+r['width']/2,r['y']+r['height']/2)
        rail_x=center(geometry['BASE_RAIL'][0])[0]
        aligned=geometry['ACTIVE_RAIL']+geometry['INTERMEDIATE_NODES']+geometry['TERMINAL_CAP']+geometry['NODE_OUTER_HALO']+geometry['NODE_RING']
        axis_max=max(axis_max,*[abs(rail_x-center(item)[0]) for item in aligned])
        for halo,ring,core in zip(geometry['NODE_OUTER_HALO'],geometry['NODE_RING'],geometry['NODE_CORE']):
            hx,hy=center(halo);rx,ry=center(ring);cx,cy=center(core)
            concentricity_max=max(concentricity_max,abs(hx-cx),abs(hy-cy),abs(rx-cx),abs(ry-cy))
if axis_max>.25: errors.append(f'AXIS_INVARIANT_FAILED:{axis_max}')
if concentricity_max>.25: errors.append(f'NODE_CONCENTRICITY_FAILED:{concentricity_max}')
html=(BASE/'catalog/MOTION_EFFECTS_CATALOG.html').read_text(encoding='utf-8') if (BASE/'catalog/MOTION_EFFECTS_CATALOG.html').exists() else ''
for forbidden in ('https://','http://','cdn.','fonts.googleapis.com'):
    if forbidden in html: errors.append(f'EXTERNAL_RESOURCE:{forbidden}')
print(json.dumps({'motion_system_pass':not errors,'errors':errors,'source_fidelity':{'minimum_ssim':metrics.get('minimum_observed_ssim'),'axis_max_css_px':axis_max,'concentricity_max_css_px':concentricity_max}},indent=2))
sys.exit(1 if errors else 0)
