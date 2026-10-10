"""Package the audited branching revision without changing its level data."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'outputs'
STEM = 'v8-1573528-branching'
level = OUT / f'{STEM}.gmd'
validation_path = OUT / f'{STEM}-validation.json'
validation = json.loads(validation_path.read_text())
digest = hashlib.sha256(level.read_bytes()).hexdigest()
assert digest == validation['sha256']
assert all(not r['errors'] for r in validation['route_checks'])
assert all(not r['errors'] for r in validation['independent_replay'])
assert all(r['both_branches_correct'] for r in validation['random_checks'])

previews = {
    'branching-final-sheet.png': 'preview',
    'branching-native-attempt-2.png': 'native-wall-present',
    'branching-native-attempt-3.png': 'native-wall-absent',
    'branching-native-ship.png': 'native-ship',
    'branching-native-wave.png': 'native-wave',
}
for source, suffix in previews.items():
    shutil.copy2(ROOT / 'work/previews' / source, OUT / f'{STEM}-{suffix}.png')

validation['visual_review'] = {
    'atlas_camera_views': 31,
    'native_editor_rooms': ['PARALLAX', 'FAULTLINE'],
    'native_play_preview': 'Opening, Ignore Damage enabled; randomized starting states observed.',
    'native_full_completion': False,
}
validation_path.write_text(json.dumps(validation, indent=2) + '\n')

notes = f'''# v8 — dark branching revision

[Final .gmd]({STEM}.gmd) · [31-view preview]({STEM}-preview.png) · [Validation]({STEM}-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× speed portals cover **85.71%** of the timeline. **26,934 objects**. All seven requested modes; no swing. Earlier exports remain intact.

## Changes

- Added **50 fitted fakeouts**: 25 false ledge extensions and 25 blind L-shaped recesses. Extensions attach to platform edges; recesses sit inside solid structures. Their artwork does not add colliders.
- Darkened the structures while keeping wall-switch states brighter than the surrounding geometry. Removed the blinking wave masks, pulsing trim and moving flight-room plates. The export contains no Pulse or Alpha triggers. Small moving decorative elements remain outside the playing area in other rooms.
- Reworked ship and wave into **18 structural phrases**, mixing long holds, short corrections, separated knife gates, floating barriers and enclosed ducts. Gravity changes and wave size changes vary the controls between phrases.
- Changed the later sequence to spider → ship → robot → ball → UFO → cube. These rooms have new input scores: clustered spider transfers, inverted ship movement, robot orb catches, unequal ball transfers, a different UFO contour and a cube finale with mixed-gravity orb transfers.

## Randomized white switches

There are **34 independent decisions**, each with an equal chance of starting with its wall present or absent. Each decision resolves about **0.94 seconds before its orb** and stays fixed while you approach it.

| Visible state | Correct action | Wrong action |
| --- | --- | --- |
| Wall present | Hit the white switch to remove it | Skipping leaves the wall |
| No wall | Skip the white switch | Hitting creates the wall |

The switches use Claim Touch so their activation does not also cause an ordinary jump or UFO flap. This behavior was checked against the [official RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf). Native Advanced Random branches, toggle-orb properties and collision flags were checked against [FlowVix's object schema](https://github.com/FlowVix/gd-info-explorer/blob/main/src/lib/schema.txt) and [G.js's trigger implementation](https://github.com/g-js-api/G.js/blob/main/src/lib/general-purpose.ts).

Native evidence shows the first wall [present on attempt 2]({STEM}-native-wall-present.png) and [absent on attempt 3]({STEM}-native-wall-absent.png). These are unmodified GD screenshots. The upper-left colored squares and controls belong to the installed preview interface.

## Verification and limits

- The actual .gmd imports into GD with all **26,934 objects**. Native serialization retains the random branches, Claim Touch settings and non-colliding artwork flags.
- All 34 exported switch circuits pass both correct outcomes and both wrong-choice cases. This is a serialized-logic check; every switch was not clicked through in native play.
- **49,408 finite-body route samples** pass. A separate approximate input replay passes all **15 rooms**. The reference route assumes each switch starts with a wall; branch tests check the no-wall alternative separately.
- Normal/mini states at orbs, per-room camera setup, spike bounds, group separation and absence of flight-room motion triggers pass the structural audit.
- Inspected **31 atlas-based camera views**, the [native ship]({STEM}-native-ship.png), the [native second wave]({STEM}-native-wave.png), and three opening attempts for randomization.

**Full native completion and the requested insane-to-extreme demon difficulty remain unverified.** The opening preview used Ignore Damage. Approximate physics does not fully reproduce native triangle collisions, portal entry offsets or input buffering; passing these checks is not proof of a damage-enabled completion.

Build and audit instructions are in `work/CURRENT.md`. SHA-256: `{digest}`.
'''
(OUT / f'{STEM}-notes.md').write_text(notes)

(ROOT / 'work/CURRENT.md').write_text('''# Current exported level

Latest: `outputs/v8-1573528-branching.gmd`, internal name **v8**. Read its `-notes.md` and `-validation.json` before editing. This revision follows the accepted structural cleanup and changes flight patterns, later room order, visibility and randomized wall decisions.

Current raw: `work/v8-branching.level`. Current plan: `work/branching-plan.json`. Current native import snapshot: `work/branching-native-import.level`. Keep prior exports intact, especially `outputs/v8-1573528-clean.gmd`.

The latest export has 26,934 objects, 34 independent randomized wall choices, 50 fitted fakeouts and 18 flight phrases. Song 1573528; duration 205.192 seconds. All seven modes except swing. Native 0.5 speed covers 85.714% of the timeline; no time warp. Normal size portal is 99; mini is 101. Retain per-room camera resets after mode portals and Claim Touch 445 on the randomized toggle orbs.

## Rebuild

Run sequentially from the workspace root:

```sh
rtk proxy python3 work/branching_layout.py
rtk proxy env GD_SKIN_SOURCE=work/branching-base.gmd GD_SKIN_TARGET=work/branching-skinned.gmd GD_SKIN_PLAN=work/branching-plan.json GD_SKIN_RAW=work/v8-branching-base.level GD_SKIN_OUTPUT_RAW=work/v8-branching-skinned.level GD_SKIN_AUDIT=work/branching-skin-audit.json python3 work/clean_visuals.py
rtk proxy python3 work/branching_fakeouts.py
rtk proxy python3 work/check_branching_route.py
rtk proxy python3 work/replay_branching.py
```

Import the resulting .gmd through the native bridge and refresh `work/branching-native-import.level`. Then run `rtk proxy python3 work/audit_branching.py`. Native random-state observations in that audit refer to screenshots from this revision, not automated native gameplay tests; refresh them if the logic changes.

Preview with `GD_PREVIEW_LEVEL=work/v8-branching.level` and `GD_PREVIEW_PLAN=work/branching-plan.json` when calling `work/preview_memory.py`. Existing final views use prefix `branching-final`; 31 camera positions are recorded by their filenames. `work/package_branching.py` packages those inspected previews and copies the final .gmd to Downloads after checking the audited hash.

`work/memory_layout.py` still describes an older score. `work/branching_layout.py` imports it and overrides the revised portions. Running `work/clean_visuals.py` without the environment arguments rebuilds the older clean artifact. Do not treat either default output as the latest revision.

Full native completion and exact demon difficulty remain unverified. The script checks use an approximate physics model. Native random starting states and ship/wave artwork were inspected; the complete level was not played through with damage enabled.
''')

destination = (Path(__file__).resolve().parents[1]/'build/exports') / level.name
assert destination.parent.is_dir()
if destination.exists():
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == digest, 'Different existing Downloads export: preserve it.'
else:
    shutil.copy2(level, destination)
assert hashlib.sha256(destination.read_bytes()).hexdigest() == digest
print(json.dumps({'final_file': str(destination), 'sha256': digest, 'bytes': destination.stat().st_size, 'notes': str(OUT / f'{STEM}-notes.md')}, indent=2))
