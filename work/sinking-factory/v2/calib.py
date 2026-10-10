import sys, json
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import refrender as RR, lookstats as LS
from PIL import Image
R = RR.R; R.load_atlas(); names = RR.load_names()
lvl = RR.Level(sys.argv[1]); tag = sys.argv[2]; pts = json.loads(sys.argv[3])
rows = []
for cx, cy in pts:
    f = HERE / 'shots' / tag / f'{int(cx)}.png'
    f.parent.mkdir(exist_ok=True, parents=True)
    RR.shot(lvl, names, cx, cy, f, ppu=1.0)
    s = LS.stats(Image.open(f)); s['x'] = cx; rows.append(s)
    print(cx, s['mean'], s['black'], s['bright'], s['edge'], s['largeScaleVar'], s['bands'], flush=True)
json.dump(rows, open(HERE / 'shots' / tag / 'stats.json', 'w'))
import statistics as st
for k in ['mean', 'black', 'bright', 'vbright', 'edge', 'largeScaleVar', 'std']:
    v = sorted(r[k] for r in rows)
    print(f'{k:14} p10={v[len(v)//10]:.4f} med={st.median(v):.4f} p90={v[len(v)*9//10]:.4f}')
print('bands med', [round(st.median(r['bands'][i] for r in rows), 4) for i in range(6)])
print('hue mean', [round(sum(r['hue'][i] for r in rows) / len(rows), 3) for i in range(12)])
