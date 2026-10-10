"""Package the targeted v8 revision and its bounded validation evidence."""
from pathlib import Path
from collections import Counter
import json, hashlib, csv, shutil, sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'work/handoff/tools'))
from gmd import read_gmd, decompress

stem = 'v8-1573528-refined'
level = ROOT / f'outputs/{stem}.gmd'
p = json.loads((ROOT / 'work/memory-plan.json').read_text())
v = json.loads((ROOT / f'outputs/{stem}-validation.json').read_text())
a = json.loads((ROOT / 'work/refined-audit.json').read_text())
r = json.loads((ROOT / 'work/memory-replay.json').read_text())
c = json.loads((ROOT / 'work/camera-native-measurements.json').read_text())
assert v['rooms_with_nominal_overlaps'] == 0 and not any(z['errors'] for z in r)
assert not a['native_size_state']['mismatched_samples'] and len(a['nonship_preservation']) == 13
assert v['sha256'] == a['sha256'] == hashlib.sha256(level.read_bytes()).hexdigest()

def objects(raw):
    out = []
    for token in raw.split(';')[1:]:
        if token:
            q = token.split(',')
            out.append(dict(zip(q[::2], q[1::2])))
    return out

exported = objects(decompress(read_gmd(level)['k4'][1]))
native = objects((ROOT / 'work/refined-native-import.level').read_text())
assert len(exported) == len(native) == p['objects']
assert Counter(o['1'] for o in exported) == Counter(o['1'] for o in native)
for oid in ('99', '101', '1914', '1913', '2925'):
    orig = sorted((o for o in exported if o['1'] == oid), key=lambda o:float(o['2']))
    live = sorted((o for o in native if o['1'] == oid), key=lambda o:float(o['2']))
    for left, right in zip(orig, live):
        assert abs(float(left['2']) - float(right['2'])) < .055
        assert abs(float(left['3']) - float(right['3'])) < .012
        for key in {'99':[], '101':[], '1914':['71','101','36'], '1913':['371'], '2925':['111']}[oid]:
            assert float(left[key]) == float(right[key]), (oid, key, left, right)

v.update(regressions=a, independent_model_replay=r,
         native_validation=dict(imported=True, imported_objects=len(native),
             object_id_counts_match=True, size_portals_and_camera_settings_survive_import=True,
             opening_visually_inspected=True,
             camera_probe=dict(modes_inspected=['cube','ship','wave'],
                  refreshed_ship_and_wave_reference_rows_match=True, measurements=c),
             full_completion_verified=False, difficulty_verified=False,
             note='Native visual inspection used the existing Ignore Damage editor setting. It is not completion verification.'))
(ROOT / f'outputs/{stem}-validation.json').write_text(json.dumps(v, indent=2))
shutil.copy2(ROOT / 'work/previews/final-refined-sheet.png', ROOT / f'outputs/{stem}-preview.png')
with (ROOT / f'outputs/{stem}-inputs.csv').open('w') as fh:
    w = csv.DictWriter(fh, fieldnames=['time','x','mode','kind','hold','down','orb_id','gravity','target','symbol','activate'], extrasaction='ignore')
    w.writeheader()
    w.writerows(p['controls'])

notes = f'''# v8 — size, camera, ship and structure fixes

[Final .gmd]({stem}.gmd) · [Native opening screenshot]({stem}-native-preview.png) · [Section previews]({stem}-preview.png) · [Validation]({stem}-validation.json)

This revises the existing accepted level. The internal name remains **v8**, with song **1573528**, a **3:25.19** duration, seven modes excluding swing, and native 0.5× speed for **85.71%** of the level. Previous .gmd files are preserved.

- **Preserved gameplay:** all thirteen non-ship sections keep the same gameplay objects and input timings, with size portals corrected separately. This includes the opening cube, orb arrangements, memory decisions, speed schedule and section order.
- **Fixed size state:** the earlier generator reversed normal-size portal 99 and mini portal 101; its checker repeated the same error. Both are corrected. Wave exits and room transitions explicitly restore normal size. The second wave now follows normal → mini → normal → mini → normal, matching its intended wave slopes.
- **Harder ships:** PARALLAX and UNDERTOW now use different continuous, spike-lined flight contours, replacing broad galleries and bypassable floating dividers. Their wall shapes demand controlled climbs, dives and height changes. This is a geometric difficulty increase; the exact demon rating remains unverified.
- **Camera correction:** free-camera, zoom and vertical lock are refreshed after each mode entry. The separate native probe reproduced a 67.5-pixel vertical shift at ship entry, then confirmed matching reference positions in ship and wave after the correction. The entire y = 0–300 playfield fits in the tested view. The final opening was also inspected in Geometry Dash.
- **Purposeful structures:** suspended platforms have columns or ceiling supports; precision caps form piston heads; rail and spider shelves sit inside connected housings; the second wave's blades share continuous backing and lane-change supports. False routes retain the same visual construction as real routes. Small service plates move inside wall recesses. Existing collision faces remain aligned with their visible skins.

The empty level shown during testing was **v8 CAMERA TEST**, a separate diagnostic copy. It is not the final artifact.

## Checks

- Native import succeeded with **{p['objects']:,} objects**. The native snapshot matches all exported object ID counts, size portals and camera settings.
- A continuous size-state trace passes **{len(p['paths']):,} route samples** and all **36 required orb inputs**. The same check rejects the earlier file's size-state bug.
- Serialized second-wave portal order is checked independently of the generator constants.
- Approximate input replay and finite-body geometry checks pass all fifteen rooms, with no nominal block/spike overlaps.
- All **{v['spike_count']:,} spikes** lie within the designed playfield. All forty memory choices still affect real gates.
- The first cube and the other twelve non-ship gameplay scores match the previous version.

**Full native completion and an Insane/Extreme difficulty rating are not verified.** Ship/UFO/ball dynamics and exact portal contact offsets remain approximate in the replay model. Native visual checks used the existing Ignore Damage setting.

## Research used for the corrections

- [G.js native object constants](https://github.com/g-js-api/G.js/blob/main/src/constants.ts): normal and mini portal IDs.
- [G.js camera implementation](https://github.com/g-js-api/G.js/blob/main/src/lib/general-purpose.ts): free camera, static vertical targets and zoom properties.
- [GD player-physics reference](https://boomlings.dev/reference/player_physics/gamemodes): mode behaviour and the limits of documented ship physics.
- [Earlier song and memory research](v8-1573528-memory-notes.md).

SHA-256: `{v['sha256']}`
'''
(ROOT / f'outputs/{stem}-notes.md').write_text(notes)
print(json.dumps(dict(file=str(level), bytes=level.stat().st_size, objects=p['objects'],
                      imported=True, native_completion_verified=False), indent=2))
