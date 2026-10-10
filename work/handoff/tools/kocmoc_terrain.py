"""Reads the OBSIDIAN CHOIR layout and exposes its geometry to the decorator.
Occupancy is rasterised at 5 units because the corridor tiles are music-aligned
(continuous x), not snapped to the 15-unit grid."""
import sys, math
from collections import defaultdict
sys.path.insert(0, '.')
from gdparse import load

G = 5.0
SIZES = {'1910': 15.0, '1': 30.0}

class Terrain:
    def __init__(self, path='../level/layout.level'):
        self.head, self.objs = load(path)
        self.gameplay = [o for o in self.objs
                         if not (o.get('121') == '1' and o.get('134') == '1')]
        self.cells = set()
        self.blocks = []
        for o in self.gameplay:
            base = SIZES.get(o['1'])
            if base is None: continue
            s = base * float(o.get('128', o.get('32', 1)) or 1)
            x, y = float(o['2']), float(o['3'])
            self.blocks.append((x, y, s))
            for cx in range(int(math.floor((x - s / 2) / G)), int(math.ceil((x + s / 2) / G))):
                for cy in range(int(math.floor((y - s / 2) / G)), int(math.ceil((y + s / 2) / G))):
                    self.cells.add((cx, cy))
        xs = [float(o['2']) for o in self.gameplay]
        self.x0, self.x1 = min(xs), max(xs)
        self.col = defaultdict(set)
        for cx, cy in self.cells: self.col[cx].add(cy)
        self._surf = None

    def solid_pt(self, x, y): return (int(math.floor(x / G)), int(math.floor(y / G))) in self.cells

    def free(self, x, y, pad=1):
        cx, cy = int(math.floor(x / G)), int(math.floor(y / G))
        for a in range(-pad, pad + 1):
            for b in range(-pad, pad + 1):
                if (cx + a, cy + b) in self.cells: return False
        return True

    def surfaces(self):
        """[(x, y, nx, ny)] one per exposed 5u face, sorted by x."""
        if self._surf is not None: return self._surf
        out = []
        for (cx, cy) in self.cells:
            for nx, ny in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                if (cx + nx, cy + ny) not in self.cells:
                    out.append(((cx + .5) * G + nx * G / 2, (cy + .5) * G + ny * G / 2, nx, ny))
        out.sort()
        self._surf = out
        return out

    def open_span(self, x, lo=-90, hi=200):
        cx = int(math.floor(x / G)); occ = self.col.get(cx, set())
        best = (0, 0, 0); run = None
        for r in range(lo, hi + 1):
            if r not in occ:
                if run is None: run = r
            else:
                if run is not None:
                    if r - run > best[0]: best = (r - run, run, r - 1)
                    run = None
        if run is not None and hi + 1 - run > best[0]: best = (hi + 1 - run, run, hi)
        return (best[1] * G, (best[2] + 1) * G)

    def near(self, x, y, dist=90.0):
        cx, cy = int(math.floor(x / G)), int(math.floor(y / G))
        rad = int(dist / G)
        step = max(1, rad // 6)
        for a in range(-rad, rad + 1, step):
            for b in range(-rad, rad + 1, step):
                if (cx + a, cy + b) in self.cells: return True
        return False

    def open_spans(self, x, lo=-90, hi=200, minrun=2):
        cx = int(math.floor(x / G)); occ = self.col.get(cx, set())
        out = []; run = None
        for r in range(lo, hi + 1):
            if r not in occ:
                if run is None: run = r
            else:
                if run is not None:
                    if r - run >= minrun: out.append((run * G, r * G))
                    run = None
        if run is not None and hi + 1 - run >= minrun: out.append((run * G, (hi + 1) * G))
        return out
