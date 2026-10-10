"""Long strips of a Sinking Factory build (time-evaluated palette/motion via preview_memory)."""
import os, sys, json
from pathlib import Path
from PIL import Image
HERE = Path(__file__).parent; SF = HERE.parent; ROOT = SF.parents[1]
level = sys.argv[1]; manifest = sys.argv[2]; tag = sys.argv[3]
os.environ['GD_PREVIEW_PLAN'] = str(manifest); os.environ['GD_PREVIEW_LEVEL'] = str(level)
sys.path.insert(0, str(ROOT / 'work'))
import preview_memory as P
R = P.R
R.SHEETS += ['FireSheet_01', 'GJ_ParticleSheet']; R.load_atlas()
for o in P.objs:
    if o['1'] == '899' and '23' not in o: o['23'] = '1'
for o in P.objs:
    if o['1'] in ['10','11','12','13','47','111','660','745','1331','99','101','200','201','202','203','1334','36','84','141','1330','1333','1704','1751']:
        o['21'] = '1010x'; o['22'] = '1010x'
P.head += ',kSdummy,0'
segs = json.loads(sys.argv[4]) if len(sys.argv) > 4 else [[16700, 18700], [18700, 20700], [20700, 22700], [22700, 24800]]
out = HERE / 'shots' / tag; out.mkdir(parents=True, exist_ok=True)
for a, b in segs:
    oo, pal = P.snapshot((a + b) / 2)
    pal._c[1010] = ((0, 0, 0), False, 1)
    oo = [o for o in oo if int(o['1']) not in [1755, 2909, 2921, 1520, 1934] and not P.names.get(int(o['1']), '').startswith('edit_')]
    for o in oo:
        if o.get('21') == '1010x': o['21'] = o['22'] = '99999'
    pal._c[99999] = ((255, 255, 255), False, 1)
    f = out / f'{a}-{b}.png'
    R.render(oo, pal, P.names, a, b, -200, 660, ppu=0.8, bg=(20, 8, 8), out=str(f))
    print('rendered', f, flush=True)
