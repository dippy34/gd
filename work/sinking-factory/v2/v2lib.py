"""Shared pieces for the MELTDOWN v2 atmosphere upgrade.

The base is the shipped MELTDOWN level (meltdown.level, identical to the .gmd in
Downloads). Source gameplay objects are never edited here; new objects are
decoration only (NoTouch + Passable), and every new object carries editor
layer 31 so it can be isolated in the GD editor.
"""
from pathlib import Path
import sys, math, json, bisect
from collections import defaultdict

HERE = Path(__file__).resolve().parent
SF = HERE.parent                      # work/sinking-factory
WORK = SF.parent                      # work/
sys.path.insert(0, str(WORK / 'handoff/tools'))
sys.path.insert(0, str(SF / 'vendor'))
import gdparse, gmd                   # noqa: E402

START, END = 16785.0, 24660.0
ROOT_V2 = 700                         # alpha root for everything this upgrade adds
EDITOR_LAYER = '31'

SPEED = json.loads((SF / 'inspection-plan.json').read_text())['speed_schedule']


def xt(t):
    return sum(max(0, min(t, SPEED[i + 1][0] if i + 1 < len(SPEED) else t) - a) * v for i, (a, v) in enumerate(SPEED))


def tx(x):
    for i, (t, v) in enumerate(SPEED):
        if i + 1 == len(SPEED) or x < xt(SPEED[i + 1][0]):
            return t + (x - xt(t)) / v


def fmt(v):
    if isinstance(v, float):
        s = f'{v:.4f}'.rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    return str(v)


def load_levels():
    H, S = gdparse.load(SF / 'source.level')
    h, O = gdparse.load(SF / 'meltdown.level')
    assert len(O) == 36779 and len(S) == 6620
    return H, S, h, O


# ---------------------------------------------------------------- camera
# Gamemode bounds / camera centres per stretch (world units). Ship, wave and UFO
# are bounded modes (10-block window); the robot/cube camera follows the player.
# Zoom from the source's zoom triggers: 0.75 for the ship, 1.0 after x=18195.
CAM = [  # (x, centre_y, zoom)
    # Bounded modes centre on their 10-block window: ship portal y=75 -> [0,300],
    # wave portal y=180 -> [30,330], UFO portal y=75 -> [0,300]. Robot/cube follow.
    (16785, 150, 0.75), (18180, 150, 0.75), (18195, 180, 1.0), (20670, 180, 1.0),
    (20700, 300, 1.0), (21700, 300, 1.0), (22100, 250, 1.0), (22425, 190, 1.0),
    (22665, 150, 1.0), (24660, 150, 1.0),
]


def cam(x):
    xs = [c[0] for c in CAM]
    i = max(0, min(len(CAM) - 2, bisect.bisect_right(xs, x) - 1))
    (x0, y0, z0), (x1, y1, z1) = CAM[i], CAM[i + 1]
    q = 0 if x1 == x0 else min(1, max(0, (x - x0) / (x1 - x0)))
    return y0 + (y1 - y0) * q, z0 if q < 1 else z1


def band(x, pad=0):
    cy, z = cam(x)
    hh = 160 / z + pad
    return cy - hh, cy + hh


# ---------------------------------------------------------------- builder
class Builder:
    def __init__(self, O, header):
        self.O = O
        self.head = gdparse.parse_header(header)
        self.added = []
        self.colors = {}          # cid -> dict(rgb, blend, op)
        used = {int(g) for o in O for g in o.get('57', '').split('.') if g}
        self.next_group = max(ROOT_V2, max(used)) + 1
        self.used_groups = used
        self.channels_in_use = {int(c['6']) for c in gdparse.parse_ks38(self.head['kS38']) if '6' in c}

    def group(self):
        self.next_group += 1
        return self.next_group

    def color(self, cid, rgb, blend=False, op=1.0):
        assert 650 <= cid <= 699 and cid not in self.channels_in_use, cid
        self.colors[cid] = dict(rgb=tuple(int(round(c)) for c in rgb), blend=blend, op=op)
        return cid

    def add(self, oid, x, y, ch, z, order=0, sx=1.0, sy=None, rot=0.0, groups=(), fx=False, fy=False,
            ldm=False, hsv=None, detail=None, extra=None):
        o = {'1': str(oid), '2': fmt(float(x)), '3': fmt(float(y)), '21': str(ch), '24': str(z), '25': str(order),
             '64': '1', '67': '1', '121': '1', '134': '1', '20': '0', '61': EDITOR_LAYER}
        if detail is not None:
            o['22'] = str(detail)
        if sy is None:
            sy = sx
        if abs(sx - 1) > 1e-4 or abs(sy - 1) > 1e-4:
            o['128'] = fmt(float(sx)); o['129'] = fmt(float(sy))
        if rot:
            o['6'] = fmt(float(rot))
        if fx:
            o['4'] = '1'
        if fy:
            o['5'] = '1'
        o['57'] = '.'.join(str(g) for g in dict.fromkeys([ROOT_V2, *groups]))
        if ldm:
            o['103'] = '1'
        if hsv is not None:
            o['41'] = '1'; o['43'] = hsv
        if extra:
            o.update({str(k): str(v) for k, v in extra.items()})
        self.added.append(o)
        return o

    def trigger(self, oid, x, y=None, **kw):
        o = {'1': str(oid), '2': fmt(float(x)), '3': str(y if y is not None else 1500 + 30 * (len(self.added) % 10)),
             '36': '1', '20': '0', '61': EDITOR_LAYER}
        o.update({str(k): fmt(v) if isinstance(v, float) else str(v) for k, v in kw.items()})
        self.added.append(o)
        return o

    # triggers -------------------------------------------------------
    def move(self, g, x, dx, dy, dur, easing=0, rate=2.0):
        return self.trigger(901, x, **{'51': g, '28': float(dx), '29': float(dy), '10': float(dur), '30': easing, '85': rate})

    def alpha(self, g, x, dur, op):
        return self.trigger(1007, x, **{'51': g, '10': float(dur), '35': float(op)})

    def pulse(self, ch, x, rgb, fi, hold, fo):
        return self.trigger(1006, x, **{'51': ch, '45': float(fi), '46': float(hold), '47': float(fo),
                                         '7': int(rgb[0]), '8': int(rgb[1]), '9': int(rgb[2]), '52': 0})

    def rotate(self, g, center_g, x, deg, dur, easing=0):
        return self.trigger(1346, x, **{'51': g, '71': center_g, '68': float(deg), '10': float(dur), '30': easing})

    # export ---------------------------------------------------------
    def header_string(self, restyle):
        cs = gdparse.parse_ks38(self.head['kS38'])
        out = []
        for c in cs:
            if '6' in c and int(c['6']) in restyle:
                rgb, blend, op = restyle[int(c['6'])]
                c = dict(c)
                c['1'], c['2'], c['3'] = str(rgb[0]), str(rgb[1]), str(rgb[2])
                if blend is not None:
                    c['5'] = '1' if blend else '0'
                if op is not None:
                    c['7'] = fmt(float(op))
            out.append('_'.join(f'{k}_{v}' for k, v in c.items()))
        for cid, c in sorted(self.colors.items()):
            r, g, b = c['rgb']
            out.append(f"1_{r}_2_{g}_3_{b}_4_-1_6_{cid}_7_{fmt(float(c['op']))}_15_1_18_0_8_1_5_{1 if c['blend'] else 0}")
        head = dict(self.head)
        head['kS38'] = '|'.join(out) + '|'
        return ','.join(f'{k},{v}' for k, v in head.items())

    def level_string(self, restyle):
        return self.header_string(restyle) + ';' + ''.join(','.join(f'{k},{v}' for k, v in o.items()) + ';' for o in self.O + self.added)


def hsv_value(v):
    """GD HSV string: hue shift 0, saturation x1, value multiplier v (not additive)."""
    return f'0a1a{v:.3f}a0a0'


# ---------------------------------------------------------------- reachable space
NON_WALL = {'10', '11', '12', '13', '47', '111', '660', '745', '99', '101', '200', '201', '202', '203', '1334', '36', '84',
            '141', '1333', '1330', '1704', '1751', '35', '67', '140'}
PLAY_IDS = {'1', '211', '208', '209', '94', '468', '1338', '1339', '693', '216', '217', '458', '8', '1717', '1718', '36',
            '84', '141', '1333', '1330', '1704', '1751', '35', '67', '140', '10', '11', '12', '13', '47', '111', '660',
            '745', '1331', '99', '101', '200', '201', '202', '203', '1334', '392', '2926'}
ROUTE_SECTIONS = [  # x0, x1, y0, y1, seed on the route
    (16875, 18195, 0, 300, (16890, 150)), (18195, 20685, 30, 330, (18215, 180)),
    (20685, 22665, -15, 720, (20700, 330)), (22665, 24660, 0, 300, (22680, 150)),
]


def reachable(S, cell=10):
    """Every cell a player could occupy (including dead ends), by flood fill from each
    gamemode's portal with all gameplay objects as walls. Returns a shapely geometry."""
    import numpy as np
    from shapely.geometry import box as sbox
    from shapely.ops import unary_union as uu
    walls = [(float(o['2']), float(o['3'])) for o in S if o['1'] in PLAY_IDS and o['1'] not in NON_WALL
             and '6' not in o.get('57', '').split('.') and 16500 <= float(o['2']) <= 25000]
    parts = []
    for x0, x1, y0, y1, seed in ROUTE_SECTIONS:
        nx = int((x1 - x0) / cell) + 1; ny = int((y1 - y0) / cell) + 1
        grid = np.zeros((ny, nx), dtype=np.uint8)
        for wx, wy in walls:
            if wx + 21 < x0 or wx - 21 > x1 or wy + 21 < y0 or wy - 21 > y1:
                continue
            i0 = max(0, int((wx - 21 - x0) / cell)); i1 = min(nx - 1, int((wx + 21 - x0) / cell))
            j0 = max(0, int((wy - 21 - y0) / cell)); j1 = min(ny - 1, int((wy + 21 - y0) / cell))
            grid[j0:j1 + 1, i0:i1 + 1] = 1
        reach = np.zeros_like(grid)
        si = int((seed[0] - x0) / cell); sj = int((seed[1] - y0) / cell)
        stack = [(sj, si)]
        while stack:
            j, i = stack.pop()
            if reach[j, i] or grid[j, i]:
                continue
            reach[j, i] = 1
            for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                jj, ii = j + dj, i + di
                if 0 <= jj < ny and 0 <= ii < nx and not reach[jj, ii] and not grid[jj, ii]:
                    stack.append((jj, ii))
        for j in range(ny):
            row = reach[j]
            i = 0
            while i < nx:
                if row[i]:
                    k = i
                    while k < nx and row[k]:
                        k += 1
                    parts.append(sbox(x0 + i * cell, y0 + j * cell, x0 + k * cell, y0 + (j + 1) * cell))
                    i = k
                else:
                    i += 1
    return uu(parts)
