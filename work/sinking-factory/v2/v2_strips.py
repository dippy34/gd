"""Camera-band strips across the whole decorated window (what the player sees, end to end)."""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v2_preview as VP, v2lib as L

level = sys.argv[1]; tag = sys.argv[2]
P = VP.load(level)
R = P.R
od = HERE / 'shots' / tag; od.mkdir(parents=True, exist_ok=True)
SEGS = [(16700, 18250), (18150, 20750), (20650, 22700), (22600, 24760)]
files = []
for a, b in SEGS:
    mid = (a + b) / 2
    oo, pal = P.snapshot(mid)
    pal._c[1010] = ((0, 0, 0), False, 1); pal._c[99999] = ((255, 255, 255), False, 1)
    oo = [o for o in oo if int(o['1']) not in (1755, 2909, 2921, 1520, 1934, 1913, 1914, 31) and not P.names.get(int(o['1']), '').startswith('edit_')]
    lo = min(L.band(x)[0] for x in range(a, b, 50)); hi = max(L.band(x)[1] for x in range(a, b, 50))
    f = od / f'strip-{a}-{b}.png'
    R.render(oo, pal, P.names, a, b, lo, hi, ppu=0.7, bg=pal.get(1000)[0], out=str(f))
    im = Image.open(f); d = ImageDraw.Draw(im)
    # camera band outline (what the player sees at each x)
    for x in range(a, b, 10):
        l, h = L.band(x)
        px = (x - a) * .7
        d.point([(px, (hi - h) * .7), (px, (hi - l) * .7)], fill=(0, 255, 120))
    im.save(f); files.append(f)
    print('strip', f, im.size, flush=True)
