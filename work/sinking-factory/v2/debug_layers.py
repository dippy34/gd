import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v2_preview as VP
level, x, cy, zoom, tag = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
P = VP.load(level); R = P.R
oo, pal = P.snapshot(x)
pal._c[1010] = ((0, 0, 0), False, 1); pal._c[99999] = ((255, 255, 255), False, 1)
oo = [o for o in oo if int(o['1']) not in (1755, 2909, 2921, 1520, 1934, 1913, 1914, 31) and not P.names.get(int(o['1']), '').startswith('edit_')]
hw, hh = 285 / zoom, 160 / zoom
variants = {
    'no-v2': [o for o in oo if o.get('61') != '31'],
    'v2-only': [o for o in oo if o.get('61') == '31'],
    'z-5': [o for o in oo if o.get('24') == '-5'],
    'z-3': [o for o in oo if o.get('24') == '-3'],
    'z-5-v2': [o for o in oo if o.get('24') == '-5' and o.get('61') == '31'],
}
out = Path('shots') / 'debug'; out.mkdir(parents=True, exist_ok=True)
for k, sel in variants.items():
    R.render(sel, pal, P.names, x - hw, x + hw, cy - hh, cy + hh, ppu=1.0, bg=(40, 40, 60), out=str(out / f'{tag}-{k}.png'))
    print(k, len(sel))
