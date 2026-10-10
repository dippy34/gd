"""Package the dark revision after native and scripted checks."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'
STEM='v8-1573528-nocturne'
source=OUT/f'{STEM}.gmd'
validation=json.loads((OUT/f'{STEM}-validation.json').read_text())
digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest==validation['sha256']
assert all(not r['errors'] for r in validation['route_checks']+validation['independent_replay'])
for name,suffix in [('nocturne-review-sheet.png','preview'),('nocturne-rest-sheet.png','more-views'),
                    ('nocturne-native-switches.jpg','native-switches'),
                    ('nocturne-native-spider.jpg','native-spider'),('nocturne-native-wave.jpg','native-wave')]:
 shutil.copy2(ROOT/'work/previews'/name,OUT/f'{STEM}-{suffix}{Path(name).suffix}')

notes=f'''# v8 — darker false routes and eased wave

[Final .gmd]({STEM}.gmd) · [Preview]({STEM}-preview.png) · [More rooms]({STEM}-more-views.png) · [Validation]({STEM}-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× speed for **85.71%** of the timeline. **34,010 objects**. All seven requested modes, excluding swing.

## This revision

**Wave:** Added 5.5 world units of clearance on each side of the reference path, widening the openings by 11 units. This applies to both waves' ducts, knife gates, floating barriers and phrase boundaries. Their input timings, speed portals, gravity changes and mini/normal transitions remain the same.

**Spider:** Restored the older spider's rows of framed landing shelves, with multiple false shelves at different heights and apparent openings cut across still-solid banks. Real and false shelves share the same dim frame treatment. False rails terminate at actual pillars so the linework follows the structures. Both spider sections retain their existing collision geometry and timings.

**Fakeouts:** There are 244 false teleport shelf segments, 136 false landing rails and 597 apparent openings in solid banks across the level. The two spider rooms contain 385 of these individual visual decoys. False shelf artwork is non-colliding; a false opening masks a bank whose original collision remains active. These visual choices replace the previous sparse, small recesses.

**Darkness and switches:** The background is black. Structural fills use RGB (5, 6, 5); contact edges use (12, 14, 10). The white randomized-orb artwork is hidden and replaced with small, dim olive switch plates, without glow, particles or pulses. Their brightest channel is (26, 29, 20). Ordinary colored gameplay orbs and mode/size/gravity portals retain their native designs.

The 34 independent random decisions keep the same rule: **wall present → hit the switch; wall absent → skip it.** A wrong hit creates the wall. The native input objects, Claim Touch setting, groups and random trigger branches remain intact. The relevant native properties were checked against [FlowVix's schema](https://github.com/FlowVix/gd-info-explorer/blob/main/src/lib/schema.txt); the [official editor guide](https://www.robtopgames.com/files/GDEditor.pdf) documents trigger-orb and group behavior.

## Checks

- Imported the final .gmd into GD with **34,010 objects**; native object counts and the new palette match the export.
- Inspected the [dim switches during native play]({STEM}-native-switches.jpg), the [first spider room]({STEM}-native-spider.jpg), and the [second wave]({STEM}-native-wave.jpg). The opening preview used the existing Ignore Damage setting. The bright magenta squares and controls at the upper left belong to the installed preview interface.
- Inspected 20 atlas-based camera views spanning all 15 rooms.
- All **49,408 route samples** pass; independent approximate replay passes all **15 rooms**.
- Verified all non-wave collision objects and the complete input score against the preceding branching export. Verified the 11-unit increase at each wave gate.
- All 34 switch circuits pass both starting-state cases. Native import preserves hidden-orb, Claim Touch and non-colliding switch-art properties.

**A full damage-enabled native completion and exact demon difficulty remain unverified.** The physics model approximates triangle collisions, portal offsets and buffering. The darker presentation and extra false routes still need player feedback for final balance.

Earlier exports remain intact. Rebuild details are in `work/CURRENT.md`.

SHA-256: `{digest}`
'''
(OUT/f'{STEM}-notes.md').write_text(notes)

(ROOT/'work/CURRENT.md').write_text('''# Current exported level

Latest: `outputs/v8-1573528-nocturne.gmd`, internal name **v8**. Read `outputs/v8-1573528-nocturne-notes.md` and its validation JSON before editing. This revision darkens the branching build, restores layered spider fakeouts and adds 5.5 units of clearance on each side of both wave paths.

Raw: `work/v8-nocturne.level`. Plan: `work/nocturne-plan.json`. Native snapshot: `work/nocturne-native-import.level`. Preserve earlier exports and `work/revision-before-nocturne/`.

The current file has 34,010 objects, 34 random wall decisions, 977 individual visual decoy features, and the unchanged 550-input reference score. Song 1573528; duration 205.192 seconds; native 0.5 speed covers 85.714% of the timeline. Normal portal is 99; mini is 101. Keep the camera resets, native speed portals and all seven modes except swing.

Native 1594 switch input objects are hidden with 135 and retain Claim Touch 445, No Glow 96 and No Particle 507. Eight pieces of non-colliding dark artwork follow each active-orb group. Do not remove the hidden inputs or merge the mutually exclusive visible groups. The 34 wall decisions are unchanged from branching.

## Build

Run sequentially from the workspace root:

```sh
rtk proxy python3 work/nocturne_layout.py
rtk proxy env GD_SKIN_SOURCE=work/nocturne-base.gmd GD_SKIN_TARGET=work/nocturne-skinned.gmd GD_SKIN_PLAN=work/nocturne-plan.json GD_SKIN_RAW=work/v8-nocturne-base.level GD_SKIN_OUTPUT_RAW=work/v8-nocturne-skinned.level GD_SKIN_AUDIT=work/nocturne-skin-audit.json python3 work/clean_visuals.py
rtk proxy python3 work/nocturne_fakeouts.py
rtk proxy python3 work/check_nocturne_route.py
rtk proxy python3 work/replay_nocturne.py
```

Import the new file through the native bridge and refresh `work/nocturne-native-import.level`, then run `rtk proxy python3 work/audit_nocturne.py`. Its native visual-review entries describe the inspected current screenshots; refresh those observations after further edits.

Use `GD_PREVIEW_LEVEL=work/v8-nocturne.level` and `GD_PREVIEW_PLAN=work/nocturne-plan.json` with `work/preview_memory.py`. Current inspected camera positions are in `nocturne-review-*` and `nocturne-rest-*` under `work/previews`. Package with `rtk proxy python3 work/package_nocturne.py` after the audit and visual review.

The new generator imports `branching_layout.py`, which imports `memory_layout.py`; neither older generator's default export is the current level. `clean_visuals.py` also defaults to an older export unless the environment arguments above are provided.

Full native completion and exact demon difficulty remain unverified. Native artwork and import were inspected; all room replays pass an approximate physics model.
''')

destination=(Path(__file__).resolve().parents[1]/'build/exports')/source.name
assert destination.parent.is_dir()
if destination.exists():
 assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest, 'Preserve different existing export.'
else:shutil.copy2(source,destination)
assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest
print(json.dumps(dict(file=str(destination),sha256=digest,bytes=destination.stat().st_size,notes=str(OUT/f'{STEM}-notes.md')),indent=2))
