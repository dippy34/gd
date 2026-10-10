"""Approximate GD renderer: real atlas sprites, real colour channels, real z-order.
Run with /usr/bin/python3 (has PIL + numpy)."""
import plistlib, re, sys, math, os
from pathlib import Path
from PIL import Image
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gdparse import load, parse_header, parse_ks38

RES = Path(os.environ.get('GD_RESOURCES', str(Path.home()/'Library/Application Support/Steam/steamapps/common/Geometry Dash/Geometry Dash.app/Contents/Resources'))).expanduser()
SHEETS = ['GJ_GameSheet', 'GJ_GameSheet02', 'GJ_GameSheet03', 'GJ_GameSheet04', 'GJ_GameSheetGlow']
SUF = '-hd'          # -hd sheets are 2x
PXU = 2.0            # atlas px per world unit for -hd sheets

_atlas, _frames = {}, {}
def load_atlas():
    if not (RES / 'GJ_GameSheet-hd.plist').is_file():
        raise FileNotFoundError('Set GD_RESOURCES to your own Geometry Dash Resources folder; game atlases are not bundled.')
    for s in SHEETS:
        pl = RES / f'{s}{SUF}.plist'; pn = RES / f'{s}{SUF}.png'
        if not pl.exists(): continue
        d = plistlib.load(open(pl, 'rb'))
        _atlas[s] = Image.open(pn).convert('RGBA')
        for k, v in d['frames'].items():
            if k in _frames: continue
            _frames[k] = (s, v)
def rect(s):
    return [int(n) for n in re.findall(r'-?\d+', s)]

_cache = {}
def radial(d, power=2.2):
    import numpy as np
    from PIL import Image as I
    yy, xx = np.mgrid[0:d, 0:d]
    r = np.sqrt((xx - d/2 + .5)**2 + (yy - d/2 + .5)**2) / (d/2)
    a = np.clip(1 - r, 0, 1) ** power
    arr = np.zeros((d, d, 4), 'uint8'); arr[:, :, :3] = 255
    arr[:, :, 3] = (a * 255).astype('uint8')
    return I.fromarray(arr)

SYNTH = {'__glow_small': 20, '__glow_med': 40, '__glow_large': 80}
def sprite(nm):
    if nm in _cache: return _cache[nm]
    if nm in SYNTH:
        _cache[nm] = radial(SYNTH[nm]); return _cache[nm]
    if nm not in _frames:
        _cache[nm] = None; return None
    sheet, f = _frames[nm]
    x, y, w, h = rect(f['textureRect'])
    # TexturePacker records the unrotated sprite dimensions in textureRect.
    # A rotated atlas entry occupies h by w pixels in the packed texture.
    cw, ch = (h, w) if f.get('textureRotated') else (w, h)
    img = _atlas[sheet].crop((x, y, x + cw, y + ch))
    if f.get('textureRotated'):
        img = img.transpose(Image.ROTATE_90)
    sw, sh = rect(f['spriteSourceSize'])
    ox, oy = rect(f['spriteOffset'])
    canvas = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    canvas.paste(img, (int(round((sw - w) / 2 + ox)), int(round((sh - h) / 2 - oy))))
    _cache[nm] = canvas
    return canvas

def load_names(path):
    m = {}
    for line in open(path):
        if ':' not in line: continue
        k, v = line.rsplit(':', 1); k = k.strip(); v = v.strip()
        if v.lstrip('-').isdigit(): m.setdefault(int(v), k)
    return m

# ---------- colour resolution ----------
def hsv_apply(rgb, hsv):
    import colorsys
    h, s, v, sa, va = (hsv.split('a') + ['0'] * 5)[:5]
    h = float(h); s = float(s); v = float(v); sa = sa in ('1', 'true'); va = va in ('1', 'true')
    r, g, b = [c / 255 for c in rgb]
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    hh = (hh + h / 360.0) % 1.0
    ss = min(1, max(0, ss + s if sa else ss * s))
    vv = min(1, max(0, vv + v if va else vv * v))
    r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
    return (int(r * 255), int(g * 255), int(b * 255))

class Palette:
    def __init__(self, head, objs):
        H = parse_header(head)
        self.base = {}
        for c in parse_ks38(H.get('kS38', '')):
            if '6' not in c: continue
            cid = int(c['6'])
            self.base[cid] = dict(rgb=(int(float(c.get('1', 255))), int(float(c.get('2', 255))), int(float(c.get('3', 255)))),
                                  blend=c.get('5') == '1', op=float(c.get('7', 1)),
                                  copy=int(c['9']) if c.get('9') else None, hsv=c.get('10'))
        self.trig = defaultdict(list)     # channel -> [(x, rgb, blend, op)]
        for o in objs:
            if o.get('1') == '899' and '23' in o:
                try:
                    self.trig[int(o['23'])].append((float(o['2']),
                        (int(float(o.get('7', 255))), int(float(o.get('8', 255))), int(float(o.get('9', 255)))),
                        o.get('17') == '1', float(o.get('35', 1))))
                except Exception: pass
        for k in self.trig: self.trig[k].sort()
        self.at_x = None; self._c = {}
    def set_x(self, x):
        self.at_x = x; self._c = {}
    def get(self, cid, depth=0):
        if cid in self._c: return self._c[cid]
        if depth > 6: return ((255, 255, 255), False, 1.0)
        out = None
        if self.at_x is not None and cid in self.trig:
            best = [t for t in self.trig[cid] if t[0] <= self.at_x]
            if best:
                _, rgb, bl, op = best[-1]; out = (rgb, bl, op)
        if out is None:
            b = self.base.get(cid)
            if b is None: out = ((255, 255, 255), False, 1.0)
            elif b['copy'] is not None:
                rgb, bl, op = self.get(b['copy'], depth + 1)
                if b['hsv'] and b['hsv'] != 'None': rgb = hsv_apply(rgb, b['hsv'])
                out = (rgb, b['blend'], b['op'])
            else: out = (b['rgb'], b['blend'], b['op'])
        self._c[cid] = out
        return out

def tint(img, rgb, alpha):
    r, g, b = rgb
    src = img.split()
    from PIL import ImageChops
    solid = Image.new('RGBA', img.size, (r, g, b, 255))
    out = Image.merge('RGBA', (solid.split()[0], solid.split()[1], solid.split()[2],
                               src[3].point(lambda v: int(v * alpha))))
    # Multiply each intrinsic sprite channel. This retains native portal hues
    # while giving the same result for grayscale decoration and gradients.
    rr = ImageChops.multiply(out.split()[0], src[0])
    gg = ImageChops.multiply(out.split()[1], src[1])
    bb = ImageChops.multiply(out.split()[2], src[2])
    return Image.merge('RGBA', (rr, gg, bb, out.split()[3]))

def fget(o, k, d=0.0):
    try: return float(o.get(k, d))
    except Exception: return d

def render(objs, palette, names, x0, x1, y0, y1, ppu=1.6, bg=(0,0,0), out='out.png',
           progress=False):
    W = int((x1 - x0) * ppu); Hh = int((y1 - y0) * ppu)
    import numpy as np
    acc = np.zeros((Hh, W, 3), dtype=np.float32)
    acc[:, :] = np.array(bg, dtype=np.float32)
    palette.set_x((x0 + x1) / 2)
    sel = [o for o in objs if x0 - 400 <= fget(o, '2') <= x1 + 400 and y0 - 400 <= fget(o, '3') <= y1 + 400]
    def key(o):
        # On a Z layer, blending batches are behind opaque batches in GD.
        blend = palette.get(int(fget(o, '21', 1)))[1]
        return (int(fget(o, '24', 0)), 0 if blend else 1, fget(o, '25', 0))
    sel.sort(key=key)
    drawn = 0
    for o in sel:
        oid = int(o['1'])
        nm = names.get(oid)
        if nm is None: continue
        base = sprite(nm)
        if base is None: continue
        detail = None; glowspr = None
        if not nm.startswith('__'):
            d2 = nm.replace('_001.png', '_2_001.png')
            if d2 in _frames: detail = sprite(d2)
            g = nm.replace('_001.png', '_glow_001.png')
            if o.get('96') != '1' and g in _frames: glowspr = sprite(g)
        sx = fget(o, '128', fget(o, '32', 1) or 1) or 1
        sy = fget(o, '129', sx) or sx
        if '128' not in o and '32' in o: sx = sy = fget(o, '32', 1)
        w = max(1, int(abs(base.width * sx * ppu / PXU)))
        h = max(1, int(abs(base.height * sy * ppu / PXU)))
        if w > 6000 or h > 6000: continue
        img = base.resize((w, h), Image.BILINEAR)
        if o.get('4') == '1': img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if o.get('5') == '1': img = img.transpose(Image.FLIP_TOP_BOTTOM)
        rot = fget(o, '6')
        if rot: img = img.rotate(-rot, expand=True, resample=Image.BILINEAR)
        cid = int(fget(o, '21', 1))
        rgb, blend, op = palette.get(cid)
        if '43' in o and o.get('41') == '1': rgb = hsv_apply(rgb, o['43'])
        layers = [(img, rgb, op, blend)]
        if detail is not None:
            cid2 = int(fget(o, '22', cid)); rgb2, bl2, op2 = palette.get(cid2)
            if '44' in o and o.get('42') == '1': rgb2 = hsv_apply(rgb2, o['44'])
            d = detail
            dw = max(1, int(abs(d.width * sx * ppu / PXU))); dh = max(1, int(abs(d.height * sy * ppu / PXU)))
            if dw <= 6000 and dh <= 6000:
                d = d.resize((dw, dh), Image.BILINEAR)
                if o.get('4') == '1': d = d.transpose(Image.FLIP_LEFT_RIGHT)
                if o.get('5') == '1': d = d.transpose(Image.FLIP_TOP_BOTTOM)
                if rot: d = d.rotate(-rot, expand=True, resample=Image.BILINEAR)
                layers.append((d, rgb2, op2, bl2))
        if glowspr is not None and blend:
            g = glowspr
            gw = max(1, int(abs(g.width * sx * ppu / PXU))); gh = max(1, int(abs(g.height * sy * ppu / PXU)))
            if gw <= 6000 and gh <= 6000:
                g = g.resize((gw, gh), Image.BILINEAR)
                if rot: g = g.rotate(-rot, expand=True, resample=Image.BILINEAR)
                layers.insert(0, (g, rgb, op * .8, True))
        img = tint(img, rgb, op)
        cx = (fget(o, '2') - x0) * ppu; cy = (y1 - fget(o, '3')) * ppu
        px = int(cx - img.width / 2); py = int(cy - img.height / 2)
        ax0, ay0 = max(0, px), max(0, py)
        ax1, ay1 = min(W, px + img.width), min(Hh, py + img.height)
        if ax1 <= ax0 or ay1 <= ay0: continue
        for li, (lim, lrgb, lop, lbl) in enumerate(layers):
            lim = tint(lim, lrgb, lop)
            lpx = int(cx - lim.width / 2); lpy = int(cy - lim.height / 2)
            bx0, by0 = max(0, lpx), max(0, lpy)
            bx1, by1 = min(W, lpx + lim.width), min(Hh, lpy + lim.height)
            if bx1 <= bx0 or by1 <= by0: continue
            crop = np.asarray(lim.crop((bx0 - lpx, by0 - lpy, bx1 - lpx, by1 - lpy)), dtype=np.float32)
            a = crop[:, :, 3:4] / 255.0; c = crop[:, :, :3]
            region = acc[by0:by1, bx0:bx1]
            if lbl: acc[by0:by1, bx0:bx1] = np.minimum(255.0, region + c * a)
            else:   acc[by0:by1, bx0:bx1] = region * (1 - a) + c * a
        drawn += 1
        if progress and drawn % 2000 == 0: print('  ..', drawn, file=sys.stderr)
    Image.fromarray(acc.astype('uint8')).save(out)
    return drawn, len(sel)

if __name__ == '__main__':
    load_atlas()
    names = load_names('../research/objectids.yml')
    names[1887] = '__glow_small'; names[1886] = '__glow_med'; names[1888] = '__glow_large'
    # PREVIEW ONLY: stand-ins for IDs whose sprite is generated by the game
    # (3D-line pieces, outline pieces) so composition can be judged. These do not
    # affect the built level.
    for i in (507, 508, 512, 513, 514, 578, 579, 584, 585, 587, 597):
        names.setdefault(i, 'd_gradient_c_05_001.png')
    for i in (468, 1338, 1339, 1835, 1836, 1837, 1155, 1207, 1224):
        names.setdefault(i, 'blockOutline_06_001.png')
    for i in (1353, 1354, 1743, 1744, 1790, 1792, 1804, 1833):
        names.setdefault(i, 'block009b_01_001.png')
    for i in (94, 136, 569, 902, 1099, 1202, 1220, 1510, 1511, 1755, 1758, 1760,
              1761, 1892, 2950):
        names.setdefault(i, 'square_01_001.png')
    head, objs = load(sys.argv[1] if len(sys.argv) > 1 else '../research/109381612.level')
    pal = Palette(head, objs)
    import json
    wins = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [[2000, 2600, 1000]]
    tag = sys.argv[3] if len(sys.argv) > 3 else 'kocmoc'
    for w in wins:
        a, b, yc = w[0], w[1], w[2]
        d, s = render(objs, pal, names, a, b, yc - 180, yc + 180, ppu=1.7,
                      out=f'shots/{tag}-{int(a)}.png')
        print(f'{tag} x={a}-{b} y~{yc}: drew {d}/{s}')
