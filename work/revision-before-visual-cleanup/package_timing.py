"""Package the harder timing revision without replacing the accepted source."""
from pathlib import Path
from collections import Counter
import sys, json, hashlib, shutil, csv

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gmd import read_gmd,decompress
stem='v8-1573528-timing'
level=ROOT/f'outputs/{stem}.gmd'
p=json.loads((ROOT/'work/memory-plan.json').read_text())
v=json.loads((ROOT/f'outputs/{stem}-validation.json').read_text())
a=json.loads((ROOT/'work/timing-audit.json').read_text())
r=json.loads((ROOT/'work/memory-replay.json').read_text())
w=json.loads((ROOT/'work/timing-window-comparison.json').read_text())
assert v['rooms_with_nominal_overlaps']==0 and not any(z['errors'] for z in r)
assert v['sha256']==a['sha256']==hashlib.sha256(level.read_bytes()).hexdigest()
assert len(w['tests'])==41
assert all(z['results']['current']['sampled_success_count']<z['results']['previous']['sampled_success_count'] for z in w['tests'])

def parse(raw):
    out=[]
    for t in raw.split(';')[1:]:
        if t:
            ps=t.split(',');out.append(dict(zip(ps[::2],ps[1::2])))
    return out

file_objects=parse(decompress(read_gmd(level)['k4'][1]))
native=parse((ROOT/'work/timing-native-import.level').read_text())
assert len(native)==len(file_objects)==p['objects']
assert Counter(o['1'] for o in native)==Counter(o['1'] for o in file_objects)
for oid in ('99','101','1914','1913','2925'):
    oo=sorted([o for o in file_objects if o['1']==oid],key=lambda o:float(o['2']))
    nn=sorted([o for o in native if o['1']==oid],key=lambda o:float(o['2']))
    for o,n in zip(oo,nn):
        # The bridge emits six significant digits for world positions.
        assert abs(float(o['2'])-float(n['2']))<.055
        assert abs(float(o['3'])-float(n['3']))<.012
        for k in {'99':[],'101':[],'1914':['71','101','36'],'1913':['371'],'2925':['111']}[oid]:
            assert float(o[k])==float(n[k])

v.update(regressions=a,single_input_model_comparison=w,independent_model_replay=r,
         native_validation=dict(imported=True,objects=len(native),object_id_counts_match=True,
             size_and_camera_settings_survive_import=True,opening_visually_inspected=True,
             full_completion_verified=False,difficulty_verified=False,
             note='Opening inspected with the existing Ignore Damage setting; no native completion claim.'))
(ROOT/f'outputs/{stem}-validation.json').write_text(json.dumps(v,indent=2))
shutil.copy2(ROOT/'work/previews/timing-final-sheet.png',ROOT/f'outputs/{stem}-preview.png')
with (ROOT/f'outputs/{stem}-inputs.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=['time','x','mode','kind','hold','down','orb_id','gravity','target','symbol','activate'],extrasaction='ignore')
    writer.writeheader();writer.writerows(p['controls'])

rows=[]
for mode in ('cube','robot','ball','ufo','spider'):
    z=w['summary'][mode]
    rows.append(f"| {mode.title()} | {z['tests']} | {z['previous_median_ms']:.2f} ms | {z['current_median_ms']:.2f} ms |")
table='\n'.join(rows)
notes=f'''# v8 — harder timings and deliberate fakeouts

[Final .gmd]({stem}.gmd) · [Native opening screenshot]({stem}-native-preview.png) · [Section previews]({stem}-preview.png) · [Validation]({stem}-validation.json)

This revision builds on `v8-1573528-refined.gmd`. The previous file remains intact. Internal name: **v8**. Song: **1573528**. Duration: **3:25.19**. Native 0.5× speed: **85.71%**.

## What changed

- **Cube:** restraints before takeoff catch early jumps; launch gates and orb-exit gates catch late jumps and mistimed activations. The existing musical score and recognizable platform sequences remain.
- **Robot:** takeoff and release have separate constraints. Teeth cover new divider faces so a mistimed release cannot gain an unintended landing platform. Short and long holds retain their distinct authored lengths.
- **Ball:** constrained departures and transfer throats bound both early and late gravity flips; the alternating rail structures remain.
- **UFO:** staggered intake and exit gates tighten hop timing, including the inverted section.
- **Spider:** both rooms have tighter entry and exit shoulders around each teleport. RECALL has the smaller remaining horizontal allowance.
- **Fakeouts:** **100 recessed false doorways** are attached to real wall banks and structural housings. Each leads into an actual solid dead end. Their frame language matches the real openings. Existing memory switches, misleading landing plates, room structures and moving service plates remain.

Both ship rooms and both wave rooms are unchanged, including gameplay and decoration. The corrected size portals, camera refreshes, speed schedule, all input timestamps, and intended route coordinates match the previous revision.

## Timing comparison

These are **approximate model sensitivity intervals**, not verified native click windows. One input is shifted at a time in 1/240-second steps while other inputs stay fixed. Each test stops 0.70 seconds after the input; the successful interval is capped at ±20 steps. Robot release tests change hold duration separately.

| Mode | Distinct input tests | Previous median model interval | New median model interval |
|---|---:|---:|---:|
{table}

All **41** compared inputs had a smaller successful interval in the new model. The unchanged reference score passes all fifteen rooms. These figures establish a relative change under the same model; they do not assign an Insane/Extreme rating. Some intervals are asymmetric around the reference input.

## Validation and limits

- Native Geometry Dash import succeeds with **{p['objects']:,} objects**. Native object ID counts match the export; size portals and camera settings survive import.
- All **{v['nominal_path_samples']:,}** nominal finite-body samples pass the exported block/spike audit. All **{v['spike_count']:,} spikes** remain within y = 0–300.
- Continuous size-state checks pass, including orb inputs and the second wave's normal/mini alternation.
- All forty live memory decisions still control real barriers. Each added false door was checked against an actual collision bank.
- Ship and wave rooms, initial settings, camera objects and musical input score are compared directly with the previous file.
- Inspected section renders and the native opening. The native visual inspection used the existing Ignore Damage setting.

**Full native completion and exact demon difficulty remain unverified.** The replay does not fully reproduce native physics, buffering, triangle hitboxes or portal contact offsets. In particular, passing these checks is not proof of a complete damage-enabled run.

[Player hitbox reference](https://boomlings.dev/reference/player_physics/hitboxes) and [mode physics reference](https://boomlings.dev/reference/player_physics/gamemodes) informed finite-body and teleport checks. [Earlier revision notes](v8-1573528-refined-notes.md) contain the song, portal-ID and camera research.

SHA-256: `{v['sha256']}`
'''
(ROOT/f'outputs/{stem}-notes.md').write_text(notes)
print(json.dumps(dict(file=str(level),bytes=level.stat().st_size,objects=p['objects'],
                     fakeouts=len(p['fakeouts']),native_import=True,completion_verified=False),indent=2))
