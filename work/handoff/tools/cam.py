"""Where the camera actually is, per x.

The old build hung its sky at y 400-680, which is off the top of the screen for
most of the level -- only the bottom edge of each shape was ever visible. This
module is the single source of truth for the visible band, and both the builder
and the preview renderer use it.
"""
import sys
sys.path.insert(0, '.')

HALF = 165.0          # half the visible height at GD's default zoom
CUBE_CY = 95.0        # cube on the ground: the camera keeps the floor low in frame
WAVE = [(5706.9, 7466.4), (8884.7, 19456.0)]

def in_wave(x):
    return any(a <= x <= b for a, b in WAVE)

def make(T):
    """Returns cam_y(x): the centre of the visible band."""
    import bisect
    xs, ys = [], []
    x = -400.0
    while x < 20600:
        if in_wave(x):
            # only the enclosed corridor counts: a span must have solid above and
            # below it, otherwise the empty sky under the level wins every time
            spans = [s for s in T.open_spans(x, 0, 73, minrun=3)
                     if s[1] - s[0] >= 40 and not T.free(x, s[0] - 8, 0)
                     and not T.free(x, s[1] + 8, 0)]
            if spans:
                lo, hi = max(spans, key=lambda s: s[1] - s[0])
                cy = (lo + hi) / 2
            else:
                cy = 170.0
        else:
            cy = CUBE_CY
        xs.append(x); ys.append(cy); x += 30
    # smooth, because the camera does not snap
    sm = list(ys)
    for _ in range(6):
        sm = [sm[0]] + [(sm[i - 1] + 2 * sm[i] + sm[i + 1]) / 4 for i in range(1, len(sm) - 1)] + [sm[-1]]
    def cam_y(px):
        i = bisect.bisect_left(xs, px)
        i = max(0, min(len(sm) - 1, i))
        return sm[i]
    return cam_y
