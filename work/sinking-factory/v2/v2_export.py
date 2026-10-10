"""Build the final MELTDOWN v2 level, wrap it as a .gmd, validate, and copy to Downloads."""
import sys, json, hashlib, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v2_build as VB
import v2lib as L

ctx, ch = VB.build('final')
raw = VB.B.level_string(VB.RESTYLE)
level = HERE / 'out' / 'v2-final.level'
level.write_text(raw)

fields = L.gmd.read_gmd((Path(__file__).resolve().parents[3]/'outputs/The Sinking Factory - MELTDOWN.gmd'))
fields['k4'] = ('s', L.gmd.compress(raw))
fields['k2'] = ('s', 'Factory Meltdown v2')
fields['k48'] = ('i', str(len(VB.B.O) + len(VB.B.added)))
outputs = L.SF.parents[1] / 'outputs'
out = outputs / 'The Sinking Factory - MELTDOWN v2.gmd'
L.gmd.write_gmd(out, fields)
dl = (Path(__file__).resolve().parents[3]/'build/exports/The Sinking Factory - MELTDOWN v2.gmd')
shutil.copy2(out, dl)

res = subprocess.run(['/usr/bin/python3', str(HERE / 'validate_v2.py'), str(level), str(dl)], capture_output=True, text=True)
validation = json.loads(res.stdout)
(outputs / 'The Sinking Factory - MELTDOWN v2 Validation.json').write_text(json.dumps(validation, indent=2))

manifest = dict(
    base='The Sinking Factory - MELTDOWN.gmd (sha256 %s)' % hashlib.sha256(
        (Path(__file__).resolve().parents[3]/'outputs/The Sinking Factory - MELTDOWN.gmd').read_bytes()).hexdigest(),
    output=str(dl), output_sha256=hashlib.sha256(dl.read_bytes()).hexdigest(),
    passes=ctx.report, restyle={k: v[0] for k, v in VB.RESTYLE.items()},
    new_channels={k: v for k, v in sorted(VB.B.colors.items())}, groups=[L.ROOT_V2, VB.B.next_group],
    speed_schedule=L.SPEED, controls=[],
)
(HERE / 'out' / 'v2-manifest.json').write_text(json.dumps(manifest, indent=1, default=str))
print(json.dumps({k: validation[k] for k in ('passed', 'failures', 'total_objects', 'added_objects', 'sha256', 'name')}, indent=1))
