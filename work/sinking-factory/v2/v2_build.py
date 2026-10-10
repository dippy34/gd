"""MELTDOWN v2: Flamewall / Avernus atmosphere pass over the shipped MELTDOWN.

Gameplay is untouched: source objects are copied byte-for-byte from MELTDOWN,
which itself only retinted them. Everything added here is decoration.

Passes (each measured against the reference videos, see refs/video-targets.json):
  1. restyle   - MELTDOWN body channels pushed toward near-black warm metal
  2. bake      - per-object HSV value from a light field (fires, lava, seams)
  3+           - atmosphere objects (see atmos.py)
"""
import sys, json, math, hashlib, copy, random
from pathlib import Path
from collections import defaultdict, Counter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v2lib as L
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union

H, S, h, O = L.load_levels()
NSRC = len(S)
B = L.Builder(copy.deepcopy(O), h)
MAN = json.loads((L.SF / 'meltdown-manifest.json').read_text())
BEATS = MAN['measured_onsets']
rng = random.Random(24660)

# ------------------------------------------------------------------ geometry
# Wall bodies exactly as MELTDOWN derived them (ship + wave from the slope audit,
# robot/smelter from the source block groups).
segments = json.loads((L.SF / 'audit/slope-boundaries.json').read_text())['segments']
solid_parts = []; corridor_edges = []
for s in segments:
    x, y = s['center']
    if not 16875 <= x < 20685:
        continue
    a, b = [tuple(p) for p in s['edge']]
    if 18195 <= x < 18855:
        continue
    outer = -180 if s['side'] == 'lower' else 650
    shape = Polygon([a, b, (b[0], outer), (a[0], outer)]).intersection(box(16875, -180, 20685, 650))
    if not shape.is_valid:
        shape = shape.buffer(0)
    solid_parts.append(shape); corridor_edges.append(LineString([a, b]))
for o in S:
    x = float(o.get('2', 0)); y = float(o.get('3', 0))
    if o['1'] == '468' and 18195 <= x < 20685 and '6' not in o.get('57', '').split('.'):
        if y <= 210:
            solid_parts.append(box(x - 15, -180, x + 15, y - .8))
        elif y > 240:
            solid_parts.append(box(x - 15, y + .8, x + 15, 650))
bygroup = defaultdict(list)
for o in S:
    x = float(o.get('2', 0)); y = float(o.get('3', 0)); gg = tuple(o.get('57', '').split('.'))
    if 20685 <= x < 22665 and o['1'] in ['211', '208', '209'] and '6' not in gg:
        bygroup[gg].append(box(x - 15, y - 15, x + 15, y + 15))
smelter = [unary_union(p).buffer(0) for p in bygroup.values()]
TERRAIN = unary_union(solid_parts + smelter).buffer(0)

# Gameplay hull: every source object a player can touch or must read.
PLAY_IDS = {'1', '211', '208', '209', '94', '468', '1338', '1339', '693', '216', '217', '458', '8', '1717', '1718', '36',
            '84', '141', '1333', '1330', '1704', '1751', '35', '67', '140', '10', '11', '12', '13', '47', '111', '660',
            '745', '1331', '99', '101', '200', '201', '202', '203', '1334', '392', '2926'}
play_boxes = []
for o in S:
    if o['1'] in PLAY_IDS:
        x = float(o['2']); y = float(o['3'])
        if 16500 <= x <= 25000:
            play_boxes.append(box(x - 15, y - 15, x + 15, y + 15))
PLAY = unary_union(play_boxes)

# ------------------------------------------------------------------ 1. restyle
# Opaque body channels: darker, warmer (targets: ~50% near-black pixels, std ~0.15).
RESTYLE = {
    600: ((8, 3, 3), None, None), 601: ((15, 5, 4), None, None), 610: ((10, 3, 3), None, None),
    602: ((7, 3, 3), None, None), 603: ((17, 7, 6), None, None), 611: ((3, 2, 2), None, None),
    612: ((40, 9, 5), None, None), 613: ((84, 34, 19), None, None), 619: ((10, 5, 5), None, None),
    636: ((20, 9, 7), None, None), 637: ((14, 7, 6), None, None), 617: ((36, 15, 9), None, None),
    606: ((118, 22, 6), None, None), 608: ((78, 10, 5), None, None), 609: ((150, 66, 32), None, None),
    604: ((236, 86, 22), None, None),
    # MELTDOWN's four-quarter glows read as soft boxes; keep them but quieter.
    630: ((218, 46, 13), True, .30), 631: ((255, 102, 26), True, .34),
    # corridor seam glow carries more of the light now that the walls are darker
    639: ((226, 62, 16), True, .32),
}
BODY = {600, 601, 610, 602, 603, 611, 612, 613, 619, 636, 637, 617, 609}
EMISSIVE = {604, 605, 606, 607, 608, 614, 615, 616, 621, 623}
GLOWS = {630, 631, 632, 639}

# ------------------------------------------------------------------ 2. light field
LIGHTS = []   # (kind, geometry, intensity, sigma)
for e in MAN['emitters']:
    if e['type'] == 'fire':
        w = e['width']; hgt = e['height']
        LIGHTS.append(('fire', Point(e['x'], e['y'] + hgt * .25), .9, max(60, .36 * max(w, hgt))))
    elif e['type'] == 'sparks':
        LIGHTS.append(('spark', Point(e['x'], e['y']), .25, 55))
for f in MAN['fixtures']:
    if f['type'] == 'furnace':
        LIGHTS.append(('furnace', Point(f['x'], f['y']), .7, 120))
    elif f['type'] == 'turbine':
        LIGHTS.append(('hub', Point(f['x'], f['y']), .22, f['r'] * .7))
for x, top, bottom in [(21150, 445, 85), (22005, 480, 65), (22515, 390, 120)]:
    LIGHTS.append(('stream', LineString([(x, top), (x, bottom)]), .85, 75))
for a, b, y in [(16810, 18170, 390), (18220, 20650, 425), (20710, 22625, 520), (22700, 24630, 385)]:
    for x in range(int(a + 75), int(b - 20), 170):
        LIGHTS.append(('lamp', Point(x, y - 38), .32, 55))
for e in corridor_edges:
    LIGHTS.append(('seam', e, .30, 38))


def light_at(x, y):
    lo, hi = L.band(x)
    yrel = min(1, max(0, (y - lo) / (hi - lo)))
    amb = .06 + .30 * (1 - yrel) ** 2.2          # warm light rising from below
    tot = amb
    p = Point(x, y)
    for kind, g, inten, sig in LIGHTS:
        bx0, by0, bx1, by1 = g.bounds
        if x < bx0 - 3 * sig or x > bx1 + 3 * sig or y < by0 - 3 * sig or y > by1 + 3 * sig:
            continue
        d = g.distance(p)
        tot += inten * math.exp(-d * d / (2 * sig * sig))
    return tot


def bake():
    """Baked light: every MELTDOWN decoration object gets an HSV value from the light
    field. Metal falls to near-black away from heat; emissive paint keeps a floor so
    vents and flames still read, but only glow fully near real heat."""
    changed = 0
    for o in B.O[NSRC:]:
        if o['1'] in ('1006', '1007', '901', '1346', '2921') or o.get('21') is None:
            continue
        ch = int(o['21'])
        if o['1'] == '580':                          # stencilled labels: sink them into the dark
            o['41'] = '1'; o['43'] = L.hsv_value(.22); changed += 1
            continue
        vent_bar = o['1'] == '211' and ch in (616, 608) and o.get('24') == '-1'
        if vent_bar:
            x = float(o['2']); y = float(o['3'])
            v = max(.10, min(1.15, .06 + 1.05 * light_at(x, y)))
            o['41'] = '1'; o['43'] = L.hsv_value(v); changed += 1
            continue
        if ch in BODY:
            lo_v, base, gain, hi_v = .08, .08, 1.00, 1.35
        elif ch in EMISSIVE:
            lo_v, base, gain, hi_v = .30, .32, .95, 1.20
        elif ch in GLOWS:
            lo_v, base, gain, hi_v = .25, .22, 1.00, 1.00
        else:
            continue
        x = float(o['2']); y = float(o['3'])
        expo = .72 if x < 18195 else 1.0
        v = max(lo_v, min(hi_v, base + gain * expo * light_at(x, y)))
        o['41'] = '1'; o['43'] = L.hsv_value(v)
        changed += 1
    return changed


PASSES = ['back_haze', 'far_silhouettes', 'corridor_light', 'hot_glows', 'lava_floor', 'hangers', 'soot', 'smoke', 'embers',
          'bokeh', 'hazard_backing', 'foreground', 'front_haze', 'entry_ramp', 'exit_flare', 'pulses']


def build(stage='all', upto=None):
    import atmos as A
    n = bake()
    ctx = A.Ctx(B, S, TERRAIN, PLAY, LIGHTS, BEATS, rng)
    ctx.light_at = light_at
    ctx.reach = L.reachable(S)
    ch = A.channels(B)
    for name in PASSES:
        getattr(A, name)(ctx, ch)
        if upto and name == upto:
            break
    A.fades(ctx)
    ctx.report['baked'] = n
    return ctx, ch


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    upto = sys.argv[2] if len(sys.argv) > 2 else None
    ctx, ch = build(stage, upto)
    out = HERE / 'out' / f'v2-{stage}.level'
    out.write_text(B.level_string(RESTYLE))
    print(json.dumps(ctx.report), 'added', len(B.added), 'total', len(B.O) + len(B.added))
    print(out)
