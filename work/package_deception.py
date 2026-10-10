"""Package the scoped spider treatment and mechanical fakeout revision."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs';STEM='v8-1573528-deception'
file=OUT/f'{STEM}.gmd'
V=json.loads((OUT/f'{STEM}-validation.json').read_text())
digest=hashlib.sha256(file.read_bytes()).hexdigest()
assert digest==V['sha256']
assert all(not r['errors'] for r in V['route_checks']+V['independent_replay'])
assert all(b['wrong_hit_collides'] for b in V['bait_checks'])
shutil.copy2(ROOT/'work/previews/deception-final-sheet.png',OUT/f'{STEM}-preview.png')
shutil.copy2(ROOT/'work/previews/deception-final-17900.png',OUT/f'{STEM}-ship-branch.png')
shutil.copy2(ROOT/'work/previews/deception-final-22600.png',OUT/f'{STEM}-spider.png')

notes=f'''# v8 — spider-only linework and mechanical fakeouts

[Final .gmd]({STEM}.gmd) · [18-view preview]({STEM}-preview.png) · [Validation]({STEM}-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× speed for **85.71%** of the timeline. **30,508 objects**.

## Scope corrected

Both spider sections are identical to the preceding nocturne file: **2,262 objects** in BLIND ELEVATOR and **3,293 objects** in RECALL. Their 385 visual decoys and dense shelf linework remain.

Removed all **592** copied false shelf and painted-gap features outside those spider rooms. The other rooms use their earlier clean structural surfaces, the dark palette and the eased wave geometry. Randomized switches retain their dim olive artwork and original behavior.

## Different kinds of wrong choices

**17 live bait orbs.** These use native yellow-jump or blue-gravity orb mechanics. They occupy deliberately selected gaps between required inputs, with at least 0.28 seconds from each required click and additional exclusion around robot holds. Hitting each retained bait creates a collision in the approximate replay; skipping it preserves the original input score. A candidate that did not produce a collision was removed.

Required and bait orbs share the same normal size and a constant 13% opacity, with glow and particles disabled. This avoids identifying the bait through a different size or brighter outline. The opacity is set once at the start and never flashes.

**Four genuine blind branches.** Collision geometry is cut to form real openings:

| Room | Tempting wrong move | Result |
| --- | --- | --- |
| BLINDFOLD | Continue downward through a required wave turn | The lower branch ends against a solid cap |
| FAULTLINE | Continue the mini-wave climb | The upper branch closes while the real route turns away |
| PARALLAX | Dive into a lower service duct | A live gravity portal sits inside the detour, followed by a solid end |
| UNDERTOW | Maintain altitude past the required descent | The straight branch ends while the intended route drops |

These branches share the existing wall surfaces. Their entries have actual open space and their ends have actual collision. [Ship branch preview]({STEM}-ship-branch.png).

The existing **34 randomized wall decisions** remain: wall present → hit; wall absent → skip. All seven modes and the original 550-input reference score are retained.

## LIMBO study

Inspected MindCap's original showcase at [0:22](https://www.youtube.com/watch?v=ryBbuH_SPbs&t=22s), [0:45](https://www.youtube.com/watch?v=ryBbuH_SPbs&t=45s) and [1:08](https://www.youtube.com/watch?v=ryBbuH_SPbs&t=68s). The references show grouped orb choices, alternate destinations around coherent platform masses, and distinct visual framing for each room. The design takeaway used here is to give a misleading object a specific relationship to the player's next decision. The new geometry and timings were authored for this level.

## Verification

- Exact serialized-object comparisons confirm that both spider sections are unchanged.
- All non-spider shelf overlays are removed; remaining layer-11 artwork belongs to the spider rooms or the existing randomized switch skins.
- The **49,408-sample** route check passes, and approximate independent replay passes all **15 rooms**.
- Each of the **17 bait inputs** produces a solid or spike collision in the wrong-input model. All four branch approaches have body clearance up to their solid caps.
- The 34 randomized switch circuits pass both starting-state cases.
- Inspected 18 atlas-based camera views spanning all 15 rooms.

**A fresh native import/playtest was not completed because GD was being used concurrently. Full native completion and exact demon difficulty remain unverified.** The scripted models approximate native orb physics, input buffering and portal collision. Branch checks establish geometric access and solid endpoints, rather than a native alternate-input completion.

Earlier exports remain intact. Rebuild details are in `work/CURRENT.md`.

SHA-256: `{digest}`
'''
(OUT/f'{STEM}-notes.md').write_text(notes)
(ROOT/'work/CURRENT.md').write_text('''# Current exported level

Latest: `outputs/v8-1573528-deception.gmd`, internal name **v8**. Read its notes and validation JSON before editing. The user wanted the nocturne shelf/line effect retained ONLY in the spider, and different mechanical fakes elsewhere, informed by LIMBO.

Current raw: `work/v8-deception.level`. Current plan: `work/deception-plan.json`. Preserve all earlier exports, especially `outputs/v8-1573528-nocturne.gmd`, and `work/revision-before-deception/`.

Both spider rooms match nocturne object-for-object. All 592 non-spider nocturne visual decoys were removed. New mechanics: 17 live orb baits, four physically carved blind branches, one live gravity portal within a ship detour. The 34 randomized wall switches, camera, seven modes, original input score, eased wave clearance and dark palette remain.

Required and bait orbs share native scale 1 and group 8500, whose opacity is set to .13 once at x=0. This is a static dimming trigger, not flashing. Randomized switch skins remain on their original mutually exclusive groups. Do not apply the spider's linework or pass-through shelves to other rooms again.

## Rebuild

Run sequentially:

```sh
rtk proxy python3 work/deception_layout.py
rtk proxy env GD_SKIN_SOURCE=work/deception-base.gmd GD_SKIN_TARGET=work/deception-skinned.gmd GD_SKIN_PLAN=work/deception-plan.json GD_SKIN_RAW=work/v8-deception-base.level GD_SKIN_OUTPUT_RAW=work/v8-deception-skinned.level GD_SKIN_AUDIT=work/deception-skin-audit.json python3 work/clean_visuals.py
rtk proxy python3 work/deception_finish.py
rtk proxy python3 work/check_deception_choices.py
rtk proxy python3 work/prune_deception_baits.py
rtk proxy python3 work/check_deception_route.py
rtk proxy python3 work/replay_deception.py
rtk proxy python3 work/check_deception_branches.py
rtk proxy python3 work/audit_deception.py
```

`deception_layout.py` reads the preserved nocturne collision build. `deception_finish.py` restores only the accepted spider artwork and randomized switch skins. Candidate pruning happens after the wrong-input replay; regenerate before re-running pruning. The final export has 30,508 objects and SHA-256 in its validation JSON.

The replay now checks portal y/scale against player position, so a live portal inside a wrong branch does not affect the intended route just because its x coordinate is crossed. This is still an approximate model.

Render with `GD_PREVIEW_LEVEL=work/v8-deception.level GD_PREVIEW_PLAN=work/deception-plan.json` using `work/preview_memory.py`. The 18 inspected views are `work/previews/deception-final-*`. Package with `rtk proxy python3 work/package_deception.py`.

A fresh native import was not completed because GD was being used concurrently. The native audit is optional: when a fresh import is available, save its snapshot to `work/deception-native-import.level` before re-running the audit. Do not reuse an older snapshot or old native screenshots as verification of this revision. Full native completion and exact demon rating remain unverified.
''')
destination=(Path(__file__).resolve().parents[1]/'build/exports')/file.name
assert destination.parent.is_dir()
if destination.exists():assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest
else:shutil.copy2(file,destination)
assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest
print(json.dumps(dict(file=str(destination),bytes=destination.stat().st_size,sha256=digest,notes=str(OUT/f'{STEM}-notes.md')),indent=2))
