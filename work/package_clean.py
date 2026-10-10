from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
stem='v8-1573528-clean'
V=json.loads((ROOT/f'outputs/{stem}-validation.json').read_text())
level=ROOT/f'outputs/{stem}.gmd'
assert hashlib.sha256(level.read_bytes()).hexdigest()==V['sha256']
assert V['rooms_with_nominal_overlaps']==0 and V['visual_cleanup']['all_gameplay_properties_identical']
assert hashlib.sha256((ROOT/'outputs/v8-1573528-timing.gmd').read_bytes()).hexdigest()=='325eb46a7e1ce583694d5056185172b168ada16471ee52e13cb2d7eaf865a3bc'

points=[(4250,'CUTWIRE / robot'),(22400,'BLIND ELEVATOR / spider'),(14900,'OFFBEAT / UFO')]
out=Image.new('RGB',(2000,1905),(18,19,20));draw=ImageDraw.Draw(out)
try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
except OSError:font=ImageFont.load_default()
for row,(x,name) in enumerate(points):
    for col,prefix in enumerate(('timing-final','clean-final')):
        a=col*1000;b=row*635
        im=Image.open(ROOT/f'work/previews/{prefix}-{x}.png').convert('RGB')
        out.paste(im,(a,b+50));draw.text((a+20,b+12),f'{"PREVIOUS" if col==0 else "CLEANUP"} — {name}',font=font,fill=(215,215,205))
out.save(ROOT/f'outputs/{stem}-comparison.png')
shutil.copy2(ROOT/'work/previews/clean-final-sheet.png',ROOT/f'outputs/{stem}-preview.png')
shutil.copy2(ROOT/'outputs/v8-1573528-timing-inputs.csv',ROOT/f'outputs/{stem}-inputs.csv')
notes=f'''# v8 — structural cleanup

[Final .gmd]({stem}.gmd) · [Before / after]({stem}-comparison.png) · [All 15 rooms]({stem}-preview.png) · [Native opening]({stem}-native-preview.png) · [Validation]({stem}-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× portals for **85.71%** of the timeline. **28,984 objects**.

The visible structures have been rebuilt from the existing solid geometry. Joined platforms share an exposed outer boundary. Crossing support cages, nested platform frames, and all 100 oversized false door boxes have been removed. Seventy-one small inset faces fit within their actual platform bodies, clear of attached timing banks. Spike graphics use filled silhouettes; adjacent teeth no longer draw outlines through one another. Native spikes retain their collision settings and are hidden behind the replacement artwork.

All gameplay positions, sizes, rotations and behavior properties match the previous timing revision. The same 489 planned inputs, seven modes, forty functional memory decisions, mini/normal portals, camera locks, speed changes, moving code tokens and moving service plates remain. The earlier timing file remains intact.

Validation:

- Inspected 30 atlas-based renders, covering all fifteen rooms, with the exported camera and trigger states.
- Imported the actual .gmd in Geometry Dash. Inspected the native opening during play and the robot, spider and second-wave structures in the editor.
- Native import retains 28,984 objects; object ID counts match. Checked 15,809 collision, camera, interaction and replacement-spike-art objects against native serialization, allowing its position/scale rounding.
- All 12,328 rebuilt structural art boxes fit within the union of real solid bounds. Outside-playfield service recesses are excluded from this containment check.
- The 49,395-sample finite-body route audit passes, all 2,766 native spikes remain inside the playfield, and all forty live memory choices still control their original barriers.

The native opening check used the existing Ignore Damage setting. **Full native completion and exact demon difficulty remain unverified.** Scripted previews approximate the engine, and the route model does not prove a damage-enabled completion.

Rebuild: `rtk proxy python3 work/clean_visuals.py`, then `rtk proxy python3 work/check_clean.py`. The cleanup reads the frozen timing revision and writes its own export; `memory_layout.py` still generates the earlier timing revision. For import validation, capture the imported file to `work/clean-native-import.level`, then run `work/audit_clean_visuals.py` and `work/package_clean.py`.

SHA-256: `{V['sha256']}`
'''
(ROOT/f'outputs/{stem}-notes.md').write_text(notes)
(ROOT/'work/CURRENT.md').write_text('''# Current exported level

Latest: `outputs/v8-1573528-clean.gmd`, internal name v8. Read its `-notes.md` and `-validation.json` before editing. This is the visual cleanup following the hard timing revision.

`work/v8-clean.level` is its raw data. `work/memory-plan.json` remains the unchanged gameplay plan. `work/v8-memory.level` and `work/memory_layout.py` represent the previous timing build, not the latest art. `work/clean_visuals.py` applies the cleanup to the frozen previous build in `work/revision-before-visual-cleanup/`.

Keep the seven-mode timing score, all forty memory decisions, corrected native size portal IDs (99 normal / 101 mini), per-room camera refresh and song 1573528. Avoid rebuilding per-collider outlined frames or oversized fake doors. Native completion is still unverified.
''')
download=(Path(__file__).resolve().parents[1]/'build/exports')/level.name
if download.exists():assert download.read_bytes()==level.read_bytes(),'Refuse to replace a different Downloads file'
else:shutil.copy2(level,download)
print(json.dumps(dict(file=str(level),downloads_copy=str(download),bytes=level.stat().st_size,sha256=V['sha256']),indent=2))
