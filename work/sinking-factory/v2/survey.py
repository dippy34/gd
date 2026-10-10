"""First-pass survey of a reference level: ids, triggers, channels, layers."""
import sys, json, math
from pathlib import Path
from collections import Counter, defaultdict
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / 'handoff/tools'))
import gdparse, render as R
names = R.load_names(str(HERE.parents[1] / 'handoff/research/objectids.yml'))
path = sys.argv[1]
head, objs = gdparse.load(path)
H = gdparse.parse_header(head)
print('objects', len(objs))
print('header keys', {k: (v[:60] if k != 'kS38' else len(v)) for k, v in H.items()})
ids = Counter(o['1'] for o in objs)
print('\nTOP IDS')
for oid, n in ids.most_common(70):
    print(f'{oid:>6} {n:>7} {n/len(objs)*100:5.1f}%  {names.get(int(oid),"?")}')
xs = [float(o.get('2', 0)) for o in objs]
ys = [float(o.get('3', 0)) for o in objs]
print('\nx range', min(xs), max(xs), 'y range', min(ys), max(ys))
chans = {}
for c in gdparse.parse_ks38(H.get('kS38', '')):
    if '6' in c: chans[int(c['6'])] = c
print('\nkS38 channels', len(chans))
for cid in sorted(chans)[:400]:
    c = chans[cid]
    print(cid, 'rgb', c.get('1'), c.get('2'), c.get('3'), 'blend' if c.get('5') == '1' else '', 'op', c.get('7'), 'copy', c.get('9'), 'hsv', c.get('10'))
col = Counter(o.get('21', 'def') for o in objs)
print('\nmain colour channel usage top 40', col.most_common(40))
det = Counter(o.get('22', 'def') for o in objs)
print('detail channel usage top 20', det.most_common(20))
z = Counter(o.get('24', '0') for o in objs)
print('\nz-layers', sorted(z.items(), key=lambda kv: int(kv[0])))
rot = sum(1 for o in objs if float(o.get('6', 0)) % 360 != 0)
print('rotated', rot / len(objs))
sc = [float(o.get('32', o.get('128', 1))) for o in objs]
print('scale quantiles', [round(sorted(sc)[int(q * (len(sc) - 1))], 3) for q in (0, .05, .25, .5, .75, .95, .99, 1)])
trig = Counter(o['1'] for o in objs if names.get(int(o['1']), '').startswith('edit_') or o['1'] in ('899', '901', '1006', '1007', '1049', '1346', '1914', '1913', '2903', '2904'))
print('\ntrigger-ish ids', trig.most_common(60))
