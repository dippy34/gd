"""Same frame measurement as the one run on the reference videos, for PNG renders.

The browser version drew each video frame into a 320px-wide canvas (bilinear)
and measured luminance, near-black share, edge density, large-scale variance
share, vertical bands and chroma-weighted hue. This reproduces that math so a
render of the level can be compared number-for-number with the references.
"""
import sys, json, math
import numpy as np
from PIL import Image

def stats(img):
    img = img.convert('RGB')
    W = 320; H = round(320 * img.height / img.width)
    a = np.asarray(img.resize((W, H), Image.BILINEAR), dtype=np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    n = lum.size
    mx = a.max(-1); mn = a.min(-1); c = mx - mn
    h = np.zeros_like(c)
    m = c > 0.04
    rr = (mx == r) & m; gg = (mx == g) & m & ~rr; bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / c[rr]) % 6
    h[gg] = (b - r)[gg] / c[gg] + 2
    h[bb] = (r - g)[bb] / c[bb] + 4
    h = (h * 60 + 360) % 360
    hue = np.zeros(12)
    np.add.at(hue, (h[m] // 30).astype(int) % 12, c[m])
    hue = hue / (hue.sum() or 1)
    bands = [float(lum[int(i * H / 6):int((i + 1) * H / 6)].mean()) for i in range(6)]
    edge = float((np.abs(lum[1:-1, 2:] - lum[1:-1, :-2]) + np.abs(lum[2:, 1:-1] - lum[:-2, 1:-1])).mean())
    mean = float(lum.mean())
    BX, BY = 16, 9
    by = np.minimum(BY - 1, (np.arange(H) / H * BY).astype(int))
    bx = np.minimum(BX - 1, (np.arange(W) / W * BX).astype(int))
    idx = by[:, None] * BX + bx[None, :]
    sums = np.bincount(idx.ravel(), lum.ravel(), BX * BY); cnt = np.bincount(idx.ravel(), None, BX * BY)
    block = (sums / np.maximum(cnt, 1))[idx]
    vt = float(((lum - mean) ** 2).sum()); vl = float(((block - mean) ** 2).sum())
    q = np.quantile(lum, [.05, .25, .5, .75, .95])
    return dict(mean=round(mean, 4), q=[round(float(v), 4) for v in q], rgb=[round(float(v.mean()), 4) for v in (r, g, b)],
                black=round(float((lum < .06).mean()), 4), bright=round(float((lum > .5).mean()), 4),
                vbright=round(float((lum > .8).mean()), 4), hue=[round(float(v), 3) for v in hue],
                bands=[round(v, 4) for v in bands], edge=round(edge, 4), largeScaleVar=round(vl / vt if vt else 0, 4),
                std=round(math.sqrt(vt / n), 4))

if __name__ == '__main__':
    rows = {p: stats(Image.open(p)) for p in sys.argv[1:]}
    keys = ['mean', 'black', 'bright', 'vbright', 'edge', 'largeScaleVar', 'std']
    print(f"{'file':42}" + ''.join(f'{k:>14}' for k in keys) + '   bands(top->bottom)')
    for p, s in rows.items():
        print(f'{p[-42:]:42}' + ''.join(f'{s[k]:>14}' for k in keys) + '   ' + ' '.join(f'{v:.3f}' for v in s['bands']))
    ref = json.load(open(__file__.replace('lookstats.py', 'refs/video-targets.json')))
    for name in ['avernus', 'flamewall']:
        t = ref[name]
        print(f"{name.upper()+' median':42}" + ''.join(f'{(t[k][1] if isinstance(t[k], list) and len(t[k]) == 3 else t[k]):>14}' for k in keys) + '   ' + ' '.join(f'{v:.3f}' for v in t['bands']))
