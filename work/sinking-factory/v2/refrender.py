"""Render windows of a reference level with the atlas renderer.

Adds to render.Palette: colour triggers that copy another channel (50) with an
HSV shift (49), and trigger-less channel 1 default. Objects are pre-sorted by x
so dense levels (400k objects) render quickly.
"""
import sys, os, json, pickle, bisect, math
from pathlib import Path
HERE = Path(__file__).parent
TOOLS = HERE.parents[1] / 'handoff/tools'
sys.path.insert(0, str(TOOLS))
import gdparse, render as R
from collections import defaultdict

def load_names():
    names = R.load_names(str(HERE.parents[1] / 'handoff/research/objectids.yml'))
    names[1887] = '__glow_small'; names[1886] = '__glow_med'; names[1888] = '__glow_large'
    for i in (507, 508, 512, 513, 514, 578, 579, 584, 585, 587, 597):
        names.setdefault(i, 'd_gradient_c_05_001.png')
    for i in (468, 1338, 1339, 1835, 1836, 1837, 1155, 1207, 1224):
        names.setdefault(i, 'blockOutline_06_001.png')
    for i in (1353, 1354, 1743, 1744, 1790, 1792, 1804, 1833):
        names.setdefault(i, 'block009b_01_001.png')
    for i in (94, 136, 569, 902, 1099, 1202, 1220, 1510, 1511, 1755, 1758, 1760, 1761, 1892, 2950):
        names.setdefault(i, 'square_01_001.png')
    return names

class Pal(R.Palette):
    def __init__(self, head, objs):
        super().__init__(head, objs)
        self.trig = defaultdict(list)
        for o in objs:
            if o.get('1') != '899': continue
            try:
                cid = int(o.get('23', 1))
                self.trig[cid].append((float(o['2']),
                    (int(float(o.get('7', 255))), int(float(o.get('8', 255))), int(float(o.get('9', 255)))),
                    o.get('17') == '1', float(o.get('35', 1)), int(o['50']) if o.get('50') else None, o.get('49')))
            except Exception:
                pass
        for k in self.trig: self.trig[k].sort(key=lambda t: t[0])
    def get(self, cid, depth=0):
        if cid in self._c: return self._c[cid]
        if cid == 1010: return ((0, 0, 0), False, 1.0)        # GD special channel: Black
        if cid == 1011: return ((255, 255, 255), False, 1.0)  # GD special channel: White
        if depth > 8: return ((255, 255, 255), False, 1.0)
        out = None
        if self.at_x is not None and cid in self.trig:
            best = [t for t in self.trig[cid] if t[0] <= self.at_x]
            if best:
                _, rgb, bl, op, copy, hsv = best[-1]
                if copy:
                    rgb = self.get(copy, depth + 1)[0]
                    if hsv: rgb = R.hsv_apply(rgb, hsv)
                out = (rgb, bl, op)
        if out is None:
            out = super().get(cid, depth)
        self._c[cid] = out
        return out

class Level:
    def __init__(self, path):
        cache = Path(str(path) + '.pkl')
        if cache.exists() and cache.stat().st_mtime > Path(path).stat().st_mtime:
            self.head, self.objs = pickle.load(open(cache, 'rb'))
        else:
            self.head, self.objs = gdparse.load(path)
            pickle.dump((self.head, self.objs), open(cache, 'wb'), protocol=4)
        self.objs.sort(key=lambda o: R.fget(o, '2'))
        self.xs = [R.fget(o, '2') for o in self.objs]
        self.pal = Pal(self.head, self.objs)
    def window(self, x0, x1, margin=450):
        a = bisect.bisect_left(self.xs, x0 - margin); b = bisect.bisect_right(self.xs, x1 + margin)
        return self.objs[a:b]

TRIGGERS = {'899', '901', '1006', '1007', '1049', '1268', '1346', '1347', '1520', '1585', '1595', '1611', '1612', '1613', '1616', '1811', '1812', '1814', '1815', '1817', '1818', '1819', '1912', '1913', '1914', '1915', '1916', '1917', '1932', '1934', '1935', '2015', '2016', '2062', '2066', '2067', '2068', '2899', '2900', '2901', '2903', '2904', '2905', '2907', '2909', '2910', '2911', '2912', '2913', '2914', '2915', '2916', '2917', '2919', '2920', '2921', '2922', '2923', '2924', '2925', '2999', '3006', '3007', '3008', '3009', '3010', '3011', '3012', '3013', '3014', '3015', '3016', '3017', '3018', '3019', '3020', '3021', '3022', '3023', '3024', '3029', '3030', '3031', '3032', '3033', '3600', '3602', '3603', '3604', '3605', '3606', '3607', '3608', '3609', '3612', '3613', '3614', '3615', '3617', '3618', '3619', '3620', '3640', '3641', '3642', '3643', '3660', '3661', '3662', '31', '22', '23', '24', '25', '26', '27', '28', '32', '33', '55', '56', '57', '58', '59', '1755', '1818'}

def shot(level, names, cx, cy, out, w=570, h=320, ppu=2.0, bg=None):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    oo = [o for o in level.window(x0, x1) if o['1'] not in TRIGGERS and o.get('135') != '1']
    level.pal.set_x(cx)
    if bg is None:
        bg = level.pal.get(1000)[0]
    return R.render(oo, level.pal, names, x0, x1, y0, y1, ppu=ppu, bg=bg, out=str(out))

if __name__ == '__main__':
    R.load_atlas(); names = load_names()
    lvl = Level(sys.argv[1]); tag = sys.argv[2]
    pts = json.loads(sys.argv[3])
    od = HERE / 'shots'; od.mkdir(exist_ok=True)
    for p in pts:
        cx, cy = p[0], p[1]
        f = od / f'{tag}-{int(cx)}-{int(cy)}.png'
        d, s = shot(lvl, names, cx, cy, f)
        print(f, 'drew', d, 'of', s, flush=True)
