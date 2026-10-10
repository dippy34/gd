"""Layer breakdown of one reference window: what sits on each z-layer, lit or dark, blending or opaque."""
import sys, json, math, colorsys
from pathlib import Path
from collections import Counter, defaultdict
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import refrender as RR
R = RR.R
names = RR.load_names()
lvl = RR.Level(sys.argv[1]); cx, cy = float(sys.argv[2]), float(sys.argv[3])
w, h = 570, 320
x0, x1, y0, y1 = cx - w/2, cx + w/2, cy - h/2, cy + h/2
lvl.pal.set_x(cx)
oo = [o for o in lvl.window(x0, x1, 60) if o['1'] not in RR.TRIGGERS and y0 - 60 <= R.fget(o, '3') <= y1 + 60]
rows = defaultdict(list)
for o in oo:
    cid = int(R.fget(o, '21', 1)); rgb, bl, op = lvl.pal.get(cid)
    if '43' in o and o.get('41') == '1': rgb = R.hsv_apply(rgb, o['43'])
    lum = (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]) / 255
    sc = R.fget(o, '128', R.fget(o, '32', 1)); sy = R.fget(o, '129', sc)
    z = int(R.fget(o, '24', 0))
    rows[z].append(dict(id=o['1'], name=names.get(int(o['1']), '?'), lum=lum, bl=bl, op=op, sc=abs(sc), sy=abs(sy), rot=R.fget(o, '6') % 90 != 0, rgb=rgb, zo=R.fget(o, '25', 0), cid=cid))
print('window', cx, cy, 'objects', len(oo))
for z in sorted(rows):
    r = rows[z]; n = len(r)
    blend = [x for x in r if x['bl']]; opq = [x for x in r if not x['bl']]
    def q(vals):
        vals = sorted(vals); return [round(vals[int(p*(len(vals)-1))], 3) for p in (.1, .5, .9)] if vals else []
    print(f"\nZ {z:>3}: n={n} blending={len(blend)} ({len(blend)/n:.0%})  opaque lum p10/50/90={q([x['lum'] for x in opq])}  blend lum*op={q([x['lum']*x['op'] for x in blend])}")
    ids = Counter((x['id'], x['name'][:26], x['bl']) for x in r).most_common(12)
    for (oid, nm, bl), c in ids:
        sel = [x for x in r if x['id'] == oid and x['bl'] == bl]
        print(f"     {oid:>5} {nm:26} {'BL' if bl else '  '} x{c:<4} lum={q([x['lum'] for x in sel])} op={q([x['op'] for x in sel])} scale={q([x['sc'] for x in sel])} rot={sum(x['rot'] for x in sel)/len(sel):.0%} rgb~{sel[len(sel)//2]['rgb']} ch={Counter(x['cid'] for x in sel).most_common(2)}")
