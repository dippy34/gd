"""Independent checks for MELTDOWN v2. Re-derives everything from the files.

usage: validate_v2.py LEVEL [GMD]
"""
import sys, json, math, hashlib
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
SF = HERE.parent
sys.path.insert(0, str(SF.parent / 'handoff/tools'))
sys.path.insert(0, str(SF / 'vendor'))
import gdparse, gmd
from shapely.geometry import box, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree

level = Path(sys.argv[1]); gmd_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
H0, SRC = gdparse.load(SF / 'source.level')
HM, MEL = gdparse.load(SF / 'meltdown.level')
HV, V = gdparse.load(level)
NS, NM = len(SRC), len(MEL)
fail = []
def check(cond, msg):
    if not cond:
        fail.append(msg)
    return cond

# 1. source gameplay objects: identical to MELTDOWN's copies (which only retinted visuals)
src_changed_vs_melt = sum(1 for a, b in zip(MEL[:NS], V[:NS]) if a != b)
check(src_changed_vs_melt == 0, f'{src_changed_vs_melt} source objects differ from MELTDOWN')
gameplay_keys_changed = 0
for a, b in zip(SRC, V[:NS]):
    d = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    if a['1'] == '2921':
        d -= {'176', '188', '10'}
    if d - {'21', '22', '24', '25'}:
        gameplay_keys_changed += 1
check(gameplay_keys_changed == 0, f'{gameplay_keys_changed} source objects have non-visual key changes')

# 2. MELTDOWN decoration: only the HSV value keys may change
melt_changed = Counter()
bad_melt = 0
for a, b in zip(MEL[NS:], V[NS:NM]):
    d = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    if d - {'41', '43'}:
        bad_melt += 1
    for k in d: melt_changed[k] += 1
check(bad_melt == 0, f'{bad_melt} MELTDOWN deco objects changed beyond HSV')
check(len(V) >= NM, 'objects missing')

# 3. header: everything but the colour table identical; source + MELTDOWN channels only retuned where intended
h0 = gdparse.parse_header(HM); h1 = gdparse.parse_header(HV)
check({k: v for k, v in h0.items() if k != 'kS38'} == {k: v for k, v in h1.items() if k != 'kS38'}, 'header settings changed')
c0 = {c['6']: c for c in gdparse.parse_ks38(h0['kS38']) if '6' in c}
c1 = {c['6']: c for c in gdparse.parse_ks38(h1['kS38']) if '6' in c}
src_channels = {c['6'] for c in gdparse.parse_ks38(gdparse.parse_header(H0)['kS38']) if '6' in c}
for cid, c in c0.items():
    check(cid in c1, f'channel {cid} missing')
    if cid in src_channels:
        check(c1[cid] == c, f'source channel {cid} changed')
    elif c1.get(cid) != c:
        diff = {k for k in set(c) | set(c1[cid]) if c.get(k) != c1[cid].get(k)}
        check(diff <= {'1', '2', '3', '5', '7'} and 600 <= int(cid) <= 641, f'channel {cid} changed keys {diff}')
new_channels = sorted(int(k) for k in set(c1) - set(c0))
check(all(650 <= c <= 699 for c in new_channels), f'new channels outside 650-699: {new_channels}')

# 4. new objects
new = V[NM:]
used_groups_before = {int(g) for o in MEL for g in o.get('57', '').split('.') if g}
DECO_OK = {'211', '693', '3637', '1764', '1011', '1886', '1887', '1888', '1849', '1853', '157', '158', '159', '3050'}
TRIG_OK = {'901', '1006', '1007', '1346'}
ids = Counter(o['1'] for o in new)
check(set(ids) <= DECO_OK | TRIG_OK, f'unexpected ids {set(ids) - DECO_OK - TRIG_OK}')
new_groups = set()
for o in new:
    gg = [int(g) for g in o.get('57', '').split('.') if g]
    new_groups.update(gg)
    if o['1'] in TRIG_OK:
        tgt = int(o.get('51', 0))
        if o['1'] == '1006':
            check(o.get('52', '0') == '0' and 650 <= tgt <= 699, f'pulse targets {tgt}')
        else:
            check(tgt >= 700 and tgt not in used_groups_before, f'trigger {o["1"]} targets group {tgt}')
            if o['1'] == '1346':
                check(int(o['71']) >= 700 and int(o['71']) not in used_groups_before, 'rotate centre group')
        continue
    check(o.get('121') == '1' and o.get('134') == '1', f'object without NoTouch/Passable {o}')
    check(700 in gg and all(g >= 700 and g not in used_groups_before for g in gg), f'bad groups {gg}')
    check(650 <= int(o['21']) <= 699, f'bad channel {o["21"]}')
    check(o.get('61') == '31', 'editor layer')
    check(16540 <= float(o['2']) <= 24700, f'object outside the window x={o["2"]}')
    check(all(math.isfinite(float(o[k])) for k in ('2', '3')), 'non-finite position')

# 5. nothing opaque drawn in front of gameplay may overlap it
PLAY_IDS = {'1', '211', '208', '209', '94', '468', '1338', '1339', '693', '216', '217', '458', '8', '1717', '1718', '36',
            '84', '141', '1333', '1330', '1704', '1751', '35', '67', '140', '10', '11', '12', '13', '47', '111', '660',
            '745', '1331', '99', '101', '200', '201', '202', '203', '1334', '392', '2926'}
play = [box(float(o['2']) - 15, float(o['3']) - 15, float(o['2']) + 15, float(o['3']) + 15)
        for o in SRC if o['1'] in PLAY_IDS and 16500 <= float(o['2']) <= 25000]
tree = STRtree(play)
chan = {int(k): c for k, c in c1.items()}
def blending(cid):
    c = chan.get(int(cid), {})
    return c.get('5') == '1'
def radius(o):
    sx = abs(float(o.get('128', 1))); sy = abs(float(o.get('129', sx)))
    base = {'211': 30, '693': 30, '3637': 50, '1764': 8, '1011': 30, '1888': 80, '1886': 64, '1887': 48, '1849': 47,
            '1853': 71, '157': 30, '158': 30, '159': 30, '3050': 24}[o['1']]
    return .5 * math.hypot(base * sx, base * sy)
# gameplay objects sit on B3 (z=-1) at order -5 (structures) and 40 (hazards)
front_opaque = []
for o in new:
    if o['1'] in TRIG_OK or blending(o['21']):
        continue
    z = int(o.get('24', 0)); order = int(o.get('25', 0))
    if z >= 1 or (z == -1 and order > -5):
        front_opaque.append(o)
overlaps = 0
for o in front_opaque:
    r = radius(o)
    shape = Point(float(o['2']), float(o['3'])).buffer(r)
    for i in tree.query(shape):
        p = play[i] if not hasattr(i, 'intersects') else i
        if p.intersects(shape):
            # soft shadow glows fade to nothing at their edge: allow the outer 40% to graze
            if o['1'] in ('1888', '1886', '1887'):
                if p.distance(Point(float(o['2']), float(o['3']))) > r * .6:
                    continue
            overlaps += 1
            break
check(overlaps == 0, f'{overlaps} opaque objects in front of gameplay overlap gameplay')

# 5b. ...and none may cover space the player can actually fly or run through.
# Flood-fill the free space from each gamemode portal inside its bounds, with every
# gameplay object (slopes, blocks, hazards) as a wall; cells are 10 units.
import numpy as np
CELL = 10
SECTIONS = [  # x0, x1, y0, y1, seed (a point on the route)
    (16875, 18195, 0, 300, (16890, 150)), (18195, 20685, 30, 330, (18215, 180)),
    (20685, 22665, -15, 720, (20700, 330)), (22665, 24660, 0, 300, (22680, 150)),
]
walls = [box(float(o['2']) - 21, float(o['3']) - 21, float(o['2']) + 21, float(o['3']) + 21)
         for o in SRC if o['1'] in PLAY_IDS and o['1'] not in ('10', '11', '12', '13', '47', '111', '660', '745', '99', '101',
                                                                 '200', '201', '202', '203', '1334', '36', '84', '141', '1333',
                                                                 '1330', '1704', '1751', '35', '67', '140')
         and '6' not in o.get('57', '').split('.') and 16500 <= float(o['2']) <= 25000]
reach_cells = 0; covered = 0
front_opaque_ctr = 0
for x0, x1, y0, y1, seed in SECTIONS:
    nx = int((x1 - x0) / CELL) + 1; ny = int((y1 - y0) / CELL) + 1
    grid = np.zeros((ny, nx), dtype=np.uint8)            # 1 = wall
    for w in walls:
        bx0, by0, bx1, by1 = w.bounds
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
            continue
        i0 = max(0, int((bx0 - x0) / CELL)); i1 = min(nx - 1, int((bx1 - x0) / CELL))
        j0 = max(0, int((by0 - y0) / CELL)); j1 = min(ny - 1, int((by1 - y0) / CELL))
        grid[j0:j1 + 1, i0:i1 + 1] = 1
    reach = np.zeros_like(grid)
    si = int((seed[0] - x0) / CELL); sj = int((seed[1] - y0) / CELL)
    stack = [(sj, si)] if grid[sj, si] == 0 else []
    while stack:
        j, i = stack.pop()
        if reach[j, i] or grid[j, i]:
            continue
        reach[j, i] = 1
        for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            jj, ii = j + dj, i + di
            if 0 <= jj < ny and 0 <= ii < nx and not reach[jj, ii] and not grid[jj, ii]:
                stack.append((jj, ii))
    reach_cells += int(reach.sum())
    for o in front_opaque:
        ox, oy = float(o['2']), float(o['3'])
        if not (x0 <= ox <= x1):
            continue
        front_opaque_ctr += 1
        r = radius(o) * (.6 if o['1'] in ('1888', '1886', '1887') else 1.0)
        i0 = max(0, int((ox - r - x0) / CELL)); i1 = min(nx - 1, int((ox + r - x0) / CELL))
        j0 = max(0, int((oy - r - y0) / CELL)); j1 = min(ny - 1, int((oy + r - y0) / CELL))
        if i1 >= i0 and j1 >= j0 and oy - r <= y1 and oy + r >= y0 and reach[j0:j1 + 1, i0:i1 + 1].any():
            covered += 1
check(covered == 0, f'{covered} opaque front objects cover reachable route space')

# 6. export
report = dict(source_objects=NS, meltdown_objects=NM, total_objects=len(V), added_objects=len(new),
              meltdown_deco_hsv_retuned=melt_changed.get('43', 0), new_channels=len(new_channels),
              new_groups=len([g for g in new_groups if g >= 700]), front_opaque_checked=len(front_opaque),
              route_cells_reachable=reach_cells, front_objects_route_checked=front_opaque_ctr,
              ids=dict(ids.most_common()))
if gmd_path:
    f = gmd.read_gmd(gmd_path)
    check(gmd.decompress(f['k4'][1]) == level.read_text(), 'gmd does not decode to the level string')
    check(int(f['k48'][1]) == len(V), 'k48 object count mismatch')
    check(f['k45'][1] == '1569886', 'song changed')
    report['gmd'] = str(gmd_path); report['sha256'] = hashlib.sha256(gmd_path.read_bytes()).hexdigest()
    report['name'] = f['k2'][1]
report['passed'] = not fail
report['failures'] = fail[:20]
print(json.dumps(report, indent=2))
sys.exit(0 if not fail else 1)
